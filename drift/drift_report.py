class DriftReport:

    def generate(self, drifts, exposures, database_risks):
        report = {
            "total_drifts": len(drifts),
            "total_exposures": len(exposures),
            "critical_risks": len(database_risks),
            "drifts": drifts,
            "exposures": exposures,
            "critical_risks": database_risks
        }

        return report