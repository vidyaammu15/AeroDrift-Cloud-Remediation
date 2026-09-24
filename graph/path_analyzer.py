import networkx as nx


class PathAnalyzer:

    def __init__(self, graph):
        self.graph = graph

    def find_path(self, source, target):
        try:
            return nx.shortest_path(self.graph, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def can_reach(self, source, target):
        return nx.has_path(self.graph, source, target)

    def find_port_path(self, source, target, protocol, port):
        filtered_graph = nx.DiGraph()

        for u, v, data in self.graph.edges(data=True):
            if (
                data.get("protocol") == protocol
                and data.get("port") == port
            ):
                filtered_graph.add_edge(u, v, **data)

        if source in filtered_graph and target not in filtered_graph:
            for node in self.graph.successors(source):
                if node in filtered_graph:
                    filtered_graph.add_edge(source, node)

        if target not in filtered_graph:
            for predecessor in self.graph.predecessors(target):
                if predecessor in filtered_graph:
                    filtered_graph.add_edge(predecessor, target)

        try:
            return nx.shortest_path(filtered_graph, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None