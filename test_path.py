from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology
from graph.path_analyzer import PathAnalyzer

collector = MockAWSCollector()
cloud_data = collector.collect()

topology = CloudTopology()
graph = topology.build(cloud_data)

analyzer = PathAnalyzer(graph)

source = "INTERNET"
target = "i-db-001"

path = analyzer.find_path(source, target)

print("\nNetwork Path Analysis")
print("=" * 50)

if path:
    print("Path Found:")
    print(" -> ".join(path))
else:
    print("No path found.")

print("\nInternet can reach database:", analyzer.can_reach(source, target))