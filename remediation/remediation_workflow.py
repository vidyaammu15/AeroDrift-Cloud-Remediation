import json

from remediation_generator import generate_remediation
from remediation_executor import remediate_public_ingress, DATA_FILE


def run_workflow():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    group = next(
        (g for g in data["security_groups"] if g["id"] == "sg-db"),
        None,
    )
    if group is None:
        print("ERROR: sg-db not found.")
        return

    public_rule = any(
        r.get("protocol") == "tcp"
        and r.get("port") == 3306
        and r.get("source") == "0.0.0.0/0"
        for r in group["rules"]
    )

    if not public_rule:
        print("No public TCP 3306 rule detected. No remediation needed.")
        return

    print("Detected public database exposure.")
    print("\nGenerated remediation plan:")
    print(generate_remediation("sg-db", 3306, "0.0.0.0/0"))

    approval = input("\nApprove simulated remediation? (yes/no): ").strip().lower()
    if approval != "yes":
        print("Remediation cancelled.")
        return

    changed = remediate_public_ingress("sg-db", 3306, approved=True)
    updated = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    updated_group = next(
        g for g in updated["security_groups"] if g["id"] == "sg-db"
    )

    still_public = any(
        r.get("protocol") == "tcp"
        and r.get("port") == 3306
        and r.get("source") == "0.0.0.0/0"
        for r in updated_group["rules"]
    )

    print("Final verification:", "PASS" if changed and not still_public else "FAIL")


if __name__ == "__main__":
    run_workflow()

