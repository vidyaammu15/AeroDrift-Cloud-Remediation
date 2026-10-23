import json
import sys
from pathlib import Path

from graph.topology import CloudTopology
from history.topology_store import save_snapshot
from reports.incident_report import generate_incident_report
from history.topology_store import list_snapshots
from drift.database_exposure import DatabaseExposureDetector

try:
    from . import remediation_executor
    from .remediation_executor import remediate_public_ingress
    from .remediation_generator import generate_remediation
    from .audit_logger import log_event
    from .rollback_manager import create_backup
    from .audited_rollback import audited_rollback
except ImportError:
    import remediation_executor
    from remediation_executor import remediate_public_ingress
    from remediation_generator import generate_remediation
    from audit_logger import log_event
    from rollback_manager import create_backup
    from audited_rollback import audited_rollback



def generate_workflow_report(
    cloud_data,
    remediation_outcome,
    verification_status,
    rollback_status="NOT_REQUIRED",
    configuration_changes=None,
):
    """Generate an incident report from the supplied workflow results."""
    try:
        risks = DatabaseExposureDetector().detect(cloud_data)
        snapshots = list_snapshots()
        return generate_incident_report(
            database_risks=risks,
            snapshot_history=snapshots,
            configuration_changes=configuration_changes or {},
            remediation_outcome=remediation_outcome,
            verification_status=verification_status,
            rollback_status=rollback_status,
        )
    except Exception as exc:
        print(f"ERROR: Incident report generation failed: {exc}")
        return None


