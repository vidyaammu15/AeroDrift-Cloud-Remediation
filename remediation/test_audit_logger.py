import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from remediation.audit_logger import (
    initialize_audit_db,
    log_event,
    get_audit_events,
)


class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "audit.db"
        initialize_audit_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_event_is_saved(self):
        log_event(
            "REMEDIATION", "sg-db", 3306, True,
            "PASS", "Test event", self.db_path,
        )
        events = get_audit_events(self.db_path)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "REMEDIATION")
        self.assertEqual(events[0]["security_group"], "sg-db")
        self.assertEqual(events[0]["port"], 3306)
        self.assertEqual(events[0]["approved"], 1)
        self.assertEqual(events[0]["result"], "PASS")

    def test_events_are_persistent(self):
        log_event("FIRST", result="PASS", db_path=self.db_path)
        log_event("SECOND", result="FAIL", db_path=self.db_path)
        events = get_audit_events(self.db_path)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "SECOND")
        self.assertEqual(events[1]["event_type"], "FIRST")

    def test_invalid_approval_is_rejected(self):
        with self.assertRaises(ValueError):
            log_event("TEST", approved="yes", db_path=self.db_path)

    def test_invalid_event_type_is_rejected(self):
        with self.assertRaises(ValueError):
            log_event("", db_path=self.db_path)

    def test_database_table_exists(self):
        with closing(sqlite3.connect(self.db_path)) as connection:
            row = connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='remediation_audit'"
            ).fetchone()
        self.assertIsNotNone(row)


if __name__ == "__main__":
    unittest.main(verbosity=2)
