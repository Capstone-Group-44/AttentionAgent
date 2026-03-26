import os
import sqlite3

import pytest

from db.database import Database


@pytest.fixture
def test_db_path(tmp_path):
    return tmp_path / "focuscam_test.sqlite3"


@pytest.fixture
def isolated_database(monkeypatch, test_db_path):
    def fake_init(self):
        self.db_path = os.fspath(test_db_path)
        self._initialize()

    monkeypatch.setattr(Database, "__init__", fake_init)
    Database()
    return test_db_path


@pytest.fixture
def db_connection(isolated_database):
    conn = sqlite3.connect(os.fspath(isolated_database))
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


@pytest.fixture
def seeded_user(db_connection):
    user_id = "user-123"
    db_connection.execute(
        """
        INSERT INTO users (user_id, username, display_name, email)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, "testuser", "Test User", "test@example.com"),
    )
    db_connection.commit()
    return user_id
