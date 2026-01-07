import uuid
from .database import Database

class SessionRepository:
    def __init__(self):
        self.db = Database()

    def start_session(self, user_id, screen_width, screen_height):
        conn = self.db.connect()
        cur = conn.cursor()

        session_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO sessions (session_id, user_id, start_time, screen_width, screen_height)
            VALUES (?, ?, datetime('now'), ?, ?)
        """, (session_id, user_id, screen_width, screen_height))

        conn.commit()
        conn.close()

        return session_id

    def end_session(self, session_id, duration_seconds):
        conn = self.db.connect()
        cur = conn.cursor()

        cur.execute("""
            UPDATE sessions
            SET end_time = datetime('now'),
                duration_seconds = ?
            WHERE session_id = ?
        """, (duration_seconds, session_id))

        conn.commit()
        conn.close()
