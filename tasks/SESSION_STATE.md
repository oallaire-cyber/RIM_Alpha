# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.29.0` — F32 Graph Visual Behaviour Panel. Branch: feature/iteration_4.

## Last Updated
2026-03-21 — v2.29.0 complete. 445 tests passing.

---

## 🔴 Active Work In Progress

_None. v2.29.0 complete._

**Next feature**: **F31c** Lifecycle-Aware Simulation — see ROADMAPv3.md Iteration 5.

---

## ✅ Recently Completed (last 2 sessions)

### Session N+11 (this session — v2.29.0 F32 Graph Visual Behaviour Panel)
- **v2.29.0** — **F32 Graph Visual Behaviour Panel**:
  - `ui/panels/graph_visual_panel.py`: NEW — consolidated visual settings panel. 4 presets
    (Clean / Analysis / Lifecycle Audit / Sandbox Edit), exposure opacity (F20 moved here),
    per-status lifecycle opacity sliders (F21 upgraded — replaces hardcoded 0.5), quadrant
    border encoding toggle, Save as Schema Default button.
  - `config/schema_loader.py`: `GraphVisualConfig` dataclass; `_parse_graph_visual_config()`;
    `_graph_visual_config_to_dict()`; wired into `SchemaConfig`, `_parse_schema()`, `_schema_to_dict()`.
  - `schemas/default/schema.yaml` + `schemas/it_security/schema.yaml`: `graph_visual_config` block.
  - `utils/state_manager.py`: `VISUAL_PANEL_DEFAULTS` (`vp_*` keys) + `init_visual_panel_state()`
    registered in `init_all()`.
  - `visualization/node_styles.py`: `_QUADRANT_BORDER_COLORS`; `create_node_config()` accepts
    `visual_config` dict; per-status opacity from map; quadrant border encoding block.
  - `visualization/graph_renderer.py`: `render_graph()` / `render_subgraph()` accept `visual_config`;
    `render_graph_streamlit()` builds `visual_config` from `vp_*` state with legacy fallback.
  - `ui/home.py`: Display Options expander → Color Options (color_by only); visual panel wired
    after layout management; schema defaults seeded into `vp_*` on first load.
  - `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md`, `docs/CONFIGURATION_MANAGER.md`,
    `docs/help_overview.md`, `docs/welcome.md`, `docs/help_visual_panel.md` (NEW), `README.md`: updated.
    `CHANGELOG.md` v2.29.0. `ROADMAPv3.md` F32 done.
  - **Bug fix**: `UnboundLocalError` on `exposure_results` in `render_visualization_tab` — pre-existing
    unbound local; fixed by initialising from session state before the quadrant filter block.
  - **Bug fix**: Quadrant border encoding was NOK — two root causes: (1) `_QUADRANT_BORDER_COLORS` keys
    were capitalised ("Critical"/"High") but actual values are lowercase ("critical"/"frequency");
    (2) `risk_quadrant` was not copied onto node dicts in the exposure overlay — added alongside
    `base_exposure` / `exposure`.
  - **445 tests passing.**

### Session N+10 (v2.28.1 TRI Delta removal)
- **v2.28.1** — **TRI Delta removed from Mitigation Exposure & What-If**:
  - Root cause: `TRI = likelihood × severity^1.5` is mitigation-independent; counterfactual TRI delta was always 0.
  - `pages/4_📊_Mitigation_Exposure.py`: removed `delta_tri` computation + "TRI Delta ↑" column; added `pct_covered` metric (EL Delta / base_exposure_of_covered_risks × 100) and "% EL (Covered Risks)" column.
  - `pages/3_🔬_What-If_Analysis.py`: replaced "Total TRI" summary card with "Max Single Risk EL" (responds correctly to mitigation toggles); removed "Baseline TRI", "Modified TRI", "Δ TRI" from per-risk delta table.
  - `docs/help_mitigation_exposure.md`: column reference updated; explanatory note added on why TRI Delta is absent.
  - `CLAUDE.md`: development workflow updated — manual-test gate added between pytest and docs/commit steps.
  - `CHANGELOG.md` v2.28.1 entry. `ROADMAPv3.md` F6 + F7 entries updated.
  - **445 tests passing.**

