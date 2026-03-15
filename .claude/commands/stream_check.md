Review the changes in $ARGUMENTS (file path or diff) and verify stream discipline — no agent should refactor outside their assigned lane.

Stream boundaries:
- **Stream A** owns: `ui/`, `visualization/`, CSS. Must NOT touch `services/`, `database/`, or `config/`.
- **Stream B** owns: `config/`, `models/`, CRUD forms, `utils/state_manager.py`. Must NOT touch exposure math.
- **Stream C** owns: `services/exposure_calculator.py`, `services/influence_analysis.py`, `services/mitigation_analysis.py`. Must NOT touch UI layer.

For each file changed, report:
- Which stream owns it
- Whether any changes cross a stream boundary
- If a cross-stream change is found: [VIOLATION] — name the boundary crossed, explain why it's a problem, and propose how to either split the work or document it as a cross-stream dependency in `tasks/SESSION_STATE.md`

If all changes are in-lane: confirm [OK] with a one-line summary of what each stream's changes do.
