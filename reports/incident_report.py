from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)


def generate_incident_report(
    database_risks,
    snapshot_history=None,
    configuration_changes=None,
    output_path="reports/aerodrift_incident_report.pdf",
    remediation_outcome="Not provided",
    verification_status="Not provided",
    rollback_status="Not provided",
):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="AeroTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#163A5F"),
    ))

    story = [
        Paragraph("AeroDrift Cloud Incident Report", styles["AeroTitle"]),
        Paragraph(
            "Generated: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            styles["Normal"],
        ),
        Spacer(1, 8 * mm),
        Paragraph("1. Executive Summary", styles["Heading2"]),
    ]

    risks = database_risks or []
    critical_count = sum(
        risk.get("severity", "").upper() == "CRITICAL"
        for risk in risks
    )

    story.append(Paragraph(
        f"Total database risks: {len(risks)}. "
        f"Critical risks: {critical_count}. "
        "This report describes the supplied cloud data.",
        styles["BodyText"],
    ))

    story.extend([
        Spacer(1, 5 * mm),
        Paragraph("2. Security Risks", styles["Heading2"]),
    ])

    rows = [["Security Group", "Port", "Severity", "Details"]]
    for risk in risks:
        rows.append([
            str(risk.get("security_group", "Unknown")),
            str(risk.get("port", "Unknown")),
            str(risk.get("severity", "Unknown")),
            Paragraph(
                str(risk.get("message", "No details")),
                styles["BodyText"],
            ),
        ])

    if len(rows) == 1:
        rows.append(["None", "-", "-", "No risks supplied"])

    risk_table = Table(
        rows,
        colWidths=[32 * mm, 18 * mm, 25 * mm, 95 * mm],
        repeatRows=1,
    )
    risk_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(risk_table)

    story.extend([
        Spacer(1, 6 * mm),
        Paragraph("3. Historical Snapshots", styles["Heading2"]),
    ])

    history_rows = [["Created At", "Source", "Nodes", "Edges", "Snapshot ID"]]
    for snapshot in (snapshot_history or []):
        history_rows.append([
            str(snapshot.get("created_at", "-")),
            str(snapshot.get("source", "-")),
            str(snapshot.get("node_count", "-")),
            str(snapshot.get("edge_count", "-")),
            str(snapshot.get("snapshot_id", "-"))[:8],
        ])

    if len(history_rows) == 1:
        history_rows.append(["No snapshots supplied", "-", "-", "-", "-"])

    history_table = Table(history_rows, repeatRows=1)
    history_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#287271")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(history_table)

    story.extend([
        Spacer(1, 6 * mm),
        Paragraph("4. Configuration Changes", styles["Heading2"]),
    ])

    changes = configuration_changes or {}
    if changes:
        for group_id, details in changes.items():
            story.append(Paragraph(
                f"<b>{group_id}</b>: before={details.get('before')}; "
                f"after={details.get('after')}",
                styles["BodyText"],
            ))
            story.append(Spacer(1, 2 * mm))
    else:
        story.append(Paragraph(
            "No configuration changes were supplied.",
            styles["BodyText"],
        ))

    story.extend([
        Spacer(1, 6 * mm),
        Paragraph("5. Remediation Status", styles["Heading2"]),
    ])

    status_rows = [
        ["Status Field", "Reported Result"],
        ["Remediation Outcome", escape(str(remediation_outcome))],
        ["Verification Status", escape(str(verification_status))],
        ["Rollback Status", escape(str(rollback_status))],
    ]

    status_table = Table(
        status_rows,
        colWidths=[55 * mm, 115 * mm],
        repeatRows=1,
    )
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(status_table)

    story.extend([
        Spacer(1, 6 * mm),
        Paragraph("6. Recommended Actions", styles["Heading2"]),
        Paragraph(
            "• Remove public access from database ports such as TCP 3306.<br/>"
            "• Restrict database ingress to approved application security groups.<br/>"
            "• Review configuration changes and verify remediation afterward.<br/>"
            "• Use the approved remediation workflow before applying changes.",
            styles["BodyText"],
        ),
        Spacer(1, 5 * mm),
        Paragraph(
            "This report reflects the supplied data and does not confirm "
            "live cloud remediation or production security.",
            styles["Italic"],
        ),
    ])

    doc.build(story)
    return output
