import os
import socket
import sqlite3
import uuid
from datetime import datetime, timezone
from threading import Event
from unittest.mock import MagicMock

import firebase_admin
import pytest
from firebase_admin import delete_app, firestore

from db.database import Database
from scripts import build_reports
from services.focus_tracking_worker import FocusTrackingWorker


def _emulator_host():
    host = os.getenv("FIRESTORE_EMULATOR_HOST")
    if not host:
        pytest.skip("Set FIRESTORE_EMULATOR_HOST to run Firestore emulator integration tests.")
    return host


def _assert_emulator_reachable(host):
    hostname, port = host.split(":", 1)
    with socket.create_connection((hostname, int(port)), timeout=1):
        return


@pytest.fixture
def firestore_emulator_client():
    host = _emulator_host()
    try:
        _assert_emulator_reachable(host)
    except OSError as exc:
        pytest.skip(f"Firestore emulator at {host} is not reachable: {exc}")

    project_id = os.getenv("FIRESTORE_EMULATOR_PROJECT_ID", "attention-agent-test")
    app = firebase_admin.initialize_app(
        options={"projectId": project_id},
        name=f"test-{uuid.uuid4()}",
    )
    client = firestore.client(app=app)

    try:
        yield client
    finally:
        delete_app(app)


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
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def seeded_user(db_connection):
    user_id = "user-firestore-test"
    db_connection.execute(
        """
        INSERT INTO users (user_id, username, display_name, email)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, "firestoreuser", "Firestore User", "firestore@example.com"),
    )
    db_connection.commit()
    return user_id


@pytest.fixture
def worker(monkeypatch):
    monkeypatch.setattr("services.focus_tracking_worker.FocusSampleRepository", MagicMock())
    return FocusTrackingWorker(
        user_id="user-firestore-test",
        session_id=f"session-{uuid.uuid4()}",
        stop_event=Event(),
        error_callback=MagicMock(),
    )


def test_upsert_session_to_firestore_writes_document(worker, firestore_emulator_client):
    session_ref = firestore_emulator_client.collection("sessions").document(worker.session_id)
    session_ref.delete()

    worker._upsert_session_to_firestore(firestore_emulator_client)

    snapshot = session_ref.get()
    assert snapshot.exists

    data = snapshot.to_dict()
    assert data["userId"] == worker.user_id
    assert data["sessionId"] == worker.session_id
    assert data["startTime"] is not None
    assert data["createdAt"] is not None

    session_ref.delete()


def test_push_sample_to_firestore_writes_nested_document(worker, firestore_emulator_client):
    sample_id = f"sample-{uuid.uuid4()}"
    sample_ref = (
        firestore_emulator_client.collection("sessions")
        .document(worker.session_id)
        .collection("focusSamples")
        .document(sample_id)
    )
    sample_ref.delete()

    worker._push_sample_to_firestore(
        firestore_emulator_client,
        sample_id=sample_id,
        ts=1710000000.5,
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

    snapshot = sample_ref.get()
    assert snapshot.exists

    data = snapshot.to_dict()
    assert data == {
        "timestamp": datetime.fromtimestamp(1710000000.5, tz=timezone.utc),
        "timestampEpoch": 1710000000.5,
        "timestampIso": "2024-03-09T16:00:00.500000+00:00",
        "leftIrisX": 0.11,
        "leftIrisY": 0.22,
        "rightIrisX": 0.33,
        "rightIrisY": 0.44,
        "faceX": 10.0,
        "faceY": 20.0,
        "faceW": 100.0,
        "faceH": 120.0,
        "leftEyeX": 12.0,
        "leftEyeY": 24.0,
        "leftEyeW": 30.0,
        "leftEyeH": 18.0,
        "rightEyeX": 60.0,
        "rightEyeY": 24.0,
        "rightEyeW": 30.0,
        "rightEyeH": 18.0,
        "leftEyeDx": 1.1,
        "leftEyeDy": 1.2,
        "rightEyeDx": 1.3,
        "rightEyeDy": 1.4,
        "symDx": 0.4,
        "symDy": 0.5,
        "yaw": 2.0,
        "pitch": 3.0,
        "roll": 4.0,
        "label": 1,
        "faceZ": 30.0,
        "attentionState": 1,
        "focusScore": 0.87,
        "sessionId": worker.session_id,
        "userId": worker.user_id,
    }

    sample_ref.delete()
    firestore_emulator_client.collection("sessions").document(worker.session_id).delete()


def test_sync_report_for_session_writes_report_document(
    monkeypatch,
    firestore_emulator_client,
    db_connection,
    seeded_user,
    isolated_database,
):
    session_id = f"session-{uuid.uuid4()}"
    report_ref = firestore_emulator_client.collection("reports").document(session_id)
    report_ref.delete()

    db_connection.execute(
        """
        INSERT INTO sessions (session_id, user_id, start_time, end_time, duration_seconds, screen_width, screen_height)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, seeded_user, "2026-03-16T10:00:00+00:00", "2026-03-16T10:00:06+00:00", 6.0, 1920, 1080),
    )
    db_connection.executemany(
        """
        INSERT INTO focus_samples (
            focus_sample_id, session_id, timestamp,
            left_iris_x, left_iris_y, right_iris_x, right_iris_y,
            face_x, face_y, face_z,
            attention_state, focus_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (f"sample-{uuid.uuid4()}", session_id, 0.0, 0.1, 0.2, 0.3, 0.4, 1.0, 2.0, 3.0, 1, 0.9),
            (f"sample-{uuid.uuid4()}", session_id, 2.0, 0.1, 0.2, 0.3, 0.4, 1.0, 2.0, 3.0, 0, 0.3),
            (f"sample-{uuid.uuid4()}", session_id, 5.0, 0.1, 0.2, 0.3, 0.4, 1.0, 2.0, 3.0, 1, 0.6),
        ],
    )
    db_connection.commit()

    monkeypatch.setattr(build_reports, "_init_firestore", lambda key_path, project_id: firestore_emulator_client)

    ok = build_reports.sync_report_for_session(
        db_path=os.fspath(isolated_database),
        key_path="unused-for-emulator",
        project_id="attention-agent-test",
        session_id=session_id,
    )

    assert ok is True

    snapshot = report_ref.get()
    assert snapshot.exists

    data = snapshot.to_dict()
    assert data["sessionId"] == session_id
    assert data["userId"] == seeded_user
    assert data["avgFocusScore"] == pytest.approx(0.6)
    assert data["totalFocusTime"] == pytest.approx(3.0)
    assert data["totalDistractionTime"] == pytest.approx(3.0)
    assert data["createdAt"] == datetime.fromisoformat("2026-03-16T10:00:06+00:00")

    report_ref.delete()
