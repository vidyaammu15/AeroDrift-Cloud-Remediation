import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "remediation_audit.db"
)


def initialize_audit_db(db_path=None):
    """Create the audit database and table if needed."""
    path = Path(db_path) if db_path else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS remediation_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    security_group TEXT,
                    port INTEGER,
                    approved INTEGER,
                    result TEXT NOT NULL,
                    details TEXT
                )
            """)
    return path


def log_event(
    event_type,
    security_group=None,
    port=None,
    approved=None,
    result="INFO",
    details=None,
    db_path=None,
):
    """Save one audit event without overwriting existing events."""
    if not isinstance(event_type, str) or not event_type.strip():
        raise ValueError("event_type must be a non-empty string")

    if approved is not None and type(approved) is not bool:
        raise ValueError("approved must be True, False, or None")

    path = initialize_audit_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("""
                INSERT INTO remediation_audit
                (timestamp, event_type, security_group, port,
                 approved, result, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                event_type,
                security_group,
                port,
                None if approved is None else int(approved),
                result,
                details,
            ))

    return timestamp


def get_audit_events(db_path=None, limit=100):
    """Return recent audit events, newest first."""
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer")

    path = initialize_audit_db(db_path)

    with closing(sqlite3.connect(path)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT id, timestamp, event_type, security_group,
                   port, approved, result, details
            FROM remediation_audit
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    initialize_audit_db()
    print("Audit database initialized:", DEFAULT_DB)
    print("Recent remediation events:")
    for event in get_audit_events():
        print(event)
