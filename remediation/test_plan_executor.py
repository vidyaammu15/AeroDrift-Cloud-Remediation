import unittest
from unittest.mock import patch

from remediation.plan_executor import validate_plan, execute_plan

VALID_PLAN = {
    "operation": "remove_public_ingress",
    "security_group_id": "sg-db",
    "protocol": "tcp",
    "port": 3306,
    "source": "0.0.0.0/0",
}


class TestPlanExecutor(unittest.TestCase):
    def test_accepts_valid_plan(self):
        self.assertTrue(validate_plan(VALID_PLAN))

    def test_rejects_unknown_operation(self):
        plan = {**VALID_PLAN, "operation": "run_shell"}
        with self.assertRaises(ValueError):
            validate_plan(plan)

    def test_rejects_unexpected_field(self):
        plan = {**VALID_PLAN, "command": "whoami"}
        with self.assertRaises(ValueError):
            validate_plan(plan)

    def test_rejects_wrong_security_group(self):
        plan = {**VALID_PLAN, "security_group_id": "sg-other"}
        with self.assertRaises(ValueError):
            validate_plan(plan)

    def test_rejects_wrong_port(self):
        plan = {**VALID_PLAN, "port": 22}
        with self.assertRaises(ValueError):
            validate_plan(plan)

    def test_rejects_non_dictionary(self):
        with self.assertRaises(ValueError):
            validate_plan("print('unsafe')")

    def test_requires_approval(self):
        with patch(
            "remediation.plan_executor.remediate_public_ingress"
        ) as executor:
            result = execute_plan(VALID_PLAN, approved=False)
            self.assertFalse(result)
            executor.assert_not_called()

    def test_dispatches_only_after_approval(self):
        with patch(
            "remediation.plan_executor.remediate_public_ingress",
            return_value=True,
        ) as executor:
            result = execute_plan(VALID_PLAN, approved=True)
            self.assertTrue(result)
            executor.assert_called_once_with(
                "sg-db", 3306, approved=True
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
