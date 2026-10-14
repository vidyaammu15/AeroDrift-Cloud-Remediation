import json
from pathlib import Path

from remediation_generator import generate_remediation
from remediation_executor import remediate_public_ingress
import remediation_executor


def run_workflow(data_file=None):
    target_file = Path(data_file) if data_file else remediation_executor.DATA_FILE
    original_executor_file = remediation_executor.DATA_FILE

    try:
        remediation_executor.DATA_FILE = target_file
        data = json.loads(target_file.read_text(encoding="utf-8"))

        group = next(
            (g for g in data.get("security_groups", []) if g.get("id") == "sg-db"),
            None,
        )
        if group is None:
            print("ERROR: sg-db not found.")
            return False

        public_rule = any(
            r.get("protocol") == "tcp"
            and r.get("port") == 3306
            and r.get("source") == "0.0.0.0/0"
            for r in group.get("rules", [])
        )

        if not public_rule:
            print("No public TCP 3306 rule detected. No remediation needed.")
            return True

        print("Detected public database exposure.")
        print("\nGenerated remediation plan:")
        print(generate_remediation("sg-db", 3306, "0.0.0.0/0"))

        approval = input("\nApprove simulated remediation? (yes/no): ").strip().lower()
        if approval != "yes":
            print("Remediation cancelled.")
            return False

        changed = remediate_public_ingress("sg-db", 3306, approved=True)
        updated = json.loads(target_file.read_text(encoding="utf-8"))
        updated_group = next(
            (g for g in updated.get("security_groups", []) if g.get("id") == "sg-db"),
            None,
        )

        if updated_group is None:
            print("Final verification: FAIL — sg-db not found.")
            return False

        rules = updated_group.get("rules", [])
        still_public = any(
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

        passed = changed and not still_public and web_rule_preserved
        print("Public rule removed:", not still_public)
        print("Web rule preserved:", web_rule_preserved)
        print("Final verification:", "PASS" if passed else "FAIL")
        return passed

    finally:
        remediation_executor.DATA_FILE = original_executor_file


if __name__ == "__main__":
    import sys
    run_workflow(sys.argv[1] if len(sys.argv) > 1 else None)
