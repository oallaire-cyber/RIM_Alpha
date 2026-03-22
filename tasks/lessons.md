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

## Token/Context Efficiency Rules Learned
- _[example: Re-reading full ROADMAP when only Stream B section was needed]_
  → **Rule**: Read only the relevant stream section. Use Ctrl+F equivalent — ask for specific section by name.
