import json
import os
import tempfile
from pathlib import Path


def create_backup(data_file, backup_file):
    """Save a validated JSON snapshot before a simulated change."""
    source = Path(data_file)
    backup = Path(backup_file)

    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(
        data.get("security_groups"), list
    ):
        raise ValueError("Invalid cloud configuration")

    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(
        json.dumps(data, indent=4) + "\n",
        encoding="utf-8",
    )
    return backup


def rollback(data_file, backup_file, approved=False):
    """Restore a saved JSON snapshot only with explicit approval."""
    if approved is not True:
        print("Rollback cancelled: explicit approval is required.")
        return False

    target = Path(data_file)
    backup = Path(backup_file)

    if not backup.is_file():
        raise FileNotFoundError(f"Backup not found: {backup}")

    snapshot = json.loads(backup.read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict) or not isinstance(
        snapshot.get("security_groups"), list
    ):
        raise ValueError("Invalid rollback snapshot")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            json.dump(snapshot, temp_file, indent=4)
            temp_file.write("\n")
            temp_path = Path(temp_file.name)

        os.replace(temp_path, target)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    restored = json.loads(target.read_text(encoding="utf-8"))
    if restored != snapshot:
        raise RuntimeError("Rollback verification failed")

    print("Rollback completed: configuration restored.")
    print("Rollback verification: PASS")
    return True
