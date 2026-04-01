# RIM — Lessons Learned
> Updated after every user correction. Reviewed at session start.

## Architecture Mistakes to Avoid
<!-- Add entries as: [date] — [mistake] → [rule to prevent it] -->

- _[example: 2025-01 — Added type-specific if/else for a ContextNode]_
  → **Rule**: ContextNodes are YAML-only. Zero app code. Period.

- _[example: 2025-01 — Wrote exposure calculation without checking scope_node_ids]_
  → **Rule**: Every query touching the graph must accept and propagate scope_node_ids. Check Golden Rule B before writing any query.

## Process Mistakes to Avoid
- _[example: Started implementing before reading ROADMAPv2.md stream assignment]_
  → **Rule**: Always check stream assignment first. Do not do out-of-lane refactoring.

- [2026-03-21] Edited files inside `.claude/worktrees/pensive-gauss/` — that worktree is ephemeral and discarded after merging.
  → **Rule**: ALWAYS work in the main repo root `C:\Users\olive\Documents\RIM_Alpha\`. Never write to any path under `.claude/worktrees/`. The worktree is a Claude-internal sandbox; all real work lives in the main repo.

- [2026-03-21] Finished v2.27.0 without doing documentation pass — user had to explicitly request it.
  → **Rule**: Documentation pass is MANDATORY as part of the finish sequence. Apply changes to all of:
    `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md`, `docs/CONFIGURATION_MANAGER.md`,
    `docs/help_overview.md`, `docs/welcome.md`, `docs/help_exposure.md`, `README.md`.
    For any feature with its own UX workflow: create `docs/help_<feature>.md` and register in `ui/home.py` `_HELP_FILES`.
    Do not draft only — apply the changes directly in the same session as the feature implementation.

## Known Unresolved Issues (observed, unable to reproduce)

- [2026-04-01] **Graph canvas blank after likelihood/severity edit** — user observed: after editing
  a risk's L or S in Data Management while a dedicated scope was active, the risk appeared in the
  Dashboard metric but not on the canvas graph. Deselecting the scope showed only mitigations.
  A full browser reload + DB reconnect resolved it. Could not be reproduced in subsequent attempts.
  Suspected cause: stale session-state graph cache (`exposure_results` / `graph_data` in
  `ss`) not invalidated after the CRUD edit triggers a DB write. Potentially cleared by implementing
  an explicit `ss["graph_data"] = None` after any risk update in `unified_crud_tab.py`.
  **Status**: Open — flag for regression during Iteration 6 testing.

## Token/Context Efficiency Rules Learned
- _[example: Re-reading full ROADMAP when only Stream B section was needed]_
  → **Rule**: Read only the relevant stream section. Use Ctrl+F equivalent — ask for specific section by name.
