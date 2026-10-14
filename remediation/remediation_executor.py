import json
import os
import tempfile
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "simulated_live_cloud.json"


def remediate_public_ingress(security_group_id, port, approved=False):
    if approved is not True:
        print("Remediation cancelled: explicit approval is required.")
        return False

    if not isinstance(security_group_id, str) or not security_group_id.startswith("sg-"):
        raise ValueError("Invalid security group ID")

    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Port must be an integer from 1 to 65535")

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    groups = data.get("security_groups", [])
    group = next((g for g in groups if g.get("id") == security_group_id), None)

    if group is None:
        raise ValueError(f"Security group not found: {security_group_id}")

    original_rules = group.get("rules", [])
    updated_rules = [
        rule for rule in original_rules
        if not (
            rule.get("protocol") == "tcp"
            and rule.get("port") == port
            and rule.get("source") == "0.0.0.0/0"
        )
    ]

    if len(updated_rules) == len(original_rules):
        print("No matching public rule found; no change made.")
        return False

    group["rules"] = updated_rules

    still_public = any(
        rule.get("protocol") == "tcp"
        and rule.get("port") == port
        and rule.get("source") == "0.0.0.0/0"
        for rule in group["rules"]
    )
    if still_public:
        raise RuntimeError("Verification failed; refusing to save.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            json.dump(data, temp_file, indent=4)
            temp_file.write("\n")
            temp_path = Path(temp_file.name)

        os.replace(temp_path, DATA_FILE)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

    print(f"SIMULATION: Removed public TCP port {port} from {security_group_id}.")
    print("Verification passed: public rule is absent.")
    return True


if __name__ == "__main__":
    answer = input(
        "Approve simulated removal of public TCP 3306 from sg-db? (yes/no): "
    ).strip().lower()

    remediate_public_ingress("sg-db", 3306, approved=(answer == "yes"))
