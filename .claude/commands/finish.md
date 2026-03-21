The current feature implementation is complete. Execute the standard RIM finalization sequence in order:

Feature context: $ARGUMENTS

1. **Run tests**
   Execute: `.\venv\Scripts\activate; py -m pytest tests/ -v`
   If any tests fail, stop and fix them before proceeding.

2. **Full documentation pass** — MANDATORY, not optional. Update ALL of:
   - `CHANGELOG.md` — add version section at top
   - `ROADMAPv3.md` — mark the feature complete with strikethrough + ✅ version tag; update ROADMAPv2.md if touching it
   - `README.md` — add to Key Features table; bump "Current Version" line
   - `docs/USER_GUIDE.md` — add feature section; update version footer
   - `docs/ARCHITECTURE.md` — update Neo4j schema block if new nodes/relationships; update version footer
   - `docs/METHODOLOGY.md` — add math/model subsection if new metrics/formulas; update version footer
   - `docs/CONFIGURATION_MANAGER.md` — document any new schema YAML blocks
   - `docs/help_overview.md` — add row to Core Capabilities table
   - `docs/welcome.md` — add capability block
   - `docs/help_exposure.md` — update if feature affects exposure or alerting
   - If the feature has its own UX workflow: create `docs/help_<feature>.md` and register it in `ui/home.py` `_HELP_FILES`

3. **Apply all documentation updates**
   Write or edit each file. Do not just draft — apply changes directly.

4. **Update `tasks/SESSION_STATE.md`**
   Mark the feature complete, clear the Active Work In Progress section, update Recently Completed and Key Decisions.

5. **Provide git commit text**
   Format:
   ```
   feat(vX.YY.Z): short description

   - key change
   - key change

   Closes [F-number]
   ```
