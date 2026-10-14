from pathlib import Path

from remediation.rollback_manager import rollback
from remediation.audit_logger import log_event


def audited_rollback(data_file, backup_file, approved=False, audit_db=None):
    options = {"db_path": audit_db} if audit_db else {}

    log_event(
        "ROLLBACK_REQUESTED",
        result="APPROVED" if approved is True else "CANCELLED",
        approved=approved if type(approved) is bool else None,
        details=f"Target: {Path(data_file).name}",
        **options,
    )

    if approved is not True:
        print("Rollback cancelled: explicit approval is required.")
        return False

    try:
        result = rollback(data_file, backup_file, approved=True)
        log_event(
            "ROLLBACK_VERIFICATION",
            result="PASS" if result else "FAIL",
            approved=True,
            details=f"Target: {Path(data_file).name}",
            **options,
        )
        return result
    except Exception as exc:
        log_event(
            "ROLLBACK_VERIFICATION",
            result="ERROR",
            approved=True,
            details=f"{type(exc).__name__}: {exc}",
            **options,
        )
        raise
