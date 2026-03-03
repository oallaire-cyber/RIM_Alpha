# 📝 Changelog

All notable changes to the Risk Influence Map (RIM) application.

---

## [v2.12.0] - 2026-03-03

### [F4] One-Click Visualization Export

**New Features:**

- **Visualization Export**: Users can now export the active styled graph view to PNG or PDF directly from the PyVis canvas or Streamlit container.
  - Added an "📥 Export" button alongside the fullscreen toggle within the interactive graph container.
  - The export extracts the canvas adjusting to the user's screen resolution, preserving current viewport, layouts, and zoom exactly as displayed.
  - Supports PNG and PDF generation purely client-side via `jspdf` CDN injection, respecting transparency and color styling without requiring backend rendering.

**Files Modified:**
- `visualization/graph_options.py` — Added `get_export_js()` containing HTML/CSS/JS export mechanics.
- `visualization/graph_renderer.py` — Injected the generated export capability into the PyVis HTML layout string.

---

## [v2.11.0] - 2026-03-02

### Risk Subtype System (Schema-Driven Domain Extensions)

**New Feature:**

- **Risk Subtypes**: Added a schema-driven subtype system to risk nodes, allowing domain-specific extension fields to be attached to risks without modifying the exposure calculation engine.
  - 9 built-in subtypes: Generic, Cyber — Entry Point-Oriented, Cyber — Target-Oriented, Supply Chain / Industrial, Engineering / Technical, Programme / Schedule, Regulatory / Compliance, Financial / Contractual, Strategic.
  - Each subtype defines `applies_to` levels (business, operational, or both) and optional `extension_fields` (string, enum, boolean, integer, float).
  - Extension fields are stored as flat `ext_*` prefixed properties on the Neo4j `:Risk` node.

**Schema & Data Layer:**

- `schemas/default/schema.yaml` — Added `subtypes:` list under `entities.risk` with 9 subtype definitions and their extension fields.
- `config/schema_loader.py` — Added `RiskSubtypeFieldConfig` and `RiskSubtypeConfig` dataclasses. Added `subtypes` field and `get_subtypes_for_level()` helper to `RiskEntityConfig`. Updated parsing (`_parse_risk_entity()`) and serialization (`_risk_entity_to_dict()`) for full round-trip support.

**Database Layer:**

- `database/queries/risks.py` — `create_risk()` and `update_risk()` now accept `subtype` and `ext_fields` parameters with dynamic Cypher SET/REMOVE clauses. `get_all_risks()` and `get_risk_by_id()` now return `subtype` and dynamically captured `ext_*` properties via `properties(r)`.
- `database/manager.py` — `RiskGraphManager.create_risk()` and `update_risk()` updated to pass through `subtype` and `ext_fields`.

**UI Layer:**

- `ui/tabs/risks_tab.py` — Risk creation form now includes a "Subtype" selectbox (filtered by selected level) and dynamically rendered extension fields. Risk list view shows subtype badge and domain fields in detail expander.
- `ui/home.py` — Statistics dashboard shows risk count breakdown by subtype when >1 distinct subtype exists.

**Import/Export:**

- `services/export_service.py` — Added `_clean_risk_df()` helper. Exported risk sheets now include `subtype` column and dynamic `ext_*` columns (all-null columns dropped).
- `services/import_service.py` — `_import_risks()` reads `subtype` and `ext_*` columns from Excel, passing them to `create_risk()`.

**Tests:**

- `tests/test_risk_subtypes.py` — 37 unit tests covering schema parsing, extension field types, `get_subtypes_for_level()`, serialization round-trip, and dataclass defaults.

**Engine Boundary:** Zero modifications to `services/exposure_calculator.py`, `services/influence_analysis.py`, or `services/mitigation_analysis.py`.

---

## [v2.10.9] - 2026-02-27

### F3 — Complexity Toggle (Simple vs. Advanced Mode)

**UX Simplification & Graph Filtering:**

- **UI Complexity Toggle:** Introduced a "Simple / Advanced" segmented toggle in the main sidebar. Tailored for non-technical stakeholders, the Simple mode drastically reduces UI clutter by hiding advanced tabs (Mitigations, Influences, Import/Export, Config, etc.) and defaulting to just Visualization and Risks.
- **Advanced Filters Ghosting:** In Simple mode, the extensive graph filters and layout presets are hidden behind a single "Show Advanced Filters" button. When exposed, all scoping and filtering functionality remains fully operational.
- **Graph Node & Edge Ghosting:** The visualization algorithm now natively supports a focal transparency mode. In Simple mode, only the Top 10 most exposed risk nodes (configurable) and all Top Program Objectives (TPOs) are rendered fully opaque. All other context nodes, minor risks, and their connecting edges are rendered with 10% opacity, providing orienting context without visual noise.
- **Configurable Simple Mode:** Added `SIMPLE_MODE_CONFIG` to `config/settings.py` allowing administrators to easily tweak which tabs are allowed, the number of top risks to display, and the exact ghosting opacity for the Simple Mode.

---

## [v2.10.8] - 2026-02-27

### F1 & F2 — Progressive UI Loading & Intelligent Caching

**Performance & UX Enhancements:**

