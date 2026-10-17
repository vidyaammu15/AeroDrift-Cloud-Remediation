
from history.topology_store import list_snapshots, get_snapshot


def compare_snapshots(old_snapshot_id, new_snapshot_id, db_path=None):
    old_snapshot = (
        get_snapshot(old_snapshot_id, db_path)
        if db_path else get_snapshot(old_snapshot_id)
    )
    new_snapshot = (
        get_snapshot(new_snapshot_id, db_path)
        if db_path else get_snapshot(new_snapshot_id)
    )

    if old_snapshot is None or new_snapshot is None:
        raise ValueError("One or both snapshot IDs were not found.")

    old_nodes = {
        node["id"]: node for node in old_snapshot["graph"]["nodes"]
    }
    new_nodes = {
        node["id"]: node for node in new_snapshot["graph"]["nodes"]
    }

    old_edges = {
        (edge["source"], edge["target"], repr(sorted(edge.items())))
        for edge in old_snapshot["graph"]["edges"]
    }
    new_edges = {
        (edge["source"], edge["target"], repr(sorted(edge.items())))
        for edge in new_snapshot["graph"]["edges"]
    }

    old_cloud = old_snapshot["cloud_data"]
    new_cloud = new_snapshot["cloud_data"]

    old_groups = {
        group.get("id", group.get("group_id", group.get("name", str(i)))): group
        for i, group in enumerate(old_cloud.get("security_groups", []))
    }
    new_groups = {
        group.get("id", group.get("group_id", group.get("name", str(i)))): group
        for i, group in enumerate(new_cloud.get("security_groups", []))
    }

    security_group_changes = {}
    for group_id in sorted(set(old_groups) | set(new_groups)):
        before = old_groups.get(group_id)
        after = new_groups.get(group_id)
        if before != after:
            security_group_changes[group_id] = {
                "before": before,
                "after": after,
            }

    return {
        "old_snapshot_id": old_snapshot_id,
        "new_snapshot_id": new_snapshot_id,
        "added_nodes": sorted(set(new_nodes) - set(old_nodes)),
        "removed_nodes": sorted(set(old_nodes) - set(new_nodes)),
        "added_edges": sorted(new_edges - old_edges),
        "removed_edges": sorted(old_edges - new_edges),
        "node_attribute_changes": {
            node_id: {
                "before": old_nodes[node_id],
                "after": new_nodes[node_id],
            }
            for node_id in set(old_nodes) & set(new_nodes)
            if old_nodes[node_id] != new_nodes[node_id]
        },
        "security_group_changes": security_group_changes,
        "cloud_configuration_changed": old_cloud != new_cloud,
    }


def print_snapshot_history(db_path=None):
    snapshots = (
        list_snapshots(db_path)
        if db_path else list_snapshots()
    )

    if not snapshots:
        print("No topology snapshots found.")
        return

    print("\nTopology Snapshot History")
    print("-" * 70)

    for snapshot in snapshots:
        print(
            f"ID: {snapshot['snapshot_id']} | "
            f"Time: {snapshot['created_at']} | "
            f"Source: {snapshot['source']} | "
            f"Nodes: {snapshot['node_count']} | "
            f"Edges: {snapshot['edge_count']}"
        )
