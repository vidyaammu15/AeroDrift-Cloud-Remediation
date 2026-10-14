import json
import tempfile
import unittest
from pathlib import Path

from remediation.audited_rollback import audited_rollback
from remediation.audit_logger import get_audit_events
from remediation.rollback_manager import create_backup


class TestAuditedRollback(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_file = self.root / "cloud.json"
        self.backup_file = self.root / "backup.json"
        self.audit_db = self.root / "audit.db"

        self.original = {
            "security_groups": [{
                "id": "sg-db",
                "rules": [{
                    "protocol": "tcp",
                    "port": 3306,
                    "source": "sg-web",
                }],
            }]
        }
        self.data_file.write_text(
            json.dumps(self.original), encoding="utf-8"
        )
        create_backup(self.data_file, self.backup_file)

        changed = {
            "security_groups": [{
                "id": "sg-db",
                "rules": [],
            }]
        }
        self.data_file.write_text(
            json.dumps(changed), encoding="utf-8"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_approved_rollback_is_logged(self):
        result = audited_rollback(
            self.data_file, self.backup_file,
            approved=True, audit_db=self.audit_db,
        )
        self.assertTrue(result)

        restored = json.loads(
            self.data_file.read_text(encoding="utf-8")
        )
        self.assertEqual(restored, self.original)

        events = get_audit_events(self.audit_db)
        self.assertEqual(
            [e["event_type"] for e in events],
            ["ROLLBACK_VERIFICATION", "ROLLBACK_REQUESTED"],
        )
        self.assertEqual(events[0]["result"], "PASS")

    def test_rejected_rollback_is_logged(self):
        before = self.data_file.read_text(encoding="utf-8")
        result = audited_rollback(
            self.data_file, self.backup_file,
            approved=False, audit_db=self.audit_db,
        )
        self.assertFalse(result)
        self.assertEqual(
            self.data_file.read_text(encoding="utf-8"), before
        )

        events = get_audit_events(self.audit_db)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "ROLLBACK_REQUESTED")
        self.assertEqual(events[0]["result"], "CANCELLED")
        self.assertEqual(events[0]["approved"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
