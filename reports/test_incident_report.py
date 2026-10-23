
import json
from pathlib import Path

from drift.database_exposure import DatabaseExposureDetector
from history.topology_store import list_snapshots
from reports.incident_report import generate_incident_report

ROOT = Path(__file__).resolve().parent.parent


def main():
    cloud_file = ROOT / "data" / "drifted_cloud.json"
    cloud_data = json.loads(cloud_file.read_text(encoding="utf-8"))

    risks = DatabaseExposureDetector().detect(cloud_data)
    snapshots = list_snapshots()

    output_file = ROOT / "reports" / "aerodrift_incident_report.pdf"

    result = generate_incident_report(
        database_risks=risks,
        snapshot_history=snapshots,
        output_path=output_file,
        remediation_outcome="SUCCESS",
        verification_status="PASS",
        rollback_status="NOT_REQUIRED",
    )

    print("PDF report generated:", result)
    print("Database risks included:", len(risks))
    print("Historical snapshots included:", len(snapshots))
    print("PDF file exists:", result.exists())
    print("PDF size (bytes):", result.stat().st_size)

    assert result.exists(), "PDF was not created"
    assert result.stat().st_size > 0, "PDF is empty"

    print("Incident report generation: PASS")


if __name__ == "__main__":
    main()
