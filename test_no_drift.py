from drift.drift_detector import DriftDetector, load_json

baseline = load_json("data/baseline_cloud.json")

detector = DriftDetector(baseline, baseline)

drifts = detector.detect_security_group_drift()

print("\nAeroDrift No-Drift Test")
print("=" * 50)
print("Drifts detected:", len(drifts))

if not drifts:
    print("PASS - No drift detected")
else:
    print("FAIL - Unexpected drift detected")