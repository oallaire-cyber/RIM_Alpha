# 🏗️ RIM Architecture

Technical documentation for developers working on the Risk Influence Map application.

---

## Overview

RIM follows a **modular architecture** with clear separation of concerns:


```
┌─────────────────────────────────────────────────────────────┐
│                         app.py                               │
│          (Thin entry point → delegates to ui/home.py)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌───────────┬───────────┬───────────┬───────────┬───────────┐
    ▼           ▼           ▼           ▼           ▼           ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────────┐
│1_Config  ││2_Data    ││2_Sim     ││3_What-If ││4_Mit     ││  (app.py /   │
│(Config)  ││Management││(Simulator││Analysis  ││Exposure  ││  ui/home.py) │
└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└──────────────┘
     │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    utils/db_manager.py                       │
│               (Shared Singleton Connection)                  │
└─────────────────────┬───────────────────────────────────────┘

                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ config/ │  │ database/│  │ services/│  │   ui/    │
   │ Settings│  │ Neo4j    │  │ Business │  │ Streamlit│
   │         │  │ Queries  │  │ Logic    │  │ Components│
   └─────────┘  └──────────┘  └──────────┘  └──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             ┌──────────────┐    ┌──────────┐
             │visualization/│    │  models/ │
             │ Graph Render │    │ Data     │
             │ Node/Edge    │    │ Classes  │
             │ Styles       │    │ Enums    │
             └──────────────┘    └──────────┘
```

---

## Package Structure

### `/config` - Application Settings

```
config/
├── __init__.py      # Exports all settings
├── settings.py      # Constants and configuration
└── schema_loader.py # YAML schema system (SchemaConfig, AnalysisScopeConfig, RiskSubtypeConfig, etc.)
```

### `/utils` — Centralised Utilities

```
utils/
├── __init__.py        # Re-exports helpers + state manager
├── state_manager.py   # Centralized st.session_state key registries & init
├── db_manager.py      # Shared singleton connection (st.cache_resource)
├── helpers.py         # Formatting helpers
└── markdown_loader.py # Cached docs/*.md file loader
```

**Key exports**:
- `APP_TITLE`, `APP_ICON`, `LAYOUT_MODE`
- `NEO4J_DEFAULT_URI`, `NEO4J_DEFAULT_USER`
- `RISK_LEVELS`, `RISK_CATEGORIES`, `TPO_CLUSTERS`
- Color definitions, status options

### `/database` - Data Access Layer

```
database/
├── __init__.py      # Exports RiskGraphManager
├── connection.py    # Neo4j driver management
├── manager.py       # Facade for all DB operations
└── queries/
    ├── __init__.py
    ├── risks.py      # Risk CRUD operations
    ├── tpos.py       # TPO CRUD operations
    ├── influences.py # Influence relationships
    ├── mitigations.py # Mitigation CRUD
    └── analysis.py   # Analytical queries
```

**Key classes**:

```python
class RiskGraphManager:
    """Facade for all database operations."""
    
    def __init__(self, uri, user, password):
        self.driver = Neo4jConnection(uri, user, password)
    
    # Risk operations
    def create_risk(self, **kwargs) -> str
    def get_risk(self, reference: str) -> dict
    def get_all_risks(self) -> List[dict]
    def update_risk(self, reference: str, **kwargs) -> bool
    def delete_risk(self, reference: str) -> bool
    
    # Influence operations
    def create_influence(self, source_ref, target_ref, **kwargs)
    def get_all_influences(self) -> List[dict]
    def get_semantic_influences(self) -> List[dict]
    
    # Mitigation operations
    def create_mitigation(self, **kwargs) -> str
    def create_mitigates_relationship(self, mit_ref, risk_ref, **kwargs)
    
    # Generic Entity operations
    def create_unified_entity(self, type_id: str, id: str, ...)
    def create_unified_relationship(self, type_id: str, id: str, ...)
    
    # Analysis
    def get_graph_for_visualization(self) -> Tuple[nodes, edges]
    def calculate_exposure(self, scope_node_ids=None) -> dict
```

