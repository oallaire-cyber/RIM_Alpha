# RIM Manual Test Script — Pre-Iteration 6 Test & Fix Campaign
> **Version**: v2.30.0 | **Date**: 2026-03-23
> **Purpose**: Systematic end-to-end validation of all features added in Iterations 3–5.
> Use this document to execute tests, record pass/fail, and log bugs to `tasks/lessons.md`.

---

## Quick-Reference: User Roles

| ID | Role | Description | Tests |
|----|------|-------------|-------|
| **R1** | Risk Manager | Program-level owner; uses Dashboard, Simulation, Scope, Alerts | C1–C12, E1–E6 |
| **R2** | Risk Analyst | Functional team; uses CRUD, Lifecycle, What-If | B1–B8, D1–D4 |
| **R3** | Config Admin | Schema config, Import/Export, DB admin | A1–A4 |
| **R4** | Program Director | Read-only executive consumer; uses Dashboard, Mitigation Exposure | C1, D3, D4 |

---

## Dataset Reference

### Pre-existing TC01–TC07 (mathematical verification)
Load from: `scripts/demo_tc_dataset.cypher`
Scope shortcuts: `TC01 - Baseline`, `TC02 - Simple Chain`, etc. (pre-configured in default schema)

### TC08 (feature coverage)
Load from: `scripts/tc08_feature_coverage.cypher`
Scope shortcut: `TC08 - Feature Coverage` (pre-configured in default schema)

**TC08 nodes at a glance:**

| ID | Name | Level | L | S | Status | Notes |
|----|------|-------|---|---|--------|-------|
| tc08-…0001 | Business Risk Alpha | Business | 6 | 8 | Active | BR1 — Critical quadrant |
| tc08-…0002 | Business Risk Beta | Business | 3 | 4 | Active | BR2 — Marginal quadrant |
| tc08-…0003 | Op Risk Upstream | Operational | 10 | 10 | Active | OR1 — Unmitigated |
| tc08-…0004 | Op Risk Downstream | Operational | 6 | 6 | Active | OR2 — Has M1 (High) |
| tc08-…0005 | Op Risk Accepted | Operational | 5 | 5 | Accepted | OR3 — Lifecycle inactive |
| tc08-…0006 | Op Risk Suppressed | Operational | 4 | 3 | Suppressed | OR4 — Lifecycle inactive |
| tc08-…0007 | Business Risk Template | Business | 5 | 5 | Active | is_template=true |

**TC08 expected exposure results (active risks only):**

| Risk | Base | Mitigation | Upstream Influence | Limitation | Eff. Factor | Final | Quadrant | TRI (α=1.5) |
|------|------|------------|-------------------|------------|-------------|-------|----------|-------------|
| OR1 | 100 | None (1.0) | None | 0.0 | 1.0 | **100** | critical | ≈ 316.2 |
| OR2 | 36 | M1 High (0.3) | OR1 Critical, resid=1.0 → limit=1.0 | 1.0 | 0.3+0.7×1.0=**1.0** | **36** | critical | ≈ 135.8 |
| BR1 | 48 | M2 Medium (0.5) | OR2 Strong=0.75, resid=1.0 → limit=0.75 | 0.75 | 0.5+0.5×0.75=**0.875** | **42** | critical | ≈ 135.8 |
| BR2 | 12 | None (M3 unlinked) | None | 0.0 | 1.0 | **12** | marginal | ≈ 13.5 |

**Key insight**: OR2 has a High mitigation (M1) but its Final Exposure remains 36 (same as Base). This is the TC04 lesson — an unmitigated upstream risk (OR1) fully nullifies the downstream mitigation.

**Mitigation Exposure deltas** (for test D3):
- M2 (Medium, BR1): remove → BR1 Final goes 42→48 → **Δ = +6.0** (largest actual impact)
- M1 (High, OR2): remove → OR2 Final stays 36→36 → **Δ = 0.0** (nullified by upstream)
- M3 (Proposed, unlinked): no coverage → Δ = 0.0

---

## Group A — Setup & Configuration (Role: R3)

