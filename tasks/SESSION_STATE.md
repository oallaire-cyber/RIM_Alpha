# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.21.0` — Iteration 2: F26 Contextual Property Panel + JS click bridge

## Last Updated
2026-03-15 — Iteration 2 session: F26 + 3 post-implementation bug fixes

---

## 🔴 Active Work In Progress
<!-- No task is mid-implementation. All committed. Next up is Iteration 3. -->

**Feature**: Iteration 3 — F28 Advanced Scope Filter UI + F29 Interactive Scope Sandbox (not yet started)
**Stream**: B + A
**Status**: 0% — planning not yet started

**Next immediate step**:
> Begin planning F28 (Advanced Scope Filter UI) and F29 (Interactive Scope Sandbox).
> These are independent of Iterations 1–2 and can be tackled in either order.
> See ROADMAPv2.md Iteration 3 section for full task details.

**Blocked on**: Nothing — user should confirm which feature to tackle first (F28 or F29, or both together).

---

## ✅ Recently Completed (last 2 sessions)

### Session N-1 (v2.20.0–v2.20.3)
- **v2.20.0** — F25 (remove TPO dashboard metrics), F30 (cycle detection with
  human-readable warnings), F27 (graph canvas search bar).
- **v2.20.1** — 5 bugs from manual testing: Bug 1 partial fix (routing through
  `filter_mgr.add_node_to_scope()`), Bug 2 (UUID→name in cycle warnings),
  Bug 3 (scope bypass of level/status pre-filters in `analysis.py`), Bug 4
  (edge list scope filtering in `unified_crud_tab.py`), Bug 5 (`scope_include_
  mitigations` checkbox + `show_mitigations` injection).
- **v2.20.2** — Bug 1 second fix: `add_node_to_scope` in `filters.py` was
  importing a non-existent `load_schema` and calling `save_schema` with wrong
  arity → silently failed → YAML never written.
- **v2.20.3** — Bug 1 **final fix**: `create_unified_entity` returns
  `Optional[str]` for risk/mitigation but `dict` for context nodes; guard
  `"id" in new_item` was a substring search on the UUID string → always False.
  Fixed by branching on `isinstance(new_item, str)` vs `dict`.

### Session N (this session — v2.21.0)
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
    with `Section` dataclass. Sections: Identity, Exposure Metrics, Graph
    Position, Influence Analysis, Mitigation Summary, Edit. Graceful N/A for
    unavailable data.
  - Wired in `ui/home.py`: captures `clicked_node_id` from graph render,
    merges into `selected_node_id`, renders `render_node_property_panel`.

---

## 🧠 Key Decisions Made (not in docs yet)

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

- **`create_unified_entity` return type inconsistency** (from prior session):
  risk/mitigation return `str`, context nodes return `dict`. Branch on
  `isinstance(new_item, str)` vs `dict` at all call sites.

- **`config.settings._active_schema` singleton vs fresh disk read**: See prior
  session notes.

---

## ⚠️ Known Issues / Tech Debt

- **F22 and F23 appear twice each in `ROADMAPv2.md`** Stream B section —
  deduplicate when next touching that file.

- **`pydantic` and `openpyxl` not installed in venv** — 8 tests fail on import.
  Unrelated to this work. 365 tests pass otherwise.

- **`schemas/default/schema.yaml` was edited by user** in the same commit as
  v2.20.1 (removed impact_levels from `impacts_tpo` context edge, changed line
  style to solid, added null default to `capability_level`). Tracked in git.

---

## 📋 Open Questions Pending User Decision

1. **Iteration 3 start**: F28 (Advanced Scope Filter UI) vs F29 (Interactive
   Scope Sandbox) — which to tackle first, or both together?

2. **Branch hygiene**: Push `feature/work_stream_AB` to remote when ready.

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
Current task: Iteration 3 — F28 Advanced Scope Filter UI + F29 Interactive Scope Sandbox.
Ask the user which feature to start with (or both together) before planning.
```
