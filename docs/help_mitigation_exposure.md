# Mitigation Exposure View

## What this page shows

The **Mitigation Exposure View** answers a single question for each active mitigation:

> *How much would portfolio exposure increase if this mitigation were removed?*

This **counterfactual (marginal) approach** gives you an objective ranking of which mitigations are protecting the portfolio the most, rather than relying on subjective priority ratings.

---

## How it works

For each mitigation M in scope:

1. A **baseline** portfolio exposure is computed with all mitigations active.
2. A **counterfactual** is computed with M disabled (its relationships to risks are excluded).
3. The **EL Delta** = counterfactual final exposure − baseline final exposure.

A high EL Delta means the portfolio would be significantly more exposed without that mitigation — it is **critical to your risk posture**.

> **Why no TRI Delta?** The Tail Risk Indicator (`TRI = likelihood × severity^1.5`) is a property of each risk's intrinsic parameters — mitigations reduce *exposure* (through the mitigation factor) but do not alter likelihood or severity directly. Therefore TRI is the same with or without a mitigation and a counterfactual TRI delta would always be zero.

---

## Columns explained

| Column | Meaning |
|--------|---------|
| **Mitigation** | Name of the mitigation control |
| **Type** | Dedicated / Inherited / Baseline |
| **Status** | Proposed / In Progress / Implemented / Deferred |
| **Level** | Risk level(s) the mitigation addresses (Business / Operational / Mixed) |
| **Risks Covered** | Number of in-scope risks this mitigation directly addresses |
| **EL Delta ↑** | Exposure increase (EL units) if this mitigation is removed |
| **% Portfolio EL** | EL Delta as a percentage of total unmitigated base exposure across the whole portfolio |
| **% EL (Covered Risks)** | EL Delta as a percentage of the base exposure of *only the risks this mitigation covers*. For focused mitigations (e.g., covering 1–2 high-severity risks) this is a more meaningful effectiveness signal than % Portfolio EL. |

---

## Scope and lifecycle filtering

- **Scope**: Only risks and mitigations within the active scope are included. If no scope is active, the full graph is used.
- **Inactive risks**: By default, Accepted / Watching / Suppressed / Closed risks are excluded. Enable *"Include inactive risks (worst-case)"* to see the full latent exposure.
- **Level filter**: Narrows the display to mitigations that cover Business or Operational risks. The deltas are always computed at portfolio level — the filter only affects which rows are shown.

---

## Interpreting results

- **High EL Delta + Implemented status** → critical control; ensure it stays in place.
- **High EL Delta + Proposed/Deferred status** → unacceptable gap; prioritise implementation.
- **Low EL Delta** → mitigation has limited measurable impact; may indicate overlap with other controls or data quality issues (e.g., effectiveness not set).
- **Zero EL Delta** → mitigation covers only risks with no likelihood/severity data, or is fully redundant with another control.

---

## Relationship to What-If Analysis

The **What-If Analysis** page lets you *interactively* toggle multiple mitigations and observe the combined portfolio effect.

The **Mitigation Exposure View** computes the *individual* marginal value of each mitigation independently, making it suitable for prioritisation and reporting rather than scenario exploration.
