import time
import uuid
from .database import Database

class FocusSampleRepository:
    def __init__(self):
        self.db = Database()

    def insert_sample(
        self, session_id, timestamp,
        left_x, left_y, right_x, right_y,
        face_x, face_y, face_z,
        attention_state, focus_score,
        face_w=None, face_h=None,
        left_eye_x=None, left_eye_y=None, left_eye_w=None, left_eye_h=None,
        right_eye_x=None, right_eye_y=None, right_eye_w=None, right_eye_h=None,
        left_eye_dx=None, left_eye_dy=None,
        right_eye_dx=None, right_eye_dy=None,
        sym_dx=None, sym_dy=None,
        yaw=None, pitch=None, roll=None,
        label=None,
    ):
        conn = self.db.connect()
        try:
            cur = conn.cursor()

            sample_id = str(uuid.uuid4())

            cur.execute("""
                INSERT INTO focus_samples (
                    focus_sample_id, session_id, timestamp,
                    face_x, face_y, face_w, face_h,
                    left_eye_x, left_eye_y, left_eye_w, left_eye_h,
                    right_eye_x, right_eye_y, right_eye_w, right_eye_h,
                    left_eye_dx, left_eye_dy, right_eye_dx, right_eye_dy,
                    sym_dx, sym_dy, yaw, pitch, roll, label,
                    left_iris_x, left_iris_y,
                    right_iris_x, right_iris_y,
                    face_z,
                    attention_state, focus_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample_id, session_id, timestamp,
                face_x, face_y, face_w, face_h,
                left_eye_x, left_eye_y, left_eye_w, left_eye_h,
                right_eye_x, right_eye_y, right_eye_w, right_eye_h,
                left_eye_dx, left_eye_dy, right_eye_dx, right_eye_dy,
                sym_dx, sym_dy, yaw, pitch, roll, label,
                left_x, left_y, right_x, right_y,
                face_z,
                attention_state, focus_score
            ))

            conn.commit()
            return sample_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_recent_attention_states(self, session_id, seconds_ago=30):
        """Return a list of attention_state values recorded in the last *seconds_ago* seconds."""
        cutoff = time.time() - seconds_ago
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT attention_state FROM focus_samples "
                "WHERE session_id = ? AND timestamp >= ?",
                (session_id, cutoff),
            )
            return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()
