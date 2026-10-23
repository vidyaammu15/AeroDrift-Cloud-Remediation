import json
import subprocess
import sys
import time
import threading
import queue
from pathlib import Path

root = Path(__file__).resolve().parent
live = root / "data" / "simulated_live_cloud.json"
event = root / "data" / "simulation_event.json"
baseline = root / "data" / "baseline_cloud.json"
monitor = root / "simulation" / "detection_monitor.py"

live_backup = live.read_bytes()
event_backup = event.read_bytes() if event.exists() else None
process = None
messages = queue.Queue()

def read_output(stream):
    try:
        for line in iter(stream.readline, ""):
            messages.put(line.rstrip())
    finally:
        messages.put(None)

try:
    # Start from a clean baseline.
    live.write_bytes(baseline.read_bytes())
    event.write_text(json.dumps({
        "action": "public_rule_removed",
        "timestamp": time.time() - 1
    }), encoding="utf-8")

    # -u makes monitor output unbuffered.
    process = subprocess.Popen(
        [sys.executable, "-u", str(monitor)],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )

    reader = threading.Thread(
        target=read_output,
        args=(process.stdout,),
        daemon=True
    )
    reader.start()

    # Allow the monitor to start before triggering the change.
    time.sleep(1)

    data = json.loads(live.read_text(encoding="utf-8"))
    db = next(sg for sg in data["security_groups"] if sg["id"] == "sg-db")
    rule = {
        "protocol": "tcp",
        "port": 3306,
        "source": "0.0.0.0/0"
    }

    if rule not in db["rules"]:
        db["rules"].append(rule)

    start = time.perf_counter()

    live.write_text(json.dumps(data, indent=4), encoding="utf-8")
    event.write_text(json.dumps({
        "action": "public_rule_added",
        "timestamp": time.time()
    }), encoding="utf-8")

    deadline = time.perf_counter() + 7
    detected = False

    while time.perf_counter() < deadline:
        remaining = deadline - time.perf_counter()
        try:
            line = messages.get(timeout=remaining)
        except queue.Empty:
            break

        if line is None:
            break

        print(line)

        if "AeroDrift: Cloud Change Detected" in line:
            elapsed = time.perf_counter() - start
            detected = True
            print(f"\nMeasured trigger-to-alert time: {elapsed:.3f} seconds")

            if elapsed < 5:
                print("PASS: Simulated alert appeared in under 5 seconds.")
            else:
                print("FAIL: Simulated alert took 5 seconds or longer.")
            break

    if not detected:
        print("FAIL: No alert received within 7 seconds.")

finally:
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
        if process.stdout:
            process.stdout.close()

    live.write_bytes(live_backup)

    if event_backup is not None:
        event.write_bytes(event_backup)
    elif event.exists():
        event.unlink()

    print("\nOriginal simulation files restored.")
