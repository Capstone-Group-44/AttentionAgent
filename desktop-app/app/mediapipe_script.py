import cv2
import mediapipe as mp
import numpy as np
import sys
import os
import time
import csv

# Add the project root to sys.path to allow importing from XGBoost and db.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import Database
from db.focus_sample_repository import FocusSampleRepository
from db.session_repository import SessionRepository
from db.user_repository import UserRepository

try:
    from XGBoost.src.predict import predict_focus
except ImportError:
    # Fallback if running from root
    try:
        from src.predict import predict_focus
    except ImportError:
        print("Error: Could not import predict_focus. Make sure you are running from the project root or app directory.")
        sys.exit(1)

class FocusDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)

        # Screen dimensions (using default from example if not detectable,
        # or we could try to get actual screen size, but for consistency with model training data,
        # we might need to scale or use what the model expects.
        # The example used 1512x982. Let's stick to that or use the frame size?)
        # The model likely expects the screen size to be what the user is looking at.
        # For now, I'll use the example values as defaults but allow overrides.
        self.screen_width = 1920
        self.screen_height = 1080

        self._init_db()
        self._init_session()

    def _init_db(self):
        self.db = Database()
        self.user_repo = UserRepository()
        self.session_repo = SessionRepository()
        self.focus_repo = FocusSampleRepository()

    def _init_session(self):
        username = os.environ.get("ATTAGENT_USERNAME", "local_user")
        user_id = self._get_or_create_user(username)
        self.session_start_time = time.time()
        self.session_id = self.session_repo.start_session(user_id, self.screen_width, self.screen_height)

    def _get_or_create_user(self, username):
        user = self.user_repo.get_user_by_username(username)
        if user:
            return user[0]
        display_name = username
        email = f"{username}@local"
        return self.user_repo.create_user(username, display_name, email)

    def _save_sample(self, sample, focused_prediction, focused_probability):
        attention_state = "UNKNOWN"
        focus_score = None
        if focused_prediction is not None:
            attention_state = "FOCUSED" if focused_prediction else "NOT_FOCUSED"
            focus_score = focused_probability

        self.focus_repo.insert_sample(
            self.session_id,
            time.time(),
            sample["left_gaze_x"],
            sample["left_gaze_y"],
            sample["right_gaze_x"],
            sample["right_gaze_y"],
            sample["face_x"],
            sample["face_y"],
            sample["face_z"],
            attention_state,
            focus_score,
        )

    def _close_db(self):
        if getattr(self, "session_id", None) and getattr(self, "session_start_time", None):
            duration = time.time() - self.session_start_time
            self.session_repo.end_session(self.session_id, duration)
        self._export_csv()

    def _export_csv(self):
        db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db"))
        csv_path = os.path.join(db_dir, "focus_samples.csv")
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM focus_samples ORDER BY timestamp ASC")
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        conn.close()

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Wrote CSV to {csv_path}")

    def get_landmark_coords(self, landmarks, idx, width, height):
        return (landmarks[idx].x * width, landmarks[idx].y * height)

    def get_iris_center(self, landmarks, iris_indices, width, height):
        # Average the landmarks for the iris
        x_coords = [landmarks[i].x for i in iris_indices]
        y_coords = [landmarks[i].y for i in iris_indices]
        avg_x = sum(x_coords) / len(x_coords)
        avg_y = sum(y_coords) / len(y_coords)
        return avg_x * width, avg_y * height

    def run(self):
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        print("Starting Focus Detector... Press 'q' to quit.")

        try:
            while self.cap.isOpened():
                success, image = self.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                # To improve performance, optionally mark the image as not writeable to pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(image)

                # Draw the face mesh annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                img_h, img_w, _ = image.shape

                focus_status = "Unknown"
                focus_prob = None
                is_focused = None

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        landmarks = face_landmarks.landmark

                        # Extract features required by the model
                        # Left Iris: 468, 469, 470, 471, 472
                        # Right Iris: 473, 474, 475, 476, 477

                        left_gaze_x, left_gaze_y = self.get_iris_center(landmarks, [468, 469, 470, 471, 472], img_w, img_h)
                        right_gaze_x, right_gaze_y = self.get_iris_center(landmarks, [473, 474, 475, 476, 477], img_w, img_h)

                        # Face center (using nose tip - landmark 1)
                        face_x, face_y = self.get_landmark_coords(landmarks, 1, img_w, img_h)
                        face_z = landmarks[1].z # Z is relative depth

                        scale_x = self.screen_width / img_w
                        scale_y = self.screen_height / img_h

                        left_gaze_x  *= scale_x
                        right_gaze_x *= scale_x
                        face_x       *= scale_x

                        left_gaze_y  *= scale_y
                        right_gaze_y *= scale_y
                        face_y       *= scale_y

                        # Construct sample
                        sample = {
                            "screen_width": self.screen_width,
                            "screen_height": self.screen_height,
                            "left_gaze_x": left_gaze_x,
                            "left_gaze_y": left_gaze_y,
                            "right_gaze_x": right_gaze_x,
                            "right_gaze_y": right_gaze_y,
                            "face_x": face_x,
                            "face_y": face_y,
                            "face_z": face_z,
                        }

                        print("LIVE SAMPLE:", sample)

                        try:
                            prediction_results = predict_focus([sample])
                            if prediction_results:
                                result = prediction_results[0]
                                is_focused = result["focused_prediction"]
                                focus_prob = result["focused_probability"]
                                focus_status = "FOCUSED" if is_focused else "NOT FOCUSED"

                                # Print to terminal (optional, maybe throttle this)
                                # print(f"Status: {focus_status}, Prob: {focus_prob:.4f}")

                        except Exception as e:
                            print(f"Prediction error: {e}")

                        # Draw gaze points
                        cv2.circle(image, (int(left_gaze_x), int(left_gaze_y)), 3, (255, 255, 0), -1)
                        cv2.circle(image, (int(right_gaze_x), int(right_gaze_y)), 3, (255, 255, 0), -1)
                        cv2.circle(image, (int(face_x), int(face_y)), 3, (255, 0, 255), -1)

                        self._save_sample(sample, is_focused, focus_prob)

                        color = (0, 255, 0) if focus_status == "FOCUSED" else (0, 0, 255)
                        cv2.putText(image, f"Status: {focus_status}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                        if focus_prob is not None:
                            cv2.putText(image, f"Prob: {focus_prob:.2f}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


                cv2.imshow('Attention Agent - Focus Detector', image)
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
        finally:
            self.cap.release()
            self._close_db()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = FocusDetector()
    detector.run()
