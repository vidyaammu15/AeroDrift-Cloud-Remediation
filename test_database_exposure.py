from drift.drift_detector import load_json
from drift.database_exposure import DatabaseExposureDetector

cloud_data = load_json("data/drifted_cloud.json")

detector = DatabaseExposureDetector()
risks = detector.detect(cloud_data)

print("\nAeroDrift Database Exposure Detection")
print("=" * 50)

if risks:
    for risk in risks:
        print("Security Group:", risk["security_group"])
        print("Port:", risk["port"])
        print("Severity:", risk["severity"])
        print("Message:", risk["message"])
else:
    print("No database exposure detected.")