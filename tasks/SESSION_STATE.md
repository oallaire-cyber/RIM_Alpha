# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.20.3` — Bug-fix patch series on top of Iteration 1 (F25 + F30 + F27)

## Last Updated
2026-03-14 — Bug-fix session: 3× Bug 1 (scope-add), graph search clear crash, scope persistence

---

## 🔴 Active Work In Progress
<!-- No task is mid-implementation. All committed. Next up is Iteration 2. -->

**Feature**: Iteration 2 — F26 Contextual Property Panel (not yet started)
**Stream**: A
**Status**: 0% — planning complete, not yet implemented

**Next immediate step**:
> Implement F26: replace `render_inline_editor` below the graph with a rich
> `NodePropertyPanel`. Before doing so, decide on the click-to-select approach:
>
> **Option A (recommended)**: Keep PyVis, inject a JS `window.parent.postMessage`
> bridge so canvas clicks set `selected_node_id` in Streamlit session state via
> a thin `st.components.v1.declare_component` wrapper. Preserves all existing
> rendering pipeline (node styles, colors, focus_node_ids).
>
> **Option B**: Replace PyVis with `streamlit-agraph` or `streamlit-vis-network`
> (native `return_value` support). Larger change — rewrites `graph_renderer.py`.
>
> The user has been informed of this architectural choice and has NOT yet decided.
> **Ask user which option they prefer before implementing F26.**

**Blocked on**:
> User decision: Option A (JS postMessage bridge) vs Option B (replace PyVis)
> for wiring canvas-click → `selected_node_id` → property panel update.

---

## ✅ Recently Completed (last 2 sessions)

### Session N-1 (Iteration 1 + bug fixes v2.20.0–v2.20.2)
- **v2.20.0** — F25 (remove TPO dashboard metrics), F30 (cycle detection with
  human-readable warnings), F27 (graph canvas search bar). Commits on
  `feature/work_stream_AB`.
- **v2.20.1** — 5 bugs from manual testing: Bug 1 partial fix (routing through
  `filter_mgr.add_node_to_scope()`), Bug 2 (UUID→name in cycle warnings),
  Bug 3 (scope bypass of level/status pre-filters in `analysis.py`), Bug 4
  (edge list scope filtering in `unified_crud_tab.py`), Bug 5 (`scope_include_
  mitigations` checkbox + `show_mitigations` injection).
- **v2.20.2** — Bug 1 second fix: `add_node_to_scope` in `filters.py` was
  importing a non-existent `load_schema` and calling `save_schema` with wrong
  arity → silently failed → YAML never written. Fixed to use
  `config.settings.get_active_schema()` + correct `save_schema(schema, name)`.
  Also fixed graph search clear button (`StreamlitAPIException`: must use
  `on_click` callback, not set widget key in script body after widget render).

### Session N (this session — v2.20.3)
- **v2.20.3** — Bug 1 **final fix** (root cause): `create_unified_entity`
  returns `Optional[str]` (raw UUID) for `risk`/`mitigation`, but a `dict`
  with `"id"` for context nodes. The guard `"id" in new_item` performed a
  **substring search** on the UUID string — almost always `False` — so the
  scope insert was silently skipped before even reaching persistence code.
  Fixed by branching on `isinstance(new_item, str)` vs `dict`.

---

## 🧠 Key Decisions Made (not in docs yet)

- **PyVis click-to-select is architecturally impossible** with `st.components.v1.html`
  (one-way iframe, no JS→Python event channel). The inline editor / property
  panel below the graph is only populated today via Graph Search or Influence
  Explorer dropdown. F26 must address this before a "click node → see details"
  UX can work. Two options proposed (see Active Work above).

- **`create_unified_entity` return type inconsistency**: risk/mitigation return
  `str`, context nodes return `dict`. Any code touching the return value of
  `create_unified_entity` must branch on `isinstance`. No fix to the manager
  layer was made (would be a broader refactor); the UI layer now handles both.

- **`config.settings._active_schema` is a module-level singleton** loaded once
  at import time. `render_scope_selector` reads scopes fresh from disk via
  `SchemaLoader().load_schema()` on every rerun. These are two separate schema
  object trees — mutating one does not affect the other. `add_node_to_scope`
  must save to YAML so the fresh disk-read picks up the change.

---

## ⚠️ Known Issues / Tech Debt

- **F22 and F23 appear twice each in `ROADMAPv2.md`** Stream B section —
  deduplicate when next touching that file (pre-existing, noted in CLAUDE.md).

- **`pydantic` and `openpyxl` not installed in venv** — 24 tests are skipped /
  error out on import. Unrelated to this work. 378 tests pass otherwise.

- **`schemas/default/schema.yaml` was edited by user** in the same commit as
  v2.20.1 (removed impact_levels from `impacts_tpo` context edge, changed line
  style to solid, added null default to `capability_level`). This is tracked in
  git but not separately documented.

---

## 📋 Open Questions Pending User Decision

1. **F26 implementation path**: Option A (JS postMessage bridge, keep PyVis) vs
   Option B (replace PyVis with a bidirectional component). Must be decided
   before Iteration 2 can start.

2. **Branch hygiene**: `feature/work_stream_AB` is ahead of
   `origin/feature/work_stream_AB` by several commits (not yet pushed in this
   session). User should `git push` when ready.

---

## 🔁 Resumption Prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first, then continue where we left off.
Current task: Iteration 2 — F26 Contextual Property Panel.
Before starting, ask the user whether they want Option A (JS postMessage bridge
to keep PyVis) or Option B (replace PyVis with a bidirectional component) for
wiring canvas-click → selected_node_id → property panel.
```
