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


def _calculate_session_metrics(conn, session_id, duration_seconds):
    cur = conn.execute(
        """
        SELECT timestamp, attention_state, focus_score
        FROM focus_samples
        WHERE session_id = ?
        ORDER BY timestamp ASC
        """,
        (session_id,),
    )
    rows = cur.fetchall()
    if not rows:
        return None

    focus_time = 0.0
    distraction_time = 0.0

    for i in range(len(rows) - 1):
        ts = rows[i]["timestamp"]
        next_ts = rows[i + 1]["timestamp"]
        if ts is None or next_ts is None:
            continue
        delta = max(0.0, float(next_ts) - float(ts))
        state = rows[i]["attention_state"]
        if state == 1:
            focus_time += delta
        elif state == 0:
            distraction_time += delta

    if duration_seconds:
        try:
            observed = float(rows[-1]["timestamp"]) - float(rows[0]["timestamp"])
            remaining = max(0.0, float(duration_seconds) - observed)
        except Exception:
            remaining = 0.0
        if remaining > 0:
            last_state = rows[-1]["attention_state"]
            if last_state == 1:
                focus_time += remaining
            elif last_state == 0:
                distraction_time += remaining

    cur = conn.execute(
        """
        SELECT AVG(focus_score) AS avg_focus_score
        FROM focus_samples
        WHERE session_id = ? AND focus_score IS NOT NULL
        """,
        (session_id,),
    )
    avg_focus_score = cur.fetchone()["avg_focus_score"]

    return {
        "avg_focus_score": float(avg_focus_score) if avg_focus_score is not None else None,
        "total_focus_time": float(focus_time),
        "total_distraction_time": float(distraction_time),
    }


def _sync_reports(conn, db):
    cur = conn.execute(
        """
        SELECT session_id, user_id, start_time, end_time, duration_seconds
        FROM sessions
        ORDER BY start_time DESC
        LIMIT 1
        """
    )
    for row in cur.fetchall():
        metrics = _calculate_session_metrics(
            conn, row["session_id"], row["duration_seconds"]
        )
        if metrics is None:
            continue

        created_at = row["end_time"] or row["start_time"]
        doc = {
            "avgFocusScore": metrics["avg_focus_score"],
            "createdAt": _parse_timestamp(created_at),
            "sessionId": row["session_id"],
            "totalDistractionTime": metrics["total_distraction_time"],
            "totalFocusTime": metrics["total_focus_time"],
            "userId": row["user_id"],
        }
        db.collection("reports").document(row["session_id"]).set(doc, merge=True)


def main():
    parser = argparse.ArgumentParser(
        description="Build and sync per-session reports to Firestore."
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

    if not os.path.exists(args.db_path):
        raise SystemExit(f"SQLite DB not found: {args.db_path}")
    if not os.path.exists(args.key_path):
        raise SystemExit(f"Service account JSON not found: {args.key_path}")

    cred = credentials.Certificate(args.key_path)
    firebase_admin.initialize_app(cred, {"projectId": args.project_id})
    db = firestore.client()

    conn = _connect_db(args.db_path)
    try:
        _sync_reports(conn, db)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
