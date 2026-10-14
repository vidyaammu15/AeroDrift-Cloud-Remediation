
import json
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "simulated_live_cloud.json"


def remediate_public_ingress(security_group_id, port, approved=False):
    if not approved:
        print("Remediation cancelled: approval is required.")
        return False

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    group = next(
        (g for g in data["security_groups"] if g["id"] == security_group_id),
        None,
    )

    if group is None:
        raise ValueError(f"Security group not found: {security_group_id}")

    original_rules = group["rules"]
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

    # Preserve the original file unless the change can be verified.
    group["rules"] = updated_rules
    if any(
        rule.get("protocol") == "tcp"
        and rule.get("port") == port
        and rule.get("source") == "0.0.0.0/0"
        for rule in group["rules"]
    ):
        raise RuntimeError("Verification failed; refusing to save.")

    DATA_FILE.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    print(f"SIMULATION: Removed public TCP port {port} from {security_group_id}.")
    print(f"Verification passed: public rule is absent.")
    return True


if __name__ == "__main__":
    answer = input(
        "Approve simulated removal of public TCP 3306 from sg-db? (yes/no): "
    ).strip().lower()

    remediate_public_ingress(
        "sg-db",
        3306,
        approved=(answer == "yes"),
    )
