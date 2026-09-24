from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology
from graph.path_analyzer import PathAnalyzer

collector = MockAWSCollector("data/drifted_cloud.json")
cloud_data = collector.collect()

topology = CloudTopology()
graph = topology.build(cloud_data)

analyzer = PathAnalyzer(graph)

path = analyzer.find_port_path(
    "INTERNET",
    "i-db-001",
    "tcp",
    3306
)

print("\nAeroDrift Port-Aware Path Analysis")
print("=" * 50)

if path:
    print("TCP 3306 Exposure Path:")
    print(" -> ".join(path))
    print("Risk: CRITICAL")
else:
    print("No TCP 3306 exposure path found.")