
import json
from pathlib import Path

from graph.topology import CloudTopology
from history.topology_store import save_snapshot, list_snapshots, get_snapshot

ROOT = Path(__file__).resolve().parent.parent
CLOUD_FILE = ROOT / "data" / "mock_cloud.json"
DB_FILE = ROOT / "data" / "topology_history.db"


def main():
    cloud_data = json.loads(CLOUD_FILE.read_text(encoding="utf-8"))

    topology = CloudTopology()
    graph = topology.build(cloud_data)

    snapshot_id = save_snapshot(
        graph,
        cloud_data,
        db_path=DB_FILE,
        source="mock",
    )

    print("Snapshot saved successfully.")
    print("Snapshot ID:", snapshot_id)
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    snapshots = list_snapshots(DB_FILE)
    print("\nTotal snapshots:", len(snapshots))

    restored = get_snapshot(snapshot_id, DB_FILE)
    assert restored is not None, "Snapshot retrieval failed"
    assert restored["cloud_data"] == cloud_data
    assert len(restored["graph"]["nodes"]) == graph.number_of_nodes()
    assert len(restored["graph"]["edges"]) == graph.number_of_edges()

    print("Snapshot retrieval: PASS")
    print("Cloud data verification: PASS")
    print("Graph verification: PASS")


if __name__ == "__main__":
    main()
