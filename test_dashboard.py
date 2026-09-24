from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology
from drift.database_exposure import DatabaseExposureDetector
from dashboard.cli_dashboard import AeroDriftDashboard

collector = MockAWSCollector("data/drifted_cloud.json")
cloud_data = collector.collect()

topology = CloudTopology()
graph = topology.build(cloud_data)

risks = DatabaseExposureDetector().detect(cloud_data)

dashboard = AeroDriftDashboard()

print("\nAeroDrift CLI Dashboard")
print("=" * 50)

dashboard.show_topology(graph)
dashboard.show_risk(risks)