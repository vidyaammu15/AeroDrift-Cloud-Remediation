import json
import tempfile
import unittest
from pathlib import Path

from remediation.rollback_manager import create_backup, rollback


class TestRollbackManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_file = self.root / "cloud.json"
        self.backup_file = self.root / "cloud.backup.json"

        self.original = {
            "security_groups": [
                {
                    "id": "sg-db",
                    "rules": [
                        {
                            "protocol": "tcp",
                            "port": 3306,
                            "source": "sg-web",
                        }
                    ],
                }
            ]
        }
        self.data_file.write_text(
            json.dumps(self.original, indent=4), encoding="utf-8"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_backup_and_rollback_restore_original(self):
        create_backup(self.data_file, self.backup_file)

        changed = json.loads(
            self.data_file.read_text(encoding="utf-8")
        )
        changed["security_groups"][0]["rules"].append({
            "protocol": "tcp",
            "port": 3306,
            "source": "0.0.0.0/0",
        })
        self.data_file.write_text(json.dumps(changed), encoding="utf-8")

        self.assertTrue(
            rollback(self.data_file, self.backup_file, approved=True)
        )
        restored = json.loads(
            self.data_file.read_text(encoding="utf-8")
        )
        self.assertEqual(restored, self.original)

    def test_approval_required(self):
        create_backup(self.data_file, self.backup_file)
        before = self.data_file.read_text(encoding="utf-8")

        self.assertFalse(
            rollback(self.data_file, self.backup_file, approved=False)
        )
        self.assertEqual(
            self.data_file.read_text(encoding="utf-8"), before
        )

    def test_missing_backup_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            rollback(
                self.data_file,
                self.root / "missing.json",
                approved=True,
            )

    def test_backup_preserves_original_snapshot(self):
        create_backup(self.data_file, self.backup_file)
        saved = json.loads(
            self.backup_file.read_text(encoding="utf-8")
        )
        self.assertEqual(saved, self.original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
