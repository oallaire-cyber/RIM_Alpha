The current feature implementation is complete. Execute the standard RIM finalization sequence in order:

Feature context: $ARGUMENTS

1. **Run tests**
   Execute: `.\venv\Scripts\activate; py -m pytest tests/ -v`
   If any tests fail, stop and fix them before proceeding.

2. **Identify documentation to update**
   - `CHANGELOG.md` — add entry for the new version
   - `ROADMAPv2.md` — mark the feature complete with version tag (e.g., ~~[F18]~~ ✅ _(v2.18.0)_)
   - `README.md` — update if user-facing features or project structure changed
   - `docs/` files — update if the feature affects any help section content (remember: these are runtime-loaded into the live UI)
   - Any affected files in `docs/` folder

3. **Draft all documentation updates**
   Show the exact text changes for each file that needs updating.

4. **Update `tasks/SESSION_STATE.md`**
   Mark the feature complete, clear the Active Work In Progress section, update Recently Completed.

5. **Provide git commit text**
   Format:
   ```
   feat(vX.YY.Z): short description

   - key change
   - key change

   Closes [F-number]
   ```
