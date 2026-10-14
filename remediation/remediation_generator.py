
import ast


def generate_remediation(security_group, port, source):
    """Generate a remediation plan for a public ingress rule."""
    if not isinstance(security_group, str) or not security_group.startswith("sg-"):
        raise ValueError("Invalid security group ID")

    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Invalid port")

    if source != "0.0.0.0/0":
        raise ValueError("This generator handles public IPv4 ingress only")

    tree = ast.Module(
        body=[
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[
                        ast.Constant(
                            value=(
                                "SIMULATION ONLY: revoke public ingress "
                                f"for {security_group}, TCP port {port}"
                            )
                        )
                    ],
                    keywords=[],
                )
            )
        ],
        type_ignores=[],
    )

    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


if __name__ == "__main__":
    plan = generate_remediation("sg-db", 3306, "0.0.0.0/0")
    print("Generated remediation plan:")
    print(plan)