### A1 — Load TC08 via Reset Demo Data
**Pre-condition**: Neo4j is running; app is running.
**Steps**:
1. Navigate to ⚙️ Configuration → Data Management tab
2. Scroll to **🔄 Reset Demo Data** section
3. Verify three green ✅ status lines: ODT, TC, and TC08 files all found
4. Check the confirmation checkbox
5. Click **🔄 Reset Demo Data**
6. Watch the three progress bars: ODT (New Space) → TC (TC01-TC07) → TC08 (Feature Coverage)
7. Confirm the success banner shows all three statement counts

**Expected result**:
- Success message: "✅ Reset complete — deleted N nodes, loaded M nodes (X ODT + Y TC + Z TC08 statements executed)"
- TC08 statement count Z should be in the range 20–35
- Neo4j Browser verify: `MATCH (n) RETURN labels(n), count(n) ORDER BY labels(n)`
  → Risk ≥ 7 TC08 rows, Mitigation ≥ 3, TPO ≥ 1

**Alternative** (if app unavailable): paste `scripts/tc08_feature_coverage.cypher` directly in Neo4j Browser.

---

### A2 — Verify Default Schema Loads
**Pre-condition**: App is running (`streamlit run app.py`)
**Steps**:
1. Navigate to ⚙️ Configuration page
2. Confirm active schema is "Default"
3. Check no red error banners
4. Expand "Entity Configuration" — verify Risk, Mitigation, TPO entities shown
5. Expand "Scopes" section — confirm `TC08 - Feature Coverage` scope is listed

**Expected result**: Schema loads cleanly; TC08 scope visible; no validation errors.

---

### A3 — Export DB to JSON Backup
**Pre-condition**: TC08 loaded in Neo4j
**Steps**:
1. Navigate to ⚙️ Configuration → Import/Export tab
2. Click "Export Database to JSON"
3. Wait for download; open the file

**Expected result**: JSON file downloads; contains `Risk`, `Mitigation`, `TPO` sections with TC08 nodes. File size > 5 KB.

---

### A4 — Import TC08 XLSX Round-Trip
**Pre-condition**: TC08 XLSX available (if generated)
**Steps**:
1. In Configuration → Import/Export, click "Clear Database" (or use Cypher `MATCH (n) DETACH DELETE n`)
2. Upload `test_datasets/TC08_Feature_Coverage.xlsx`
3. Verify node count matches A1

**Expected result**: Same 7 risks, 3 mitigations, 1 TPO re-created. No import errors.
> **Skip** if XLSX has not been generated; mark as "deferred".

---

## Group B — Data Management (Role: R2)

### B1 — Create a Business Risk
**Pre-condition**: TC08 loaded; navigate to 💾 Data Management → Risks tab
**Steps**:
1. Click "Add New Risk"
2. Set: Level=Business, Name="[TEST] New Business Risk", L=4, S=5, Status=Active, Category=Programme
3. Save

**Expected result**: Risk created with Base Exposure = 4×5 = **20**. Appears in Risks list. Click the risk → property panel shows Base Exposure = 20.

---

### B2 — Edit Risk: Change Probability
**Pre-condition**: B1 risk exists
**Steps**:
1. Find "[TEST] New Business Risk" in Risks list, click Edit
2. Change Probability from 4 to 6
3. Save
4. Navigate to Home; run exposure calculation

**Expected result**: Base Exposure updates to 6×5 = **30** in the node property panel.

---

### B3 — Create Operational Risk with Subtype
**Pre-condition**: TC08 loaded; Data Management → Risks tab
**Steps**:
1. Click "Add New Risk"
2. Set Level=Operational
3. Confirm subtype selectbox appears below level selector
4. Select subtype (e.g., "Supply Chain Dependency") if available
5. Set Name="[TEST] Op Risk with Subtype", L=5, S=6, Status=Active
6. Save

**Expected result**: Subtype selectbox is shown after level=Operational is selected. Risk saved successfully. Subtype visible in property panel.

---

