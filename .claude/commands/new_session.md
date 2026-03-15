We are starting a new development session. Do not begin any implementation until I explicitly confirm.

**Important — working directory**: Always operate from the main repository root. If in doubt, run `git worktree list` and use the path listed first (not any path under `.claude/worktrees/`). All file paths below are relative to that root.

1. Read `tasks/SESSION_STATE.md`
2. Read the relevant stream section of `ROADMAPv2.md` for the active feature (not the whole file)
3. If an active feature is in progress, read the current `tasks/todo.md`

Then summarize in this format:

---

**Last completed**: [feature + version]
**In progress**: [feature ID + name + % complete]
**Active stream**: [A / B / C]
**Files already modified**: [list]
**Next immediate step**: [one precise sentence]
**Blockers / open decisions needing your input**: [list or "none"]

---

Wait for me to confirm or redirect before doing anything.