### Session N+9 (v2.28.0 F6 Mitigation Exposure View)
- **v2.28.0** — **F6 Mitigation Exposure View**:
  - `pages/4_📊_Mitigation_Exposure.py`: NEW — counterfactual per-mitigation impact page. Loads baseline via same pattern as What-If; for each mitigation computes portfolio exposure without it (N+1 `calculate_exposure` runs); displays ranked table (EL Delta ↑, % Portfolio EL, Risks Covered, Level). Scope-aware, lifecycle-filtered, level filter sidebar.
  - `utils/state_manager.py`: `MITIGATION_EXPOSURE_DEFAULTS` dict + `init_mitigation_exposure_state()` added; registered in `init_all()`.
  - `docs/help_mitigation_exposure.md`: NEW runtime-loaded help article.
  - `docs/help_overview.md`, `docs/welcome.md`, `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`: updated for F6.
  - `CHANGELOG.md` v2.28.0 entry. `ROADMAPv3.md` F6 marked complete.
  - **445 tests passing.**

### Session N+8 (v2.27.1 fixes + subtype selection)
- **v2.27.1** — Post-release fixes + Subtype Selection:
  - `config/schema_loader.py`: `expected_loss_threshold` → `high_exposure_threshold`; backward-compat parse fallback.
  - `schemas/default/schema.yaml` + `schemas/it_security/schema.yaml`: key renamed.
  - `ui/home.py`: display text "Expected Loss" → "High Exposure" throughout `_render_threshold_alerts`.
  - `core/attribute.py`: `__post_init__` alias `"boolean"` → `"bool"`, `"integer"` → `"int"` before `AttributeType()` lookup.
  - `pages/1_⚙️_Configuration.py`: YAML backup `open()` calls now specify `encoding='utf-8'`.
  - `database/queries/analysis.py`: node-set safety filter strips edges whose source/target is absent from the canvas node list (fixes INSTANTIATES AssertionError).
  - `ui/tabs/unified_crud_tab.py`: `_render_risk_subtype_fields()` — new helper renders subtype selectbox (filtered by level) + extension fields after generic form. Wired into both create form and edit card.
  - `tests/test_alerts.py` + `tests/test_templates.py`: field name updated.
  - Full documentation pass for v2.27.0 (help_templates.md, help_alerts.md, USER_GUIDE, ARCHITECTURE, METHODOLOGY, CONFIGURATION_MANAGER, help_overview, welcome, help_exposure, README).
  - `/finish` skill + `tasks/lessons.md` updated to enforce doc pass.
  - **445 tests passing.**

### Session N+7 (v2.27.0 U14 + F5)
- **v2.27.0** — **U14 Generic Risk Template Architecture** + **F5 Threshold Alerts**:
  - `models/risk.py`: `is_template: bool = False` field + `is_generic_template` property; `to_dict`/`from_dict` updated.
  - `database/queries/risks.py`: `create_risk(is_template)`, `update_risk(is_template)`, `get_all_risks(exclude_templates=True)`, `get_risks_with_filters(exclude_templates=True)`; NEW: `get_all_templates()`, `create_instantiates_rel()`, `get_instances_of_template()`, `get_template_of_instance()`.
  - `database/manager.py`: `create_risk(is_template)`, `update_risk(is_template)`, `get_all_risks(exclude_templates)` wrappers; `create_unified_entity`/`update_unified_entity` pass `is_template` through; 4 new template method wrappers.
  - `schemas/default/schema.yaml` + `schemas/it_security/schema.yaml`: `is_template` boolean attribute; `instantiates` context edge (INSTANTIATES, dashed); `alert_thresholds` block.
  - `config/schema_loader.py`: `AlertThresholdsConfig` dataclass; `AnalysisConfig.alert_thresholds`; `_parse_analysis` + `_analysis_to_dict` updated.
  - `ui/tabs/unified_crud_tab.py`: `_render_template_library()` — template expander with instance counts, instantiation form, delete button.
  - `ui/panels/node_property_panel.py`: `_render_template_info()` new function; registered as `📋 Template` section in property panel; `_render_exposure()` shows info for templates.
  - `ui/home.py`: `_render_threshold_alerts()` function; called after quadrant distribution in exposure expander.
  - `tests/test_templates.py`: NEW — 25 tests.
  - `tests/test_alerts.py`: NEW — 11 tests.
  - **445 tests passing.**

