import networkx as nx

class PathAnalyzer:
    def __init__(self, graph):
        self.graph = graph

    def find_path(self, source, target):
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None

    def can_reach(self, source, target):
        return nx.has_path(self.graph, source, target)