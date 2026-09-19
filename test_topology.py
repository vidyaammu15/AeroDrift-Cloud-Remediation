from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology

collector = MockAWSCollector()
cloud_data = collector.collect()

topology = CloudTopology()
graph = topology.build(cloud_data)

topology.show_graph()

print("\nTotal Nodes:", graph.number_of_nodes())
print("Total Edges:", graph.number_of_edges())