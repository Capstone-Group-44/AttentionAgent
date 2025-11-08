import cv2
import mediapipe as mp
import numpy as np
import csv
import time
import pyautogui  # for getting screen size

# Initialize MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

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
    "left_iris_x", "left_iris_y",
    "right_iris_x", "right_iris_y",
    "face_x", "face_y",
    "face_z",
    "focused?"
])

# Start camera
cap = cv2.VideoCapture(0)
prev_time = time.time()

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        face_landmarks = results.multi_face_landmarks[0]

        # Get iris landmarks
        LEFT_IRIS = [469, 470, 471, 472]
        RIGHT_IRIS = [474, 475, 476, 477]

        left_iris = np.array([(int(face_landmarks.landmark[i].x * w),
                               int(face_landmarks.landmark[i].y * h)) for i in LEFT_IRIS])
        right_iris = np.array([(int(face_landmarks.landmark[i].x * w),
                                int(face_landmarks.landmark[i].y * h)) for i in RIGHT_IRIS])

        (l_cx, l_cy), _ = cv2.minEnclosingCircle(left_iris)
        (r_cx, r_cy), _ = cv2.minEnclosingCircle(right_iris)

        #  Get face center landmark (e.g., tip of nose) 
        nose_tip = face_landmarks.landmark[1]
        face_x, face_y, face_z = nose_tip.x, nose_tip.y, nose_tip.z

        # Draw iris positions on screen 
        cv2.circle(frame, (int(l_cx), int(l_cy)), 2, (0, 255, 0), -1)
        cv2.circle(frame, (int(r_cx), int(r_cy)), 2, (0, 255, 0), -1)
        cv2.circle(frame, (int(face_x * w), int(face_y * h)), 3, (255, 0, 0), -1)

        # Normalize iris & face positions to screen size 
        left_iris_screen_x = (l_cx / w) * screen_width
        left_iris_screen_y = (l_cy / h) * screen_height
        right_iris_screen_x = (r_cx / w) * screen_width
        right_iris_screen_y = (r_cy / h) * screen_height

        face_screen_x = face_x * screen_width
        face_screen_y = face_y * screen_height

        # Write to CSV 
        timestamp = round(time.time() - prev_time, 3)
        csv_writer.writerow([
            timestamp,
            screen_width, screen_height,
            round(left_iris_screen_x, 2), round(left_iris_screen_y, 2),
            round(right_iris_screen_x, 2), round(right_iris_screen_y, 2),
            round(face_screen_x, 2), round(face_screen_y, 2),
            round(face_z, 4)
        ])

    cv2.imshow("Iris + Face Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to stop
        break

cap.release()
cv2.destroyAllWindows()
csv_file.close()
print(f"✅ Data saved to {csv_filename}")
