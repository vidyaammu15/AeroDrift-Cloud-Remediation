"""Allowlisted dispatcher for approved simulated remediation operations."""

from remediation.remediation_executor import remediate_public_ingress

_ALLOWED_PLAN_KEYS = {
    "operation",
    "security_group_id",
    "protocol",
    "port",
    "source",
}

def validate_plan(plan):
    """Validate a remediation plan as data; never execute generated Python."""
    if not isinstance(plan, dict):
        raise ValueError("Plan must be a dictionary")

    if set(plan.keys()) != _ALLOWED_PLAN_KEYS:
        raise ValueError("Plan contains missing or unexpected fields")

    if plan["operation"] != "remove_public_ingress":
        raise ValueError("Operation is not allowlisted")

    if plan["security_group_id"] != "sg-db":
        raise ValueError("Only the configured demo database group is allowed")

    if plan["protocol"] != "tcp":
        raise ValueError("Only TCP is supported")

    if type(plan["port"]) is not int or plan["port"] != 3306:
        raise ValueError("Only the demo database port 3306 is allowed")

    if plan["source"] != "0.0.0.0/0":
        raise ValueError("Only the configured public IPv4 source is supported")

    return True


def execute_plan(plan, approved=False):
    """Dispatch a validated plan to the existing simulation executor."""
    validate_plan(plan)

    if approved is not True:
        print("Remediation cancelled: explicit approval is required.")
        return False

    return remediate_public_ingress(
        plan["security_group_id"],
        plan["port"],
        approved=True,
    )