**Schema Dataclass Hierarchy** (`schema_loader.py`):

```python
@dataclass
class AnalysisScopeConfig:
    id: str                             # Machine-readable identifier
    name: str                           # Display name
    description: str = ""               # Purpose of the scope
    node_ids: List[str] = field(...)     # UUIDs of nodes in scope
    include_connected_edges: bool = True # Auto-include edges between scope nodes
    show_boundary_edges: bool = False    # Show edges crossing scope boundary
    color: str = "#808080"              # Scope color for visualization

@dataclass
class SchemaConfig:
    # ... other fields ...
    scopes: List[AnalysisScopeConfig]    # Zero or more scope definitions
```

### `/models` - Data Models

```
models/
├── __init__.py      # Exports all models
├── enums.py         # Enumeration types
├── risk.py          # Risk data class
├── tpo.py           # TPO data class
├── mitigation.py    # Mitigation data class
└── relationships.py # Relationship data classes
```

**Enumerations** (`enums.py`):

```python
class RiskLevel(Enum):
    BUSINESS = "Business"
    OPERATIONAL = "Operational"

class RiskCategory(Enum):
    PROGRAMME = "Programme"
    PRODUIT = "Produit"
    INDUSTRIEL = "Industriel"
    SUPPLY_CHAIN = "Supply Chain"

class RiskOrigin(Enum):
    NEW = "New"
    LEGACY = "Legacy"

class MitigationType(Enum):
    DEDICATED = "Dedicated"
    INHERITED = "Inherited"
    BASELINE = "Baseline"

class MitigationStatus(Enum):
    IMPLEMENTED = "Implemented"
    IN_PROGRESS = "In Progress"
    PROPOSED = "Proposed"
    DEFERRED = "Deferred"

class Effectiveness(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
```

### `/services` - Business Logic

```
services/
├── __init__.py
├── exposure_calculator.py      # Quantitative exposure scoring (EL, TRI, quadrant)
├── influence_analysis.py       # Network analysis algorithms
├── mitigation_analysis.py      # Coverage and gap analysis
├── trigger_engine.py           # Lifecycle trigger review (U12)
├── auto_acceptance_engine.py   # Auto-acceptance with severity ceiling + quadrant guards (U12)
├── archive_engine.py           # Archive alert generation (U12)
├── import_service.py           # Excel import logic
└── export_service.py           # Excel export logic
```

**Exposure Calculator** (`exposure_calculator.py`):

```python
# Configuration constants
EFFECTIVENESS_SCORES = {
    "Critical": 0.9,
    "High": 0.7,
    "Medium": 0.5,
    "Low": 0.3
}

INFLUENCE_STRENGTH_SCORES = {
    "Critical": 1.0,
    "Strong": 0.75,
    "Moderate": 0.5,
    "Weak": 0.25
}

def calculate_exposure(risks, influences, mitigations, mitigates_rels) -> ExposureResult:
    """
    Calculate exposure for all risks.
    
    Returns:
        ExposureResult with:
        - residual_risk_percent: float
        - weighted_risk_score: float
        - max_single_exposure: float
        - risk_exposures: List[RiskExposure]
    """
```

**Influence Analysis** (`influence_analysis.py`):

```python
class InfluenceAnalyzer:
    """Analyze influence network for insights."""
    
    def get_top_propagators(self, limit=10) -> List[dict]
    def get_convergence_points(self, limit=10) -> List[dict]
    def get_critical_paths(self, limit=5) -> List[dict]
    def get_bottlenecks(self, limit=10) -> List[dict]
    def get_risk_clusters(self) -> List[List[str]]
```

### `/ui` - User Interface