- **F1: Progressive UI Loading**: Deployed pagination components across all core CRUD tables (Risks, Mitigations, TPOs, Influences, Custom Entities, Custom Relationships) in the UI. Large data schemas are now gracefully divided into manageable chunks, dramatically improving frontend rendering speeds and interaction snappiness during full graph investigations.
- **F2: Intelligent Structural Caching**: Integrated Streamlit's `@st.cache_data` caching engine profoundly into the backbone operations to eliminate redundant re-evaluation. 
  - **Graph Layouts**: Algorithmically intense network distributions (Sugiyama layered, specific clustering, categorical spread) are now strictly memoized.
  - **Influence Engine**: The computationally expensive BFS pathways processing (Critical paths, bottlenecks, clusters) are securely keyed to the *exact bound analysis scope context*. Cached evaluations strictly respect graph topology and selected scoped nodes to eliminate cross-contamination data leakage while boosting repeated visits dynamically.
  - **Mutation Observers**: All 18 unique Database generic & semantic data modifications dynamically call a cache invalidation trigger. Every created, modified, or severed edge ensures the cache operates firmly against truthful graph topologies.

---

## [v2.10.7] - 2026-02-27

### Bug Fixes
- **Analysis Scopes**: Fixed an internal `TypeError` where the old `scope_node_ids` parameter was being passed to the `get_influence_analysis` and `get_mitigation_analysis` functions, causing the Analysis visual tab to crash. These methods have now been correctly updated to expect and use the `active_scopes` list of config objects for dynamic subgraph rendering.

---
## [v2.10.6] - 2026-02-27

### U9 — Scope Completeness Enforcement

**Core Architecture & Engine Updates:**

- **Configuration:** Added `scope_type` to `AnalysisScopeConfig`, defaulted to `"scope"`, setting up for future SubGraph features.
- **Database queries:** Updated `get_statistics()` and `get_all_nodes_for_selection()` to accept and use `active_scopes`.
- **Advanced Graph Queries:** Overhauled `get_influence_analysis()` and `get_mitigation_analysis()` to compute sub-analysis boundaries entirely within the context of active scopes.

**UI/UX Enhancements:**

- **CRUD Forms:** Node creation now offers an internal "Add this new X to active scope(s)" option when boundaries apply. Deletion requests similarly split between "Remove from Scopes" vs global deletion.
- **Scope Filters:** All UI components relying on entity selectors (Explorer node pickers, relationship bindings) are bound dynamically to the current active scope.

---

## [v2.10.5] - 2026-02-27

### Exposure Calculation Visibility

**Verification & Trace Mechanics:**
- Implemented a "Calculation Trace" within the exposure engine that records step-by-step mathematical operations (base values, mitigation reductions, and influence limitations).
- Appended a list of string traces to `RiskExposureResult`.
- Updated the "Risk Exposure Analysis" dashboard in `ui/home.py` to display an expandable "View Calculation Trace" for every risk listed in the top exposures table, providing absolute transparency into the arithmetic behind the final scores.

---

## [v2.10.4] - 2026-02-27

### U8 — Relationship Semantic Types

**Core Architecture & Engine Updates:**

- **Semantic Routing Model**
  - Introduced `semantic` attribute to the `RelationshipTypeDefinition` schema object (`influence`, `context`, `cluster`).
  - Re-routed the `calculate_exposure()` exposure engine to exclusively process relationships designated as `semantic: influence`.
  - Defined defaults for kernel relationships: `INFLUENCES` and `MITIGATES` act as `semantic: influence`, while `IMPACTS_TPO` and custom edges default to `semantic: context`.
  - Updated graph analysis and export functions to dynamically query the registry for `semantic: influence` boundaries instead of hardcoding `INFLUENCES`.

**Files Modified:**
- `schemas/default/schema.yaml` — Explicitly added `semantic` assignments for built-in edge configurations.
- `core/relationship.py` — Added runtime support for mapping semantic configurations.
- `database/manager.py` — Refactored engine fetchers into the new `get_semantic_influences()` proxy to respect semantic limits on metrics, exports, and path logic.

---

## [v2.10.3] - 2026-02-26

### U7 — Computed Risk Level

**Core Features & Algorithmic Updates:**

- **Computed Risk Distance**
  - Replaced static use of `level` for graph hierarchical positioning with a dynamically computed distance.
  - Cypher query enhancements to compute shortest path (`INFLUENCES*0..10`) to the nearest TPO.
  - Distances are now calculated on-the-fly (`computed_distance`) during read operations.
  - Introduced `is_orphan` flag for risks with no path to any TPO.

**UI/UX Enhancements:**

- **Risk Management Tab Updates** (`ui/tabs/risks_tab.py`)
  - The Risk expansion headers now display `⚠️ Orphan` badges for disconnected risks.
  - Shows `[Dist N]` alongside risk names for contextual visibility of depth.
- **Hierarchical Layout Restructuring** (`ui/layouts.py`)
  - "Hierarchical (Sugiyama)" algorithm updated to position nodes across vertical layers `1..N` dynamically scaling down by `computed_distance` to TPOs.

**Files Modified:**
- `database/queries/risks.py` — Updated core read queries to include shortest path calculation.
- `database/queries/influences.py` — Updated network traversal queries (`get_downstream_risks`, `get_upstream_risks`) for consistent distance output.
- `ui/tabs/risks_tab.py` — Updated UI list expansion renderer.
- `ui/layouts.py` — Modified Semantic Layer evaluation within Sugiyama layout logic.

---

## [v2.10.0] - 2026-02-24

### U3 — Centralized State Management

**Refactoring:**

