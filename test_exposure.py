from drift.drift_detector import load_json
from drift.exposure_detector import ExposureDetector

cloud_data = load_json("data/drifted_cloud.json")

detector = ExposureDetector()
exposures = detector.detect(cloud_data)

print("\nAeroDrift Exposure Detection")
print("=" * 50)

if exposures:
    for exposure in exposures:
        print("Security Group:", exposure["security_group"])
        print("Port:", exposure["port"])
        print("Severity:", exposure["severity"])
        print("Message:", exposure["message"])
else:
    print("No Internet exposure detected.")