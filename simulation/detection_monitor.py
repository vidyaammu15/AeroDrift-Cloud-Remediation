
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
EVENT_FILE = DATA_DIR / "simulation_event.json"

POLL_INTERVAL = 0.1


def load_json(path):
    with open(path, "r") as file:
        return json.load(file)


def main():
    print("\nAeroDrift Detection Monitor")
    print("=" * 45)
    print(f"Watching: {LIVE_FILE}")
    print(f"Polling interval: {POLL_INTERVAL} seconds")
    print("Press Ctrl+C to stop.\n")

    # Ignore events that happened before monitoring began.
    startup_time = time.time()
    last_signature = None
    last_event_timestamp = startup_time

    try:
        while True:
            if LIVE_FILE.exists() and EVENT_FILE.exists():
                baseline = load_json(BASELINE_FILE)
                current = load_json(LIVE_FILE)
                event = load_json(EVENT_FILE)

                event_time = event.get("timestamp", 0)
                action = event.get("action", "")

                detector = DriftDetector(baseline, current)
                drifts = detector.detect_security_group_drift()

                if action == "public_rule_added" and drifts:
                    signature = json.dumps(drifts, sort_keys=True)

                    if (
                        signature != last_signature
                        and event_time >= startup_time
                        and event_time > last_event_timestamp
                    ):
                        detected_at = time.time()
                        elapsed = max(0, detected_at - event_time)

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
                            print("FAIL: Detection took 5 seconds or longer.")

                        last_signature = signature
                        last_event_timestamp = event_time

                elif action == "public_rule_removed" or not drifts:
                    last_signature = None
                    last_event_timestamp = max(
                        last_event_timestamp, event_time
                    )

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nDetection monitor stopped.")


if __name__ == "__main__":
    main()
