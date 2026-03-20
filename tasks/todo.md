# Task: U12 — Risk Lifecycle Engine
**Stream**: B + C (cross-stream)
**Started**: 2026-03-20
**Target version**: v2.25.0

## Plan
- [x] Step 1: models/enums.py — 4 new RiskStatus + LIFECYCLE_INACTIVE_STATUSES
- [x] Step 2: models/risk.py — field renames, new fields, is_inactive property
- [x] Step 3: schemas/default/schema.yaml + schemas/it_security/schema.yaml — statuses + lifecycle_rules
- [x] Step 4: config/schema_loader.py — LifecycleRulesConfig + QuadrantThresholdsConfig + parser + serializer
- [x] Step 5: database/queries/risks.py — exclude_inactive param, field renames, get_archive_candidates
- [x] Step 6a: services/trigger_engine.py — NEW
- [x] Step 6b: services/auto_acceptance_engine.py — NEW
- [x] Step 6c: services/archive_engine.py — NEW
- [x] Step 7: utils/state_manager.py — LIFECYCLE_DEFAULTS + init_lifecycle_state
- [x] Step 8: pages/2_💾_Data_Management.py — Lifecycle Engine expander + Accepted Risks toggle
- [x] Step 9: tests/test_lifecycle.py — NEW (25 test cases, 3 testing gates)
- [x] Step 10: Migration script + CHANGELOG + ROADMAPv3 + SESSION_STATE + todo.md
- [ ] Run full test suite

## Implementation Notes
- `exclude_inactive=True` default enforces archived exclusion at DB query layer (not inside ExposureCalculator)
- `from_dict` migration-safe fallbacks: `trigger_condition = data.get("trigger_condition") or data.get("activation_condition")`
- TriggerEngine is human-review only — no eval() on free text; future: use `simpleeval` library
- `get_graph_data` NOT changed — canvas still shows all risks; F32 handles opacity for Watching/Suppressed

## Testing Checklist
- [ ] Automated tests written — YES (tests/test_lifecycle.py)
- [ ] `.\venv\Scripts\activate; py -m pytest tests/` passes
- [ ] Manual walkthrough documented in `walkthrough.md`
- [ ] Scope completeness verified (if graph-touching)

## Documentation Updates
- [x] `CHANGELOG.md`
- [x] `ROADMAPv3.md` (mark U12 complete)
- [x] `tasks/SESSION_STATE.md`

## Git Commit
```
feat(v2.25.0): U12 Risk Lifecycle Engine

- 6-state lifecycle: Accepted, Watching, Suppressed, Closed added to RiskStatus
- LIFECYCLE_INACTIVE_STATUSES constant; is_inactive property on Risk model
- Field renames: activation_condition → trigger_condition, activation_decision_date → acceptance_date
- New fields: acceptance_owner, archive_date
- risk_lifecycle_rules YAML block: acceptance_threshold, severity_ceiling, archive_retention_days
- LifecycleRulesConfig + QuadrantThresholdsConfig in schema_loader (parse + serialise)
- exclude_inactive=True default on get_all_risks / get_risks_with_filters
- New services: TriggerEngine, AutoAcceptanceEngine, ArchiveEngine
- Data Management: Lifecycle Engine expander + Accepted Risks toggle
- scripts/migrate_activation_to_lifecycle.cypher: idempotent field rename migrations
- tests/test_lifecycle.py: 25 test cases covering all 3 testing gates

Closes U12
```