```
ui/
├── __init__.py       # Exports components
├── home.py           # Home page rendering (dashboard, viz, analysis)
├── components.py     # Reusable UI components
├── dynamic_tabs.py   # Schema-driven tab rendering
├── dynamic_forms.py  # Schema-driven form builder
├── filters.py        # FilterManager class
├── layouts.py        # Layout generators + LayoutManager
├── legend.py         # Graph legend rendering
├── sidebar.py        # Sidebar sections
├── styles.py         # CSS injection
├── panels/
│   ├── __init__.py
│   ├── influence_panel.py    # Influence analysis UI
│   ├── mitigation_panel.py   # Mitigation analysis UI
│   └── graph_visual_panel.py # F32 — consolidated visual behaviour settings
└── tabs/
    ├── __init__.py
    ├── unified_crud_tab.py  # Generic data grids/forms for any entity
    ├── risk_mitigations_tab.py # Specialized drag-and-drop links
    └── import_export_tab.py # Excel export/import logic
```

**Home Page** (`home.py`):

Contains all dashboard/visualization/analysis rendering functions extracted
from the monolithic `app.py` (v2.9.0). Key functions:

```python
# Session state
def init_session_state()              # Home-specific state

# Sidebar
def render_connection_sidebar()       # Neo4j connection panel
def render_help_section()             # Loads docs/*.md via markdown_loader
def render_scope_selector()           # Analysis scope picker

# Dashboard
def render_welcome_page()             # Loads docs/welcome.md
def render_statistics_dashboard()     # Scoped statistics
def render_exposure_dashboard()       # Exposure calculation

# Visualization
def render_visualization_tab()        # Graph + filters + explorer + layouts
def render_visualization_filters()    # Filter sidebar
def render_influence_explorer()       # Node traversal
def render_graph_options()            # Physics, edge visibility, capture
def render_layout_management()        # Save/load/preset layouts

# Orchestrator
def render_main_content(manager)      # Wires everything together
```

**FilterManager** (`filters.py`):

```python
class FilterManager:
    """Manage filter state and application."""
    
    def __init__(self, session_state):
        self.state = session_state
        self.active_scopes = []          # List[AnalysisScopeConfig]
    
    def apply_preset(self, preset_name: str)
    def get_filter_summary(self) -> str
    def filter_nodes(self, nodes: List) -> List
    def filter_edges(self, edges: List) -> List
    
    # Scope management
    def set_active_scopes(self, scopes: List)
    def clear_scopes(self)
    def get_scope_node_ids(self) -> Optional[Set[str]]
    def add_node_to_scope(self, scope_id: str, node_id: str)
    def remove_node_from_scope(self, scope_id: str, node_id: str)
```

**LayoutManager** (`layouts.py`):

```python
class LayoutManager:
    """Manage saved layouts."""
    
    def save_layout(self, name: str, positions: dict)
    def load_layout(self, name: str) -> dict
    def list_layouts(self) -> List[str]
    def delete_layout(self, name: str)

# Layout generators
def generate_hierarchical_layout(nodes, edges) -> dict  # Sugiyama algorithm
def generate_layered_layout(nodes) -> dict
def generate_category_layout(nodes) -> dict
def generate_tpo_cluster_layout(nodes, edges) -> dict
```

### `/visualization` - Graph Rendering

```
visualization/
├── __init__.py        # Exports render functions
├── colors.py          # Color palette and gradients
├── node_styles.py     # Node shape/color functions
├── edge_styles.py     # Edge style functions
├── graph_options.py   # PyVis configuration
└── graph_renderer.py  # Main rendering logic
```

**Node Styles** (`node_styles.py`):

```python
# Shape mapping
RISK_SHAPES = {
    "business": "diamond",    # ◆ Pointed = danger
    "operational": "dot",      # ● Circle = foundation
}
MITIGATION_SHAPE = "box"       # 🛡️ Rounded = shield
TPO_SHAPE = "hexagon"          # ⬡ Goal

def style_risk_node(risk: dict, color_mode: str) -> dict:
    """Generate PyVis node options for a risk."""

def style_mitigation_node(mitigation: dict) -> dict:
    """Generate PyVis node options for a mitigation."""

def style_tpo_node(tpo: dict) -> dict:
    """Generate PyVis node options for a TPO."""
```