- **New `utils/state_manager.py` module** — single source of truth for all `st.session_state` key definitions, default values, and initialization
  - Five domain registries: `CONNECTION_DEFAULTS`, `CONNECTION_FORM_DEFAULTS`, `HOME_UI_DEFAULTS`, `CONFIG_PAGE_DEFAULTS`, `ANALYSIS_CACHE_DEFAULTS`
  - Domain-specific init functions: `init_connection_state()`, `init_home_state()`, `init_config_page_state()`, `init_analysis_cache_state()`, `init_all()`
  - Generic `init_defaults(dict)` initializer (set-if-absent semantics)
  - Thin `get()` / `set()` wrappers around `st.session_state` for future extensibility

- **Removed scattered state initialization** — three separate `init_*` functions and ad-hoc `if key not in st.session_state` checks consolidated
  - `utils/db_manager.py` — removed local `init_connection_state()`, re-exports from `state_manager`
  - `ui/home.py` — `init_session_state()` now delegates to `state_manager.init_home_state()`; ad-hoc `neo4j_uri`/`neo4j_user` init removed
  - `pages/1_⚙️_Configuration.py` — `init_session_state()` now delegates to `state_manager.init_config_page_state()`
  - `ui/panels/influence_panel.py` — ad-hoc cache init replaced with `init_analysis_cache_state()`
  - `ui/panels/mitigation_panel.py` — ad-hoc cache init replaced with `init_analysis_cache_state()`

- **`utils/__init__.py`** — added `state_manager` exports to public API

**Files Added:**
- `utils/state_manager.py` — Centralized state key registries and init functions
- `tests/test_state_manager.py` — 14 unit tests covering all init functions, get/set wrappers, and idempotency

**Files Modified:**
- `utils/db_manager.py` — Removed local `init_connection_state()`
- `utils/__init__.py` — Added state manager exports
- `ui/home.py` — Simplified `init_session_state()` + removed ad-hoc init
- `pages/1_⚙️_Configuration.py` — Simplified `init_session_state()`
- `ui/panels/influence_panel.py` — Uses `init_analysis_cache_state()`
- `ui/panels/mitigation_panel.py` — Uses `init_analysis_cache_state()`

---

## [v2.9.0] - 2026-02-23

### U1 & U2 — Externalize Static Content + Decouple Entry Point

**Major Refactoring:**

- **U1: Externalized Static Content**
  - Moved ~380 lines of hardcoded markdown from `app.py` into 7 standalone `.md` files under `docs/`
  - Help section content: `help_overview.md`, `help_scopes.md`, `help_exposure.md`, `help_influence.md`, `help_mitigations.md`, `help_layouts.md`
  - Welcome page content: `welcome.md`
  - Content loaded at runtime via new `utils/markdown_loader.py` helper with `@st.cache_data` caching
  - Graceful fallback if a documentation file is missing

- **U2: Decoupled Entry Point**
  - Extracted all 15 rendering functions from `app.py` into new `ui/home.py` module (~700 lines)
  - Slimmed `app.py` from **1,485 lines → ~60 lines** — now a thin orchestrator
  - `app.py` handles only: `st.set_page_config()`, style injection, session state init, header, connection sidebar, and delegation to `render_main_content()`
  - New `render_main_content()` function in `ui/home.py` encapsulates the entire connected-state body
  - All existing functionality preserved — no user-facing changes

**Files Added:**
- `docs/help_overview.md` — Help: Overview tab
- `docs/help_scopes.md` — Help: Scopes tab
- `docs/help_exposure.md` — Help: Exposure tab
- `docs/help_influence.md` — Help: Influence tab
- `docs/help_mitigations.md` — Help: Mitigations tab
- `docs/help_layouts.md` — Help: Layouts tab
- `docs/welcome.md` — Welcome page content
- `utils/markdown_loader.py` — Cached markdown file loader
- `ui/home.py` — All home page rendering functions
- `tests/test_markdown_loader.py` — Unit tests for docs loading

**Files Modified:**
- `app.py` — Slimmed from 1,485 → ~60 lines; all logic moved to `ui/home.py`
- `ui/__init__.py` — Added exports for `ui.home` module

---


## [v2.8.0] - 2026-02-20

### Unified Demo Dataset & Reset Button

**New Features:**

- **Unified TC01-TC07 Demo Dataset** (`demo_tc_dataset.cypher`)
  - Self-contained Cypher loader for 7 test cases (TC01–TC07) covering all major RIM scenario types
  - **37 risks**, **25 mitigations**, **18 influences**, **2 TPOs**, **3 TPO impacts**
  - Idempotent `MERGE`-based statements using UUID v5 deterministic IDs — safe to reload without creating duplicates
  - Entities prefixed `[TCxx]` to coexist with SNR demo data in the same database

- **Excel Demo Dataset** (`test_datasets/DEMO_Complete.xlsx`)
  - Excel equivalent of `demo_tc_dataset.cypher`, color-coded by test case
  - Use for Import/Export feature demonstrations

- **8 Pre-configured Analysis Scopes** (`schemas/default/schema.yaml`)
  - `snr_demo` — Full SNR nuclear program (RS-01–08, RO-01–07 + connected mitigations/TPOs via `include_connected_edges`)
  - `tc01_baseline` through `tc07_influence_strengths` — One scope per test case, each with pre-wired UUID `node_ids`
  - TC scopes use deterministic UUIDs matching `demo_tc_dataset.cypher` — no post-import update step required
  - Selecting all 8 scopes simultaneously yields the full combined graph

