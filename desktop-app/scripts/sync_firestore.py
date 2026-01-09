import argparse
import datetime
import os
import sqlite3

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def _parse_timestamp(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            return value
    return value


def _connect_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _sync_users(conn, db):
    cur = conn.execute(
        "SELECT user_id, username, display_name, email, created_at FROM users"
    )
    for row in cur.fetchall():
        doc = {
            "username": row["username"],
            "displayName": row["display_name"],
            "email": row["email"],
            "createdAt": _parse_timestamp(row["created_at"]),
        }
        db.collection("users").document(row["user_id"]).set(doc, merge=True)


def _sync_sessions(conn, db):
    cur = conn.execute(
        """
        SELECT session_id, user_id, start_time, end_time, duration_seconds,
               screen_width, screen_height
        FROM sessions
        """
    )
    for row in cur.fetchall():
        doc = {
            "userID": row["user_id"],
            "startTime": _parse_timestamp(row["start_time"]),
            "endTime": _parse_timestamp(row["end_time"]),
            "durationSeconds": row["duration_seconds"],
            "screenWidth": row["screen_width"],
            "screenHeight": row["screen_height"],
        }
        db.collection("sessions").document(row["session_id"]).set(doc, merge=True)


def _sync_focus_samples(conn, db):
    cur = conn.execute(
        """
        SELECT focus_sample_id, session_id, timestamp,
               left_iris_x, left_iris_y, right_iris_x, right_iris_y,
               face_x, face_y, face_z, attention_state, focus_score
        FROM focus_samples
        """
    )
    for row in cur.fetchall():
        doc = {
            "timestamp": _parse_timestamp(row["timestamp"]),
            "leftIrisX": row["left_iris_x"],
            "leftIrisY": row["left_iris_y"],
            "rightIrisX": row["right_iris_x"],
            "rightIrisY": row["right_iris_y"],
            "faceX": row["face_x"],
            "faceY": row["face_y"],
            "faceZ": row["face_z"],
            "attentionState": row["attention_state"],
            "focusScore": row["focus_score"],
        }
        session_ref = db.collection("sessions").document(row["session_id"])
        session_ref.collection("focusSamples").document(
            row["focus_sample_id"]
        ).set(doc, merge=True)


def main():
    parser = argparse.ArgumentParser(
        description="Sync local SQLite data into Firestore."
    )
    parser.add_argument(
        "--db-path",
        default=os.path.join("desktop-app", "db", "attagent.sqlite3"),
        help="Path to SQLite database file.",
    )
    parser.add_argument(
        "--key-path",
        default=os.path.join(
            "desktop-app",
            "keys",
            "attention-agent-30bd0-firebase-adminsdk-fbsvc-1274d6f933.json",
        ),
        help="Path to Firebase service account JSON key.",
    )
    parser.add_argument(
        "--project-id",
        default="attention-agent-30bd0",
        help="Firebase project ID.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        raise SystemExit(f"SQLite DB not found: {args.db_path}")
    if not os.path.exists(args.key_path):
        raise SystemExit(f"Service account JSON not found: {args.key_path}")

    cred = credentials.Certificate(args.key_path)
    firebase_admin.initialize_app(cred, {"projectId": args.project_id})
    db = firestore.client()

    conn = _connect_db(args.db_path)
    try:
        _sync_users(conn, db)
        _sync_sessions(conn, db)
        _sync_focus_samples(conn, db)
    finally:
        conn.close()

    print("Sync complete.")


if __name__ == "__main__":
    main()