**Edge Styles** (`edge_styles.py`):

```python
def style_influence_edge(influence: dict) -> dict:
    """Generate PyVis edge options for an influence."""

def style_mitigation_edge(mitigates: dict) -> dict:
    """Generate PyVis edge options for a mitigates relationship."""

def style_tpo_impact_edge(impact: dict) -> dict:
    """Generate PyVis edge options for a TPO impact."""
```

---

## Data Flow

### Creating a Risk

```
User Input (Data Management form)
    │
    ▼
render_unified_crud_tab() [ui/tabs/unified_crud_tab.py]
    │
    ▼
RiskGraphManager.create_unified_entity("risk", ...) [database/manager.py]
    │
    ▼
RiskGraphManager.create_risk() (internal route)
    │
    ▼
RiskQueries.create() [database/queries/risks.py]
    │
    ▼
Neo4j (Cypher CREATE query)
    │
    ▼
st.success() + st.rerun()
```

### Rendering the Graph

```
User clicks Visualization tab
    │
    ▼
render_visualization_tab() [ui/home.py]
    │
    ├─── FilterManager.filter_nodes/edges() [ui/filters.py]
    │
    ├─── LayoutManager.load_layout() [ui/layouts.py] (if saved)
    │
    ▼
render_graph_streamlit() [visualization/graph_renderer.py]
    │
    ├─── style_risk_node() [visualization/node_styles.py]
    ├─── style_mitigation_node()
    ├─── style_tpo_node()
    ├─── style_influence_edge() [visualization/edge_styles.py]
    ├─── style_mitigation_edge()
    └─── style_tpo_impact_edge()
    │
    ▼
PyVis Network.show() → HTML
    │
    ▼
st.components.v1.html()
```

### Calculating Exposure

```
User clicks "Calculate Exposure"
    │
    ▼
RiskGraphManager.calculate_exposure() [database/manager.py]
    │
    ▼
calculate_exposure() [services/exposure_calculator.py]
    │
    ├─── Gather all risks, influences, mitigations
    ├─── Topological sort (handle cycles)
    ├─── For each risk:
    │    ├─── Calculate base exposure
    │    ├─── Calculate mitigation factor
    │    ├─── Calculate influence limitation
    │    └─── Calculate final exposure
    └─── Aggregate global metrics
    │
    ▼
ExposureResult dataclass
    │
    ▼
render_exposure_dashboard() [ui/home.py]
```

### Scope Filtering Flow

```
User selects scope(s) in sidebar
    │
    ▼
render_scope_selector() [ui/home.py]
    │
    ├─── SchemaLoader.load_schema() → schema.scopes
    ├─── Optional: "Show connected neighbors" toggle
    │
    ▼
FilterManager.set_active_scopes() [ui/filters.py]
    │
    ├─── Stores active scopes
    ├─── get_scope_node_ids() → union of all node IDs
    ├─── get_filters_for_query() → {scope_node_ids, scope_include_neighbors}
    │
    ▼
get_graph_data(filters) [database/queries/analysis.py]
    │
    ├─── Smart scope expansion:
    │    ├─── Keep risks whose id ∈ scope_node_ids
    │    ├─── Add mitigations connected to scoped risks
    │    ├─── Add TPOs connected to scoped risks
    │    └─── (Optional) Add 1-hop risk neighbors
    └─── Filter edges: keep only if both endpoints in expanded set
    │
    ├──► Visualization shows scoped subgraph
    ├──► _compute_stats_from_graph() [ui/home.py] → Scoped statistics dashboard
    ├──► Data Management UI filters scope dropdowns and restricts edits
    ├──► get_influence_analysis(scope_node_ids) → Scoped influence analysis
    ├──► get_mitigation_analysis(scope_node_ids) → Scoped mitigation analysis
    └──► calculate_exposure(scope_node_ids, include_neighbors) → Scoped exposure
```

