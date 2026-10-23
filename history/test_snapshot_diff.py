
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import sqlite3
import tempfile
from pathlib import Path
from contextlib import contextmanager
from graph.topology import CloudTopology
from history.topology_store import save_snapshot
from history.snapshot_diff import compare_snapshots

@contextmanager
def _database_connection(db_path):
    con = sqlite3.connect(db_path)
    try:
        with con:
            yield con
    finally:
        con.close()

ROOT = Path(__file__).resolve().parent.parent


def main():
    baseline = json.loads(
        (ROOT / "data" / "mock_cloud.json").read_text(encoding="utf-8")
    )
    changed = json.loads(
        (ROOT / "data" / "drifted_cloud.json").read_text(encoding="utf-8")
    )

    topology = CloudTopology()
    baseline_graph = topology.build(baseline)
    changed_graph = topology.build(changed)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        db_path = Path(temp_dir) / "test_history.db"

        old_id = save_snapshot(
            baseline_graph, baseline, db_path=db_path, source="baseline"
        )
        new_id = save_snapshot(
            changed_graph, changed, db_path=db_path, source="drifted"
        )

        result = compare_snapshots(old_id, new_id, db_path=db_path)

        print("Historical Snapshot Comparison")
        print("Added nodes:", result["added_nodes"])
        print("Removed nodes:", result["removed_nodes"])
        print("Added edges:", result["added_edges"])
        print("Removed edges:", result["removed_edges"])
        print("Node attribute changes:", result["node_attribute_changes"])

        print("Security group changes:", result["security_group_changes"])
        print("Cloud configuration changed:", result["cloud_configuration_changed"])

        assert result["cloud_configuration_changed"], (
            "Expected baseline and drifted cloud configurations to differ"
)

        assert result["old_snapshot_id"] == old_id
        assert result["new_snapshot_id"] == new_id

        # Confirm the SQLite database can be opened and closed cleanly.
        with sqlite3.connect(db_path) as con:
            count = con.execute(
                "SELECT COUNT(*) FROM snapshots"
            ).fetchone()[0]
        assert count == 2, f"Expected 2 snapshots, got {count}"

        print("Two snapshots stored and retrieved: PASS")
        print("Snapshot comparison test: PASS")


if __name__ == "__main__":
    main()
