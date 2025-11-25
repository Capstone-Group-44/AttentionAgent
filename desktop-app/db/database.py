import sqlite3
import os

class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, "focuscam.sqlite3")
        self._initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self):
        conn = self.connect()
        cursor = conn.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as f:
            cursor.executescript(f.read())

        conn.commit()
        conn.close()