- **🔄 Reset Demo Data Button** (`pages/1_⚙️_Configuration.py` → Data Management tab)
  - One-click wipe + reload of the entire demo dataset to a reproducible state
  - Loads **both** `demo_data_loader_en.cypher` (SNR) and `demo_tc_dataset.cypher` (TC01-TC07) in sequence
  - File availability status shown before the button; button disabled if files are missing
  - Two separate progress bars (SNR then TC), each vanishing on completion
  - Before/after node count shown in success message
  - Automatically invalidates the Database tab's cached stats on completion

**Bug Fixes:**

- Fixed `TypeError: argument of type 'NoneType' is not iterable` crash on graph render when an `INFLUENCES` edge has a `null` `influence_type` property in Neo4j (`visualization/colors.py`, `visualization/edge_styles.py`, `ui/tabs/influences_tab.py`)

**Files Added:**
- `demo_tc_dataset.cypher` — TC01-TC07 idempotent Cypher loader (~49 KB)
- `test_datasets/DEMO_Complete.xlsx` — Color-coded Excel demo dataset

**Files Modified:**
- `schemas/default/schema.yaml` — Added 8 analysis scopes (snr_demo + tc01–tc07)
- `pages/1_⚙️_Configuration.py` — Added `render_demo_reset_section()` and `_execute_demo_reset()`, hoisted DB guard in `render_data_management()`
- `visualization/colors.py` — None-guard in `get_influence_color()`
- `visualization/edge_styles.py` — None-guard in `create_influence_edge_config()`
- `ui/tabs/influences_tab.py` — None-guard in `_render_influence_list()`

---

## [v2.7.0] - 2026-02-16


### Multi-page Application Structure

**Major Refactoring:**

- **Multi-page Architecture**
  - Converted single-page app to Streamlit multi-page structure
  - **Home**: `app.py` (Dashboard, Visualization, Analysis)
  - **Configuration**: `pages/1_⚙️_Configuration.py` (formerly `app_config.py`)
  - **Simulation**: `pages/2_🎲_Simulation.py` (formerly `calibration_simulator.py`)

- **Singleton Database Connection** (`utils/db_manager.py`)
  - Implemented `RiskGraphManager` as a singleton using `st.cache_resource`
  - Database connection persisted across page navigation
  - Sidebar connection panel synchronized across all pages

- **UX/UI Improvements**
  - Streamlines navigation via sidebar
  - Cleaner interface with separated concerns (Config vs Analysis vs Simulation)

**Files Added:**
- `pages/1_⚙️_Configuration.py`
- `pages/2_🎲_Simulation.py`
- `utils/db_manager.py`
- `tests/test_db_connection_pooling.py`

**Files Modified:**
- `app.py` — Refactored to remove Config/Sim logic, integrated db_manager
- `README.md` — Updated navigation instructions
- `docs/` — Updated to reflect new structure

---

## [v2.6.1] - 2026-02-14

### Scope Improvements

**New Features:**

- **Smart Scope Filtering** (`database/queries/analysis.py`)
  - Scoped graph automatically includes mitigations and TPOs connected to in-scope risks
  - Optional 1-hop risk neighbor expansion via "Show connected neighbors" toggle
  - Edges filtered to only include those between the expanded node set

- **Scoped CRUD Tabs** (`app.py`)
  - Risks, TPOs, Mitigations, and Influences tabs now show only entities within the active scope
  - Scope expansion includes connected mitigations, TPOs, and optional risk neighbors

- **Scoped Analysis** (`database/manager.py`)
  - `get_influence_analysis(scope_node_ids=...)` pre-filters risks, influences, and TPO impacts
  - `get_mitigation_analysis(scope_node_ids=...)` pre-filters risks, mitigations, and mitigates relationships
  - Internal cross-reference calls also pass scope for consistent results

- **Scoped Statistics Dashboard** (`app.py`)
  - `_compute_stats_from_graph()` computes statistics from filtered graph data when scope is active
  - Correctly counts risk levels, origins, TPOs, mitigations, and edge types

- **Scope-Limited Influence Explorer** (`app.py`)
  - Node selector dropdown filtered to only show nodes within the active scope

- **Exposure with Neighbor Expansion** (`database/manager.py`)
  - `calculate_exposure(scope_node_ids=..., include_neighbors=...)` optionally includes 1-hop risk neighbors
  - Mitigations found via MITIGATES relationships (not by scope ID membership)

**Bug Fixes:**

- Fixed statistics dashboard showing 0 for all counts (wrong field names: `type`/`label` → `node_type`/`edge_type`)
- Fixed Business/Operational risk counts at 0 (comparing schema IDs vs DB labels)
- Fixed exposure calculation ignoring mitigations when scope active (mitigations filtered by scope set which only contains risk IDs)
- Fixed CRUD tabs showing "No renderer for tab" errors (missing tab renderers)

**Files Modified:**
- `app.py` — CRUD tab scoping, stats fix, influence explorer scoping, neighbor toggle, exposure neighbor pass-through
- `database/queries/analysis.py` — Smart scope expansion in `get_graph_data()`
- `database/manager.py` — `scope_node_ids` on `get_influence_analysis()`, `get_mitigation_analysis()`, `calculate_exposure()` mitigation fix
- `ui/filters.py` — `scope_include_neighbors` passthrough

---

## [v2.6.0] - 2026-02-14

### Analysis Scopes

**New Features:**