### Session N+6 (v2.26.0 documentation pass)
- Documentation updates for F7 What-If Analysis + broader doc refresh:
  - `docs/help_whatif.md`: NEW in-app help article; registered in `ui/home.py` `_HELP_FILES`
  - `docs/help_overview.md`: What-If row added
  - `docs/welcome.md`: What-If capability block added
  - `docs/USER_GUIDE.md`: What-If + Lifecycle sections added; navigation updated; health thresholds corrected; version → v2.26.0
  - `docs/ARCHITECTURE.md`: 5-page diagram; lifecycle services; WHATIF_DEFAULTS; init functions
  - `README.md`: version v2.26.0; 3 new Key Features; Analysis Tools + nav updated; pages/services structure updated
  - `CHANGELOG.md`: Documentation section added under v2.26.0
  - **409 tests passing.**

### Session N+5 (v2.26.0 F7 What-If Analysis)
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

- **F32 `risk_quadrant` overlay pattern**: `risk_quadrant` is computed at exposure-calculation time
  and stored only in `exposure_results["risk_results"]`. It is overlaid onto node dicts in
  `render_visualization_tab` alongside `base_exposure`/`exposure`. Without this overlay,
  `create_node_config()` cannot see the quadrant. This is the same pattern as exposure overlays.

- **F32 `_QUADRANT_BORDER_COLORS` keys are lowercase**: The four values returned by
  `_compute_risk_quadrant()` are `"critical"`, `"frequency"`, `"severity"`, `"marginal"` — all
  lowercase. The colour map must use these exact strings. Do not capitalise.

- **F32 quadrant borders require exposure to be calculated first**: If no exposure calculation
  has been run, nodes have no `risk_quadrant` attribute and borders silently do not appear.
  This is by design — borders are derived from computed values, not raw node properties.


- **`high_exposure_threshold` — not `expected_loss_threshold`**: The raw exposure score
  is not an "Expected Loss" in the financial sense. EL will be introduced later with the
  compound Poisson loss model (SPICE calibration, LEC). Until then, threshold alerts compare
  against `high_exposure_threshold` (same 0-100 scale as `final_exposure`).

- **`boolean` YAML type → `AttributeType.BOOL`**: `AttributeType` enum value is `"bool"`,
  not `"boolean"`. The alias mapping is in `core/attribute.py` `__post_init__`. Any new
  schema attribute type of `boolean` or `integer` will be correctly resolved.

- **INSTANTIATES edge safety filter in `get_graph_data`**: After collecting all edges,
  a `_node_ids` set filter strips any edge whose source or target is not in the canvas.
  This is a general safety measure, not just for INSTANTIATES. Applied before scope filtering.

- **Subtype selector rendered after `build_entity_form`**: `_render_risk_subtype_fields()`
  mutates `form_data` in place. It reads `form_data["level"]` (set by the generic form)
  to filter subtypes. Works for both create (existing_data={}) and edit (pre-fill from node dict).

- **U14 `is_template` exclusion is a second independent axis** (orthogonal to lifecycle):
  templates are excluded via `(r.is_template IS NULL OR r.is_template = false)` WHERE clause
  in both `get_all_risks` and `get_risks_with_filters`. `exclude_templates=True` by default,
  same pattern as `exclude_inactive`. CRUD forms pass both `exclude_inactive=False` and
  `exclude_templates=False` to see everything.

- **U14 `update_risk` uses COALESCE for is_template**: `r.is_template = COALESCE($is_template_val, r.is_template, false)`.
  Caller passes `None` meaning "leave unchanged"; any boolean value overwrites the property.
  Param key is `is_template_val` (not `is_template`) to avoid collision with existing code.

- **Templates excluded from canvas via `get_risks_with_filters`**: `get_graph_data` in
  `analysis.py` calls `get_risks_with_filters` which now defaults to `exclude_templates=True`.
  No change needed to `get_graph_data` itself.

- **Template library is a separate expander** in Data Management Risks tab, not mixed into
  the main risk list. Main list = active specific risks only. Templates only appear in the
  `📋 Risk Templates` expander for management and instantiation.



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
v2.29.0 complete (F32 Graph Visual Behaviour Panel), 445 tests passing.
ROADMAPv3.md is the authoritative roadmap.
Next task: Iteration 5 — F31c Lifecycle-Aware Simulation.
Branch: feature/iteration_4.
```
