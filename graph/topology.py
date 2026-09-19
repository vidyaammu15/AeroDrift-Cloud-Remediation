import networkx as nx


class CloudTopology:

    def __init__(self):
        self.graph = nx.DiGraph()

    def build(self, cloud_data):

        self.graph.add_node(
            "INTERNET",
            type="EXTERNAL"
        )

        for vpc in cloud_data["vpcs"]:
            self.graph.add_node(
                vpc["id"],
                type="VPC",
                name=vpc["name"]
            )

        for subnet in cloud_data["subnets"]:
            self.graph.add_node(
                subnet["id"],
                type="SUBNET",
                name=subnet["name"],
                subnet_type=subnet["type"]
            )

            self.graph.add_edge(
                subnet["vpc_id"],
                subnet["id"],
                relation="contains"
            )

        for sg in cloud_data["security_groups"]:
            self.graph.add_node(
                sg["id"],
                type="SECURITY_GROUP",
                name=sg["name"]
            )

        for instance in cloud_data["instances"]:
            self.graph.add_node(
                instance["id"],
                type="EC2",
                name=instance["name"]
            )

            self.graph.add_edge(
                instance["subnet_id"],
                instance["id"],
                relation="contains"
            )

            for sg_id in instance["security_group_ids"]:
                self.graph.add_edge(
                    sg_id,
                    instance["id"],
                    relation="protects"
                )

        self._add_security_group_edges(cloud_data)

        return self.graph

    def _add_security_group_edges(self, cloud_data):

        for sg in cloud_data["security_groups"]:

            for rule in sg["rules"]:

                source = rule["source"]

                if source == "0.0.0.0/0":

                    self.graph.add_edge(
                        "INTERNET",
                        sg["id"],
                        relation="ingress",
                        protocol=rule["protocol"],
                        port=rule["port"]
                    )

                else:

                    self.graph.add_edge(
                        source,
                        sg["id"],
                        relation="ingress",
                        protocol=rule["protocol"],
                        port=rule["port"]
                    )

    def show_graph(self):

        print("\nCloud Topology")
        print("=" * 50)

        for node, data in self.graph.nodes(data=True):
            print(
                f"NODE: {node} | "
                f"TYPE: {data.get('type')}"
            )

        print("\nConnections")
        print("=" * 50)

        for source, target, data in self.graph.edges(data=True):
            print(
                f"{source} -> {target} | "
                f"{data.get('relation')}"
            )