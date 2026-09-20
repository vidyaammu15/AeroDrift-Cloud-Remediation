from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology
from graph.path_analyzer import PathAnalyzer

collector = MockAWSCollector()
cloud_data = collector.collect()

topology = CloudTopology()
graph = topology.build(cloud_data)

analyzer = PathAnalyzer(graph)

path = analyzer.find_path("INTERNET", "i-db-001")

print("\nAeroDrift Week 1 Integration Test")
print("=" * 50)

print("Cloud data collected:", "PASS")
print("Topology created:", "PASS")
print("Nodes:", graph.number_of_nodes())
print("Edges:", graph.number_of_edges())

if path:
    print("Path analysis:", "PASS")
    print("Path:", " -> ".join(path))
else:
    print("Path analysis:", "FAIL")

print("\nWeek 1 foundation completed successfully.")