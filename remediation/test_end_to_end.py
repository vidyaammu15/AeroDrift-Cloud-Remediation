from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from remediation.remediation_executor import remediate_public_ingress

test_data = {
    "security_groups": [
        {
            "id": "sg-db",
            "rules": [
                {"protocol": "tcp", "port": 3306, "source": "0.0.0.0/0"},
                {"protocol": "tcp", "port": 3306, "source": "sg-web"}
            ]
        }
    ]
}

with tempfile.TemporaryDirectory() as folder:
    test_file = Path(folder) / "cloud.json"
    test_file.write_text(json.dumps(test_data), encoding="utf-8")

    with patch("remediation.remediation_executor.DATA_FILE", test_file):
        changed = remediate_public_ingress(
            "sg-db", 3306, approved=True
        )

    result = json.loads(test_file.read_text(encoding="utf-8"))
    rules = result["security_groups"][0]["rules"]

    public_rule_remains = any(
        r.get("protocol") == "tcp"
        and r.get("port") == 3306
        and r.get("source") == "0.0.0.0/0"
        for r in rules
    )
    web_rule_remains = any(
        r.get("protocol") == "tcp"
        and r.get("port") == 3306
        and r.get("source") == "sg-web"
        for r in rules
    )

    print("Remediation executed:", changed)
    print("Public rule removed:", not public_rule_remains)
    print("Web rule preserved:", web_rule_remains)

    assert changed and not public_rule_remains and web_rule_remains
    print("END-TO-END REMEDIATION TEST: PASS")