---

## Session State Management

All `st.session_state` keys are defined, defaulted, and initialised from
a single module: **`utils/state_manager.py`**.

### Key Registries

| Registry | Keys | Used By |
|----------|------|---------|
| `CONNECTION_DEFAULTS` | `manager`, `connected` | All pages |
| `CONNECTION_FORM_DEFAULTS` | `neo4j_uri`, `neo4j_user` | Home sidebar |
| `HOME_UI_DEFAULTS` | `physics_enabled`, `color_by`, `capture_mode`, `influence_explorer_enabled`, `selected_node_id` | Home page |
| `CONFIG_PAGE_DEFAULTS` | `config_connection`, `config_connected`, `active_schema_name`, `active_schema`, `schema_modified`, `db_stats`, `health_report` | Configuration page |
| `ANALYSIS_CACHE_DEFAULTS` | `influence_analysis_cache`, `influence_analysis_timestamp`, `mitigation_analysis_cache`, `mitigation_analysis_timestamp`, `pending_explore_node` | Analysis panels |
| `SIMULATION_DEFAULTS` | `saved_simulations`, `last_sb_result`, `last_tac_result` | Simulation page — `last_sb_result` / `last_tac_result` persist the most recent compute result so that save/export buttons remain functional across reruns (F31c/d) |
| `LIFECYCLE_DEFAULTS` | `lifecycle_trigger_result`, `lifecycle_acceptance_result`, `lifecycle_archive_alerts`, `lifecycle_last_run`, `show_accepted_risks` | Data Management page |
| `WHATIF_DEFAULTS` | `whatif_baseline`, `whatif_modified`, `whatif_raw_risks`, `whatif_raw_influences`, `whatif_raw_mitigations`, `whatif_raw_mitigates`, `whatif_include_inactive` | What-If Analysis page |
| `MITIGATION_EXPOSURE_DEFAULTS` | `mitexp_baseline`, `mitexp_raw_risks`, `mitexp_raw_influences`, `mitexp_raw_mitigations`, `mitexp_raw_mitigates`, `mitexp_results`, `mitexp_include_inactive`, `mitexp_level_filter` | Mitigation Exposure View page |
| `VISUAL_PANEL_DEFAULTS` | `vp_preset`, `vp_exposure_opacity`, `vp_exposure_threshold`, `vp_lifecycle_opacity_enabled`, `vp_lifecycle_opacity`, `vp_quadrant_borders` | Graph Visual Behaviour panel (F32) |

In addition, `filter_manager` (`FilterManager`) and `layout_manager`
(`LayoutManager`) are instantiated lazily inside `init_home_state()`.

### Init Functions

```python
from utils.state_manager import (
    init_connection_state,      # CONNECTION_DEFAULTS only
    init_home_state,            # connection + form + ui + FilterManager/LayoutManager
    init_config_page_state,     # connection + config page keys
    init_analysis_cache_state,  # influence & mitigation panel caches
    init_simulation_state,      # SIMULATION_DEFAULTS
    init_lifecycle_state,       # LIFECYCLE_DEFAULTS
    init_whatif_state,          # WHATIF_DEFAULTS
    init_mitigation_exposure_state,  # MITIGATION_EXPOSURE_DEFAULTS
    init_visual_panel_state,    # VISUAL_PANEL_DEFAULTS (F32)
    init_all,                   # everything (useful for tests)
    get, set,                   # thin wrappers around st.session_state
)
```

Each consumer calls the narrowest init function it needs:

- `app.py` → `init_home_state()` (via `ui.home.init_session_state()`)
- `pages/1_⚙️_Configuration.py` → `init_config_page_state()`
- `ui/panels/influence_panel.py` → `init_analysis_cache_state()`
- `ui/panels/mitigation_panel.py` → `init_analysis_cache_state()`

