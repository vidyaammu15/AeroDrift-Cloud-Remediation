class ExposureDetector:

    def detect(self, cloud_data):
        exposures = []

        for sg in cloud_data["security_groups"]:
            for rule in sg.get("rules", []):
                if rule["source"] == "0.0.0.0/0":
                    exposures.append({
                        "security_group": sg["id"],
                        "protocol": rule["protocol"],
                        "port": rule["port"],
                        "source": rule["source"],
                        "severity": "HIGH",
                        "message": (
                            f"Internet exposure detected on "
                            f"{sg['id']} port {rule['port']}"
                        )
                    })

        return exposures