# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.22.0` — Iteration 3: F28 Advanced Scope Filter UI

## Last Updated
2026-03-15 — Iteration 3 session: F28 complete

---

## 🔴 Active Work In Progress
<!-- No task is mid-implementation. All committed. Next up is F29. -->

**Feature**: F29 Interactive Scope Sandbox (not yet started)
**Stream**: A
**Status**: 0% — planning not yet started

**Next immediate step**:
> Begin planning F29 (Interactive Scope Sandbox).
> See ROADMAPv2.md Iteration 3 section for full task details.

**Blocked on**: Nothing.

---

## ✅ Recently Completed (last 2 sessions)

### Session N-1 (v2.21.0)
- **v2.21.0** — **F26 Contextual Property Panel** (Iteration 2):
  - Created `visualization/graph_click_bridge/index.html` — thin
    `declare_component` frontend that wraps PyVis HTML in an inner `srcdoc`
    iframe and relays `node_selected` postMessages to Python via
    `Streamlit.setComponentValue()`. This closes the one-way iframe gap:
    canvas click → JS → Python session state.
  - Added `get_node_click_postmessage_js()` to `visualization/graph_options.py`
    — injects a `network.on("click")` handler (with 1100ms delay after focus
    mode) that calls `window.parent.postMessage({type:"node_selected", ...})`.
  - Modified `visualization/graph_renderer.py`: injected postMessage JS,
    registered `declare_component` at module level, changed
    `render_graph_streamlit()` to use the bridge and return `Optional[str]`.
  - Created `ui/panels/node_property_panel.py` — 6-section `NodePropertyPanel`
    with `Section` dataclass.
  - Wired in `ui/home.py`: captures `clicked_node_id` from graph render,
    merges into `selected_node_id`, renders `render_node_property_panel`.
  - Post-implementation fixes: `cdn_resources="in_line"` for PyVis to avoid
    `utils.js` 404; switched to `net.generate_html()` to fix UnicodeEncodeError
    and empty graph bug.

### Session N (this session — v2.22.0)
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
  - Also applied to scope creation/edit in Configuration page via
    `render_scope_node_editor`.

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

- **`render_graph_streamlit()` now returns `Optional[str]`**: It returns the
  UUID of the most recently clicked node (or None). Callers must handle the
  case where `None` means "no new click this rerun" (not "deselect").
  Background click returns `None` with the bridge posting `node_id: null`.
  `home.py` uses `_graph_prev_click` sentinel to distinguish "first None"
  (nothing ever clicked) from "user clicked background" (None after a UUID).

- **`net.generate_html()` is the correct PyVis API for in-memory HTML**:
  `net.html` is an instance variable initialised to `""` — it is only
  populated as a side-effect of `write_html()`. `generate_html()` renders
  the Jinja2 template and returns the string directly without any file I/O.
  Always use `generate_html()` when you need the HTML as a Python string.

- **`cdn_resources="in_line"` is required for the srcdoc bridge**: With
  `"local"` (default), PyVis embeds `<script src="lib/bindings/utils.js">` in
  the HTML. That relative URL resolves to the component's URL path, causing
  Streamlit's ComponentRequestHandler to look for the file in
  `visualization/graph_click_bridge/lib/` — where it doesn't exist. With
  `"in_line"`, all JS is embedded in the HTML and no external files are
  referenced.

- **`create_unified_entity` return type inconsistency** (from prior session):
  risk/mitigation return `str`, context nodes return `dict`. Branch on
  `isinstance(new_item, str)` vs `dict` at all call sites.

- **`config.settings._active_schema` singleton vs fresh disk read**: See prior
  session notes.

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

1. **F29 start**: Ready to plan Interactive Scope Sandbox when user confirms.

2. **Branch hygiene**: Push `feature/work_stream_AB` to remote when ready.

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
Current task: F29 Interactive Scope Sandbox (Iteration 3).
```
