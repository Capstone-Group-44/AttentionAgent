import cv2
import mediapipe as mp
import numpy as np
import csv
from datetime import datetime
import time
import pyautogui

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True, max_num_faces=1,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

screen_width, screen_height = pyautogui.size()

csv_filename = "iris_focus_tracking.csv"
csv_file = open(csv_filename, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "timestamp",
    "left_gaze_x", "left_gaze_y",
    "right_gaze_x", "right_gaze_y",
    "focused?"
])

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


def get_gaze(frame, results, w, h):
    if not results.multi_face_landmarks:
        return None, None, None, None

    lm = results.multi_face_landmarks[0]

    LEFT_IRIS = [469, 470, 471, 472]
    RIGHT_IRIS = [474, 475, 476, 477]

    left_iris = np.array([(int(lm.landmark[i].x * w),
                           int(lm.landmark[i].y * h)) for i in LEFT_IRIS])
    right_iris = np.array([(int(lm.landmark[i].x * w),
                            int(lm.landmark[i].y * h)) for i in RIGHT_IRIS])

    (l_cx, l_cy), _ = cv2.minEnclosingCircle(left_iris)
    (r_cx, r_cy), _ = cv2.minEnclosingCircle(right_iris)

    nose = lm.landmark[1]
    face_x = nose.x * w
    face_y = nose.y * h

    left_offset_x = l_cx - face_x
    left_offset_y = l_cy - face_y
    right_offset_x = r_cx - face_x
    right_offset_y = r_cy - face_y

    left_gaze_x = face_x * (screen_width / w) + \
        left_offset_x * (screen_width / w)
    left_gaze_y = face_y * (screen_height / h) + \
        left_offset_y * (screen_height / h)
    right_gaze_x = face_x * (screen_width / w) + \
        right_offset_x * (screen_width / w)
    right_gaze_y = face_y * (screen_height / h) + \
        right_offset_y * (screen_height / h)

    return left_gaze_x, left_gaze_y, right_gaze_x, right_gaze_y


def calibrate_corner(prompt):
    print(f"\nLOOK AT THE {prompt.upper()} CORNER AND PRESS SPACE")
    while True:
        success, frame = cap.read()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        cv2.putText(frame, f"Look at {prompt} corner, press SPACE",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

        cv2.imshow("Calibration", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 32:  # SPACE
            gaze = get_gaze(frame, results, w, h)
            if gaze[0] is not None:
                return gaze

        if key == 27:  # ESC
            exit()


print("\nCALIBRATION STARTED")
tl = calibrate_corner("TOP-LEFT")
tr = calibrate_corner("TOP-RIGHT")
bl = calibrate_corner("BOTTOM-LEFT")
br = calibrate_corner("BOTTOM-RIGHT")

cv2.destroyWindow("Calibration")

all_x = [tl[0], tr[0], bl[0], br[0], tl[2], tr[2], bl[2], br[2]]
all_y = [tl[1], tr[1], bl[1], br[1], tl[3], tr[3], bl[3], br[3]]

min_x, max_x = min(all_x), max(all_x)
min_y, max_y = min(all_y), max(all_y)


def screen_to_cam_x(sx):
    return int((sx / screen_width) * w)


def screen_to_cam_y(sy):
    return int((sy / screen_height) * h)


print("\nCalibration complete! Tracking started...\n")


prev_time = time.time()
LOG_INTERVAL = 0.5   # 500ms

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    left_x = left_y = right_x = right_y = None
    gaze = get_gaze(frame, results, w, h)

    if gaze[0] is not None:
        left_x, left_y, right_x, right_y = gaze

    cam_x1 = screen_to_cam_x(min_x)
    cam_x2 = screen_to_cam_x(max_x)
    cam_y1 = screen_to_cam_y(min_y)
    cam_y2 = screen_to_cam_y(max_y)

    cv2.rectangle(frame, (cam_x1, cam_y1), (cam_x2, cam_y2),
                  (0, 255, 0), 2)

    now = time.time()
    if now - prev_time >= LOG_INTERVAL:

        timestamp = datetime.now().isoformat()

        if left_x is not None:
            focused = int(min_x <= left_x <=
                          max_x and min_y <= left_y <= max_y)
        else:
            focused = 0

        csv_writer.writerow([
            timestamp,
            left_x, left_y,
            right_x, right_y,
            focused
        ])

        prev_time = now

    cv2.imshow("Iris Tracking", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
csv_file.close()

print(f"Saved to {csv_filename}")
