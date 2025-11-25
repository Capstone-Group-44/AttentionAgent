"""
This mediapipe script follows the following steps:
1. Capture video from webcam.
2. Use mediapipe to locate eyes of the user.
3. Prompt user to look at each corner of the screen. Record the coordinates of the eyes in these positions.
4. Use these cooridnates to draw a rectangle on the webcam feed representing the calibrated area.
5. Track user's eye coordinates and store them in a csv with timestamp.
   If coordinates are within the calibrated area, mark as focused (1), else not focused (0).
"""
import cv2
import mediapipe as mp
import numpy as np
import csv
from datetime import datetime
import time
import pyautogui

screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width/2)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height/2)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True, max_num_faces=1,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

calibration_data = {
    "top_left": None,
    "top_right": None,
    "bottom_left": None,
    "bottom_right": None}


csv_filename = "focus_tracker.csv"
csv_file = open(csv_filename, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "timestamp",
    "eye_center_x",
    "eye_center_y",
    "focused?"
])


for corner in calibration_data.keys():
    print(
        f"\nLOOK AT THE {corner.replace('_', ' ').upper()} CORNER AND PRESS SPACE")
    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = face_mesh.process(rgb)
        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0]
            LEFT_IRIS = [469, 470, 471, 472]
            RIGHT_IRIS = [474, 475, 476, 477]

            left_iris = np.array([((lm.landmark[i].x),
                                   (lm.landmark[i].y)) for i in LEFT_IRIS])
            right_iris = np.array([((lm.landmark[i].x),
                                    (lm.landmark[i].y)) for i in RIGHT_IRIS])

            # Compute the center (average of 4 points)
            left_center = np.mean(left_iris, axis=0)
            right_center = np.mean(right_iris, axis=0)

            iris_center = ((left_center + right_center) / 2)

        for point in calibration_data.values():
            if point is None:
                continue
            px = int(point[0] * w)
            py = int(point[1] * h)
            cv2.circle(frame, (px, py), 5, (0, 255, 0), -1)
        cv2.imshow("Iris Calibration", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32 and iris_center is not None:  # SPACE
            calibration_data[corner] = (iris_center[0], iris_center[1])
            break

        if key == 27:  # ESC
            exit()

cv2.destroyWindow("Iris Calibration")

min_x = min(calibration_data["top_left"][0], calibration_data["top_right"][0],
            calibration_data["bottom_left"][0], calibration_data["bottom_right"][0])
max_x = max(calibration_data["top_left"][0], calibration_data["top_right"][0],
            calibration_data["bottom_left"][0], calibration_data["bottom_right"][0])
min_y = min(calibration_data["top_left"][1], calibration_data["top_right"][1],
            calibration_data["bottom_left"][1], calibration_data["bottom_right"][1])
max_y = max(calibration_data["top_left"][1], calibration_data["top_right"][1],
            calibration_data["bottom_left"][1], calibration_data["bottom_right"][1])


prev_time = time.time()
LOG_INTERVAL = 0.5   # 500ms


while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    cv2.imshow("Iris Tracking", frame)
    results = face_mesh.process(rgb)
    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0]
        LEFT_IRIS = [469, 470, 471, 472]
        RIGHT_IRIS = [474, 475, 476, 477]

        left_iris = np.array([((lm.landmark[i].x),
                               (lm.landmark[i].y)) for i in LEFT_IRIS])
        right_iris = np.array([((lm.landmark[i].x),
                                (lm.landmark[i].y)) for i in RIGHT_IRIS])

        # Compute the center (average of 4 points)
        left_center = np.mean(left_iris, axis=0)
        right_center = np.mean(right_iris, axis=0)

        iris_center = ((left_center + right_center) / 2)

        now = time.time()
        if now - prev_time >= LOG_INTERVAL:

            timestamp = datetime.now().isoformat()

            if iris_center is not None:
                focused = int(min_x <= iris_center[0] <=
                              max_x and min_y <= iris_center[1] <= max_y)
            else:
                focused = 0

            csv_writer.writerow([
                timestamp,
                iris_center[0], iris_center[1],
                focused
            ])

            prev_time = now
            csv_file.flush()

    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
