# Task: F7 — What-If Analysis Sandbox
**Stream**: C + A (services + UI layer)
**Started**: 2026-03-21
**Target version**: v2.26.0

## Plan
- [x] Step 1: `utils/state_manager.py` — `WHATIF_DEFAULTS` + `init_whatif_state()` + `init_all()` registration
- [x] Step 2: `pages/3_🔬_What-If_Analysis.py` — NEW page (mitigation toggles, EL + TRI deltas, scope + lifecycle constraints)
- [ ] Step 3: Run full test suite
- [ ] Step 4: Update `CHANGELOG.md` + `ROADMAPv3.md` + `SESSION_STATE.md`

## Implementation Notes
- Toggle state stored as `st.session_state[f"whatif_toggle_{mitigation_id}"]` per mitigation (standard Streamlit checkbox key pattern)
- Raw data (risks, influences, mitigations, MITIGATES rels) cached in session at baseline time; in-memory recompute on every rerun — no DB round-trips for recomputation
- Scope filter applied identically to `manager.calculate_exposure()` (whitelist by `scope_node_ids`, filter influences + MITIGATES accordingly)
- `include_inactive` checkbox passed as `exclude_inactive=not include_inactive` to `database.queries.risks.get_all_risks()` (direct import, like Data Management page)
- Reset button re-enables all toggle keys and calls `st.rerun()`

## Testing Checklist
- [ ] `.\venv\Scripts\activate; py -m pytest tests/` passes (409+)
- [ ] Manual: page loads, Compute Baseline works, toggles recompute deltas
- [ ] Manual: scope constraint respected (only in-scope mitigations shown)
- [ ] Manual: "Include inactive risks" toggle changes risk count

## Documentation Updates
- [ ] `CHANGELOG.md`
- [ ] `ROADMAPv3.md` (mark F7 complete)
- [ ] `tasks/SESSION_STATE.md`

## Git Commit
```
feat(v2.26.0): F7 What-If Analysis Sandbox

- New page: pages/3_🔬_What-If_Analysis.py
- Toggle mitigations ON/OFF in-memory; no DB writes
- Recomputes EL + TRI on every toggle change using ExposureCalculator
- Portfolio summary: Residual Risk %, Weighted Risk Score, Total TRI with Δ deltas
- Per-risk delta table: Baseline vs Modified EL + TRI, sorted by largest EL increase
- Scope-constrained: respects active filter_manager scope
- Lifecycle-aware: exclude_inactive=True default; "Include inactive risks" checkbox for worst-case
- utils/state_manager.py: WHATIF_DEFAULTS + init_whatif_state()

Closes F7
```
