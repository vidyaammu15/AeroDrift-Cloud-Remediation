import json
from drift.drift_detector import DriftDetector, load_json

baseline = load_json("data/baseline_cloud.json")
current = load_json("data/baseline_cloud.json")

for sg in current["security_groups"]:
    if sg["id"] == "sg-web":
        sg["rules"].append({
            "protocol": "tcp",
            "port": 22,
            "source": "0.0.0.0/0"
        })

detector = DriftDetector(baseline, current)
drifts = detector.detect_security_group_drift()

print("\nAeroDrift Additional Drift Test")
print("=" * 50)

print("Drifts detected:", len(drifts))

for drift in drifts:
    print("Security Group:", drift["security_group"])
    print("Port:", drift["port"])
    print("Source:", drift["source"])
    print("Message:", drift["message"])