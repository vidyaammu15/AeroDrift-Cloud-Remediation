class DatabaseExposureDetector:

    def detect(self, cloud_data):
        risks = []

        for sg in cloud_data["security_groups"]:
            for rule in sg.get("rules", []):
                if rule["source"] == "0.0.0.0/0" and rule["port"] in [3306, 5432, 1433]:
                    risks.append({
                        "security_group": sg["id"],
                        "port": rule["port"],
                        "protocol": rule["protocol"],
                        "severity": "CRITICAL",
                        "message": (
                            f"Database port {rule['port']} in {sg['id']} "
                            f"is exposed to the Internet"
                        )
                    })

        return risks