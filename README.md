## AeroDrift: Agentic Cloud Topology & Remediation
AeroDrift is a Python-based cloud security project focused on cloud infrastructure monitoring, configuration drift detection, and network exposure analysis.
## Week-wise Project Progress Report

### Week 1: Cloud Data Collection and Topology Modeling
**Status: Completed**

**Objective:** To collect cloud infrastructure data and represent the relationships between cloud resources.

**Work Completed:**
- Developed a mock cloud data collector.
- Created sample cloud data containing VPCs, subnets, security groups, and EC2 instances.
- Implemented an AWS data collector using Boto3.
- Implemented concurrent collection of cloud resource information.
- Built a directed cloud topology graph using NetworkX.
- Developed network path analysis to examine connectivity between resources.
- Tested the collector and topology modules using simulated cloud data.

**Outcome:** A functional local cloud topology model capable of representing infrastructure resources and analyzing network paths.

### Week 2: Configuration Drift and Security Exposure Detection
**Status: Completed**

**Objective:** To detect unexpected cloud configuration changes and identify potential security risks.

**Work Completed:**
- Created baseline and drifted cloud configuration datasets.
- Implemented security group configuration drift detection.
- Detected newly added ingress rules by comparing configurations.
- Developed security exposure detection for publicly accessible ports.
- Implemented database exposure detection for TCP port 3306.
- Added port-aware network path analysis.
- Integrated drift and exposure findings into a command-line dashboard.
- Tested the system using baseline, drifted, and simulated configurations.

**Key Test Scenario:**

| Configuration | Database Port 3306 Source |
|---|---|
| Baseline | `sg-web` |
| Simulated drift | `0.0.0.0/0` |

The system detects the public ingress rule and reports the database exposure as a critical security risk.

**Outcome:** Configuration drift detection, network exposure analysis, database risk detection, and the Week 2 integration test were completed using local test data.

### Mid-Project Review: Simulated Cloud Change Detection
**Status: Simulation test completed**

**Objective:** To demonstrate detection of a simulated security group change within the 5-second target.

**Work Completed:**
- Developed a security group simulator to add and remove a public database ingress rule.
- Implemented a detection monitor to watch changes in the simulated cloud configuration.
- Compared the current configuration against the baseline.
- Reported the affected security group, protocol, port, source, and detection time.
- Verified that the public database rule could be removed and the original rule restored.

**Detection Test Results:**

| Metric | Result |
|---|---|
| Security Group | `sg-db` |
| Protocol | TCP |
| Port | 3306 |
| Public Ingress Source | `0.0.0.0/0` |
| Detection Target | Under 5 seconds |
| Recorded Detection Time | 0.040 seconds |
| Result | PASS |

**Outcome:** The local simulation detected the introduced public database rule within the 5-second target.

### Overall Progress Up to Mid-Project Review

- **Week 1:** Cloud data collection and topology modeling completed.
- **Week 2:** Configuration drift and security exposure detection completed.
- **Mid-Project Review:** Simulated cloud change detection demonstrated within the 5-second target.

The project has completed its initial cloud topology, drift detection, exposure analysis, and simulated mid-review demonstration.

**Environment Note:** The demonstrated tests use simulated cloud infrastructure. Live AWS security group modification and detection have not been validated in these results.
Week 3: Remediation Planning and Safety Controls

Status: Core simulation tests passed

Objective: To validate remediation plans and prevent unsafe or unauthorized actions.

Work Completed:

Implemented remediation plan validation.

Added checks for invalid plan formats, unexpected fields, unknown operations, and incorrect security group or port values.

Required explicit approval before remediation execution.

Implemented simulated removal of publicly exposed database ingress rules.

Verified that the intended public rule was removed while the trusted web rule was preserved.

Implemented audited rollback and tested approved and rejected rollback scenarios.

Outcome: Remediation and rollback safety controls passed the available unit and integration tests in the simulated environment.

Week 4: Historical Monitoring, Reporting, and Integration

Status: Core workflow tests passed

Objective: To maintain historical cloud configuration records and generate security incident reports.

Work Completed:

Implemented SQLite-based historical snapshot storage.

Tested snapshot retrieval and configuration comparison.

Integrated topology, drift, and exposure information into a command-line dashboard.

Generated PDF incident reports.

Integrated detection, simulated remediation, verification, snapshot recording, and incident reporting into an end-to-end workflow.

Verified that the snapshot audit event was recorded.

End-to-End Integration Test Results:

Check

Result

Public database exposure detected

PASS

Simulated public rule removal

PASS

Trusted web rule preserved

PASS

Final verification

PASS

Historical snapshot saved

PASS

Snapshot audit event recorded

PASS

Incident PDF generated

PASS

Outcome: The end-to-end simulated remediation workflow completed successfully.
