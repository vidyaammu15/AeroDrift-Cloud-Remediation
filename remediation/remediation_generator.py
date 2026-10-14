import ast


def validate_remediation_ast(tree):
    """Allow only a single print() call containing a constant string."""
    if not isinstance(tree, ast.Module) or len(tree.body) != 1:
        raise ValueError("Unsafe remediation: unexpected module structure")

    statement = tree.body[0]
    if not isinstance(statement, ast.Expr):
        raise ValueError("Unsafe remediation: only a print expression is allowed")

    call = statement.value
    if not isinstance(call, ast.Call):
        raise ValueError("Unsafe remediation: expected a function call")

    if not isinstance(call.func, ast.Name) or call.func.id != "print":
        raise ValueError("Unsafe remediation: only print() is allowed")

    if call.keywords or len(call.args) != 1:
        raise ValueError("Unsafe remediation: unexpected arguments")

    if not isinstance(call.args[0], ast.Constant) or not isinstance(call.args[0].value, str):
        raise ValueError("Unsafe remediation: print argument must be a constant string")

    return True


def generate_remediation(security_group, port, source):
    """Generate and validate a simulation-only remediation plan."""
    if not isinstance(security_group, str) or not security_group.startswith("sg-"):
        raise ValueError("Invalid security group ID")

    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Invalid port")

    if source != "0.0.0.0/0":
        raise ValueError("This generator handles public IPv4 ingress only")

    message = (
        f"SIMULATION ONLY: revoke public ingress for "
        f"{security_group}, TCP port {port}"
    )

    tree = ast.Module(
        body=[
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[ast.Constant(value=message)],
                    keywords=[],
                )
            )
        ],
        type_ignores=[],
    )

    ast.fix_missing_locations(tree)
    validate_remediation_ast(tree)
    return ast.unparse(tree)


if __name__ == "__main__":
    plan = generate_remediation("sg-db", 3306, "0.0.0.0/0")
    print("Generated and validated remediation plan:")
    print(plan)
