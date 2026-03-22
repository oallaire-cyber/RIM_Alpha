### 🎲 Simulation Page

The **Simulation** page (`🎲 Simulation` in the sidebar) provides four modes for
validating the exposure model and calibrating domain-specific parameters — all using
the live risk graph from the active DB connection where applicable.

---

#### Simulation Modes

| Mode | Data Source | Purpose |
|------|-------------|---------|
| **Monte Carlo (Random)** | Synthetic | Random scenario generation for model validation |
| **Mitigation Path** | Synthetic | Progressive mitigation curve analysis |
| **Scope-Based (Real Data)** | Live DB | Real graph topology; scope-aware; results storable |
| **TRI α Calibration** | Live DB | Sweep TRI exponent α to find the domain-appropriate value |

---

#### Monte Carlo (Random)

Generates N random risk networks with configurable:
- Number of Operational and Strategic risks
- Influence density
- Likelihood and severity ranges

Outputs: residual risk % distribution, risk score distribution, max exposure histogram.

---

#### Mitigation Path

Starts from an unmitigated network and adds mitigations progressively,
tracking the exposure reduction curve across N steps × M paths.

---

#### Scope-Based (Real Data)

Uses actual risk topology from the active DB connection:

1. Select **Scope-Based (Real Data)** mode
2. Ensure a DB connection is active (navigate to Home first if needed)
3. Active scope is shown in the sidebar info box (or Full Graph if none is set)
4. Configure parameters:
   - **Parameter mode**: Real L×I (uses DB values) or Random L×I (randomises within ranges)
   - **Number of simulations**: 100–5,000
   - **Mitigation variance %**: how much coverage varies around the real level each run
5. Optionally enable **🧟 Worst-Case Canvas** (see below)
6. Click **🚀 Run Simulation**

Results show Mean Residual Risk %, Mean Risk Score, Mean Max Exposure, and Mean Coverage,
followed by distribution charts and scatter clouds.

**Saving results:**
- **💾 Save to Comparison** — saves the run to the Saved Results tab; multiple runs can be
  compared with Δ delta columns and exported to Excel.
- **📥 Export CSV** — direct download of the raw results DataFrame without saving to the
  comparison table.

> The results panel persists across reruns, so clicking 💾 Save or 📥 Export will not
> navigate away from the results.

---

#### 🧟 Worst-Case Canvas (F31c)

The **Worst-Case Canvas** toggle (shared by Scope-Based and TRI α Calibration modes)
re-activates lifecycle-inactive risks that are normally excluded from analysis:

- **Accepted** — risks that have been formally accepted
- **Watching** — risks under monitoring but not yet active
- **Suppressed** — risks temporarily removed from active analysis
- **Closed** — risks resolved and archived

When enabled:
- A banner shows how many latent risks were re-activated
- Results are labelled `[Worst-Case]` in the Saved Results tab
- The mode field in saved records becomes `"Scope-Based (Worst-Case)"`

Use this mode to answer: *"What would our portfolio look like if all lifecycle decisions
were reversed?"* It surfaces hidden tail exposure from risks that management has accepted
or suppressed.

---

#### 📐 TRI α Calibration (F31d)

The **TRI α Calibration** mode helps domain analysts validate the TRI exponent (α).

**What is α?**

The Tail Risk Indicator is defined as:

> **TRI = Likelihood × Severity^α**

The exponent α controls how strongly high-severity risks are amplified:

| α | Effect |
|---|--------|
| 1.0 | No amplification — TRI equals base exposure (L × S) |
| 1.5 | Current default — moderate tail emphasis |
| 2.0+ | Strong tail emphasis — high-severity risks dominate |

**How to use:**

1. Select **TRI α Calibration** mode
2. Set α range (min, max, step) and runs per α
3. Choose parameter mode (Real L×I or Random L×I)
4. Optionally enable **🧟 Worst-Case Canvas**
5. Click **🚀 Run Calibration**

The engine sweeps each α value, runs N Monte Carlo iterations per α, and for each risk
computes `TRI = L × S^α` and classifies it into one of four quadrants using the same
thresholds as the main exposure engine.

**Outputs:**

- **Calibration Chart**: Mean TRI vs α with ±1σ band and P95 line; stacked quadrant
  distribution bar chart vs α. Current default (α=1.5) and recommended α annotated.
- **Calibration Report**: Table of α → Mean TRI / Std TRI / P95 TRI / quadrant %s.
  The recommended row is highlighted in green.
- **Raw Data**: Full calibration DataFrame with CSV export.

**Target profile selectbox:**

Choose the quadrant distribution that best reflects your domain:
- **Balanced**: ~25% per quadrant
- **Tail-Heavy (Critical dominant)**: ~40% Critical
- **Frequency-Heavy**: ~45% Frequency
- **Severity-Heavy**: ~50% Severity

The recommended α minimises the L2 distance to the selected target. To apply the new α,
update `tri_alpha` under `exposure_model` in `schemas/[domain]/schema.yaml`.

---

#### 📊 Saved Results Tab

All saved simulations (Scope-Based and TRI α Calibration) appear in the **📊 Saved Results**
comparison tab:

- **Comparison table**: side-by-side key metrics with Δ columns vs. the first saved run
- **Per-run expanders**: full parameters + metrics + first 50 raw rows
- **📥 Export All Runs (Excel)**: all saved runs as separate sheets in one workbook
- **🗑️ Clear All**: clears the comparison table (with confirmation checkbox)

> Saved results are session-local (in-memory). Use **Export All Runs (Excel)** to persist
> results beyond the current browser session.
