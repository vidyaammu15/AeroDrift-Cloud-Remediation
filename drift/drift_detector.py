import json


class DriftDetector:
    def __init__(self, baseline, current):
        self.baseline = baseline
        self.current = current

    def detect_security_group_drift(self):
        drifts = []

        baseline_sgs = {
            sg["id"]: sg for sg in self.baseline["security_groups"]
        }

        current_sgs = {
            sg["id"]: sg for sg in self.current["security_groups"]
        }

        for sg_id, baseline_sg in baseline_sgs.items():
            current_sg = current_sgs.get(sg_id)

            if not current_sg:
                continue

            baseline_rules = baseline_sg.get("rules", [])
            current_rules = current_sg.get("rules", [])

            for rule in current_rules:
                if rule not in baseline_rules:
                    drifts.append({
                        "type": "SECURITY_GROUP_DRIFT",
                        "security_group": sg_id,
                        "protocol": rule["protocol"],
                        "port": rule["port"],
                        "source": rule["source"],
                        "message": (
                            f"New ingress rule detected in {sg_id}: "
                            f"{rule['protocol']} port {rule['port']} "
                            f"from {rule['source']}"
                        )
                    })

        return drifts


def load_json(path):
    with open(path, "r") as file:
        return json.load(file)