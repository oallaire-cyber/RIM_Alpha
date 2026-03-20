### ♻️ Risk Lifecycle Engine

Risks move through a **6-state lifecycle** that controls whether they
participate in active exposure analysis and how they are managed over time.

---

**States:**

| Status | Active? | Meaning |
|--------|---------|---------|
| 🟢 Active | Yes | Risk is open and included in all analysis |
| 🟡 Contingent | Yes | Risk is conditional — active but not yet triggered |
| 🔵 Watching | No | Accepted risk being monitored for trigger re-activation |
| 🟠 Suppressed | No | Exposure fell below acceptance threshold after acceptance |
| ✅ Accepted | No | Formally accepted by an owner; excluded from active analysis |
| ⬛ Closed | No | Risk condition no longer exists; retained for audit |
| 🗄️ Archived | No | Retained for historical record only |

Risks in any **inactive** state (Watching, Suppressed, Accepted, Closed, Archived)
are automatically excluded from exposure calculations and statistics.

---

**Running the Lifecycle Engine:**

1. Navigate to **💾 Data Management**
2. Expand **⚙️ Lifecycle Engine**
3. Click **▶ Run Lifecycle Check**

The engine evaluates three things in one pass:

---

**1️⃣ Trigger Review** *(Watching & Suppressed risks)*

Lists all risks in Watching or Suppressed state along with their
**Trigger Condition** — the free-text description of what would re-activate the risk.

- Review each condition manually
- Click **Mark as Triggered** to return the risk to **Active** status

> Trigger conditions are free text and require human judgement.
> Automated condition evaluation is planned for a future release.

---

**2️⃣ Auto-Acceptance Candidates** *(Active risks)*

Identifies Active risks that meet acceptance criteria based on the
schema-configured `risk_lifecycle_rules`:

| Guard | Rule | Result |
|-------|------|--------|
| Severity ceiling | Severity ≥ ceiling (default 7) | Blocked — requires human decision |
| High-severity quadrant | Critical or Severity quadrant | Blocked — requires human decision |
| Exposure threshold | Final exposure > threshold (default 20) | Blocked |
| Otherwise | All guards pass | **Eligible for acceptance** |

- Eligible risks appear in the **Eligible** table — click **Accept All Eligible**
- Blocked risks appear in the **Blocked** table with the blocking reason shown
- Each blocked risk has a **🔓 Force Accept** button — use this to override the guards
  and accept the risk with human authority (records the same acceptance date)

Accepting a risk sets its status to **Accepted**, records today's date, and
removes it from active exposure calculations.

---

**3️⃣ Archive Alerts** *(Accepted & Closed risks)*

Flags risks that have been in an inactive state longer than
`archive_retention_days` (default 180 days) with no active mitigations.

- Alerts appear as warnings with the risk name and days since acceptance
- Select risks and click **Archive Selected** to move them to **Archived** status

---

**Accepted Risks Toggle:**

In Data Management, enable **Show Accepted Risks** in the sidebar to view
a read-only table of all accepted risks. From there you can:
- Review acceptance details (date, owner, trigger condition)
- **Re-open** a risk (returns to Active status)

---

**Lifecycle Rules Configuration:**

Thresholds are set in the schema YAML under `risk_lifecycle_rules`:

```yaml
risk_lifecycle_rules:
  acceptance_threshold: 20      # max final exposure for auto-acceptance
  severity_ceiling: 7           # severity at or above this blocks auto-acceptance
  archive_retention_days: 180   # days in inactive state before archive alert
  quadrant_thresholds:
    likelihood_threshold: 6
    severity_threshold_frequency: 6
    severity_threshold_severity: 7
```

Edit in **⚙️ Configuration → Schema Editor**.

---

> **Node Property Panel:** When you select a node on the graph that has
> an inactive lifecycle status, the **Exposure Metrics** section explains
> why it was excluded from the last calculation rather than showing an
> empty result.
