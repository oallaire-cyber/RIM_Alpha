# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.25.0` — U12 Risk Lifecycle Engine complete. Branch: feature/iteration_4.

## Last Updated
2026-03-20 — U12 fully implemented; tests pending run.

---

## 🔴 Active Work In Progress
<!-- No task is mid-implementation. U12 complete, ready for user test run + commit. -->

**Feature**: None — U12 complete.
**Stream**: B + C (cross-stream)
**Status**: 100% — awaiting test run + git commit.

**Next immediate step**:
> Run `.\venv\Scripts\activate; py -m pytest tests/` to verify all tests pass.
> Then commit feature/iteration_4 and run `scripts/migrate_activation_to_lifecycle.cypher` against live DB.
> Next feature: **F7 What-If Analysis** (v2.26.0) — see ROADMAPv3.md Iteration 4 sprint table.

---

## ✅ Recently Completed (last 2 sessions)

### Session N+3 (this session — v2.25.0 U12)
- **v2.25.0** — **U12 Risk Lifecycle Engine** (Iteration 4):
  - `models/enums.py`: 4 new `RiskStatus` members (ACCEPTED, WATCHING, SUPPRESSED, CLOSED) + `LIFECYCLE_INACTIVE_STATUSES` frozenset.
  - `models/risk.py`: `activation_condition` → `trigger_condition`, `activation_decision_date` → `acceptance_date`; new fields `acceptance_owner`, `archive_date`; new `is_inactive` property; migration-safe `from_dict` fallbacks.
  - `schemas/default/schema.yaml`: 4 new statuses, renamed attributes, `risk_lifecycle_rules` block.
  - `schemas/it_security/schema.yaml`: 3 new statuses (accepted, watching, suppressed; closed already existed).
  - `config/schema_loader.py`: `QuadrantThresholdsConfig` + `LifecycleRulesConfig` dataclasses; `_parse_lifecycle_rules`; `_lifecycle_rules_to_dict`; `SchemaConfig.lifecycle_rules` field.
  - `database/queries/risks.py`: `_INACTIVE_STATUSES` constant; `exclude_inactive=True` param on `get_all_risks` + `get_risks_with_filters`; COALESCE fallbacks in RETURN clauses; renamed params in `create_risk` + `update_risk` with legacy aliases; new `get_archive_candidates()`.
  - `services/trigger_engine.py`: NEW — `TriggerEngine` (human-review, no auto-eval).
  - `services/auto_acceptance_engine.py`: NEW — `AutoAcceptanceEngine` with 3 eligibility guards.
  - `services/archive_engine.py`: NEW — `ArchiveEngine`, alert generation only.
  - `utils/state_manager.py`: `LIFECYCLE_DEFAULTS` + `init_lifecycle_state()`.
  - `pages/2_💾_Data_Management.py`: Lifecycle Engine expander + Accepted Risks toggle.
  - `scripts/migrate_activation_to_lifecycle.cypher`: NEW idempotent rename migration.
  - `tests/test_lifecycle.py`: NEW — 25 test cases covering all 3 testing gates.

### Session N+2 (v2.25.0 U13)
- **v2.25.0** — **U13 Severity Rename + Dual-Metric Exposure** (Iteration 4):
  - `Risk.impact` → `Risk.severity` across all layers: schemas, model, queries, manager,
    backup service, exposure calculator, simulation page, UI panels, all tests/fixtures.
  - `_compute_risk_quadrant()` helper + `TRI = likelihood × severity^1.5` in `exposure_calculator.py`.
  - `RiskExposureResult` gains `tail_risk_indicator: float` + `risk_quadrant: str` (defaults at end).
  - Node Property Panel: Severity metric, TRI row, quadrant row with emoji labels.
  - `ui/home.py`: `_render_quadrant_distribution()` dashboard widget; quadrant multiselect sidebar filter.
  - 5 root-level cypher files moved to `scripts/` with `impact:` → `severity:` updated.
  - `docs/New Space/ODT_RIM_SpaceUseCase.cypher`: 52 Risk property references updated.
  - `scripts/migrate_impact_to_severity.cypher`: new idempotent migration script.
  - Legacy fallbacks: `r.get("severity") or r.get("impact")` in exposure calc + simulation load;
    `d.get("severity") or d.get("impact")` in backup `_risk_kwargs`.
  - Tests: 378 pass.

### Session N+1 (v2.24.0)
- **v2.24.0** — **F31 Scope-Driven Simulation & Results Storage** (Iteration 4):
  - `utils/simulation_store.py`: new file — `SimulationRecord` dataclass.
  - `utils/state_manager.py`: added `SIMULATION_DEFAULTS` + `init_simulation_state()`.
  - `pages/2_🎲_Simulation.py`: full F31 implementation — "Scope-Based (Real Data)" mode with real/random L×I toggle; `_load_scope_data()` (scope-filtered DB load, maps `probability`→`likelihood`, `level` "Business"→"Strategic"); `run_scope_based_monte_carlo()` (fixed topology, variable mitigation coverage ±variance); `run_scope_based_simulation_ui()`; `_render_save_results_button()` added to all three run UIs; `_render_saved_results_tab()` with delta comparison, per-run expanders, Excel export, clear; page wrapped in top-level "🎲 Simulator" / "📊 Saved Results" tabs; `_render_about_expander()` extracted.
  - Tests: 378 pass.

