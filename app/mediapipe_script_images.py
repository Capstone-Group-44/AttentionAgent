import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from pathlib import Path
import pyautogui

IMAGE_DIR = Path(
    "C:/Uni Tests, Assignments, Labs/Capstone Project/Images Dataset/test")
INPUT_CSV = Path(
    "C:/Uni Tests, Assignments, Labs/Capstone Project/Images Dataset/test/_annotations.csv")
OUTPUT_CSV = Path(
    "C:/Uni Tests, Assignments, Labs/Capstone Project/Images Dataset/test/_annotations_updated.csv")
# Folder to save proof images
PROOF_DIR = IMAGE_DIR / "mediapipe_proof"
PROOF_DIR.mkdir(exist_ok=True)

LEFT_IRIS = [469, 470, 471, 472]
RIGHT_IRIS = [474, 475, 476, 477]

screen_width, screen_height = pyautogui.size()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    refine_landmarks=True,
    max_num_faces=1,
    min_detection_confidence=0.5
)

df = pd.read_csv(INPUT_CSV)

new_cols = [
    "left_gaze_x", "left_gaze_y",
    "right_gaze_x", "right_gaze_y",
    "face_x", "face_y", "face_z"
]
for col in new_cols:
    df[col] = np.nan

for idx, row in df.iterrows():
    img_path = IMAGE_DIR / row["filename"]

    image = cv2.imread(str(img_path))
    if image is None:
        continue

    h, w, _ = image.shape
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        continue

    face_landmarks = results.multi_face_landmarks[0]

    nose_tip = face_landmarks.landmark[1]
    face_x, face_y, face_z = nose_tip.x, nose_tip.y, nose_tip.z

    left_iris = np.array([
        (face_landmarks.landmark[i].x * w,
         face_landmarks.landmark[i].y * h)
        for i in LEFT_IRIS
    ])
    right_iris = np.array([
        (face_landmarks.landmark[i].x * w,
         face_landmarks.landmark[i].y * h)
        for i in RIGHT_IRIS
    ])

    (l_cx, l_cy), _ = cv2.minEnclosingCircle(left_iris.astype(np.float32))
    (r_cx, r_cy), _ = cv2.minEnclosingCircle(right_iris.astype(np.float32))

    face_center_x = face_x * w
    face_center_y = face_y * h

    # Draw visuals for first 50 images to validate mediapipe results
    if idx < 50:
        vis = image.copy()

        # Left eye – green
        cv2.circle(vis, (int(l_cx), int(l_cy)), 5, (0, 255, 0), -1)
        cv2.putText(vis, "Left Eye", (int(l_cx) + 5, int(l_cy) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        # Right eye – red
        cv2.circle(vis, (int(r_cx), int(r_cy)), 5, (0, 0, 255), -1)
        cv2.putText(vis, "Right Eye", (int(r_cx) + 5, int(r_cy) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # Nose center – blue
        cv2.circle(vis, (int(face_center_x), int(
            face_center_y)), 6, (255, 0, 0), -1)
        cv2.putText(vis, "Nose", (int(face_center_x) + 5, int(face_center_y) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        # Save images with annotations
        cv2.imwrite(str(PROOF_DIR / row["filename"]), vis)

    left_offset_x = l_cx - face_center_x
    left_offset_y = l_cy - face_center_y
    right_offset_x = r_cx - face_center_x
    right_offset_y = r_cy - face_center_y

    left_gaze_x = (face_x * screen_width) + left_offset_x * (screen_width / w)
    left_gaze_y = (face_y * screen_height) + \
        left_offset_y * (screen_height / h)
    right_gaze_x = (face_x * screen_width) + \
        right_offset_x * (screen_width / w)
    right_gaze_y = (face_y * screen_height) + \
        right_offset_y * (screen_height / h)

    df.loc[idx, new_cols] = [
        left_gaze_x, left_gaze_y,
        right_gaze_x, right_gaze_y,
        face_x, face_y, face_z
    ]

df.to_csv(OUTPUT_CSV, index=False)

print(f"Updated CSV saved to {OUTPUT_CSV}")
print(f"Proof images saved to {PROOF_DIR}")
