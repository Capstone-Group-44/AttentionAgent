import cv2
import mediapipe as mp
import numpy as np
import csv
import time
import pyautogui  # for getting screen size

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True, max_num_faces=1,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

# Get screen size dynamically
screen_width, screen_height = pyautogui.size()
print(f"Detected screen size: {screen_width} x {screen_height}")

# Open CSV file for writing
csv_filename = "iris_face_tracking.csv"
csv_file = open(csv_filename, mode="w", newline="")
csv_writer = csv.writer(csv_file)

# Write header
csv_writer.writerow([
    "timestamp",
    "screen_width", "screen_height",
    "left_gaze_x", "left_gaze_y",
    "right_gaze_x", "right_gaze_y",
    "face_x", "face_y",
    "face_z",
    "focused?"
])

# Start camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

prev_record_time = time.time()
csv_start_time = None  # mark when to start writing

# Focus tracking
focus_mode = False
buffered_rows = []

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    current_time = time.time()

    # Set CSV start time when window first opens
    if csv_start_time is None:
        csv_start_time = current_time

    # Default values in case face is not detected
    left_gaze_x = left_gaze_y = None
    right_gaze_x = right_gaze_y = None
    face_screen_x = face_screen_y = face_z = None

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        # Face center (nose tip)
        nose_tip = face_landmarks.landmark[1]
        face_x, face_y, face_z = nose_tip.x, nose_tip.y, nose_tip.z
        face_screen_x = face_x * screen_width
        face_screen_y = face_y * screen_height

        # Iris landmarks
        LEFT_IRIS = [469, 470, 471, 472]
        RIGHT_IRIS = [474, 475, 476, 477]

        left_iris = np.array([(int(face_landmarks.landmark[i].x * w),
                               int(face_landmarks.landmark[i].y * h)) for i in LEFT_IRIS])
        right_iris = np.array([(int(face_landmarks.landmark[i].x * w),
                                int(face_landmarks.landmark[i].y * h)) for i in RIGHT_IRIS])

        (l_cx, l_cy), _ = cv2.minEnclosingCircle(left_iris)
        (r_cx, r_cy), _ = cv2.minEnclosingCircle(right_iris)

        # Draw iris positions
        cv2.circle(frame, (int(l_cx), int(l_cy)), 2, (0, 255, 0), -1)
        cv2.circle(frame, (int(r_cx), int(r_cy)), 2, (0, 255, 0), -1)
        cv2.circle(frame, (int(face_x * w), int(face_y * h)),
                   3, (255, 0, 0), -1)

        # Gaze estimation: iris position relative to face
        # These are offsets from face center in camera pixels
        face_center_x = face_x * w
        face_center_y = face_y * h

        left_offset_x = l_cx - face_center_x
        left_offset_y = l_cy - face_center_y
        right_offset_x = r_cx - face_center_x
        right_offset_y = r_cy - face_center_y

        # Map offsets to screen coordinates
        # Assume camera frame roughly covers full screen; scaling by screen size / frame size
        left_gaze_x = face_screen_x + left_offset_x * (screen_width / w)
        left_gaze_y = face_screen_y + left_offset_y * (screen_height / h)
        right_gaze_x = face_screen_x + right_offset_x * (screen_width / w)
        right_gaze_y = face_screen_y + right_offset_y * (screen_height / h)

    # Only record after 5 seconds of window being open
    if current_time - csv_start_time >= 5:
        if current_time - prev_record_time >= 0.05:  # 50 ms interval
            timestamp = round(current_time, 3)
            row = [
                timestamp,
                screen_width, screen_height,
                left_gaze_x, left_gaze_y,
                right_gaze_x, right_gaze_y,
                face_screen_x, face_screen_y,
                face_z,
                False  # default focused
            ]

            # Buffer rows if focus mode active
            if focus_mode:
                buffered_rows.append(row)
            else:
                csv_writer.writerow(row)

            prev_record_time = current_time

    cv2.imshow("Iris + Face Tracking", frame)
    key = cv2.waitKey(1) & 0xFF

    # ESC to exit
    if key == 27:
        break
    # F pressed -> start focus
    elif key == ord('f'):
        focus_mode = True
        buffered_rows = []
        print("🔵 Focus started")
    # N pressed -> end focus, mark buffered rows as focused
    elif key == ord('n') and focus_mode:
        focus_mode = False
        for row in buffered_rows:
            row[-1] = True
            csv_writer.writerow(row)
        buffered_rows = []
        print("🟢 Focus ended, rows marked as True")

cap.release()
cv2.destroyAllWindows()
csv_file.close()
print(f"✅ Data saved to {csv_filename}")
