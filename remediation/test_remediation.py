
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from remediation.remediation_executor import remediate_public_ingress

class TestRemediation(unittest.TestCase):
    def test_public_rule_is_removed(self):
        safe_data = {
            "security_groups": [{
                "id": "sg-db",
                "rules": [
                    {"protocol": "tcp", "port": 3306, "source": "0.0.0.0/0"},
                    {"protocol": "tcp", "port": 3306, "source": "sg-web"},
                ],
            }]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "cloud.json"
            test_file.write_text(json.dumps(safe_data), encoding="utf-8")

            with patch("remediation.remediation_executor.DATA_FILE", test_file):
                result = remediate_public_ingress("sg-db", 3306, approved=True)

            updated = json.loads(test_file.read_text(encoding="utf-8"))
            rules = updated["security_groups"][0]["rules"]

            self.assertTrue(result)
            self.assertNotIn("0.0.0.0/0", [rule["source"] for rule in rules])
            self.assertIn("sg-web", [rule["source"] for rule in rules])

    def test_no_approval_means_no_change(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "cloud.json"
            test_file.write_text(
                json.dumps({"security_groups": []}), encoding="utf-8"
            )

            with patch("remediation.remediation_executor.DATA_FILE", test_file):
                result = remediate_public_ingress("sg-db", 3306, approved=False)

            self.assertFalse(result)

    def test_missing_public_rule_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "cloud.json"
            test_file.write_text(
                json.dumps({
                    "security_groups": [{
                        "id": "sg-db",
                        "rules": [
                            {"protocol": "tcp", "port": 3306, "source": "sg-web"}
                        ],
                    }]
                }),
                encoding="utf-8",
            )
            original = test_file.read_text(encoding="utf-8")

            with patch("remediation.remediation_executor.DATA_FILE", test_file):
                result = remediate_public_ingress("sg-db", 3306, approved=True)

            self.assertFalse(result)
            self.assertEqual(test_file.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)