### B4 — Create Mitigation and Link to Risk
**Pre-condition**: B1/B2 risk exists; Data Management → Mitigations tab
**Steps**:
1. Click "Add New Mitigation"
2. Set Name="[TEST] Control", Type=Dedicated, Status=Implemented
3. Save
4. In Mitigations tab, find "[TEST] Control" → "Link to Risk"
5. Select "[TEST] New Business Risk", Effectiveness=High
6. Save the link

**Expected result**: Mitigation linked. Navigate to Home, select "[TEST] New Business Risk" on canvas → property panel shows Final Exposure = 30 × 0.3 = **9** (High effectiveness reduces by 70%).

---

### B5 — Lifecycle: Accept a Risk
**Pre-condition**: TC08 loaded; Data Management → Lifecycle Engine
**Steps**:
1. Navigate to 💾 Data Management → Lifecycle Engine expander
2. Find "[TC08] Op Risk Downstream" (OR2, Active)
3. Change status to "Accepted" using status dropdown or lifecycle button
4. Save / Apply

**Expected result**:
- OR2 status changes to Accepted
- OR2 disappears from the normal canvas (exposure calculation excludes it)
- OR2 visible in CRUD "Show inactive risks" toggle
- Lifecycle opacity: OR2 shows at reduced opacity if canvas shows accepted risks

---

### B6 — Lifecycle: Force-Accept a Blocked Risk
**Pre-condition**: A risk exists that fails auto-acceptance guards (high exposure, e.g., OR1 Final=100)
**Steps**:
1. Navigate to 💾 Data Management → Lifecycle Engine → "Archive Candidates" or "Acceptance Queue"
2. Find OR1 or another risk blocked from auto-acceptance
3. Click "🔓 Force Accept"

**Expected result**: Force Accept button is visible. After clicking, risk status changes to Accepted despite not meeting normal eligibility. Confirmation shown.

---

### B7 — Create Risk Template and Instantiate
**Pre-condition**: TC08 loaded (includes BR_TPL template)
**Steps**:
1. Navigate to 💾 Data Management → Risks tab
2. Scroll to "📋 Risk Templates" expander
3. Confirm "[TC08] Business Risk Template" appears
4. Click "Instantiate" on the template
5. Set Name="[TEST] Instantiated Risk", fill in required fields
6. Save

**Expected result**: Template visible in Templates expander (not in main risk list). After instantiation, a new Active risk "[TEST] Instantiated Risk" appears in main Risks list with an INSTANTIATES relationship edge visible on the canvas.

---

### B8 — Activate a Pre-Configured Scope
**Pre-condition**: TC08 loaded; app running
**Steps**:
1. Navigate to Home
2. In the sidebar, locate Scope Selector
3. Select "TC08 - Feature Coverage" from the scope dropdown
4. Observe canvas

**Expected result**: Canvas shows only the 4 active TC08 risks (BR1, BR2, OR1, OR2) plus connected edges. Inactive risks (OR3, OR4) and template (BR_TPL) are NOT shown. All stats and dropdowns on the page reflect only these 4 risks.

---

## Group C — Dashboard & Visualization (Role: R1)

### C1 — TC01 Baseline Math Verification
**Pre-condition**: TC01 dataset loaded (or all TC data loaded); activate scope "TC01 - Baseline"
**Steps**:
1. Navigate to Home
2. Activate scope "TC01 - Baseline"
3. Click "Calculate Exposure" (or equivalent button)
4. Check node property panel for each of the 4 TC01 risks

**Expected result**: All 4 risks show:
- Final Exposure = **1**
- Residual Risk % = **100%** (no mitigation, no influence)
- Quadrant: marginal (L=1, S=1)

---

### C2 — TC03 Mitigation Effect Math
**Pre-condition**: TC03 dataset loaded; activate scope "TC03 - Mitigation Effect"
**Steps**:
1. Activate scope "TC03 - Mitigation Effect"
2. Run exposure calculation
3. Check Final Exposure for each risk in the property panel or analysis tab

**Expected result** (exact values):

| Risk | Expected Final |
|------|---------------|
| Risk No Mitigation | **100** |
| Risk Low Mitigation | **70** |
| Risk Medium Mitigation | **50** |
| Risk High Mitigation | **30** |
| Risk Critical Mitigation | **10** |
| Risk Double Medium | **25** |
| Risk High Plus Medium | **15** |
| Risk Triple Low | **≈ 34.3** |

