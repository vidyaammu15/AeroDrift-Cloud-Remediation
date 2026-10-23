from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import tempfile
from pathlib import Path

from remediation.remediation_workflow import run_workflow
from remediation.audit_logger import get_audit_events
from history.topology_store import list_snapshots

safe_data = {
    "vpcs": [{"id": "vpc-test", "name": "Test VPC"}],
    "subnets": [{
        "id": "subnet-test",
        "name": "Test Subnet",
        "type": "private",
        "vpc_id": "vpc-test"
    }],
    "security_groups": [
        {
            "id": "sg-db",
            "name": "Database SG",
            "rules": [
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
    "instances": [{
        "id": "i-db-test",
        "name": "Test DB",
        "subnet_id": "subnet-test",
        "security_group_ids": ["sg-db"]
    }]
}

with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    cloud_file = root / "cloud.json"
    audit_db = root / "audit.db"
    history_db = root / "history.db"

    cloud_file.write_text(json.dumps(safe_data), encoding="utf-8")

    from history.topology_store import save_snapshot as real_save_snapshot

    def save_to_test_db(graph, cloud_data, source="mock"):
        return real_save_snapshot(
            graph, cloud_data, db_path=history_db, source=source
        )

    from unittest.mock import patch

    with patch(
        "remediation.remediation_workflow.save_snapshot",
        side_effect=save_to_test_db
    ):
        result = run_workflow(cloud_file, audit_db)

    snapshots = list_snapshots(db_path=history_db)
    events = get_audit_events(db_path=audit_db)
    event_types = {event["event_type"] for event in events}

    print("Workflow returned success:", result)
    print("Historical snapshots created:", len(snapshots))
    print("Snapshot audit event recorded:", "SNAPSHOT_SAVED" in event_types)
    print("Risk check recorded:", "RISK_CHECK" in event_types)

    assert result is True
    assert len(snapshots) == 1
    assert "SNAPSHOT_SAVED" in event_types
    assert "RISK_CHECK" in event_types

    print("NO-REMEDIATION SNAPSHOT TEST: PASS")