def run_workflow(data_file=None, audit_db=None):
    target_file = (
        Path(data_file) if data_file
        else Path(remediation_executor.DATA_FILE)
    )
    original_executor_file = remediation_executor.DATA_FILE
    audit_options = {"audit_db": audit_db} if audit_db else {}

    backup_file = target_file.with_name(
        target_file.stem + ".remediation-backup.json"
    )
    log_options = {"db_path": audit_db} if audit_db else {}

    try:
        remediation_executor.DATA_FILE = target_file
        data = json.loads(target_file.read_text(encoding="utf-8"))

        group = next(
            (g for g in data.get("security_groups", [])
             if g.get("id") == "sg-db"),
            None,
        )

        if group is None:
            log_event(
                "WORKFLOW_ERROR", "sg-db", 3306,
                result="FAIL",
                details="Security group not found",
                **log_options,
            )
            print("ERROR: sg-db not found.")
            return False

        public_rule = any(
            r.get("protocol") == "tcp"
            and r.get("port") == 3306
            and r.get("source") == "0.0.0.0/0"
            for r in group.get("rules", [])
        )

        if not public_rule:
            log_event(
                "RISK_CHECK", "sg-db", 3306,
                result="PASS",
                details="No public TCP 3306 rule detected",
                **log_options,
            )
            print("No public TCP 3306 rule detected. No remediation needed.")

            try:
                safe_cloud_data = json.loads(
                    target_file.read_text(encoding="utf-8")
                )
                topology = CloudTopology()
                graph = topology.build(safe_cloud_data)
                snapshot_id = save_snapshot(
                    graph,
                    safe_cloud_data,
                    source="remediation_workflow_no_remediation",
                )
                log_event(
                    "SNAPSHOT_SAVED", "sg-db", 3306,
                    approved=None, result="PASS",
                    details=f"No-remediation snapshot ID: {snapshot_id}",
                    **log_options,
                )
                print("Historical snapshot saved:", snapshot_id)

                report_path = generate_workflow_report(
                    safe_cloud_data,
                    remediation_outcome="NOT_REQUIRED",
                    verification_status="NOT_REQUIRED",
                    rollback_status="NOT_REQUIRED",
                )
                if report_path is None:
                    return False
                print("Incident report generated:", report_path)
            except Exception as exc:
                log_event(
                    "SNAPSHOT_SAVED", "sg-db", 3306,
                    approved=None, result="ERROR",
                    details=f"{type(exc).__name__}: {exc}",
                    **log_options,
                )
                print("WARNING: Snapshot saving failed:", exc)
                return False

            return True

        log_event(
            "RISK_DETECTED", "sg-db", 3306,
            result="CRITICAL",
            details="Public database ingress detected",
            **log_options,
        )

        print("Detected public database exposure.")
        print("\nGenerated remediation plan:")
        print(generate_remediation("sg-db", 3306, "0.0.0.0/0"))

        approval = input(
            "\nApprove simulated remediation? (yes/no): "
        ).strip().lower()

        if approval != "yes":
            log_event(
                "APPROVAL_REJECTED", "sg-db", 3306,
                approved=False, result="CANCELLED",
                details="User did not approve remediation",
                **log_options,
            )
            print("Remediation cancelled.")
            return False

        # Save the original configuration before making changes.
        create_backup(target_file, backup_file)
        log_event(
            "BACKUP_CREATED", "sg-db", 3306,
            approved=True, result="PASS",
            details=f"Backup: {backup_file.name}",
            **log_options,
        )
        print("Backup created:", backup_file.name)

        log_event(
            "APPROVAL_GRANTED", "sg-db", 3306,
            approved=True, result="APPROVED",
            details="User approved simulated remediation",
            **log_options,
        )

        try:
            changed = remediate_public_ingress(
                "sg-db", 3306, approved=True
            )
        except Exception as exc:
            log_event(
                "REMEDIATION_EXECUTED", "sg-db", 3306,
                approved=True, result="ERROR",
                details=f"{type(exc).__name__}: {exc}",
                **log_options,
            )
            raise

        log_event(
            "REMEDIATION_EXECUTED", "sg-db", 3306,
            approved=True,
            result="CHANGED" if changed else "NO_CHANGE",
            details="Simulated executor returned",
            **log_options,
        )

        updated = json.loads(target_file.read_text(encoding="utf-8"))
        updated_group = next(
            (g for g in updated.get("security_groups", [])
             if g.get("id") == "sg-db"),
            None,
        )
        rules = updated_group.get("rules", []) if updated_group else []

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

        passed = bool(
            changed and updated_group is not None
            and not still_public and web_rule_preserved
        )

        log_event(
            "VERIFICATION", "sg-db", 3306,
            approved=True,
            result="PASS" if passed else "FAIL",
            details=(
                f"public_rule_absent={not still_public}; "
                f"web_rule_preserved={web_rule_preserved}"
            ),
            **log_options,
        )

        print("Public rule removed:", not still_public)
        print("Web rule preserved:", web_rule_preserved)
        print("Final verification:", "PASS" if passed else "FAIL")

        if not passed:
            rollback_approval = input(
                "Verification failed. Approve rollback? (yes/no): "
            ).strip().lower()

            restored = audited_rollback(
                target_file,
                backup_file,
                approved=(rollback_approval == "yes"),
                audit_db=audit_db,
            )
            print("Rollback result:", "PASS" if restored else "NOT COMPLETED")
            return False

        try:
            final_cloud_data = json.loads(
                target_file.read_text(encoding="utf-8")
            )
            topology = CloudTopology()
            graph = topology.build(final_cloud_data)
            snapshot_id = save_snapshot(
                graph,
                final_cloud_data,
                source="remediation_workflow",
            )
            log_event(
                "SNAPSHOT_SAVED", "sg-db", 3306,
                approved=True, result="PASS",
                details=f"Snapshot ID: {snapshot_id}",
                **log_options,
            )
            print("Historical snapshot saved:", snapshot_id)

            report_path = generate_workflow_report(
                data,
                remediation_outcome="SUCCESS",
                verification_status="PASS",
                rollback_status="NOT_REQUIRED",
                configuration_changes={
                    "sg-db": {"before": group, "after": updated_group}
                },
            )
            if report_path is None:
                return False
            print("Incident report generated:", report_path)
        except Exception as exc:
            log_event(
                "SNAPSHOT_SAVED", "sg-db", 3306,
                approved=True, result="ERROR",
                details=f"{type(exc).__name__}: {exc}",
                **log_options,
            )
            print("ERROR: Snapshot saving failed:", exc)
            return False

        return True

    finally:
        remediation_executor.DATA_FILE = original_executor_file


if __name__ == "__main__":
    args = sys.argv[1:]
    data_arg = args[0] if args else None
    audit_arg = args[1] if len(args) > 1 else None
    run_workflow(data_arg, audit_arg)
