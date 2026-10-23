from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from remediation.remediation_workflow import run_workflow
from remediation.audit_logger import get_audit_events
from history.topology_store import list_snapshots

test_data = {
    "vpcs": [
        {"id": "vpc-test", "name": "Test VPC"}
    ],
    "subnets": [
        {
            "id": "subnet-test",
            "name": "Test Subnet",
            "type": "public",
            "vpc_id": "vpc-test"
        }
    ],
    "security_groups": [
        {
            "id": "sg-db",
            "name": "Database SG",
            "rules": [
                {"protocol": "tcp", "port": 3306, "source": "0.0.0.0/0"},
                {"protocol": "tcp", "port": 3306, "source": "sg-web"}
            ]
        },
        {
            "id": "sg-web",
            "name": "Web SG",
            "rules": [
                {"protocol": "tcp", "port": 80, "source": "0.0.0.0/0"}
            ]
        }
    ],
    "instances": [
        {
            "id": "i-db-test",
            "name": "Test DB",
            "subnet_id": "subnet-test",
            "security_group_ids": ["sg-db"]
        }
    ]
}

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    data_file = root / "cloud.json"
    audit_db = root / "audit.db"
    history_db = root / "history.db"

    data_file.write_text(json.dumps(test_data), encoding="utf-8")

    from history.topology_store import save_snapshot as real_save_snapshot

    def save_to_test_db(graph, cloud_data, source="mock"):
        return real_save_snapshot(
            graph,
            cloud_data,
            db_path=history_db,
            source=source
        )

    with patch(
        "remediation.remediation_workflow.save_snapshot",
        side_effect=save_to_test_db
    ):
        with patch("builtins.input", return_value="yes"):
            result = run_workflow(data_file, audit_db)

    final_data = json.loads(data_file.read_text(encoding="utf-8"))
    db_group = next(
        g for g in final_data["security_groups"] if g["id"] == "sg-db"
    )
    rules = db_group["rules"]

    public_rule_remains = any(
        r.get("protocol") == "tcp"
        and r.get("port") == 3306
        and r.get("source") == "0.0.0.0/0"
        for r in rules
    )
    web_rule_preserved = any(
        r.get("protocol") == "tcp"
        and r.get("port") == 3306
        and r.get("source") == "sg-web"
        for r in rules
    )

    snapshots = list_snapshots(db_path=history_db)
    events = get_audit_events(db_path=audit_db)
    event_types = {event["event_type"] for event in events}

    print("Workflow returned success:", result)
    print("Public database rule removed:", not public_rule_remains)
    print("Web rule preserved:", web_rule_preserved)
    print("Historical snapshots created:", len(snapshots))
    print("Snapshot audit event recorded:", "SNAPSHOT_SAVED" in event_types)

    assert result is True
    assert not public_rule_remains
    assert web_rule_preserved
    assert len(snapshots) == 1
    assert "SNAPSHOT_SAVED" in event_types

    print("WORKFLOW SNAPSHOT INTEGRATION TEST: PASS")