### Session N (v2.23.0)
- **v2.23.0** — **F29 Interactive Scope Sandbox** (Iteration 3):
  - `visualization/graph_options.py`: right-click via `network.on("oncontext")`
    using `network.getNodeAt(params.pointer.DOM)` (params.nodes unreliable).
  - `visualization/graph_click_bridge/index.html`: structured `{action, node_id}` relay.
  - `visualization/graph_renderer.py`: `render_graph_streamlit()` returns `Optional[dict]`;
    sandbox border + size boost applied LAST (after transparency); out-of-scope dimming
    at 0.25 opacity; in-scope nodes excluded from Simple mode transparency.
  - `utils/state_manager.py`: `scope_sandbox_mode`, `scope_sandbox_pending_node` in defaults.
  - `ui/home.py`: helpers `_sandbox_add/remove/_commit/_discard/_render_sandbox_action_panel`;
    scope filter bypass; node flags `_sandbox_in_scope` / `_sandbox_out_of_scope`;
    structured `graph_event` dict parsing; NO `st.rerun()` in contextmenu handler
    (causes infinite loop — component retains last value across reruns);
    sidebar toggle + Commit/Discard; ➕ New Scope inline form.
  - `docs/help_scopes.md`: Sandbox workflow documented.
  - **[F32] Graph Visual Behavior Panel** added to ROADMAPv2 Work Stream G backlog.
  - `feature/work_stream_AB` merged → `main`. Now on `feature/work_stream_C`.

---

## 🧠 Key Decisions Made (not in docs yet)

- **U12 field renames are migration-safe**: `from_dict` in `models/risk.py` reads new key first,
  falls back to old key. `get_all_risks`/`get_risk_by_id` use COALESCE in Cypher RETURN.
  Migration script (`scripts/migrate_activation_to_lifecycle.cypher`) is idempotent; run after deploy.

- **U12 `exclude_inactive=True` default on analytical DB queries**: `get_all_risks` and
  `get_risks_with_filters` exclude Accepted/Watching/Suppressed/Closed/Archived by default.
  Callers needing the full list (CRUD forms, lifecycle UI) pass `exclude_inactive=False`.
  `get_graph_data` (canvas) was NOT changed — keeps showing all risks; F32 handles opacity.

- **U12 `TriggerEngine` is manual-review only**: trigger_condition is free text; no `eval()`.
  Future programmatic evaluation: use `simpleeval` library (safe sandboxed evaluator).

- **`render_scope_node_editor` callback pattern**: Config page can't use FilterManager
  (home.py singleton). Uses caller-supplied `on_add`/`on_remove` callbacks instead.

- **JS click bridge architecture**: PyVis in inner `srcdoc` iframe; `declare_component`
  outer iframe. `window.parent.postMessage` → outer component → `setComponentValue`.
  `st.components.v1.html` is one-way only, so the outer wrapper is essential.

- **`render_graph_streamlit()` returns `Optional[dict]`**: `{"action": "click"|"contextmenu",
  "node_id": str|None}`. Legacy string fallback preserved. Background click → `node_id: null`.

- **No `st.rerun()` after contextmenu event**: Streamlit components retain their last
  `setComponentValue` across reruns. Calling `st.rerun()` after setting
  `scope_sandbox_pending_node` causes an infinite loop (same event re-fires each run).
  The sandbox action panel renders in the same script pass — no rerun needed.

- **`network.getNodeAt(params.pointer.DOM)` required for right-click**: `params.nodes`
  in vis.js `oncontext` is unreliable — often empty even when clicking a node directly.

- **Sandbox border must be applied LAST in graph_renderer.py**: `create_node_config`
  rebuilds `color` from scratch. Transparency code overwrites border colors. Sandbox
  border block must run after both, and `_sandbox_in_scope` nodes must be excluded
  from `transparent_node_ids` in Simple mode.

- **`net.generate_html()` is the correct PyVis API**: `net.html` is only populated
  as a side-effect of `write_html()`. Always use `generate_html()` for in-memory HTML.

- **`cdn_resources="in_line"` required**: Avoids 404 on `lib/bindings/utils.js` inside
  the srcdoc iframe.

- **`create_unified_entity` return type inconsistency**: risk/mitigation → `str`,
  context nodes → `dict`. Branch on `isinstance(new_item, str)` at all call sites.

---

## ⚠️ Known Issues / Tech Debt

- **F22 and F23 appear twice each in `ROADMAPv2.md`** Stream B section —
  deduplicate when next touching that file.

- **`pydantic` and `openpyxl` must be installed via venv** — always run tests
  with `source venv/Scripts/activate && python -m pytest tests/` (378 pass).

---

## 📋 Open Questions Pending User Decision

_None._

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
U13 complete (v2.25.0). ROADMAPv3.md is the authoritative roadmap.
Next task: Iteration 4 — U12 Lifecycle Engine (v2.25.0), then F7 What-If.
Branch: feature/iteration_4 (commit pending or already committed).
```
