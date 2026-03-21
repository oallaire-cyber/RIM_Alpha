### 🔬 What-If Analysis

Explore scenario impact **without changing the database**.
Toggle mitigations ON/OFF in-memory and instantly see how EL and TRI shift.

---

#### How It Works

1. **Compute Baseline** — fetches the current graph data (respecting the active scope
   and lifecycle filters) and calculates the reference `GlobalExposureResult`.
2. **Toggle mitigations** — uncheck any mitigation to remove it and its MITIGATES
   relationships from the in-memory recomputation. Re-check to restore.
3. **Results update instantly** — the portfolio summary and per-risk delta table
   reflect the current toggle state on every page render.
4. **Reset Scenario** — re-enables all mitigations to return to the baseline state.

> No database writes are performed at any point. All exploration is session-local.

---

#### Portfolio Summary Metrics

| Metric | Description |
|--------|-------------|
| **Residual Risk %** | Σ(Final Exposure) / Σ(Base Exposure) × 100 |
| **Weighted Risk Score** | Severity²-weighted aggregate (0–100) |
| **Total TRI** | Sum of Tail Risk Indicators (L × S^1.5) across all in-scope risks |

Each metric shows a **Δ delta indicator** — green when the scenario improves the
portfolio, red when it worsens it. A health status change banner appears when the
scenario shifts the portfolio between bands (Excellent / Good / Moderate / Concerning / Critical).

---

#### Per-Risk Delta Table

| Column | Meaning |
|--------|---------|
| **Baseline EL** | Final exposure with all mitigations active |
| **Modified EL** | Final exposure in the current scenario |
| **Δ EL** | Change in final exposure (positive = worse) |
| **Baseline TRI** | Tail risk indicator at baseline |
| **Modified TRI** | Tail risk indicator in the current scenario |
| **Δ TRI** | Change in TRI (positive = worse) |
| **Quadrant** | Risk classification: critical / frequency / severity / marginal |

The table is sorted by **Δ EL descending** — the risks most affected by your scenario
appear at the top.

---

#### Scope & Lifecycle Constraints

- **Scope-constrained**: only mitigations connected to in-scope risks are shown.
  Changing the scope requires re-running **Compute Baseline**.
- **Lifecycle-aware**: inactive risks (Accepted, Watching, Suppressed, Closed,
  Archived) are excluded by default. Check **"Include inactive risks (worst-case)"**
  in the sidebar to include them — useful for revealing latent tail exposure if
  suppressed risks were to re-activate.

---

#### Typical Use Cases

- **"What if this mitigation is delayed or fails?"** — disable it and read the Δ EL.
- **"Which mitigation delivers the most risk reduction?"** — disable one at a time
  and compare the Residual Risk % deltas.
- **"Worst-case scenario"** — disable all mitigations and check the Include inactive
  toggle to see unmitigated exposure including accepted/suppressed risks.
- **"Stakeholder briefing"** — use scope + toggles to isolate a domain and demonstrate
  the impact of planned mitigations in a live session.
