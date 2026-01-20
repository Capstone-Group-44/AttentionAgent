import argparse
import datetime
import os
import sqlite3
import json
import subprocess
import sys

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


def _load_sync_state(state_path):
    if not os.path.exists(state_path):
        return {}
    try:
        with open(state_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_sync_state(state_path, state):
    tmp_path = state_path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(state, f)
    os.replace(tmp_path, state_path)


def _sync_users(conn, db, last_sync_iso):
    print("Syncing users...")
    params = ()
    query = "SELECT user_id, username, display_name, email, created_at FROM users"
    if last_sync_iso:
        query += " WHERE created_at > ?"
        params = (last_sync_iso,)
    cur = conn.execute(query, params)
    max_created_at = last_sync_iso
    for row in cur.fetchall():
        doc = {
            "username": row["username"],
            "displayName": row["display_name"],
            "email": row["email"],
            "createdAt": _parse_timestamp(row["created_at"]),
        }
        db.collection("users").document(row["user_id"]).set(doc, merge=True)
        if row["created_at"] and (max_created_at is None or row["created_at"] > max_created_at):
            max_created_at = row["created_at"]
    print("Users synced.")
    return max_created_at


def _sync_sessions(conn, db, last_sync_iso):
    print("Syncing sessions...")
    params = ()
    query = """
        SELECT session_id, user_id, start_time, end_time, duration_seconds,
               screen_width, screen_height
        FROM sessions
    """
    if last_sync_iso:
        query += " WHERE start_time > ?"
        params = (last_sync_iso,)
    cur = conn.execute(query, params)
    max_start_time = last_sync_iso
    for row in cur.fetchall():
        doc = {
            "userId": row["user_id"],
            "startTime": _parse_timestamp(row["start_time"]),
            "endTime": _parse_timestamp(row["end_time"]),
            "durationSeconds": row["duration_seconds"],
            "screenWidth": row["screen_width"],
            "screenHeight": row["screen_height"],
        }
        db.collection("sessions").document(row["session_id"]).set(doc, merge=True)
        if row["start_time"] and (max_start_time is None or row["start_time"] > max_start_time):
            max_start_time = row["start_time"]
    print("Sessions synced.")
    return max_start_time


def _sync_focus_samples(conn, db, last_sync_ts):
    print("Syncing focus samples...")
    params = ()
    query = """
        SELECT focus_sample_id, session_id, timestamp,
               left_iris_x, left_iris_y, right_iris_x, right_iris_y,
               face_x, face_y, face_z, attention_state, focus_score
        FROM focus_samples
    """
    if last_sync_ts is not None:
        query += " WHERE timestamp > ?"
        params = (last_sync_ts,)
    cur = conn.execute(query, params)
    max_timestamp = last_sync_ts
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
        if row["timestamp"] is not None and (max_timestamp is None or row["timestamp"] > max_timestamp):
            max_timestamp = row["timestamp"]
    print("Focus samples synced.")
    return max_timestamp


def _run_build_reports(script_dir, db_path, key_path, project_id):
    script_path = os.path.join(script_dir, "build_reports.py")
    if not os.path.exists(script_path):
        print(f"Report script not found: {script_path}")
        return
    try:
        subprocess.run(
            [
                sys.executable,
                "-u",
                script_path,
                "--db-path",
                db_path,
                "--key-path",
                key_path,
                "--project-id",
                project_id,
            ],
            check=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        print("Report build timed out after 120 seconds.")
    except subprocess.CalledProcessError as exc:
        print(f"Report build failed: {exc}")


def main():
    parser = argparse.ArgumentParser(
        description="Sync local SQLite data into Firestore."
    )
    parser.add_argument(
        "--db-path",
        default=os.path.join("desktop-app", "db", "focuscam.sqlite3"),
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

    print("Starting Firestore sync...")

    if not os.path.exists(args.db_path):
        raise SystemExit(f"SQLite DB not found: {args.db_path}")
    if not os.path.exists(args.key_path):
        raise SystemExit(f"Service account JSON not found: {args.key_path}")

    cred = credentials.Certificate(args.key_path)
    firebase_admin.initialize_app(cred, {"projectId": args.project_id})
    db = firestore.client()

    conn = _connect_db(args.db_path)
    state_path = os.path.join(os.path.dirname(args.db_path), ".sync_state.json")
    sync_state = _load_sync_state(state_path)
    try:
        users_last = sync_state.get("users_last_sync")
        sessions_last = sync_state.get("sessions_last_sync")
        samples_last = sync_state.get("focus_samples_last_sync")

        users_last = _sync_users(conn, db, users_last)
        sessions_last = _sync_sessions(conn, db, sessions_last)
        samples_last = _sync_focus_samples(conn, db, samples_last)
    finally:
        conn.close()

    sync_state["users_last_sync"] = users_last
    sync_state["sessions_last_sync"] = sessions_last
    sync_state["focus_samples_last_sync"] = samples_last
    _save_sync_state(state_path, sync_state)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    _run_build_reports(script_dir, args.db_path, args.key_path, args.project_id)

    print("Sync complete.")


if __name__ == "__main__":
    main()
