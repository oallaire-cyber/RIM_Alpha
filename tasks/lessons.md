# RIM — Lessons Learned
> Updated after every user correction. Reviewed at session start.

## Architecture Mistakes to Avoid
<!-- Add entries as: [date] — [mistake] → [rule to prevent it] -->

- _[example: 2025-01 — Added type-specific if/else for a ContextNode]_
  → **Rule**: ContextNodes are YAML-only. Zero app code. Period.

- _[example: 2025-01 — Wrote exposure calculation without checking scope_node_ids]_
  → **Rule**: Every query touching the graph must accept and propagate scope_node_ids. Check Golden Rule B before writing any query.

## Architecture / Methodology Notes

- [2026-05-05] **`get_semantic_influences()` is a math view, not a file-format view.**
  `get_semantic_influences()` concatenates kernel `INFLUENCES` (Risk→Risk) PLUS kernel `MITIGATES`
  (Mitigation→Risk, normalized to `source_id`/`target_id`) so the exposure engine can treat both as
  influence-semantic edges uniformly. **Do NOT use it for export / file format paths** — those need
  the kernel separation that the dedicated Mitigates sheet/key already provides. Three rounds of
  TC-11 dedup hardening missed the bug because the contamination was upstream of the dedup logic.
  → **Rule**: Export / serialization paths use kernel-specific getters (`get_all_influences`,
    `get_all_mitigates_relationships`). Math / analysis paths use the semantic view.

- [2026-05-05] **Coherence audit before patching repeated bug rounds.**
  TC-11 had three rounds of dedup fixes that did not resolve the bug. After the user requested a
  coherence audit of the data structure / schema / demo data, the actual root cause (export
  contamination) surfaced in 30 minutes of static reading. The audit also revealed accumulated
  glitches from prior iterations (legacy `entities.tpo` block duplicating `context_nodes.tpo`,
  uppercase `"TPO"` filter that matches no nodes, dead `_import_tpos` method calling a removed
  manager API).
  → **Rule**: After two rounds of patching the same symptom without resolution, **STOP** and audit
    the surrounding code for accumulated drift before round 3. Static reading of related schema +
    parser + UI consumers often reveals upstream contamination that downstream patches cannot fix.

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