---

### C3 — TC04 Influence Limitation Math
**Pre-condition**: TC04 dataset; activate scope "TC04 - Influence Limitation"
**Steps**: Run exposure; check 3 downstream targets.

**Expected result**:

| Risk | Expected Final | Why |
|------|---------------|-----|
| Downstream No Influence | **10** | Critical mit only, no upstream |
| Downstream Target B | **≈ 19** | Critical mit + well-mitigated upstream (residual=0.1) |
| Downstream Target A | **100** | Critical mit fully nullified by unmitigated upstream |

---

### C4 — TC05 Convergence Math
**Pre-condition**: TC05 dataset; activate scope "TC05 - Convergence"
**Steps**: Run exposure; check Convergence Point.

**Expected result**: Convergence Point Final = **≈ 48.25**
- Limitation = (1.0 + 0.5 + 0.1 + 0.1) / 4 = 0.425
- Effective factor = 0.1 + 0.9×0.425 = 0.4825

---

### C5 — TC07 Influence Strengths Math
**Pre-condition**: TC07 dataset; activate scope "TC07 - Influence Strengths"
**Steps**: Run exposure; check 4 target risks.

**Expected result**:

| Risk | Strength | Expected Final |
|------|----------|---------------|
| Target Weak Influence | 0.25 | **32.5** |
| Target Moderate Influence | 0.50 | **55** |
| Target Strong Influence | 0.75 | **77.5** |
| Target Critical Influence | 1.00 | **100** |

---

### C6 — TRI Calculation Verification
**Pre-condition**: TC08 loaded; NO scope active (or TC08 scope active); exposure calculated
**Steps**:
1. Activate "TC08 - Feature Coverage" scope; run exposure
2. Click [TC08] Business Risk Alpha (BR1) on canvas
3. In property panel, find TRI row

**Expected result**:
- TRI ≈ **135.8** (formula: 6 × 8^1.5 = 6 × 22.627)
- Quadrant: **critical**

Also check OR1 (L=10, S=10):
- TRI ≈ **316.2** (10 × 10^1.5 = 316.2)

---

### C7 — Quadrant Distribution Widget
**Pre-condition**: TC08 scope active; exposure calculated
**Steps**:
1. Scroll to Quadrant Distribution section on Home dashboard

**Expected result**: Shows 4 active risks distributed as:
- Critical: **3** (BR1, OR1, OR2)
- Marginal: **1** (BR2)
- Frequency: 0
- Severity: 0

Donut / bar chart reflects these counts accurately.

---

### C8 — Threshold Alert Fires
**Pre-condition**: TC08 scope active; exposure calculated; default `high_exposure_threshold=50.0`
**Steps**:
1. Run exposure with TC08 scope
2. Scroll to Threshold Alerts section in dashboard

**Expected result**:
- **OR1** (Final=100) appears in the alert list (100 > 50)
- BR1 (Final=42), OR2 (Final=36), BR2 (Final=12) do NOT appear

**Optional step C8b** — lower threshold to 40:
1. Go to ⚙️ Configuration → Edit Schema → set `high_exposure_threshold` to 40 → Save
2. Re-run exposure
3. Now **BR1** (Final=42) also appears in alert (42 > 40)

---

### C9 — Visual Panel: Clean Preset
**Pre-condition**: TC08 scope; Home page
**Steps**:
1. Open "Graph Visual Behaviour" panel
2. Select preset: "Clean"
3. Observe canvas redraw

**Expected result**: Canvas redraws with thin edges, minimal style, no quadrant borders. No crash.

---

### C10 — Visual Panel: Lifecycle Opacity
**Pre-condition**: TC08 loaded (OR3 Accepted, OR4 Suppressed visible on canvas if global view)
**Steps**:
1. Deactivate scope (show all risks)
2. Open Graph Visual Behaviour panel
3. Move "Accepted" opacity slider to 0.2
4. Observe canvas

