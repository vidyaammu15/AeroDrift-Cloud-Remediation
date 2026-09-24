from drift.drift_detector import DriftDetector, load_json
from drift.exposure_detector import ExposureDetector
from drift.database_exposure import DatabaseExposureDetector
from drift.drift_report import DriftReport
from collector.mock_collector import MockAWSCollector
from graph.topology import CloudTopology
from graph.path_analyzer import PathAnalyzer

baseline = load_json("data/baseline_cloud.json")
current = load_json("data/drifted_cloud.json")

drifts = DriftDetector(
    baseline, current
).detect_security_group_drift()

exposures = ExposureDetector().detect(current)

database_risks = DatabaseExposureDetector().detect(current)

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

report = DriftReport().generate(
    drifts,
    exposures,
    database_risks
)

print("\nAeroDrift Week 2 Integration Test")
print("=" * 55)

print("Cloud Data Collection: PASS")
print("Drift Detection:", "PASS" if drifts else "FAIL")
print("Exposure Detection:", "PASS" if exposures else "FAIL")
print("Database Risk Detection:",
      "PASS" if database_risks else "FAIL")
print("NetworkX Path Analysis:", "PASS" if path else "FAIL")

print("\nFinal Risk Summary")
print("-" * 55)
print("Total Drifts:", report["total_drifts"])
print("Total Exposures:", report["total_exposures"])
print("Critical Risks:", report["critical_risks"])

if path:
    print("\nCritical Exposure Path:")
    print(" -> ".join(path))
    print("Protocol: TCP")
    print("Port: 3306")