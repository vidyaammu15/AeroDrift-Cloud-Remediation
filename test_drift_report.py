from drift.drift_detector import DriftDetector, load_json
from drift.exposure_detector import ExposureDetector
from drift.database_exposure import DatabaseExposureDetector
from drift.drift_report import DriftReport

baseline = load_json("data/baseline_cloud.json")
current = load_json("data/drifted_cloud.json")

drifts = DriftDetector(baseline, current).detect_security_group_drift()
exposures = ExposureDetector().detect(current)
database_risks = DatabaseExposureDetector().detect(current)

report = DriftReport().generate(
    drifts,
    exposures,
    database_risks
)

print("\nAeroDrift Drift Report")
print("=" * 50)
print("Total Drifts:", report["total_drifts"])
print("Total Exposures:", report["total_exposures"])
print("Critical Risks:", report["critical_risks"])

for risk in report["critical_risks"]:
    print("\nCRITICAL RISK")
    print(risk["message"])