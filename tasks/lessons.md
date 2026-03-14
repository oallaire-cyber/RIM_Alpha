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

## Token/Context Efficiency Rules Learned
- _[example: Re-reading full ROADMAP when only Stream B section was needed]_
  → **Rule**: Read only the relevant stream section. Use Ctrl+F equivalent — ask for specific section by name.