---

## Neo4j Schema

### Nodes

```cypher
// Risk
(:Risk {
    reference: String!,
    name: String!,
    description: String,
    level: "Business" | "Operational",
    category: String,
    status: "Active" | "Watching" | "Accepted" | "Suppressed" | "Closed" | "Archived",
    likelihood: Integer (1-10),
    severity: Integer (1-10),
    origin: "New" | "Legacy",
    is_contingent: Boolean,
    trigger_condition: String,
    decision_date: Date,
    is_template: Boolean,
    acceptance_date: Date,
    acceptance_owner: String,
    archive_date: Date,
    created_at: DateTime,
    updated_at: DateTime
})

// Mitigation
(:Mitigation {
    reference: String!,
    name: String!,
    description: String,
    type: "Dedicated" | "Inherited" | "Baseline",
    status: "Implemented" | "In Progress" | "Proposed" | "Deferred",
    source_entity: String,
    created_at: DateTime,
    updated_at: DateTime
})

// Top Objective (ContextNode with node_type = 'tpo')
(:ContextNode {
    node_type: 'tpo',
    reference: String!,
    name: String!,
    cluster: String,
    created_at: DateTime,
    updated_at: DateTime
})
```

### Relationships

```cypher
// Risk influences Risk
(r1:Risk)-[:INFLUENCES {
    influence_type: "Level_1" | "Level_2" | "Level_3",
    strength: "Weak" | "Moderate" | "Strong" | "Critical",
    confidence: Float,
    description: String
}]->(r2:Risk)

// Risk impacts Top Objective
(r:Risk)-[:IMPACTS_TPO {
    impact_level: "Low" | "Medium" | "High" | "Critical",
    description: String
}]->(t:ContextNode {node_type: 'tpo'})

// Mitigation mitigates Risk
(m:Mitigation)-[:MITIGATES {
    id: String!,
    effectiveness: "Low" | "Medium" | "High" | "Critical",
    description: String,
    created_at: DateTime
}]->(r:Risk)

// Risk Template instantiates specific Risk
(t:Risk {is_template: true})-[:INSTANTIATES]->(r:Risk {is_template: false})
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_exposure_calculator.py
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py
├── test_markdown_loader.py      # Docs file loading tests
├── test_exposure_calculator.py
├── test_influence_analysis.py
├── test_scopes.py              # Scope feature: 26 tests
└── ...
```

---

## Adding New Features

### Adding a New Entity Type

1. Create data model in `models/`
2. Create query module in `database/queries/`
3. Add methods to `RiskGraphManager`
4. Create node style in `visualization/node_styles.py`
5. Create tab in `ui/tabs/`
6. Wire into `ui/home.py` and `app.py`

### Adding a New Analysis

1. Add algorithm to `services/`
2. Create panel UI in `ui/panels/`
3. Add to relevant tab or sidebar

### Adding a New Layout

1. Implement generator in `ui/layouts.py`
2. Add to `PREDEFINED_LAYOUTS` dict
3. Add option to layout selector in filters

---

## Performance Considerations

### Optimization Busegies

1. **Lazy loading**: Only load data when tab is active
2. **Caching**: Use `@st.cache_data` for expensive computations
3. **Batching**: Use Cypher UNWIND for bulk operations
4. **Indexing**: Ensure Neo4j indexes on reference fields

### Known Bottlenecks

1. **Large graphs**: >100 nodes can slow PyVis rendering
2. **Exposure calculation**: O(n²) for influence limitation
3. **Layout algorithms**: Sugiyama is O(n³) worst case

---

## Dependencies

### Core

```
streamlit>=1.29.0
neo4j>=5.0.0
pyvis>=0.3.0
pandas>=2.0.0
openpyxl>=3.0.0
```

### Development

```
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
```

---

*Last updated: March 2026 | Version 2.30.0*