- **Scope Data Model** (`config/schema_loader.py`)
  - `AnalysisScopeConfig` dataclass: `id`, `name`, `description`, `node_ids`, `include_connected_edges`, `show_boundary_edges`, `color`
  - Scopes stored in `schema.yaml` under `scopes` key — portable, versionable, shareable
  - Full round-trip YAML parsing and serialization via `_parse_scopes()` / `_scope_to_dict()`

- **Scope CRUD Tab** (`app_config.py`)
  - New "📐 Scopes" tab in Configuration Manager
  - Create scopes with node picker (live from Neo4j) or manual UUID entry
  - Edit name, description, color; delete scopes
  - Changes persisted to `schema.yaml`

- **Scope Selector** (`app.py`)
  - Sidebar "📐 Analysis Scopes" expander with multi-select
  - Multiple scopes create a union of node IDs
  - Scope indicator badge showing active scope names and node count
  - "🌐 Full Graph" button to clear scope selection

- **Scoped Filtering** (`ui/filters.py`)
  - `FilterManager` methods: `set_active_scopes()`, `clear_scopes()`, `get_scope_node_ids()`, `add_node_to_scope()`, `remove_node_from_scope()`
  - `scope_node_ids` included in `get_filters_for_query()` output

- **Scoped Graph Data** (`database/queries/analysis.py`)
  - `get_graph_data()` post-filters nodes and edges to scope boundary
  - Only edges with both endpoints in scope are included

- **Scoped Exposure Calculation** (`database/manager.py`)
  - `calculate_exposure(scope_node_ids=...)` pre-filters risks, influences, mitigations, and mitigates relationships
  - Exposure dashboard passes active scope automatically

- **Test Suite** (`tests/test_scopes.py`)
  - 26 unit tests across 6 classes
  - Covers: dataclass, schema parsing, FilterManager, graph data filtering, exposure scoping

**Files Added:**
- `tests/test_scopes.py` (~400 lines)

**Files Modified:**
- `config/schema_loader.py` — Added `AnalysisScopeConfig`, parsing, serialization
- `schemas/default/schema.yaml` — Added `scopes: []` placeholder
- `ui/filters.py` — Added scope management methods
- `database/queries/analysis.py` — Scope filtering in `get_graph_data()`
- `database/manager.py` — `scope_node_ids` parameter in `calculate_exposure()`
- `app.py` — Scope selector sidebar, scoped exposure, scope indicator
- `app_config.py` — "📐 Scopes" CRUD tab

---

## [v2.5.2] - 2026-02-12

### Bug Fixes

- **Filters**: Reorganized into Core (Risks, Mitigations, Influences, Mitigates) and TPO & Related sections
- **Node spacing**: Doubled physics spring length for better readability
- **Node tooltips**: Now show name, level, origin, category, exposure
- **Edge tooltips**: Now show level and strength
- **CRUD tabs**: Fixed "No renderer" error by adding `entity_type`/`relationship_type` to schema tab configs
- **Analysis tab**: Registered renderer; moved panels out of Visualization tab to avoid duplicate keys
- **Import/Export tab**: Fixed routing in `_determine_tab_type`
- **Statistics dashboard**: Added missing Total Risks metric
- **UI**: Removed duplicate horizontal divider

**Files Modified:** `app.py`, `schemas/default/schema.yaml`, `ui/dynamic_tabs.py`, `visualization/graph_options.py`, `visualization/node_styles.py`, `visualization/edge_styles.py`

---

## [v2.5.1] - 2026-02-05

### Terminology Update: Strategic → Business Risks

**Breaking Change:**

- **Risk Level Rename**: "Strategic" risks are now called "Business" risks
  - Better reflects consequence-oriented nature of these risks
  - Aligns with program management terminology
  - Requires Neo4j data migration for existing databases

**Changes:**

- **Database Layer**
  - `database/queries/tpos.py`: TPO impact validation now accepts "Business" level
  - `database/queries/influences.py`: Influence type detection uses Business level
    - `Level1_Op_to_Strat` → `Level1_Op_to_Bus`
    - `Level2_Strat_to_Strat` → `Level2_Bus_to_Bus`
  - `database/queries/analysis.py`: Statistics queries updated
  - `database/manager.py`: All level comparisons updated

- **Visualization Layer**
  - `visualization/colors.py`: Color dictionary keys updated
  - `visualization/node_styles.py`: Shape and style lookups updated
  - `visualization/edge_styles.py`: Added legacy Strat→Bus tooltip transformation

- **Models Layer**
  - `models/enums.py`: `RiskLevel.STRATEGIC` → `RiskLevel.BUSINESS`
  - `models/enums.py`: `InfluenceType` enum values updated
  - `models/risk.py`: `is_strategic` → `is_business` property

- **UI Layer**
  - `ui/panels/influence_panel.py`: Level display and icons
  - `ui/panels/mitigation_panel.py`: Gap analysis terminology
  - `ui/layouts.py`: Layered layout level detection
  - `app.py`: Statistics display and help text

- **Schema Updates**
  - `schemas/default/schema.yaml`: Risk level id/label updated
  - Filter presets: `strategic_focus` → `business_focus`
  - Influence types in schema updated

- **Documentation**
  - README.md, METHODOLOGY.md, VISUAL_DESIGN.md, USER_GUIDE.md updated

**Migration Required:**

```cypher
-- Update risk levels
MATCH (r:Risk {level: "Strategic"})
SET r.level = "Business"
RETURN count(r);

-- Update influence types
MATCH ()-[r:INFLUENCES]->()
WHERE r.influence_type CONTAINS "Strat"
SET r.influence_type = REPLACE(
  REPLACE(r.influence_type, "Strat_to_Strat", "Bus_to_Bus"),
  "Op_to_Strat", "Op_to_Bus"
)
RETURN count(r);
```

