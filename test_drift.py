from drift.drift_detector import DriftDetector, load_json

baseline = load_json("data/baseline_cloud.json")
current = load_json("data/drifted_cloud.json")

detector = DriftDetector(baseline, current)

drifts = detector.detect_security_group_drift()

print("\nAeroDrift Drift Detection")
print("=" * 50)

if drifts:
    print("DRIFT DETECTED")

    for drift in drifts:
        print("\nSecurity Group:", drift["security_group"])
        print("Protocol:", drift["protocol"])
        print("Port:", drift["port"])
        print("Source:", drift["source"])
        print("Message:", drift["message"])
else:
    print("No drift detected.")