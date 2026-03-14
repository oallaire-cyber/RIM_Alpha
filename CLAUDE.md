# RIM Project — Claude Code Context
<!-- v2 — updated with concrete file map -->

## What This Project Is
Risk Influence Map (RIM): a Streamlit + Neo4j graph-based risk management platform.
Domain-agnostic, schema-driven (YAML), multi-domain (nuclear, space, cyber, aerospace).
Demo case: Orbital Dynamics Technologies / HORIZON-LEO constellation.
Current version: v2.17.0

## Non-Negotiable Architecture Rules

**Computational boundary**: ONLY `BusinessRisk`, `OperationalRisk`, `Mitigation` carry math weight.
All other node types are `ContextNodes` — YAML-driven, zero app code changes to add new ones.

**Scope completeness**: When a scope is active, it IS the entire graph.
Every query, stat, dropdown, and computation must respect `scope_node_ids`. Partial scope = critical bug.

**Relationship semantics**:
- `semantic: influence` → participates in exposure propagation
- `semantic: context` / `semantic: cluster` → displayable only, no math

**Computed, not stored**: Risk Level is BFS-computed at read time. Never cache/store it.

**Schema-first**: New ContextNode type = YAML change only. If you write type-specific `if/else` for a ContextNode, it will be rejected.

## Key File Map (read only what you need)

### Entry points
- `app.py` — thin entry point (~60 lines)
- `pages/1_⚙️_Configuration.py` → schema + DB admin (`app_config.py` ~2,200 lines — be surgical)
- `pages/2_💾_Data_Management.py` → unified CRUD hub
- `pages/3_🎲_Simulation.py` → Monte Carlo (`calibration_simulator.py` ~1,100 lines)

### Core logic (Stream C)
- `services/exposure_calculator.py` — ~565 lines — the exposure engine
- `services/influence_analysis.py` — graph algorithms
- `services/mitigation_analysis.py` — coverage/gaps
- `config/schema_loader.py` — ~1,100 lines — schema parsing, validation, scope parsing
- `config/settings.py` — ~350 lines — dynamic settings from active schema

### UI layer (Stream A)
- `ui/home.py` — dashboard, visualization, analysis panels
- `ui/filters.py` — fully schema-driven, no hardcoded IDs (fixed in v2.10.1)
- `ui/sidebar.py` — scope selector + filters
- `visualization/node_styles.py` — shapes: diamond=BR, dot=OR, box=MIT, hexagon=TPO
- `visualization/colors.py` — exposure gradient: green→yellow→orange→red→darkred

### State & DB (Stream B)
- `utils/state_manager.py` — centralized session state
- `utils/db_manager.py` — singleton Neo4j connection
- `models/` — Pydantic models for all entities

### Schema files
- `schemas/default/schema.yaml` — ~700 lines — ODT New Space (default)
- `schemas/it_security/schema.yaml` — ~500 lines — cybersecurity domain

### Docs — RUNTIME-LOADED into live app UI via `utils/markdown_loader.py`
Editing these files affects the live help section — treat as user-facing content:
`docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md`,
`docs/VISUAL_DESIGN.md`, `docs/CONFIGURATION_MANAGER.md`, `docs/CALIBRATION_SIMULATOR.md`

### Tests
- `tests/` — pytest. Models: fully covered. Services: partial.
- Notable: `test_scopes.py`, `test_risk_subtypes.py`, `test_exposure_calculator.py`

## Known Tech Debt
- F22 and F23 appear **twice each** in `ROADMAPv2.md` Stream B section — deduplicate when touching that file

## Before ANY Code Task
1. Check `tasks/SESSION_STATE.md` for current work-in-progress
2. Read the relevant stream section of `ROADMAPv2.md` (not the whole file)
3. For entity logic: read relevant section of schema YAML, not the whole file

## Development Workflow
1. Write plan to `tasks/todo.md` with checkable items
2. Check in before implementing if architectural decisions involved
3. Mark items complete as you go
4. On task complete: run tests → update `walkthrough.md` → update `CHANGELOG.md` + `ROADMAPv2.md` → provide git commit text
5. After any user correction: update `tasks/lessons.md`

## Environment
- **All Python/pytest commands**: prefix with `.\venv\Scripts\activate;`
- Example: `.\venv\Scripts\activate; py -m pytest tests/`
- Neo4j default: `bolt://localhost:7687` / user: `neo4j`

## Stream Assignment (parallel agents — stay in lane)
- **Stream A**: `ui/`, `visualization/`, CSS only. No DB logic.
- **Stream B**: `config/`, `models/`, CRUD forms, state. No exposure math.
- **Stream C**: `services/exposure_calculator.py`, graph algorithms, scope math.
- Cross-stream dep? Document in `tasks/SESSION_STATE.md`, pause, don't refactor out-of-lane.

## 3-Tier Hierarchy (never collapse)
Top: Business Objectives → Middle: Business Risks (C-suite) → Bottom: Operational Risks (functional teams)

## Full Reference Docs (load on demand, not by default)
- `AGENT_RULES_AND_CONTEXT.md` — complete golden rules
- `ROADMAPv2.md` — all features, streams, dependency map
- `ROADMAP_ARCHITECTURAL_REFERENCE.md` — deep architecture & phase history
- `tasks/SESSION_STATE.md` — current session state for handoff
