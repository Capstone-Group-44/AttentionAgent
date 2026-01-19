import uuid
from .database import Database

class FocusSampleRepository:
    def __init__(self):
        self.db = Database()

    def insert_sample(
        self, session_id, timestamp,
        left_x, left_y, right_x, right_y,
        face_x, face_y, face_z,
        attention_state, focus_score
    ):
        conn = self.db.connect()
        try:
            cur = conn.cursor()

            sample_id = str(uuid.uuid4())

            cur.execute("""
                INSERT INTO focus_samples (
                    focus_sample_id, session_id, timestamp,
                    left_iris_x, left_iris_y,
                    right_iris_x, right_iris_y,
                    face_x, face_y, face_z,
                    attention_state, focus_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sample_id, session_id, timestamp,
                left_x, left_y, right_x, right_y,
                face_x, face_y, face_z,
                attention_state, focus_score
            ))

            conn.commit()
            return sample_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
