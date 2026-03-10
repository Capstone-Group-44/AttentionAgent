"""
File Name: data_collection.py
Description: This script is responsible for collecting eye gaze and head pose data using a webcam. 
It utilizes MediaPipe for facial landmark detection and OpenCV for video capture and processing. 
The collected data  is saved into a CSV file for further analysis or model training.
"""
import cv2
import mediapipe as mp
import csv
import time


OUTPUT_CSV = "attention_dataset.csv"
FRAME_RATE = 30  # data is collected 30 times per second
LABELS = {"FOCUSED": 1, "NOT_FOCUSED": 0}

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
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

header = [
    "timestamp",
    "face_x", "face_y", "face_w", "face_h",
    "left_eye_x", "left_eye_y", "left_eye_w", "left_eye_h",
    "right_eye_x", "right_eye_y", "right_eye_w", "right_eye_h",
    "left_eye_dx", "left_eye_dy",
    "right_eye_dx", "right_eye_dy",
    "sym_dx", "sym_dy",
    "yaw", "pitch", "roll",
    "label"
]

with open(OUTPUT_CSV, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)


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

    # Yaw: horizontal difference of eyes
    yaw = right_eye.x - left_eye.x  # positive = looking left, negative = right

    # Pitch: vertical difference nose vs chin
    pitch = chin.y - nose.y  # positive = head down, negative = head up

    # Roll: tilt of eyes line
    roll = (right_eye.y - left_eye.y) / ((right_eye.x - left_eye.x) + 1e-6)

    return float(yaw), float(pitch), float(roll)


cap = cv2.VideoCapture(0)
prev_time = 0
current_label = LABELS["FOCUSED"]

print("Instructions:")
print("Press 'f' = label FOCUSED")
print("Press 'n' = label NOT_FOCUSED")
print("Press 'q' = quit")

with open(OUTPUT_CSV, mode="a", newline="") as f:
    writer = csv.writer(f)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if time.time() - prev_time < 1 / FRAME_RATE:
            continue
        prev_time = time.time()

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

            timestamp = time.time()

            writer.writerow([
                timestamp,
                fx, fy, fw, fh,
                lex, ley, lew, leh,
                rex, rey, rew, reh,
                left_eye_dx, left_eye_dy,
                right_eye_dx, right_eye_dy,
                sym_dx, sym_dy,
                yaw, pitch, roll,
                current_label
            ])

        cv2.imshow("Webcam", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('f'):
            current_label = LABELS["FOCUSED"]
            print("Label set to FOCUSED")
        elif key == ord('n'):
            current_label = LABELS["NOT_FOCUSED"]
            print("Label set to NOT_FOCUSED")
        elif key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
face_mesh.close()
