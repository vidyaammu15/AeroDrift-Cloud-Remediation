import json
import time
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from drift.drift_detector import DriftDetector

DATA_DIR = ROOT_DIR / "data"
BASELINE_FILE = DATA_DIR / "baseline_cloud.json"
LIVE_FILE = DATA_DIR / "simulated_live_cloud.json"

POLL_INTERVAL = 1


def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


def main():
    print("\nAeroDrift Detection Monitor")
    print("=" * 45)
    print(f"Watching: {LIVE_FILE}")
    print(f"Polling interval: {POLL_INTERVAL} second(s)")
    print("Press Ctrl+C to stop.\n")

    last_signature = None

    try:
        while True:
            if LIVE_FILE.exists():
                baseline = load_json(BASELINE_FILE)
                current = load_json(LIVE_FILE)

                detector = DriftDetector(baseline, current)
                drifts = detector.detect_security_group_drift()

                if drifts:
                    signature = json.dumps(drifts, sort_keys=True)

                    if signature != last_signature:
                        detected_at = time.time()
                        changed_at = LIVE_FILE.stat().st_mtime
                        elapsed = max(0, detected_at - changed_at)

                        print("\n" + "=" * 45)
                        print("AeroDrift: Cloud Change Detected")
                        print("=" * 45)

                        for drift in drifts:
                            print("Security Group:", drift["security_group"])
                            print("Protocol:", drift["protocol"])
                            print("Port:", drift["port"])
                            print("Source:", drift["source"])
                            print("Drift:", drift["message"])

                        print(f"\nDetection time: {elapsed:.3f} seconds")

                        if elapsed < 5:
                            print("PASS: Detection completed under 5 seconds.")
                        else:
                            print("CHECK: Detection took 5 seconds or longer.")

                        last_signature = signature

                else:
                    last_signature = None

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nDetection monitor stopped.")


if __name__ == "__main__":
    main()