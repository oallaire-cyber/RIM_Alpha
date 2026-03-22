### ⚠️ Threshold Alerts

**Threshold Alerts** automatically flag risks whose exposure scores exceed configurable
thresholds — surfaced directly in the **Exposure dashboard** on the Home page.

---

**What are Threshold Alerts?**

Two metrics are monitored against domain-configured thresholds:

| Metric | Description | Default Threshold |
|--------|-------------|-------------------|
| **Expected Loss (EL)** | Final exposure after mitigations and influence limitation | 50.0 |
| **Tail Risk Indicator (TRI)** | Likelihood × Severity^1.5 — non-linear severity weighting | 25.0 |

When a risk's EL or TRI exceeds its threshold, it appears in the alert panel.

---

**Where to Find Alerts**

After computing exposure (Home page → **⚡ Exposure** expander → **Compute**), the
**⚠️ Threshold Alerts** panel appears immediately below the quadrant distribution widget:

- **⚠️ Warning panel** (when breaches exist): two columns — EL Breaches and TRI Breaches,
  each listing the risk name, level, and actual value vs threshold
- **✅ All within thresholds** (when no breaches): a green success indicator confirms the
  portfolio is within configured bounds

> The panel only appears when `enabled: true` in the schema `alert_thresholds` block.

---

**Configuring Thresholds**

Thresholds are per-domain and set in the active schema YAML:

```yaml
analysis:
  alert_thresholds:
    expected_loss_threshold: 50.0
    tail_risk_indicator_threshold: 25.0
    enabled: true
```

To change thresholds:
1. Go to **Configuration** page → **Schema Editor**
2. Edit the `alert_thresholds` block under `analysis:`
3. Save and reload the schema

To disable alerts entirely, set `enabled: false`.

---

**Scope Awareness**

Threshold alerts respect the active scope — only risks included in the current
scope contribute to the breach list. No breaches appear for out-of-scope risks.

---

**Lifecycle Awareness**

Template risks and inactive lifecycle risks (Accepted, Watching, Suppressed, Closed,
Archived) are excluded from exposure calculations and therefore cannot trigger alerts.
Only **Active** specific risks are evaluated.

---

> **Tip:** Use TRI breaches to identify risks that may appear moderate in EL but carry
> disproportionate tail-end severity. These are the risks most likely to cause surprises.
