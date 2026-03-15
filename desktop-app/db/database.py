import sqlite3
import os

from paths import get_data_dir, resource_path

class Database:
    def __init__(self):
        self.db_path = os.path.join(get_data_dir(), "focuscam.sqlite3")
        self._initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_path, timeout=5)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self):
        conn = self.connect()
        cursor = conn.cursor()

        schema_path = resource_path(os.path.join("db", "schema.sql"))
        with open(schema_path, "r") as f:
            cursor.executescript(f.read())

        self._migrate_focus_samples(cursor)

        conn.commit()
        conn.close()

    def _migrate_focus_samples(self, cursor):
        cursor.execute("PRAGMA table_info(focus_samples)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        required_cols = {
            "face_w": "FLOAT",
            "face_h": "FLOAT",
            "left_eye_x": "FLOAT",
            "left_eye_y": "FLOAT",
            "left_eye_w": "FLOAT",
            "left_eye_h": "FLOAT",
            "right_eye_x": "FLOAT",
            "right_eye_y": "FLOAT",
            "right_eye_w": "FLOAT",
            "right_eye_h": "FLOAT",
            "left_eye_dx": "FLOAT",
            "left_eye_dy": "FLOAT",
            "right_eye_dx": "FLOAT",
            "right_eye_dy": "FLOAT",
            "sym_dx": "FLOAT",
            "sym_dy": "FLOAT",
            "yaw": "FLOAT",
            "pitch": "FLOAT",
            "roll": "FLOAT",
            "label": "INTEGER",
        }
        for col, col_type in required_cols.items():
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE focus_samples ADD COLUMN {col} {col_type}")
