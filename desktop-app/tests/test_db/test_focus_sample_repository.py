import sqlite3
import time

import pytest

from db.focus_sample_repository import FocusSampleRepository
from db.session_repository import SessionRepository


def _create_session(user_id):
    session_repo = SessionRepository()
    return session_repo.start_session(user_id=user_id, screen_width=1920, screen_height=1080)


def test_insert_sample_persists_expected_fields(isolated_database, seeded_user):
    session_id = _create_session(seeded_user)
    repo = FocusSampleRepository()
    timestamp = time.time()

    sample_id = repo.insert_sample(
        session_id=session_id,
        timestamp=timestamp,
        left_x=0.11,
        left_y=0.22,
        right_x=0.33,
        right_y=0.44,
        face_x=10.0,
        face_y=20.0,
        face_z=30.0,
        attention_state=1,
        focus_score=0.87,
        face_w=100.0,
        face_h=120.0,
        left_eye_x=12.0,
        left_eye_y=24.0,
        left_eye_w=30.0,
        left_eye_h=18.0,
        right_eye_x=60.0,
        right_eye_y=24.0,
        right_eye_w=30.0,
        right_eye_h=18.0,
        left_eye_dx=1.1,
        left_eye_dy=1.2,
        right_eye_dx=1.3,
        right_eye_dy=1.4,
        sym_dx=0.4,
        sym_dy=0.5,
        yaw=2.0,
        pitch=3.0,
        roll=4.0,
        label=1,
    )

    conn = sqlite3.connect(repo.db.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT
            focus_sample_id, session_id, timestamp,
            face_w, face_h,
            left_eye_x, left_eye_y, left_eye_w, left_eye_h,
            right_eye_x, right_eye_y, right_eye_w, right_eye_h,
            left_eye_dx, left_eye_dy, right_eye_dx, right_eye_dy,
            sym_dx, sym_dy, yaw, pitch, roll, label,
            left_iris_x, left_iris_y, right_iris_x, right_iris_y,
            face_x, face_y, face_z,
            attention_state, focus_score
        FROM focus_samples
        WHERE focus_sample_id = ?
        """,
        (sample_id,),
    ).fetchone()
    conn.close()

    assert row is not None
    row = dict(row)
    assert row == {
        "focus_sample_id": sample_id,
        "session_id": session_id,
        "timestamp": timestamp,
        "face_w": 100.0,
        "face_h": 120.0,
        "left_eye_x": 12.0,
        "left_eye_y": 24.0,
        "left_eye_w": 30.0,
        "left_eye_h": 18.0,
        "right_eye_x": 60.0,
        "right_eye_y": 24.0,
        "right_eye_w": 30.0,
        "right_eye_h": 18.0,
        "left_eye_dx": 1.1,
        "left_eye_dy": 1.2,
        "right_eye_dx": 1.3,
        "right_eye_dy": 1.4,
        "sym_dx": 0.4,
        "sym_dy": 0.5,
        "yaw": 2.0,
        "pitch": 3.0,
        "roll": 4.0,
        "label": 1,
        "left_iris_x": 0.11,
        "left_iris_y": 0.22,
        "right_iris_x": 0.33,
        "right_iris_y": 0.44,
        "face_x": 10.0,
        "face_y": 20.0,
        "face_z": 30.0,
        "attention_state": 1,
        "focus_score": 0.87,
    }


def test_insert_sample_stores_null_for_omitted_optional_fields(isolated_database, seeded_user):
    session_id = _create_session(seeded_user)
    repo = FocusSampleRepository()
    timestamp = time.time()

    sample_id = repo.insert_sample(
        session_id=session_id,
        timestamp=timestamp,
        left_x=0.11,
        left_y=0.22,
        right_x=0.33,
        right_y=0.44,
        face_x=10.0,
        face_y=20.0,
        face_z=30.0,
        attention_state=0,
        focus_score=0.12,
    )

    conn = sqlite3.connect(repo.db.db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """
        SELECT *
        FROM focus_samples
        WHERE focus_sample_id = ?
        """,
        (sample_id,),
    ).fetchone()
    conn.close()

    assert row is not None
    row = dict(row)
    assert row["focus_sample_id"] == sample_id
    assert row["session_id"] == session_id
    assert row["timestamp"] == timestamp
    assert row["left_iris_x"] == 0.11
    assert row["left_iris_y"] == 0.22
    assert row["right_iris_x"] == 0.33
    assert row["right_iris_y"] == 0.44
    assert row["face_x"] == 10.0
    assert row["face_y"] == 20.0
    assert row["face_z"] == 30.0
    assert row["attention_state"] == 0
    assert row["focus_score"] == 0.12
    assert row["face_w"] is None
    assert row["face_h"] is None
    assert row["left_eye_x"] is None
    assert row["left_eye_y"] is None
    assert row["left_eye_w"] is None
    assert row["left_eye_h"] is None
    assert row["right_eye_x"] is None
    assert row["right_eye_y"] is None
    assert row["right_eye_w"] is None
    assert row["right_eye_h"] is None
    assert row["left_eye_dx"] is None
    assert row["left_eye_dy"] is None
    assert row["right_eye_dx"] is None
    assert row["right_eye_dy"] is None
    assert row["sym_dx"] is None
    assert row["sym_dy"] is None
    assert row["yaw"] is None
    assert row["pitch"] is None
    assert row["roll"] is None
    assert row["label"] is None


def test_insert_sample_rejects_unknown_session(isolated_database):
    repo = FocusSampleRepository()

    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_sample(
            session_id="missing-session",
            timestamp=time.time(),
            left_x=0.1,
            left_y=0.2,
            right_x=0.3,
            right_y=0.4,
            face_x=1.0,
            face_y=2.0,
            face_z=3.0,
            attention_state=0,
            focus_score=0.25,
        )


def test_get_recent_attention_states_returns_only_matching_session(isolated_database, seeded_user):
    target_session_id = _create_session(seeded_user)
    other_session_id = _create_session(seeded_user)
    repo = FocusSampleRepository()
    current_time = time.time()

    repo.insert_sample(
        session_id=target_session_id,
        timestamp=current_time - 5,
        left_x=0.1,
        left_y=0.2,
        right_x=0.3,
        right_y=0.4,
        face_x=1.0,
        face_y=2.0,
        face_z=3.0,
        attention_state=1,
        focus_score=0.8,
    )
    repo.insert_sample(
        session_id=target_session_id,
        timestamp=current_time - 1,
        left_x=0.1,
        left_y=0.2,
        right_x=0.3,
        right_y=0.4,
        face_x=1.0,
        face_y=2.0,
        face_z=3.0,
        attention_state=0,
        focus_score=0.2,
    )
    repo.insert_sample(
        session_id=other_session_id,
        timestamp=current_time - 1,
        left_x=0.1,
        left_y=0.2,
        right_x=0.3,
        right_y=0.4,
        face_x=1.0,
        face_y=2.0,
        face_z=3.0,
        attention_state=1,
        focus_score=0.9,
    )

    states = repo.get_recent_attention_states(target_session_id, seconds_ago=10)

    assert states == [1, 0]


def test_get_recent_attention_states_respects_time_cutoff(isolated_database, seeded_user):
    session_id = _create_session(seeded_user)
    repo = FocusSampleRepository()
    current_time = time.time()

    repo.insert_sample(
        session_id=session_id,
        timestamp=current_time - 60,
        left_x=0.1,
        left_y=0.2,
        right_x=0.3,
        right_y=0.4,
        face_x=1.0,
        face_y=2.0,
        face_z=3.0,
        attention_state=1,
        focus_score=0.8,
    )
    repo.insert_sample(
        session_id=session_id,
        timestamp=current_time - 2,
        left_x=0.1,
        left_y=0.2,
        right_x=0.3,
        right_y=0.4,
        face_x=1.0,
        face_y=2.0,
        face_z=3.0,
        attention_state=0,
        focus_score=0.2,
    )

    states = repo.get_recent_attention_states(session_id, seconds_ago=10)

    assert states == [0]
