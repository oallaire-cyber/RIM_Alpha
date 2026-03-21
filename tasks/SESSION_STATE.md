# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.26.0` — F7 What-If Analysis complete. Branch: feature/iteration_4.

## Last Updated
2026-03-21 — F7 fully implemented, 409 tests passing.

---

## 🔴 Active Work In Progress

_None. F7 complete._

**Next feature**: **F31c** Lifecycle-Aware Simulation (v2.27.0) — see ROADMAPv3.md Iteration 5.

---

## ✅ Recently Completed (last 2 sessions)

### Session N+5 (this session — v2.26.0 F7 What-If Analysis)
- **v2.26.0** — **F7 What-If Analysis Sandbox**:
  - `pages/3_🔬_What-If_Analysis.py`: NEW — mitigation toggle checkboxes (grouped by type); Compute Baseline button fetches + scopes data; recomputes `GlobalExposureResult` in-memory on every toggle change; portfolio summary (RR%, WRS, TRI) with `st.metric` delta indicators; health status change alert; per-risk delta table (Baseline vs Modified EL + TRI, sorted by Δ EL); Reset Scenario button; "Include inactive risks" worst-case toggle.
  - `utils/state_manager.py`: `WHATIF_DEFAULTS` + `init_whatif_state()`; registered in `init_all()`.
  - **409 tests passing.**

### Session N+4 (v2.25.1 U12 polish)
- **v2.25.1** — **U12 Post-Implementation Fixes**:
  - `database/queries/risks.py`: Fixed `get_archive_candidates()` — replaced `WHERE NOT EXISTS { MATCH ... WHERE }` (Neo4j 5.x only) with `OPTIONAL MATCH` + `COUNT` aggregation pattern.
  - `pages/2_💾_Data_Management.py`: Fixed scope detection (`active_scope` → `filter_manager.get_scope_node_ids()`); added **🔓 Force Accept** button for blocked auto-acceptance candidates.
  - `ui/panels/node_property_panel.py`: Added dedicated **Lifecycle Details** block in `_render_identity()` (trigger_condition, acceptance_date, acceptance_owner, archive_date); lifecycle-aware `st.info()` messages in `_render_exposure()` per inactive status.
  - `docs/help_lifecycle.md`: NEW runtime-loaded help article (6-state lifecycle, engine sections, Force Accept, YAML config).
  - `docs/help_overview.md`: Lifecycle Engine row added to Core Capabilities table.
  - `docs/help_exposure.md`: Lifecycle-aware exclusion note added.
  - `ui/home.py`: `"Lifecycle": "help_lifecycle.md"` registered in `_HELP_FILES`.
  - **409 tests passing.**

### Session N+3 (v2.25.0 U12 implementation)
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
  - `tests/test_lifecycle.py`: NEW — 31 test cases covering all 3 services + exclusion guard.

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

- **Force Accept pattern**: Blocked risks can be manually accepted by a reviewer via
  `🔓 Force Accept` button — same DB write as auto-accept path, no eligibility check.
  Intent is explicit: human overrides the guard with full awareness.

- **Lifecycle scope detection**: Must use `st.session_state["filter_manager"].get_scope_node_ids()`
  (not `st.session_state["active_scope"]` which does not exist). Pattern from Simulation page.

- **`get_archive_candidates` Cypher compatibility**: `WHERE NOT EXISTS { MATCH ... WHERE }`
  is Neo4j 5.x only. Use `OPTIONAL MATCH` + `WITH r, COUNT(m) AS n WHERE n = 0` for all versions.

- **Neo4j "property does not exist" warning on new fields**: Normal before first write.
  `acceptance_owner`, `archive_date` etc. trigger a `01N52` warning until the first risk goes
  through the lifecycle engine and writes those properties. Not an error; warning disappears
  automatically after first acceptance.

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
  with `.\venv\Scripts\python.exe -m pytest tests/` (409 pass).

- **Canvas opacity for Watching/Suppressed risks** (F32 deferred) — inactive risks still
  show at full opacity on the canvas. `get_graph_data` intentionally not changed; F32
  Visual Panel will handle lifecycle-driven opacity encoding.

---

## 📋 Open Questions Pending User Decision

_None._

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
F7 complete (v2.26.0), 409 tests passing. ROADMAPv3.md is the authoritative roadmap.
Next task: Iteration 5 — F31c Lifecycle-Aware Simulation (v2.27.0).
Branch: feature/iteration_4.
```
