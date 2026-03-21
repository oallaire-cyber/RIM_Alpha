# Task: v2.27.1 Post-Release Fixes + Subtype Selection
**Stream**: A + B
**Started**: 2026-03-21
**Target version**: v2.27.1

## Plan
- [x] Rename `expected_loss_threshold` → `high_exposure_threshold` throughout
- [x] Fix YAML encoding (`charmap` error) in Configuration page YAML editor backup
- [x] Fix `is_template` not rendering as checkbox (`boolean` alias in `core/attribute.py`)
- [x] Fix graph `AssertionError` on INSTANTIATES edge (safety filter in `analysis.py`)
- [x] Add Subtype selector to create/edit risk forms (`unified_crud_tab.py`)
- [x] Full documentation pass (v2.27.0 + v2.27.1 features)
- [x] Run full test suite → 445 passing
- [x] Update CHANGELOG + ROADMAPv3 + SESSION_STATE + todo.md

## Git Commit
```
fix(v2.27.1): post-release fixes + risk subtype selection in forms

- high_exposure_threshold: renamed from expected_loss_threshold throughout
  (schema_loader, schema YAMLs, home.py, tests). Backward-compat parse
  fallback accepts old key. EL terminology reserved for future financial model.

- YAML encoding: open() in Configuration page YAML editor now specifies
  encoding='utf-8' for both backup read and write (Windows charmap fix).

- is_template checkbox: core/attribute.py __post_init__ adds 'boolean'→'bool'
  and 'integer'→'int' aliases before AttributeType() enum lookup. Without this,
  schema attributes typed 'boolean' silently fell back to STRING widget.

- Graph AssertionError: analysis.py get_graph_data now strips any edge whose
  source or target is absent from the canvas node set, before scope filtering.
  Prevents INSTANTIATES edges from crashing PyVis when template node is excluded.

- Subtype selection: _render_risk_subtype_fields() in unified_crud_tab.py renders
  a subtype selectbox (filtered by selected level) + extension fields after the
  generic build_entity_form(). Applied to both create and edit forms for risks.

445 tests passing.

Documentation: help_templates.md + help_alerts.md (new); USER_GUIDE, ARCHITECTURE,
METHODOLOGY, CONFIGURATION_MANAGER, help_overview, welcome, help_exposure, README
all updated for v2.27.0 features. /finish skill enforces doc pass as mandatory step.
```