---

## [v2.5.0] - 2026-02-03

### Schema Extension: Custom Entities & Relationships

**New Features:**

- **Custom Entity Types** (`config/schema_loader.py`)
  - Define user-created node types (e.g., Asset, Threat Actor)
  - Visual properties: color, shape, emoji, size
  - Custom attributes per entity type
  - Full graph visualization integration

- **Custom Relationship Types**
  - Define connections between any entities (core or custom)
  - Source/target entity specification
  - Visual properties: color, line style, bidirectional flag
  - Custom attributes per relationship type

- **Custom Attributes for Core Entities**
  - Add custom attributes to Risk, TPO, and Mitigation entities
  - Supports string, int, float, boolean, date types

- **Configuration Manager Enhancements** (`app_config.py`)
  - New "📦 Custom Entities" tab with add/edit/delete operations
  - New "🔀 Custom Relationships" tab with entity type dropdowns
  - Attribute management within entity/relationship editors

- **Test Data Generator Updates**
  - Generates instances of custom entity types
  - Creates custom relationships with random attribute values
  - Type-appropriate value generation (int/float/boolean/string)

- **Example: IT Security Schema**
  - Custom entities: Asset (🖥️), Threat Actor (👤)
  - Custom relationships: TARGETS, PROTECTS, EXPLOITS

**Files Modified:**
- `config/schema_loader.py` (+400 lines) - Added CustomEntityConfig, CustomRelationshipConfig dataclasses
- `app_config.py` (+350 lines) - Added custom entity/relationship UI editors
- `schemas/it_security/schema.yaml` - Added example custom types

**Bug Fixes:**
- Fixed sidebar legend HTML rendering issue (raw tags displayed instead of styled content)

---

## [v2.4.0] - 2026-02-03

### Configuration Manager & Schema System


**New Features:**

- **YAML Schema System** (`config/schema_loader.py`)
  - Typed dataclasses for all configuration elements (20+ classes)
  - YAML parsing with validation
  - Backward-compatible property helpers for existing code
  - Save/load/duplicate schema operations
  - Schema validation with detailed error messages

- **Configuration Manager App** (`app_config.py`)
  - Standalone Streamlit application for schema management
  - Four main tabs: Schema Management, Database, Data Management, Health Check
  - Form-based editors for all configuration elements
  - Color pickers, sliders, live previews
  - YAML preview with edit mode and validation

- **Schema Management Tab**
  - Six sub-tabs for comprehensive editing
  - Risk levels editor (color, shape, emoji, size)
  - Categories, statuses, origins editors
  - TPO clusters with color configuration
  - Mitigation types and statuses
  - Influence strengths with value sliders
  - Effectiveness and impact level editors
  - Create/duplicate/delete schema operations

- **Database Tab**
  - Database statistics dashboard
  - Schema-to-database compatibility checker
  - Migration detection with Cypher script generation
  - Node and relationship counts by type

- **Data Management Tab**
  - Clear database with confirmation
  - Demo data loader
  - JSON backup/restore functionality

- **Health Check Tab**
  - Schema validation status
  - Database connection checker
  - Data integrity checks (orphans, invalid values)
  - Comprehensive health report generation

- **Example Schemas**
  - `schemas/default/` - SMR nuclear project (Business/Operational)
  - `schemas/it_security/` - Cybersecurity example (Enterprise/Tactical, CIA-based TPOs)

**Files Added:**
- `app_config.py` (~1,500 lines)
- `config/schema_loader.py` (~700 lines)
- `schemas/default/schema.yaml` (~300 lines)
- `schemas/it_security/schema.yaml` (~320 lines)
- `docs/CONFIGURATION_MANAGER.md` - Dedicated app documentation
- `docs/CALIBRATION_SIMULATOR.md` - Dedicated calibration app documentation

**Files Modified:**
- `config/settings.py` - Dynamic schema loading with `.rim_schema` file and `RIM_SCHEMA` env var support
- `config/__init__.py` - Added schema loader exports and new config items
- `ui/legend.py` - Dynamic legend generation from active schema

**Schema Selection:**
- Set active schema via `.rim_schema` file in project root
- Or use `RIM_SCHEMA` environment variable
- Configuration Manager has "Set as Default for Main App" button
- App restart required after schema changes

---

## [v2.3.0] - 2026-02-02

### Test Suite Implementation

**New Features:**

- **Comprehensive Test Infrastructure**
  - Added pytest and pytest-cov to dependencies
  - Created `pytest.ini` configuration
  - Created `tests/conftest.py` with shared fixtures and sample data

- **Model Unit Tests** (100% coverage)
  - `test_enums.py`: Tests for all enum classes (RiskLevel, RiskStatus, etc.)
  - `test_risk.py`: Tests for Risk dataclass creation, properties, serialization
  - `test_mitigation.py`: Tests for Mitigation dataclass
  - `test_tpo.py`: Tests for TPO dataclass
  - `test_relationships.py`: Tests for Influence, TPOImpact, MitigatesRelationship

- **Utility Unit Tests** (100% coverage)
  - `test_helpers.py`: Tests for all helper functions (format_percentage, wrap_text, etc.)

