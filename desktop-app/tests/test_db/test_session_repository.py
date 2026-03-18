import sqlite3

import pytest

from db.session_repository import SessionRepository


def test_start_session_creates_session_row(isolated_database, seeded_user):
    repo = SessionRepository()

    session_id = repo.start_session(
        user_id=seeded_user,
        screen_width=1920,
        screen_height=1080,
    )

    conn = sqlite3.connect(repo.db.db_path)
    row = conn.execute(
        """
        SELECT session_id, user_id, start_time, end_time, duration_seconds, screen_width, screen_height
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] == session_id
    assert row[1] == seeded_user
    assert row[2] is not None
    assert row[3] is None
    assert row[4] is None
    assert row[5] == 1920
    assert row[6] == 1080


def test_start_session_returns_unique_ids(isolated_database, seeded_user):
    repo = SessionRepository()

    first_session_id = repo.start_session(seeded_user, 1920, 1080)
    second_session_id = repo.start_session(seeded_user, 1920, 1080)

    assert first_session_id != second_session_id


def test_end_session_updates_duration_and_end_time(isolated_database, seeded_user):
    repo = SessionRepository()
    session_id = repo.start_session(seeded_user, 1366, 768)

    repo.end_session(session_id, duration_seconds=125.5)

    conn = sqlite3.connect(repo.db.db_path)
    row = conn.execute(
        """
        SELECT end_time, duration_seconds
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] is not None
    assert row[1] == 125.5


def test_start_session_rejects_unknown_user(isolated_database):
    repo = SessionRepository()

    with pytest.raises(sqlite3.IntegrityError):
        repo.start_session("missing-user", 1920, 1080)
