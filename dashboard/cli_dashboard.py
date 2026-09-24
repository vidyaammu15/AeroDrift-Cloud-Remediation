from rich.console import Console
from rich.tree import Tree
from rich.table import Table


class AeroDriftDashboard:

    def __init__(self):
        self.console = Console()

    def show_topology(self, graph):
        tree = Tree("[bold]AeroDrift Cloud Topology[/bold]")

        internet = tree.add("INTERNET")

        for sg in graph.nodes:
            if graph.nodes[sg].get("type") == "SECURITY_GROUP":
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
            table.add_row(
                risk["security_group"],
                str(risk["port"]),
                risk["severity"],
                risk["message"]
            )

        self.console.print(table)