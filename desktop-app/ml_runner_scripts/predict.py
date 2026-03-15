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
    "loso_results_3",
    "xgb_model_subject_2.json"
))

print("Looking for model at:", MODEL_PATH)
model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

FRAME_RATE = 30

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
        face_cx = fx + fw / 2
        face_cy = fy + fh / 2

        left_eye_lms = get_eye_landmarks(landmarks, LEFT_EYE_IDX)
        lex, ley, lew, leh = normalized_bbox(left_eye_lms)
        lex_c = lex + lew / 2
        ley_c = ley + leh / 2

        right_eye_lms = get_eye_landmarks(landmarks, RIGHT_EYE_IDX)
        rex, rey, rew, reh = normalized_bbox(right_eye_lms)
        rex_c = rex + rew / 2
        rey_c = rey + reh / 2

        left_eye_dx = lex_c - face_cx
        left_eye_dy = ley_c - face_cy
        right_eye_dx = rex_c - face_cx
        right_eye_dy = rey_c - face_cy

        sym_dx = left_eye_dx - right_eye_dx
        sym_dy = left_eye_dy - right_eye_dy

        yaw, pitch, roll = compute_head_pose(landmarks)

        features = np.array([[
            fx, fy, fw, fh,
            lex, ley, lew, leh,
            rex, rey, rew, reh,
            left_eye_dx, left_eye_dy,
            right_eye_dx, right_eye_dy,
            sym_dx, sym_dy,
            yaw, pitch, roll
        ]])

        pred = model.predict(features)[0]

        if pred == 1:
            prediction_text = "FOCUSED"
        else:
            prediction_text = "NOT FOCUSED"

    cv2.putText(frame, prediction_text, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    cv2.imshow("Attention Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
face_mesh.close()
