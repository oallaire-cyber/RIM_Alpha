# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.23.0` — Iteration 3: F29 Interactive Scope Sandbox

## Last Updated
2026-03-15 — Iteration 3 session: F28 + F29 both complete

---

## 🔴 Active Work In Progress
<!-- No task is mid-implementation. All committed. Next up is F31. -->

**Feature**: F31 Scope-Driven Simulation & Results Storage (not yet started)
**Stream**: C
**Status**: 0% — planning not yet started

**Next immediate step**:
> Begin planning F31 (Scope-Driven Simulation & Results Storage).
> See ROADMAPv2.md Iteration 4 section for full task details.

**Blocked on**: Nothing.

---

## ✅ Recently Completed (last 2 sessions)

### Session N-1 (v2.22.0)
- **v2.22.0** — **F28 Advanced Scope Filter UI** (Iteration 3):
  - Created `ui/panels/scope_filter_panel.py` with three functions:
    - `_render_filter_table()` — shared core (filter controls, bulk buttons,
      `st.data_editor` with checkbox column, delta sync via callbacks).
    - `render_scope_filter_panel(manager, filter_mgr, active_scope)` — home.py
      entry point, persists via `FilterManager`.
    - `render_scope_node_editor(manager, scope, on_add, on_remove, key_prefix)`
      — config page entry point, caller-supplied callbacks, no FilterManager.
  - Modified `ui/tabs/unified_crud_tab.py`: injects collapsed expander
    "🔍 Scope Definition — Add / Remove Risks" when `type_id == "risk"` and
    scope is active.
  - Modified `pages/1_⚙️_Configuration.py`: scope creation form (removed
    `st.form`, added draft scope in session state); scope edit section
    (replaced multiselect with immediate-save `render_scope_node_editor`).
  - Filter controls: text search, Level multiselect (schema-driven), Subtype
    multiselect (schema-driven), Exposure slider (conditional on session state).

### Session N (this session — v2.23.0)
- **v2.23.0** — **F29 Interactive Scope Sandbox** (Iteration 3):
  - Extended `visualization/graph_options.py`: `get_node_click_postmessage_js()`
    now also handles `network.on("oncontext")` → right-click postMessage
    `{type:"node_action", action:"contextmenu", node_id}`.
  - Updated `visualization/graph_click_bridge/index.html`: relay structured
    `{action, node_id}` dict; legacy `node_selected` type kept as fallback.
  - Updated `visualization/graph_renderer.py`: `render_graph_streamlit()` return
    type changed to `Optional[dict]` `{"action": ..., "node_id": ...}`.
  - Updated `utils/state_manager.py`: added `scope_sandbox_mode` and
    `scope_sandbox_pending_node` to `HOME_UI_DEFAULTS`.
  - Updated `ui/home.py`:
    - Helper functions: `_sandbox_add`, `_sandbox_remove`, `_commit_sandbox`,
      `_discard_sandbox`, `_render_sandbox_action_panel`.
    - Graph section: scope filter bypass when sandbox active; green border
      indicator on effective scope members; sandbox banner; structured
      `graph_event` dict parsing; sandbox action panel after graph render.
    - Sidebar `render_scope_selector()`: 🧪 Sandbox toggle + Commit/Discard
      buttons; ➕ New Scope inline form with create-and-enter-sandbox flow.
    - Full Graph cleanup extended to clear all sandbox session keys.
  - Updated `docs/help_scopes.md`: added Sandbox section.

---

## 🧠 Key Decisions Made (not in docs yet)

- **`render_scope_node_editor` callback pattern**: The config page can't use
  `FilterManager` (it's a home.py singleton). The solution is caller-supplied
  `on_add(node_id)` / `on_remove(node_id)` callbacks that handle persistence.
  The shared core `_render_filter_table` is agnostic to persistence strategy.

- **Draft scope for creation form**: Removing `st.form` means individual widget
  values are preserved via Streamlit's normal session_state keying. The pending
  node selection is stored in `st.session_state._new_scope_draft`
  (an `AnalysisScopeConfig` with `id="__draft__"`). It is deleted on successful
  scope creation or when the user navigates away.

- **JS click bridge architecture**: PyVis is now wrapped in a `declare_component`
  (outer iframe). PyVis lives in an inner `srcdoc` iframe. `window.parent` from
  the inner iframe = outer component iframe → postMessage is received correctly.
  This is the only working architecture: `st.components.v1.html` is one-way
  (no `declare_component` protocol), so the outer wrapper is essential.

- **`render_graph_streamlit()` now returns `Optional[dict]`**: Returns
  `{"action": "click"|"contextmenu", "node_id": str|None}` or `None`.
  Callers parse `_action`/`_node_id`. Legacy string fallback preserved.
  Background click returns dict with `node_id: null`.

- **`scope_sandbox_overrides` lazy init**: NOT in `HOME_UI_DEFAULTS` to avoid a
  shared mutable dict across sessions. Initialized in `setdefault()` calls
  inside `_sandbox_add`/`_sandbox_remove`, and explicitly on toggle-on /
  New Scope creation.

- **Sandbox bypasses scope filter**: `filters.pop("scope_node_ids", None)` and
  `filters.pop("scope_include_neighbors", None)` before `get_graph_data()` so
  the full graph is visible and out-of-scope nodes can be added.

- **Net effect of overrides**: `_sb_effective = (scope.node_ids ∪ ov["add"]) − ov["remove"]`.
  This is the set used for the green border indicator and the in-scope detection
  in the action panel. Commit applies these to `FilterManager` which then
  persists to `schema.yaml` via the schema loader.

- **`net.generate_html()` is the correct PyVis API for in-memory HTML**:
  `net.html` is an instance variable initialised to `""` — it is only
  populated as a side-effect of `write_html()`. `generate_html()` renders
  the Jinja2 template and returns the string directly without any file I/O.
  Always use `generate_html()` when you need the HTML as a Python string.

- **`cdn_resources="in_line"` is required for the srcdoc bridge**: With
  `"local"` (default), PyVis embeds `<script src="lib/bindings/utils.js">` in
  the HTML. That relative URL causes a 404. With `"in_line"`, all JS is
  embedded in the HTML.

- **`create_unified_entity` return type inconsistency** (from prior session):
  risk/mitigation return `str`, context nodes return `dict`. Branch on
  `isinstance(new_item, str)` vs `dict` at all call sites.

---

## ⚠️ Known Issues / Tech Debt

- **F22 and F23 appear twice each in `ROADMAPv2.md`** Stream B section —
  deduplicate when next touching that file.

- **`pydantic` and `openpyxl` must be installed via venv** — always run tests
  with `source venv/Scripts/activate && python -m pytest tests/` (378 pass).
  Running outside the venv causes 8 import failures.

- **`schemas/default/schema.yaml` was edited by user** in the same commit as
  v2.20.1 (removed impact_levels from `impacts_tpo` context edge, changed line
  style to solid, added null default to `capability_level`). Tracked in git.

---

## 📋 Open Questions Pending User Decision

1. **F31 start**: Ready to plan Scope-Driven Simulation & Results Storage when user confirms.

2. **Branch hygiene**: Push `feature/work_stream_AB` to remote when ready.

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
Current task: F31 Scope-Driven Simulation & Results Storage (Iteration 4).
```
