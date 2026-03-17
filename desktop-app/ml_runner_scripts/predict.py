import cv2
import os
import mediapipe as mp
import numpy as np
import time
import xgboost as xgb

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.abspath(os.path.join(
    BASE_DIR,
    "..",
    "ml_dev_scripts",
    "docs",
    "loso_results_11",
    "xgb_model_subject_2_tuned.json"
))

print("Looking for model at:", MODEL_PATH)
model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

FRAME_RATE = 30
BUFFER_LEN = 5
THRESHOLD = 0.45  # Best threshold from training

LEFT_EYE_IDX = [33, 133, 159, 145, 153, 154]
RIGHT_EYE_IDX = [362, 263, 386, 374, 380, 381]
NOSE_IDX = 1
CHIN_IDX = 199
LEFT_EYE_CORNER_IDX = 33
RIGHT_EYE_CORNER_IDX = 263

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True
)

yaw_buf, pitch_buf, roll_buf = [], [], []
left_eye_motion_buf, right_eye_motion_buf = [], []
eye_gaze_mag_buf = []

prev_yaw, prev_pitch, prev_roll = 0, 0, 0
prev_left_dx, prev_left_dy = 0, 0
prev_right_dx, prev_right_dy = 0, 0


def normalized_bbox(landmarks):
    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    return x_min, y_min, x_max - x_min, y_max - y_min


def get_eye_landmarks(landmarks, indices):
    return [landmarks[i] for i in indices]


def compute_head_pose(landmarks):
    nose = landmarks[NOSE_IDX]
    chin = landmarks[CHIN_IDX]
    left_eye = landmarks[LEFT_EYE_CORNER_IDX]
    right_eye = landmarks[RIGHT_EYE_CORNER_IDX]
    yaw = right_eye.x - left_eye.x
    pitch = chin.y - nose.y
    roll = (right_eye.y - left_eye.y) / ((right_eye.x - left_eye.x) + 1e-6)
    return float(yaw), float(pitch), float(roll)


cap = cv2.VideoCapture(0)
prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    if time.time() - prev_time < 1 / FRAME_RATE:
        continue
    prev_time = time.time()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    prediction_text = "No Face"

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        fx, fy, fw, fh = normalized_bbox(landmarks)
        face_cx, face_cy = fx + fw/2, fy + fh/2

        # Left eye
        left_eye_lms = get_eye_landmarks(landmarks, LEFT_EYE_IDX)
        lex, ley, lew, leh = normalized_bbox(left_eye_lms)
        lex_c, ley_c = lex + lew/2, ley + leh/2

        # Right eye
        right_eye_lms = get_eye_landmarks(landmarks, RIGHT_EYE_IDX)
        rex, rey, rew, reh = normalized_bbox(right_eye_lms)
        rex_c, rey_c = rex + rew/2, rey + reh/2

        left_dx = lex_c - face_cx
        left_dy = ley_c - face_cy
        right_dx = rex_c - face_cx
        right_dy = rey_c - face_cy
        sym_dx = left_dx - right_dx
        sym_dy = left_dy - right_dy

        yaw, pitch, roll = compute_head_pose(landmarks)
        yaw_vel = yaw - prev_yaw
        pitch_vel = pitch - prev_pitch
        roll_vel = roll - prev_roll
        prev_yaw, prev_pitch, prev_roll = yaw, pitch, roll

        left_eye_motion = np.sqrt(
            (left_dx - prev_left_dx)**2 + (left_dy - prev_left_dy)**2)
        right_eye_motion = np.sqrt(
            (right_dx - prev_right_dx)**2 + (right_dy - prev_right_dy)**2)
        prev_left_dx, prev_left_dy = left_dx, left_dy
        prev_right_dx, prev_right_dy = right_dx, right_dy

        for buf, val in zip([yaw_buf, pitch_buf, roll_buf, left_eye_motion_buf, right_eye_motion_buf],
                            [yaw, pitch, roll, left_eye_motion, right_eye_motion]):
            buf.append(val)
            if len(buf) > BUFFER_LEN:
                buf.pop(0)

        yaw_std_5 = np.std(yaw_buf) if len(yaw_buf) == BUFFER_LEN else 0
        pitch_std_5 = np.std(pitch_buf) if len(pitch_buf) == BUFFER_LEN else 0
        eye_motion_mean_5 = np.mean(left_eye_motion_buf) if len(
            left_eye_motion_buf) == BUFFER_LEN else 0

        left_ear = leh / (lew + 1e-6)
        right_ear = reh / (rew + 1e-6)
        eye_ear_mean = (left_ear + right_ear) / 2

        left_dx_center = left_dx
        left_dy_center = left_dy
        right_dx_center = right_dx
        right_dy_center = right_dy

        left_eye_gaze_mag = np.sqrt(left_dx_center**2 + left_dy_center**2)
        right_eye_gaze_mag = np.sqrt(right_dx_center**2 + right_dy_center**2)
        eye_gaze_mag_mean = (left_eye_gaze_mag + right_eye_gaze_mag)/2

        eye_gaze_mag_buf.append(eye_gaze_mag_mean)
        if len(eye_gaze_mag_buf) > BUFFER_LEN:
            eye_gaze_mag_buf.pop(0)
        eye_gaze_mag_std_5 = np.std(eye_gaze_mag_buf) if len(
            eye_gaze_mag_buf) == BUFFER_LEN else 0

        features = np.array([[
            fx, fy, fw, fh,
            lex, ley, lew, leh,
            rex, rey, rew, reh,
            left_dx, left_dy,
            right_dx, right_dy,
            sym_dx, sym_dy,
            yaw, pitch, roll,
            yaw_vel, pitch_vel, roll_vel,
            left_eye_motion, right_eye_motion,
            yaw_std_5, pitch_std_5, eye_motion_mean_5,
            left_ear, right_ear, eye_ear_mean,
            left_dx_center, left_dy_center, right_dx_center, right_dy_center,
            left_eye_gaze_mag, right_eye_gaze_mag, eye_gaze_mag_mean,
            eye_gaze_mag_std_5
        ]])

        prob = model.predict_proba(features)[0, 1]
        prediction_text = "FOCUSED" if prob > THRESHOLD else "NOT FOCUSED"

    cv2.putText(frame, prediction_text, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Attention Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
face_mesh.close()
