# Task: v2.30.0 F31c/d Lifecycle-Aware Simulation & TRI α Calibration
**Stream**: A
**Started**: 2026-03-22
**Target version**: v2.30.0

## Plan
- [x] Add `include_inactive: bool = False` param to `_load_scope_data()` → `manager.get_all_risks(exclude_inactive=not include_inactive)`
- [x] Add `include_inactive` param to `run_scope_based_simulation_ui()` + worst-case banner
- [x] Update `_render_save_results_button` call to use `"Scope-Based (Worst-Case)"` mode label when active
- [x] Add "🧟 Worst-Case Canvas" checkbox to Scope-Based sidebar (shared with TRI α Calibration)
- [x] Add `"TRI α Calibration"` as 4th `sim_mode` radio option
- [x] Add TRI α Calibration sidebar block (α range, runs/α, param mode, worst-case toggle)
- [x] Add `_run_alpha_sweep()` — Monte Carlo per α, TRI + quadrant stats
- [x] Add `run_tri_alpha_calibration_ui()` — full 3-tab output + recommended α + save
- [x] Add `_render_tri_alpha_about_expander()` — instructions before first run
- [x] Import `_compute_risk_quadrant`, `TRI_ALPHA` from `services/exposure_calculator`
- [x] Run pytest → 445 passing
- [x] Update `CHANGELOG.md` → v2.30.0 entry
- [x] Update `ROADMAPv3.md` → F31 complete, Iteration 5 table updated
- [x] Update `SESSION_STATE.md` + `todo.md`

## Git Commit
```
feat(v2.30.0): F31c/d Lifecycle-Aware Simulation & TRI α Calibration

F31c — Worst-Case Canvas (pages/2_🎲_Simulation.py):
- _load_scope_data() gains include_inactive param;
  calls manager.get_all_risks(exclude_inactive=False) when enabled.
- "🧟 Worst-Case Canvas" checkbox in sidebar (shared by Scope-Based
  and TRI α Calibration modes).
- Banner shows count of lifecycle-inactive risks re-activated.
- Results labelled "[Worst-Case]"; SimulationRecord mode updated.

F31d — TRI α Calibration Mode (pages/2_🎲_Simulation.py):
- 4th simulation mode radio: "TRI α Calibration".
- Sidebar: α min/max/step, runs per α, param mode, worst-case toggle.
- _run_alpha_sweep(): sweeps α list; for each α runs N MC iterations
  computing TRI = L × S^α per risk; classifies quadrants via imported
  _compute_risk_quadrant(); records mean/std/p95 TRI + quadrant %s.
- run_tri_alpha_calibration_ui(): loads scope data, runs sweep, renders
  3-tab output (Calibration Chart / Report / Raw Data).
  Charts: Mean TRI ±1σ + P95 line; stacked quadrant distribution bar.
  Target profile selectbox; recommended α highlighted in table.
  Save to Saved Results (F31b) with calibration key_metrics.
- Imports: _compute_risk_quadrant + TRI_ALPHA from exposure_calculator.
- Any added to typing imports (pre-existing gap).

Closes Iteration 5. CHANGELOG v2.30.0. ROADMAPv3 F31 done.
445 tests passing.
```
