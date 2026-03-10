import os
import time
from datetime import datetime, timezone
from threading import Event
from typing import Callable, Optional

import cv2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from db.focus_sample_repository import FocusSampleRepository
from ml_runner_scripts.FocusPredictor import FocusPredictor


class FocusTrackingWorker:
    def __init__(
        self,
        *,
        user_id: str,
        session_id: str,
        stop_event: Event,
        sample_callback: Optional[Callable[[int, float, float], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.stop_event = stop_event
        self.sample_callback = sample_callback
        self.error_callback = error_callback

        self._sample_repo = FocusSampleRepository()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._model_path = os.getenv(
            "FOCUS_MODEL_PATH",
            os.path.join(base_dir, "ml_dev_scripts", "models", "xgb_model_subject_3.json"),
        )
        self._firebase_key_path = os.getenv(
            "FIREBASE_KEY_PATH",
            os.path.join(
                base_dir,
                "keys",
                "attention-agent-30bd0-firebase-adminsdk-fbsvc-1274d6f933.json",
            ),
        )
        self._firebase_project_id = os.getenv("FIREBASE_PROJECT_ID", "attention-agent-30bd0")
        self._show_preview = os.getenv("FOCUS_SHOW_PREVIEW", "1").strip() not in {"0", "false", "False"}

    def _emit_error(self, message: str):
        if self.error_callback:
            self.error_callback(message)

    def _init_firestore(self):
        if not os.path.exists(self._firebase_key_path):
            return None

        try:
            try:
                app = firebase_admin.get_app()
            except ValueError:
                cred = credentials.Certificate(self._firebase_key_path)
                app = firebase_admin.initialize_app(cred, {"projectId": self._firebase_project_id})
            return firestore.client(app=app)
        except Exception as exc:
            self._emit_error(f"Firestore initialization failed: {exc}")
            return None

    def _upsert_session_to_firestore(self, db):
        if db is None:
            return
        try:
            db.collection("sessions").document(self.session_id).set(
                {
                    "userId": self.user_id,
                    "sessionId": self.session_id,
                    "startTime": datetime.now(timezone.utc),
                    "createdAt": firestore.SERVER_TIMESTAMP,
                },
                merge=True,
            )
        except Exception as exc:
            self._emit_error(f"Failed to write session to Firestore: {exc}")

    def _push_sample_to_firestore(
        self,
        db,
        *,
        sample_id: str,
        ts: float,
        left_x: float,
        left_y: float,
        right_x: float,
        right_y: float,
        face_x: float,
        face_y: float,
        face_z: float,
        attention_state: int,
        focus_score: float,
        face_w: float,
        face_h: float,
        left_eye_x: float,
        left_eye_y: float,
        left_eye_w: float,
        left_eye_h: float,
        right_eye_x: float,
        right_eye_y: float,
        right_eye_w: float,
        right_eye_h: float,
        left_eye_dx: float,
        left_eye_dy: float,
        right_eye_dx: float,
        right_eye_dy: float,
        sym_dx: float,
        sym_dy: float,
        yaw: float,
        pitch: float,
        roll: float,
        label: int,
    ):
        if db is None:
            return
        try:
            db.collection("sessions").document(self.session_id).collection("focusSamples").document(
                sample_id
            ).set(
                {
                    "timestamp": ts,
                    "timestampIso": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
                    "leftIrisX": left_x,
                    "leftIrisY": left_y,
                    "rightIrisX": right_x,
                    "rightIrisY": right_y,
                    "faceX": face_x,
                    "faceY": face_y,
                    "faceW": face_w,
                    "faceH": face_h,
                    "leftEyeX": left_eye_x,
                    "leftEyeY": left_eye_y,
                    "leftEyeW": left_eye_w,
                    "leftEyeH": left_eye_h,
                    "rightEyeX": right_eye_x,
                    "rightEyeY": right_eye_y,
                    "rightEyeW": right_eye_w,
                    "rightEyeH": right_eye_h,
                    "leftEyeDx": left_eye_dx,
                    "leftEyeDy": left_eye_dy,
                    "rightEyeDx": right_eye_dx,
                    "rightEyeDy": right_eye_dy,
                    "symDx": sym_dx,
                    "symDy": sym_dy,
                    "yaw": yaw,
                    "pitch": pitch,
                    "roll": roll,
                    "label": int(label),
                    "faceZ": face_z,
                    "attentionState": int(attention_state),
                    "focusScore": float(focus_score),
                    "sessionId": self.session_id,
                    "userId": self.user_id,
                },
                merge=True,
            )
        except Exception as exc:
            self._emit_error(f"Failed to write sample to Firestore: {exc}")

    def _iris_center(self, landmarks, indices):
        x = sum(landmarks[i].x for i in indices) / len(indices)
        y = sum(landmarks[i].y for i in indices) / len(indices)
        return x, y

    def run(self):
        if not os.path.exists(self._model_path):
            self._emit_error(f"Model not found at: {self._model_path}")
            return

        predictor = None
        cap = None
        firestore_db = self._init_firestore()
        db_path = self._sample_repo.db.db_path
        print(f"[FocusTrackingWorker] model_path={self._model_path}")
        print(f"[FocusTrackingWorker] sqlite_db_path={db_path}")
        print(f"[FocusTrackingWorker] firebase_key_path={self._firebase_key_path}")
        if firestore_db is None:
            print("[FocusTrackingWorker] Firestore disabled/unavailable for this session.")
        else:
            print(f"[FocusTrackingWorker] Firestore enabled for project={self._firebase_project_id}")
            self._upsert_session_to_firestore(firestore_db)
        left_iris_indices = [469, 470, 471, 472]
        right_iris_indices = [474, 475, 476, 477]
        preview_window_name = "FocusCam Live"

        try:
            predictor = FocusPredictor(self._model_path)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self._emit_error("Unable to access webcam.")
                return

            while not self.stop_event.is_set():
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.01)
                    continue

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = predictor.face_mesh.process(rgb)
                if not results.multi_face_landmarks:
                    continue

                landmarks = results.multi_face_landmarks[0].landmark
                img_h, img_w = frame.shape[:2]

                features = predictor.extract_features(landmarks, img_w, img_h)
                attention_state, focus_score = predictor.predict(features)
                ts = time.time()

                (
                    feat_face_x, feat_face_y, feat_face_w, feat_face_h,
                    feat_left_eye_x, feat_left_eye_y, feat_left_eye_w, feat_left_eye_h,
                    feat_right_eye_x, feat_right_eye_y, feat_right_eye_w, feat_right_eye_h,
                    feat_left_eye_dx, feat_left_eye_dy,
                    feat_right_eye_dx, feat_right_eye_dy,
                    feat_sym_dx, feat_sym_dy,
                    feat_yaw, feat_pitch, feat_roll,
                ) = features

                left_x, left_y = self._iris_center(landmarks, left_iris_indices)
                right_x, right_y = self._iris_center(landmarks, right_iris_indices)
                nose_z = landmarks[1].z

                sample_id = self._sample_repo.insert_sample(
                    session_id=self.session_id,
                    timestamp=ts,
                    left_x=left_x,
                    left_y=left_y,
                    right_x=right_x,
                    right_y=right_y,
                    face_x=float(feat_face_x),
                    face_y=float(feat_face_y),
                    face_z=nose_z,
                    attention_state=int(attention_state),
                    focus_score=float(focus_score),
                    face_w=float(feat_face_w),
                    face_h=float(feat_face_h),
                    left_eye_x=float(feat_left_eye_x),
                    left_eye_y=float(feat_left_eye_y),
                    left_eye_w=float(feat_left_eye_w),
                    left_eye_h=float(feat_left_eye_h),
                    right_eye_x=float(feat_right_eye_x),
                    right_eye_y=float(feat_right_eye_y),
                    right_eye_w=float(feat_right_eye_w),
                    right_eye_h=float(feat_right_eye_h),
                    left_eye_dx=float(feat_left_eye_dx),
                    left_eye_dy=float(feat_left_eye_dy),
                    right_eye_dx=float(feat_right_eye_dx),
                    right_eye_dy=float(feat_right_eye_dy),
                    sym_dx=float(feat_sym_dx),
                    sym_dy=float(feat_sym_dy),
                    yaw=float(feat_yaw),
                    pitch=float(feat_pitch),
                    roll=float(feat_roll),
                    label=int(attention_state),
                )

                self._push_sample_to_firestore(
                    firestore_db,
                    sample_id=sample_id,
                    ts=ts,
                    left_x=left_x,
                    left_y=left_y,
                    right_x=right_x,
                    right_y=right_y,
                    face_x=float(feat_face_x),
                    face_y=float(feat_face_y),
                    face_z=nose_z,
                    attention_state=int(attention_state),
                    focus_score=float(focus_score),
                    face_w=float(feat_face_w),
                    face_h=float(feat_face_h),
                    left_eye_x=float(feat_left_eye_x),
                    left_eye_y=float(feat_left_eye_y),
                    left_eye_w=float(feat_left_eye_w),
                    left_eye_h=float(feat_left_eye_h),
                    right_eye_x=float(feat_right_eye_x),
                    right_eye_y=float(feat_right_eye_y),
                    right_eye_w=float(feat_right_eye_w),
                    right_eye_h=float(feat_right_eye_h),
                    left_eye_dx=float(feat_left_eye_dx),
                    left_eye_dy=float(feat_left_eye_dy),
                    right_eye_dx=float(feat_right_eye_dx),
                    right_eye_dy=float(feat_right_eye_dy),
                    sym_dx=float(feat_sym_dx),
                    sym_dy=float(feat_sym_dy),
                    yaw=float(feat_yaw),
                    pitch=float(feat_pitch),
                    roll=float(feat_roll),
                    label=int(attention_state),
                )

                if self.sample_callback:
                    self.sample_callback(int(attention_state), float(focus_score), ts)

                if self._show_preview:
                    state_text = "FOCUSED" if int(attention_state) == 1 else "DISTRACTED"
                    color = (0, 200, 0) if int(attention_state) == 1 else (0, 0, 255)
                    cv2.putText(
                        frame,
                        f"State: {state_text}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        color,
                        2,
                    )
                    cv2.putText(
                        frame,
                        f"Score: {float(focus_score):.3f}",
                        (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 255, 255),
                        2,
                    )
                    cv2.putText(
                        frame,
                        f"State value: {int(attention_state)}",
                        (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (255, 255, 0),
                        2,
                    )
                    cv2.imshow(preview_window_name, frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        self._show_preview = False
                        cv2.destroyWindow(preview_window_name)

                time.sleep(0.03)
        except Exception as exc:
            self._emit_error(f"Tracking worker failed: {exc}")
        finally:
            if cap is not None:
                cap.release()
            if self._show_preview:
                cv2.destroyAllWindows()
            if predictor is not None and getattr(predictor, "face_mesh", None) is not None:
                predictor.face_mesh.close()
