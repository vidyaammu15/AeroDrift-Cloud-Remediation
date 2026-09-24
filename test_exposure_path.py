from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology
from graph.path_analyzer import PathAnalyzer

collector = MockAWSCollector("data/drifted_cloud.json")
cloud_data = collector.collect()

topology = CloudTopology()
graph = topology.build(cloud_data)

analyzer = PathAnalyzer(graph)

path = analyzer.find_path("INTERNET", "i-db-001")

print("\nAeroDrift Exposure Path Analysis")
print("=" * 50)

if path:
    print("Exposure Path Found:")
    print(" -> ".join(path))
else:
    print("No exposure path found.")

print("\nInternet can reach database:",
      analyzer.can_reach("INTERNET", "i-db-001"))