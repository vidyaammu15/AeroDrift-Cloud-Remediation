
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "topology_history.db"


@contextmanager
def _database_connection(db_path):
    con = sqlite3.connect(db_path)
    try:
        with con:
            yield con
    finally:
        con.close()

def initialize_db(db_path=DEFAULT_DB):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with _database_connection(db_path) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                source TEXT NOT NULL,
                node_count INTEGER NOT NULL,
                edge_count INTEGER NOT NULL,
                graph_json TEXT NOT NULL,
                cloud_json TEXT NOT NULL
            )
        """)


def save_snapshot(graph, cloud_data, db_path=DEFAULT_DB, source="mock"):
    initialize_db(db_path)

    snapshot_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    graph_data = {
        "nodes": [
            {"id": str(node), **attrs}
            for node, attrs in graph.nodes(data=True)
        ],
        "edges": [
            {"source": str(src), "target": str(dst), **attrs}
            for src, dst, attrs in graph.edges(data=True)
        ],
    }

    cloud_json = json.dumps(cloud_data, sort_keys=True)
    graph_json = json.dumps(graph_data, sort_keys=True)

    with _database_connection(db_path) as con:
        con.execute("""
            INSERT INTO snapshots (
                snapshot_id, created_at, source,
                node_count, edge_count, graph_json, cloud_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_id,
            created_at,
            source,
            graph.number_of_nodes(),
            graph.number_of_edges(),
            graph_json,
            cloud_json,
        ))

    return snapshot_id


def list_snapshots(db_path=DEFAULT_DB):
    initialize_db(db_path)

    with _database_connection(db_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute("""
            SELECT snapshot_id, created_at, source, node_count, edge_count
            FROM snapshots
            ORDER BY created_at DESC
        """).fetchall()

    return [dict(row) for row in rows]


def get_snapshot(snapshot_id, db_path=DEFAULT_DB):
    initialize_db(db_path)

    with _database_connection(db_path) as con:
        con.row_factory = sqlite3.Row
        row = con.execute("""
            SELECT *
            FROM snapshots
            WHERE snapshot_id = ?
        """, (snapshot_id,)).fetchone()

    if row is None:
        return None

    result = dict(row)
    result["graph"] = json.loads(result.pop("graph_json"))
    result["cloud_data"] = json.loads(result.pop("cloud_json"))
    return result