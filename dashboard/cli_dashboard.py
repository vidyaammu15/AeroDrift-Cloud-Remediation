from rich.console import Console
from rich.tree import Tree
from rich.table import Table


class AeroDriftDashboard:

    def __init__(self):
        self.console = Console()

    def show_topology(self, graph, risky_groups=None):
        risky_groups = set(risky_groups or [])

        tree = Tree("[bold]AeroDrift Cloud Topology[/bold]")
        internet = tree.add("INTERNET")

        for sg in graph.nodes:
            if graph.nodes[sg].get("type") == "SECURITY_GROUP":
                if sg in risky_groups:
                    sg_branch = internet.add(f"[bold red]{sg} [CRITICAL][/bold red]")
                else:
                    sg_branch = internet.add(sg)

                for instance in graph.successors(sg):
                    if graph.nodes[instance].get("type") == "EC2":
                        sg_branch.add(instance)

        self.console.print(tree)

    def show_risk(self, database_risks):
        table = Table(title="AeroDrift Security Risks")

        table.add_column("Security Group")
        table.add_column("Port")
        table.add_column("Severity")
        table.add_column("Message")

        for risk in database_risks:
            critical = risk["severity"].upper() == "CRITICAL"

            style = "bold red" if critical else "yellow"

            table.add_row(
                f"[{style}]{risk['security_group']}[/{style}]",
                f"[{style}]{risk['port']}[/{style}]",
                f"[{style}]{risk['severity']}[/{style}]",
                f"[{style}]{risk['message']}[/{style}]"
            )

        self.console.print(table)