**Expected result**: OR3 ([TC08] Op Risk Accepted) fades to ~20% opacity. OR4 (Suppressed) and active risks remain at their respective opacity levels.

---

### C11 — Quadrant Border Encoding Toggle
**Pre-condition**: TC08 scope; exposure calculated
**Steps**:
1. Open Graph Visual Behaviour panel
2. Enable "Quadrant Border Encoding" (if not already on)
3. Observe canvas: critical risks should have colored borders
4. Toggle it OFF
5. Observe: borders disappear

**Expected result**:
- When ON: BR1, OR1, OR2 (all critical quadrant) show colored border; BR2 (marginal) shows different/no border
- When OFF: all borders removed; canvas returns to standard appearance

---

### C12 — Node Click → Property Panel
**Pre-condition**: TC08 scope; exposure calculated
**Steps**:
1. Click [TC08] Business Risk Alpha (BR1) on canvas
2. Inspect property panel

**Expected result**: Panel shows all of:
- Name: "[TC08] Business Risk Alpha"
- Level: Business
- Probability: 6, Severity: 8
- Base Exposure: 48
- Final Exposure: 42
- TRI: ≈ 135.8
- Quadrant: critical
- Mitigation count: 1 (M2 Medium)
- Upstream influence from: OR2 (Strong)

---

## Group D — Analysis Tools (Roles: R2, R4)

### D1 — What-If: Toggle Off a Mitigation
**Pre-condition**: TC08 scope; navigate to 🔬 What-If Analysis page
**Steps**:
1. Click "Compute Baseline" with TC08 scope active
2. Note baseline portfolio metrics (Residual %, WRS, TRI)
3. In Mitigation Toggles, uncheck "[TC08] Control Medium" (M2 on BR1)
4. Observe metric changes

**Expected result**:
- Portfolio Residual % **increases** (BR1 is now less protected)
- Per-risk delta table shows Δ EL > 0 for "[TC08] Business Risk Alpha"
  - BR1 changes: Final goes 42 → 48, Δ EL = +6
- "[TC08] Control High" (M1 on OR2): unchecking shows Δ EL = 0 (upstream OR1 nullifies it anyway)

---

### D2 — What-If: Worst-Case Canvas Toggle
**Pre-condition**: TC08 scope; What-If page
**Steps**:
1. Enable "Include inactive risks (worst-case)" toggle
2. Recompute baseline

**Expected result**:
- Banner/info shows "n latent risks included" (at minimum OR3 + OR4 = 2)
- OR3 and OR4 appear in the risk list and contribute to portfolio exposure
- Portfolio metrics worsen vs. normal baseline

---

### D3 — Mitigation Exposure View
**Pre-condition**: TC08 scope; navigate to 📊 Mitigation Exposure page
**Steps**:
1. Ensure TC08 scope is active
2. Page loads mitigation impact table

**Expected result** (key rows):

| Mitigation | EL Delta ↑ | Risks Covered |
|------------|------------|---------------|
| [TC08] Control Medium (M2) | **6.0** | 1 (BR1) |
| [TC08] Control High (M1) | **0.0** | 1 (OR2) |
| [TC08] Control Proposed (M3) | not shown | 0 (unlinked) |

- M2 shows the largest delta despite being Medium effectiveness — because M1 is nullified by upstream
- M3 does not appear in the table (no MITIGATES relationship)
- Rows sorted by EL Delta descending: M2 first, M1 second

---

### D4 — Scope Propagates to All Pages
**Pre-condition**: TC08 scope active
**Steps**:
1. With "TC08 - Feature Coverage" scope active, check:
   a. Home → canvas shows only 4 risks
   b. 🔬 What-If → risk/mitigation lists contain only TC08 items
   c. 📊 Mitigation Exposure → table shows only TC08 mitigations

**Expected result**: Scope is respected on all three pages. No risks outside the scope appear in any analysis.

---

## Group E — Simulation (Role: R1)

### E1 — Standard (Global) Simulation
**Pre-condition**: TC08 loaded; navigate to 🎲 Simulation page
**Steps**:
1. Select mode "Global" (default)
2. Set runs = 100
3. Click "Run Simulation"