- **Service Unit Tests** (Partial coverage)
  - `test_exposure_calculator.py`: Tests for ExposureCalculator and data classes
  - `test_influence_analysis.py`: Tests for InfluenceAnalyzer and results
  - `test_mitigation_analysis.py`: Tests for MitigationAnalyzer coverage analysis

**Files Added:**
- `pytest.ini` (8 lines)
- `tests/conftest.py` (262 lines)
- `tests/test_enums.py` (264 lines)
- `tests/test_risk.py` (347 lines)
- `tests/test_mitigation.py` (318 lines)
- `tests/test_tpo.py` (296 lines)
- `tests/test_relationships.py` (404 lines)
- `tests/test_helpers.py` (364 lines)
- `tests/test_exposure_calculator.py` (329 lines)
- `tests/test_influence_analysis.py` (290 lines)
- `tests/test_mitigation_analysis.py` (385 lines)

**Dependencies Added:**
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0`

---

## [v2.2.0] - 2026-02-01

### Exposure Calculation & Hierarchical Layout

**New Features:**

- **Exposure Calculation Engine** (`services/exposure_calculator.py`)
  - Quantitative risk scoring with influence limitation model
  - Base exposure = Likelihood × Impact (0-100 scale)
  - Multiplicative mitigation factor with diminishing returns
  - Influence limitation: upstream risks limit downstream mitigation effectiveness
  - Three global metrics: Residual Risk %, Weighted Risk Score, Max Single Exposure
  - Health status indicator with color coding (Excellent → Critical)
  - Detailed per-risk breakdown with reduction percentages
  - On-demand calculation via button (not real-time for performance)

- **Hierarchical Layout (Sugiyama Algorithm)** (`ui/layouts.py`)
  - Edge-crossing minimization using barycenter heuristic
  - Respects RIM semantic hierarchy (TPO → Business → Operational)
  - Connected nodes vertically aligned for readability
  - Mitigations positioned alongside target risks
  - Available as "🌳 Hierarchical" in predefined layouts

- **Help & Documentation Section** (`app.py`)
  - In-app help accessible from sidebar
  - Topic-based navigation (Overview, Exposure, Influence, Mitigations, Layouts)
  - Detailed exposure calculation methodology with formulas
  - Influence model explanation
  - Mitigation effectiveness guide
  - Layout algorithms description

- **Monte Carlo Calibration Simulator** (`calibration_simulator.py`)
  - Standalone Streamlit app for exposure model validation
  - Two simulation modes:
    - Monte Carlo: Random scenario generation
    - Mitigation Path: Progressive mitigation addition
  - Rich visualizations: distributions, scatter clouds, heatmaps, 3D plots
  - Sensitivity analysis for model parameters
  - CSV export of simulation results

**UI Enhancements:**

- New "⚡ Risk Exposure Analysis" dashboard section
- Calculate Exposure button with cached results
- Detailed exposure breakdown in expandable panel
- "❓ Help & Documentation" section in sidebar

**Files Added:**
- `services/exposure_calculator.py` (565 lines)
- `calibration_simulator.py` (1,103 lines)

---

## [v2.1.0] - 2026-01-30

### Enhanced Visualization & Semantic Design

**New Features:**

- **Semantic Shape System** (`visualization/node_styles.py`)
  - ◆ Diamonds for Business Risks (pointed = danger)
  - ● Circles for Operational Risks (foundation)
  - 🛡️ Rounded boxes for Mitigations (shield-like)
  - ⬡ Hexagons for TPOs (structural)
  - Instant visual recognition without reading labels

- **Enhanced Color Palette** (`visualization/colors.py`)
  - Exposure heat map gradient (yellow → dark red)
  - Semantic color families (warm = danger, cool = protection)
  - Mitigation type color coding (Dedicated/Inherited/Baseline)
  - Legacy risk gray border indicator

- **Edge Differentiation** (`visualization/edge_styles.py`)
  - → Standard arrows for influence relationships
  - ⊣ Bar-end arrows for mitigations ("blocking" metaphor)
  - ▷ Vee arrows for TPO impacts ("targeting" metaphor)
  - Thickness encodes strength/effectiveness

- **Border Style Encoding**
  - Solid = Active/Implemented
  - Dashed = Contingent/Proposed
  - Dotted = Archived/Deferred
  - Thick gray = Legacy risk

**UI Enhancements:**

- [L] prefix for legacy risks in labels
- 🛡️ emoji for mitigation labels
- Size variation by exposure level
- Improved legend with visual samples

---

## [v2.0.0] - 2026-01-15

### Modular Architecture Refactoring

**Breaking Changes:**

- Main entry point changed from `app_alpha.py` to `app.py`
- Package-based import structure

**Major Changes:**

- Refactored from monolithic `app_alpha.py` (6,521 lines) to modular architecture
- 100% functional equivalence maintained - no user-facing changes
- Improved code organization, maintainability, and testability

**New Package Structure:**

```
rim/
├── app.py                    # Main entry (823 → 1,193 lines)
├── config/                   # Application settings
├── database/                 # Neo4j operations
│   └── queries/              # Cypher query modules
├── models/                   # Data models and enums
├── services/                 # Business logic
├── ui/                       # Streamlit components
│   ├── panels/               # Analysis panels
│   └── tabs/                 # Tab renderers
├── visualization/            # Graph rendering
└── utils/                    # Helper functions
```

**Architecture Improvements:**

- `RiskGraphManager` as unified database facade
- Separated Cypher queries into dedicated modules:
  - `risks.py`, `tpos.py`, `influences.py`, `mitigations.py`, `analysis.py`
- `InfluenceAnalyzer` class for network analysis
- `ExcelImporter` class for structured imports
- `FilterManager` with validation and summary

**Files:**

- Legacy file `app_alpha.py` deprecated (kept for reference)

---

## [v1.5.0] - 2026-01-10

### Influence & Mitigation Analysis Panels

**New Features:**

- **Influence Analysis Panel**
  - 🎯 Top Propagators: Risks with highest downstream impact
  - ⚠️ Convergence Points: Nodes receiving multiple influences
  - 🔥 Critical Paths: Strongest chains to TPOs
  - 🚧 Bottlenecks: Single points of failure
  - 📦 Risk Clusters: Tightly interconnected groups

- **Mitigation Analysis Panel**
  - 🎯 Risk Treatment Explorer: Coverage per risk
  - 🛡️ Mitigation Impact Explorer: Risks per mitigation
  - 📊 Coverage Gap Analysis: Unmitigated risks flagged

- **Interactive Exploration**
  - "Explore in Graph" buttons
  - Neighborhood highlighting
  - Cross-reference with influence analysis

**UI Enhancements:**

- Edge visibility slider for progressive disclosure
- Analysis results cached in session state

---

## [v1.4.0] - 2025-12-28

### Mitigation Management

**New Features:**

- **Mitigation Entity Type**
  - Reference, name, description
  - Type: Dedicated, Inherited, Baseline
  - Status: Implemented, In Progress, Proposed, Deferred
  - Source entity tracking

- **Mitigates Relationship**
  - Many-to-many: One mitigation can address multiple risks
  - Effectiveness scoring (Low/Medium/High/Critical)
  - Link description

- **Mitigations Tab**
  - Create, edit, delete mitigations
  - View all mitigations with status

- **Risk Mitigations Tab**
  - Assign mitigations to risks
  - Set effectiveness per link
  - View coverage matrix

**Visualization:**

- Mitigation nodes with shield styling
- Green bar-end arrows for mitigates edges
- Mitigation filters (by type, status)
- "Risks + Mitigations" filter preset

---

## [v1.3.0] - 2025-12-20

### Filter System & Presets

**New Features:**

- **Collapsible Filter Sections**
  - ⚡ Quick Presets
  - 🎯 Risk Filters
  - 🏆 TPO Filters
  - 🎨 Display Options
  - 🔍 Influence Explorer
  - ⚙️ Graph Options
  - 💾 Layout Management

- **Quick Filter Presets**
  - 🌐 Full View
  - 🟣 Business Focus
  - 🔵 Operational Focus
  - ✅ Active Risks Only
  - ⚠️ Contingent Risks
  - 🎯 Risks Only
  - 🆕 New Risks Only
  - 📜 Legacy Risks Only

- **All/None Buttons**
  - Quick selection for multi-select filters

- **Filter Validation**
  - Summary display of active filters
  - Warning for empty results

---

## [v1.2.0] - 2025-12-15

### Risk Origin & Contingent Risks

**New Features:**

- **Risk Origin**
  - New: Program-specific risks
  - Legacy: Inherited from enterprise/other programs
  - Visual indicator (gray border, [L] prefix)

- **Contingent Risks**
  - Is Contingent flag
  - Activation condition field
  - Decision date field
  - Dashed diamond visualization

- **Origin Filter**
  - Filter by New/Legacy
  - Quick presets for each

---

## [v1.1.0] - 2025-12-10

### TPO Integration

**New Features:**

- **Top Program Objectives (TPO)**
  - Reference, name, cluster
  - Cluster categories: Product, Business, Industrial, Sustainability, Safety

- **TPO Impact Relationship**
  - Link business risks to TPOs
  - Impact level (Low/Medium/High/Critical)

- **Visualization**
  - Gold hexagon nodes for TPOs
  - Orange dash-dot edges for impacts
  - TPO cluster layout option

---

## [v1.0.0] - 2025-12-01

### Initial Release

**Core Features:**

- **Risk Management**
  - Two-level architecture (Business/Operational)
  - Four categories (Programme/Produit/Industriel/Supply Chain)
  - Likelihood × Impact scoring
  - Active/Archived status

- **Influence Mapping**
  - Three influence levels (L1: Op→Bus, L2: Bus→Bus, L3: Op→Op)
  - Strength and confidence scoring
  - Description field

- **Visualization**
  - PyVis interactive graph
  - Color coding by level
  - Multiple layout options (Layered, Category)
  - Physics toggle
  - Manual layout save/load

- **Import/Export**
  - Excel export with all entities
  - Excel import with name matching
  - Import logging

- **User Interface**
  - Streamlit-based UI
  - Tab navigation
  - Sidebar filters
  - Statistics dashboard

---

## Migration Notes

### v1.x → v2.0.0

1. Entry point changed: Run `streamlit run app.py` instead of `app_alpha.py`
2. Imports changed: If you have custom code, update imports to new package structure
3. No data migration needed: Neo4j schema unchanged

### v2.0.0 → v2.1.0

1. Node shapes changed: Diamond for business, circle for operational
2. Edge arrows changed: Bar-end for mitigations, vee for TPO impacts
3. No data migration needed

### v2.1.0 → v2.2.0

1. New exposure calculation: Run "Calculate Exposure" to use new feature
2. New layout option: "Hierarchical" added to layout dropdown
3. No data migration needed

---

*For questions or issues, please open a GitHub issue.*
