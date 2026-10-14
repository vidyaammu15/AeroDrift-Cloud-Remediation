import ast
import unittest

from remediation.remediation_generator import (
    generate_remediation,
    validate_remediation_ast,
)


class TestASTValidation(unittest.TestCase):
    def test_generated_plan_is_valid(self):
        plan = generate_remediation("sg-db", 3306, "0.0.0.0/0")
        tree = ast.parse(plan)
        self.assertTrue(validate_remediation_ast(tree))

    def test_rejects_exec(self):
        tree = ast.parse("exec('print(1)')")
        with self.assertRaises(ValueError):
            validate_remediation_ast(tree)

    def test_rejects_file_access(self):
        tree = ast.parse("open('data.json')")
        with self.assertRaises(ValueError):
            validate_remediation_ast(tree)

    def test_rejects_extra_statements(self):
        tree = ast.parse("print('safe')\nprint('unexpected')")
        with self.assertRaises(ValueError):
            validate_remediation_ast(tree)

    def test_rejects_non_constant_argument(self):
        tree = ast.parse("print(input())")
        with self.assertRaises(ValueError):
            validate_remediation_ast(tree)


if __name__ == "__main__":
    unittest.main(verbosity=2)
