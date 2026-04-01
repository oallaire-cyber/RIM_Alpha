# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.31.0` — Pre-Iteration 6 Bug Fix Release. Branch: `fix/test_fix`.

## Last Updated
2026-04-01 — v2.31.0 complete. 445 tests passing. Manual test campaign written (`tasks/test_campaign_v2.31.0.md`). Awaiting user sign-off tomorrow before merging.

---

## 🔴 Active Work In Progress

**None.** Session closed.

**Pending before merge:**
- User to execute `tasks/test_campaign_v2.31.0.md` (TC-01 through TC-13 + R1–R6)
- Manual sign-off required on all test cases
- Merge `fix/test_fix` → main after sign-off
- **Demo data reset required** before testing: load `scripts/demo_data_loader_en.cypher` into Neo4j (old `:TPO` nodes won't work with new code)

**Next phase** (after merge + test sign-off): **Iteration 6** — Financial Layer & LEC (U16, F34, F9).
A SPICE synchronisation/briefing session is required before implementation begins.

---

## ✅ Recently Completed (last 2 sessions)

### Session N+13 (this session — v2.31.0 Pre-Iteration 6 Bug Fixes)
- **v2.31.0** — **7-bug fix release** on branch `fix/test_fix`:

  **BUG 1 — Excel Export & JSON Backup crash** (`services/backup_service.py`, `database/manager.py`):
  - `EntityTypeDefinition.type_id` → `.id` in both `backup_service` entity loop and
    `manager._collect_context_data`. Export silently returned `None` (Streamlit: "Invalid binary
    data format"); backup crashed with AttributeError.

  **BUG 2 — Backup docstring** (`services/backup_service.py`):
  - Module docstring updated: removed stale `tpos`/`tpo_impacts` top-level key references;
    corrected to `context_nodes`/`context_edges`.

  **BUG 3 — TPO Impact Levels in Relationships tab** (`pages/1_⚙️_Configuration.py`):
  - Removed the `impacts_tpo` impact levels block from `render_relationship_config()`.
    Relationships tab now shows only Influence Strengths + Mitigation Effectiveness Levels.

  **BUG 4 — "Top Objective" naming** (schema YAMLs, docs, UI strings):
  - All display strings standardised to "Top Objective / Top Objectives". Internal identifiers
    (`tpo`, `impacts_tpo`) unchanged.

  **BUG 5 — Context node isolation + canvas visibility** (`database/queries/generic_entity.py`,
  `database/queries/analysis.py`):
  - `create_entity`: injects `node_type = entity_type.id` for all ContextNode types.
  - `get_all_entities`: prepends `WHERE n.node_type = $__node_type` for ContextNode types.
  - `get_graph_data`: removed `if entity_id == "tpo": continue` and
    `if rel_id == "impacts_tpo": continue` (legacy skip-guards from old hardcoded TPO path).

  **BUG 6 — Scope persistence** (`ui/filters.py`):
  - `add_node_to_scope` + `remove_node_from_scope`: replaced stale `get_active_schema()` singleton
    with `SchemaLoader().load_schema(schema_name)` — fresh disk read before every modify+save.
    Also fixed broken `load_schema()` import and missing `schema_name` arg in `remove_node_from_scope`.

  **BUG 7 — Hard-to-reproduce graph blank** (`tasks/lessons.md`):
  - Logged as unresolved; suspected stale `ss["graph_data"]` cache. Cannot reproduce reliably.

  **Excel timezone fix** (`services/export_service.py`):
  - `neo4j.time.DateTime` is NOT a Python `datetime` subclass — `isinstance` checks silently skipped
    it. New `_coerce_records()` / `_coerce_value()` helpers duck-type on `hasattr(v, "tzinfo")` and
    call `.to_native()` on Neo4j temporal types before stripping tzinfo. Applied to all DataFrames.
  - `_strip_tz()` kept as last-resort guard for pandas DatetimeTZDtype columns.
  - `export_to_excel_bytes` except block changed to `raise` (was silently returning None).

  **Demo data** (`scripts/demo_data_loader_en.cypher`, `scripts/SNR_demo_data_loader_en.cypher`):
  - All `:TPO` nodes → `:ContextNode {node_type: 'tpo', ...}`.
  - All `MATCH (t:TPO ...)` → `MATCH (t:ContextNode ...)`.
  - Verification queries updated.

  **ROADMAPv3** (`ROADMAPv3.md`):
  - **[F39] Context Node Scope Membership** added to Stream B Iteration 6 backlog.
    Allow any ContextNode to be added/removed from scopes via UI (data layer already ready).

  **Test campaign** (`tasks/test_campaign_v2.31.0.md`):
  - 13 test cases + 6 regression checks written and saved.

  **445 tests passing.**

### Session N+12 (v2.30.0 F31c/d)
- **v2.30.0** — **F31c Lifecycle-Aware Simulation & F31d TRI α Calibration**:
  - `pages/2_🎲_Simulation.py`: all changes.
    - **F31c**: `_load_scope_data()` gains `include_inactive: bool = False` param.
      "🧟 Worst-Case Canvas" sidebar checkbox (shared by Scope-Based + TRI α Calibration).
      Banner shows latent risk count; results labelled `[Worst-Case]`.
    - **F31d**: 4th radio `"TRI α Calibration"`. `_run_alpha_sweep()` + `_compute_tac_and_store()`
      + `_render_tac_results()`. Charts: Mean TRI ±1σ + P95; stacked quadrant distribution bar.
      Target profile selectbox; recommended α highlighted. Save to Saved Results.
    - **Bugfix (save button)**: Refactored monolithic `run_scope_based_simulation_ui` and
      `run_tri_alpha_calibration_ui` into compute (`_compute_sb_and_store`, `_compute_tac_and_store`)
      + render (`_render_sb_results`, `_render_tac_results`) pairs. Results stored in
      `ss["last_sb_result"]` / `ss["last_tac_result"]`; render always called when stored — this
      is what makes 💾 Save Results work on the rerun triggered by clicking it.
      `📥 Export CSV` download button added alongside Save in both result views.
    - `utils/state_manager.py`: `last_sb_result`, `last_tac_result` added to `SIMULATION_DEFAULTS`.
    - `docs/help_simulation.md` (NEW); registered in `ui/home.py` `_HELP_FILES`.
    - Full docs pass: USER_GUIDE, ARCHITECTURE, METHODOLOGY, README, help_overview,
      welcome, CHANGELOG v2.30.0, ROADMAPv3 F31 complete.
  - **445 tests passing.**

### Session N+11 (v2.29.0 F32)
- **v2.29.0** — **F32 Graph Visual Behaviour Panel** — see previous SESSION_STATE for details.
  **445 tests passing.**

---

## 🧠 Key Decisions Made (not in docs yet)

- **`neo4j.time.DateTime` is NOT a `datetime` subclass**: isinstance checks silently skip it.
  Always duck-type with `hasattr(v, "tzinfo")` and convert with `.to_native()`. Pattern is in
  `services/export_service._coerce_value()`.

- **ContextNode `node_type` must be stored at create time**: `create_entity` injects
  `node_type = entity_type.id` before the Neo4j CREATE. Nodes created before this fix lack
  `node_type` and will be invisible to `get_all_entities` and the canvas. They need manual
  Cypher patching or re-creation.

- **`get_graph_data` TPO skip-guards are gone**: The `if entity_id == "tpo": continue` and
  `if rel_id == "impacts_tpo": continue` guards were remnants of the old hardcoded TPO path.
  Both are removed. TPOs now go through the generic context node loop identically to all other
  ContextNode types.

- **`add_node_to_scope` / `remove_node_from_scope` must use fresh disk load**: The module-level
  `_active_schema` singleton in `config/settings.py` is loaded once at process start. If the
  schema changes during the session (e.g. via Config page), saving the singleton overwrites the
  file with stale content. Always use `SchemaLoader().load_schema(schema_name)` before modifying.

- **Demo data cypher files must use `:ContextNode {node_type: 'tpo'}`**: The old `:TPO` label
  is no longer read by any query. Any dataset using `:TPO` nodes will show 0 Top Objectives in
  the Data Management tab and canvas. Reset required for all existing databases.

- **Simulation page save-button pattern (compute/render split)**: See Session N+12 note.
- **F32 `risk_quadrant` overlay pattern**: See Session N+12 note.
- **F32 `_QUADRANT_BORDER_COLORS` keys are lowercase**: See Session N+12 note.

---

## ⚠️ Known Issues / Tech Debt

- **BUG 7 — Hard-to-reproduce: graph canvas blank after L/S edit** (logged in `tasks/lessons.md`):
  Suspected stale `ss["graph_data"]` / `ss["exposure_results"]` cache after a CRUD DB write.
  Potential fix: explicit `ss["graph_data"] = None` after any risk update in `unified_crud_tab.py`.
  Cannot reproduce reliably. Flag for regression during Iteration 6 testing.

- **Existing `:TPO` nodes in any live DB** need manual patching before the app will show them:
  ```cypher
  MATCH (t:TPO)
  SET t:ContextNode, t.node_type = 'tpo'
  REMOVE t:TPO
  ```

- **F22 and F23 appear twice each in `ROADMAPv2.md`** Stream B section —
  deduplicate when next touching that file.

- **`pydantic` and `openpyxl` must be installed via venv** — always run tests
  with `.\venv\Scripts\python.exe -m pytest tests/` (445 pass).

---

## 📋 Open Questions Pending User Decision

_None._

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
v2.31.0 complete (Pre-Iteration 6 bug fix release). Branch: fix/test_fix. 445 tests passing.
Manual test campaign at tasks/test_campaign_v2.31.0.md — awaiting user sign-off before merging.
After merge: Iteration 6 begins. SPICE synchronisation session required first.
ROADMAPv3.md is the authoritative roadmap.
```
