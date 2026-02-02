import uuid
from datetime import datetime
from .database import Database

class UserRepository:
    def __init__(self):
        self.db = Database()

    def create_user_with_id(self, user_id, username, display_name, email, created_at=None):
        conn = self.db.connect()
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE users
                SET username = ?, display_name = ?, email = ?
                WHERE user_id = ?
            """, (username, display_name, email, user_id))
        else:
            if created_at is None:
                created_at = datetime.utcnow().isoformat()
            cur.execute("""
                INSERT INTO users (user_id, username, display_name, email, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, display_name, email, created_at))

        conn.commit()
        conn.close()
        return user_id

    def create_user(self, username, display_name, email):
        conn = self.db.connect()
        cur = conn.cursor()

        user_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO users (user_id, username, display_name, email)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, display_name, email))

        conn.commit()
        conn.close()

        return user_id

    def get_user_by_id(self, user_id):
        conn = self.db.connect()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cur.fetchone()

        conn.close()
        return user

    def get_user_by_username(self, username):
        conn = self.db.connect()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        conn.close()
        return user
