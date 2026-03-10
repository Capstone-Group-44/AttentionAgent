import cv2
import mediapipe as mp
import numpy as np
import csv
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

HEAD_LANDMARKS = [1, 152, 234, 454]
HEAD_NAMES = ["nose_tip", "chin", "left_temple", "right_temple"]

LEFT_EYE_LANDMARKS = [33, 133, 159, 145, 469, 470, 471, 472]
LEFT_EYE_NAMES = [
    "left_eye_outer", "left_eye_inner", "left_eye_upper", "left_eye_lower",
    "left_iris_1", "left_iris_2", "left_iris_3", "left_iris_4"
]

RIGHT_EYE_LANDMARKS = [362, 263, 386, 374, 474, 475, 476, 477]
RIGHT_EYE_NAMES = [
    "right_eye_outer", "right_eye_inner", "right_eye_upper", "right_eye_lower",
    "right_iris_1", "right_iris_2", "right_iris_3", "right_iris_4"
]

ALL_LANDMARKS = HEAD_LANDMARKS + LEFT_EYE_LANDMARKS + RIGHT_EYE_LANDMARKS
ALL_NAMES = HEAD_NAMES + LEFT_EYE_NAMES + RIGHT_EYE_NAMES

csv_filename = "eye_head_tracking_labeled.csv"
csv_file = open(csv_filename, mode="w", newline="")
csv_writer = csv.writer(csv_file)

header = ["timestamp"]
for name in ALL_NAMES:
    header += [f"{name}_x", f"{name}_y", f"{name}_z"]
header += ["focused"]
csv_writer.writerow(header)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

focus_mode = False
buffered_rows = []

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to read from camera.")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    timestamp = round(time.time(), 3)

    row = [timestamp]

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        for idx in ALL_LANDMARKS:
            lm = face_landmarks.landmark[idx]
            row += [lm.x, lm.y, lm.z]

        left_iris_pts = np.array([[face_landmarks.landmark[i].x * w,
                                   face_landmarks.landmark[i].y * h] for i in LEFT_EYE_LANDMARKS[4:]], dtype=np.float32)

        right_iris_pts = np.array([[face_landmarks.landmark[i].x * w,
                                    face_landmarks.landmark[i].y * h] for i in RIGHT_EYE_LANDMARKS[4:]], dtype=np.float32)

        if len(left_iris_pts) > 0:
            (l_cx, l_cy), _ = cv2.minEnclosingCircle(left_iris_pts)
            cv2.circle(frame, (int(l_cx), int(l_cy)), 2, (0, 255, 0), -1)
        else:
            l_cx = l_cy = None

        if len(right_iris_pts) > 0:
            (r_cx, r_cy), _ = cv2.minEnclosingCircle(right_iris_pts)
            cv2.circle(frame, (int(r_cx), int(r_cy)), 2, (0, 255, 0), -1)
        else:
            r_cx = r_cy = None

    else:
        row += [None] * (len(ALL_LANDMARKS) * 3)

    row.append(0)

    if focus_mode:
        buffered_rows.append(row)
    else:
        csv_writer.writerow(row)

    cv2.imshow("Eyes + Head Tracking", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC → exit
        break
    elif key == ord('f'):  # start focus
        focus_mode = True
        buffered_rows = []
        print("Focus started")
    elif key == ord('n') and focus_mode:  # end focus
        focus_mode = False
        for row_buf in buffered_rows:
            row_buf[-1] = 1
            csv_writer.writerow(row_buf)
        buffered_rows = []
        print("Focus ended, rows marked as 1")

cap.release()
cv2.destroyAllWindows()
csv_file.close()
print(f"Data saved to {csv_filename}")