**Expected result**: Completes without crash; shows:
- Residual Risk % (histogram or metric)
- Weighted Risk Score
- TRI distribution chart
- At least one result row

---

### E2 — Scope-Based Simulation
**Pre-condition**: TC08 scope active; Simulation page
**Steps**:
1. Select mode "Scope-Based"
2. Run 100 iterations

**Expected result**: Runs only on the 4 active TC08 risks. Result count and risk names reflect the scope. Total portfolio metrics are lower than Global.

---

### E3 — Worst-Case Canvas
**Pre-condition**: TC08 scope; Scope-Based simulation mode
**Steps**:
1. Check "🧟 Worst-Case Canvas" checkbox
2. Run simulation

**Expected result**:
- Banner shows "X latent risks included" (OR3 + OR4 = 2)
- Results labelled "[Worst-Case]"
- Residual % is higher than normal scope-based run

---

### E4 — TRI α Calibration
**Pre-condition**: TC08 scope; Simulation page
**Steps**:
1. Select mode "TRI α Calibration"
2. Set α range: min=1.0, max=2.0, step=0.25
3. Set runs per α = 50
4. Click "Run Calibration"

**Expected result**:
- 3-tab output renders: Calibration Chart / Report / Raw Data
- Chart shows Mean TRI ±1σ curves for each α value (1.0, 1.25, 1.5, 1.75, 2.0)
- Report tab shows recommended α highlighted
- Raw Data tab shows the sweep table

---

### E5 — Save Results and View in Saved Results Tab
**Pre-condition**: E2 or E4 simulation completed
**Steps**:
1. After a Scope-Based run, click "💾 Save Results"
2. After a TRI α Calibration run, click "💾 Save Results"
3. Navigate to "Saved Results" tab

**Expected result**:
- Both records appear in the Saved Results tab
- Scope-Based record shows standard metrics
- Calibration record shows `recommended_alpha` and `n_alpha_values` in key metrics
- No crash on rendering

---

### E6 — Export CSV
**Pre-condition**: A simulation result is displayed (E1 or E2)
**Steps**:
1. After running simulation, click "📥 Export CSV"

**Expected result**: CSV file downloads. Open in Excel: columns include risk names, baseline exposure, simulated exposure, residual %. No encoding errors.

---

## Test Execution Log

| ID | Date | Tester | Pass / Fail / Skip | Notes |
|----|------|--------|--------------------|-------|
| A1 | | | | |
| A2 | | | | |
| A3 | | | | |
| A4 | | | | |
| B1 | | | | |
| B2 | | | | |
| B3 | | | | |
| B4 | | | | |
| B5 | | | | |
| B6 | | | | |
| B7 | | | | |
| B8 | | | | |
| C1 | | | | |
| C2 | | | | |
| C3 | | | | |
| C4 | | | | |
| C5 | | | | |
| C6 | | | | |
| C7 | | | | |
| C8 | | | | |
| C9 | | | | |
| C10 | | | | |
| C11 | | | | |
| C12 | | | | |
| D1 | | | | |
| D2 | | | | |
| D3 | | | | |
| D4 | | | | |
| E1 | | | | |
| E2 | | | | |
| E3 | | | | |
| E4 | | | | |
| E5 | | | | |
| E6 | | | | |

---

## Bug Log Template

When a test fails, log it here and in `tasks/lessons.md`:

```
**Bug**: [ID] — [short description]
**Repro**: [steps to reproduce]
**Expected**: [what should happen]
**Actual**: [what happened]
**File suspected**: [service / page / query file]
**Priority**: Critical / High / Medium / Low
```

---

## Sign-Off Criteria

- [ ] All Group A tests pass (setup verified)
- [ ] All Group C math tests pass with exact expected values
- [ ] TC08 calculation chain verified: OR1=100, OR2=36, BR1=42, BR2=12
- [ ] No Python tracebacks in the Streamlit console during any test
- [ ] pytest still passes 445 tests: `.\venv\Scripts\activate; py -m pytest tests/`
- [ ] All bugs logged to `tasks/lessons.md`

Once all items checked: proceed to Iteration 6 planning.
