# 🏗️ RIM Architecture

Technical documentation for developers working on the Risk Influence Map application.

---

## Overview

RIM follows a **modular architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                         app.py                               │
│                    (Main Entry Point)                        │
│                      1,193 lines                             │
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
└── settings.py      # Constants and configuration
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
    
    # Mitigation operations
    def create_mitigation(self, **kwargs) -> str
    def create_mitigates_relationship(self, mit_ref, risk_ref, **kwargs)
    
    # TPO operations
    def create_tpo(self, **kwargs) -> str
    def create_tpo_impact(self, risk_ref, tpo_ref, **kwargs)
    
    # Analysis
    def get_graph_for_visualization(self) -> Tuple[nodes, edges]
    def calculate_exposure(self) -> dict
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
    STRATEGIC = "Strategic"
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
├── exposure_calculator.py  # Quantitative exposure scoring
├── influence_analysis.py   # Network analysis algorithms
├── mitigation_analysis.py  # Coverage and gap analysis
├── import_service.py       # Excel import logic
└── export_service.py       # Excel export logic
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
├── components.py     # Reusable UI components
├── filters.py        # FilterManager class
├── layouts.py        # Layout generators + LayoutManager
├── legend.py         # Graph legend rendering
├── sidebar.py        # Sidebar sections
├── styles.py         # CSS injection
├── panels/
│   ├── __init__.py
│   ├── influence_panel.py   # Influence analysis UI
│   └── mitigation_panel.py  # Mitigation analysis UI
└── tabs/
    ├── __init__.py
    ├── risks_tab.py
    ├── tpos_tab.py
    ├── mitigations_tab.py
    ├── influences_tab.py
    ├── tpo_impacts_tab.py
    ├── risk_mitigations_tab.py
    └── import_export_tab.py
```

**FilterManager** (`filters.py`):

```python
class FilterManager:
    """Manage filter state and application."""
    
    def __init__(self, session_state):
        self.state = session_state
    
    def apply_preset(self, preset_name: str)
    def get_filter_summary(self) -> str
    def filter_nodes(self, nodes: List) -> List
    def filter_edges(self, edges: List) -> List
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
    "strategic": "diamond",    # ◆ Pointed = danger
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
User Input (Streamlit form)
    │
    ▼
render_risks_tab() [ui/tabs/risks_tab.py]
    │
    ▼
RiskGraphManager.create_risk() [database/manager.py]
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
render_visualization() [app.py]
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
render_exposure_dashboard() [app.py]
```

---

## Session State Management

Streamlit session state is used for:

```python
# Connection
st.session_state.neo4j_connected: bool
st.session_state.manager: RiskGraphManager

# Filters
st.session_state.filter_levels: List[str]
st.session_state.filter_categories: List[str]
st.session_state.filter_origins: List[str]
st.session_state.show_tpos: bool
st.session_state.show_mitigations: bool

# Layout
st.session_state.saved_layouts: Dict[str, dict]
st.session_state.current_layout: str

# Exposure
st.session_state.exposure_result: dict
st.session_state.exposure_calculated: bool

# UI State
st.session_state.selected_node: str
st.session_state.graph_refresh_counter: int
```

---

## Neo4j Schema

### Nodes

```cypher
// Risk
(:Risk {
    reference: String!,
    name: String!,
    description: String,
    level: "Strategic" | "Operational",
    category: String,
    status: "Active" | "Archived",
    likelihood: Integer (1-10),
    impact: Integer (1-10),
    origin: "New" | "Legacy",
    is_contingent: Boolean,
    activation_condition: String,
    decision_date: Date,
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

// TPO
(:TPO {
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

// Risk impacts TPO
(r:Risk)-[:IMPACTS_TPO {
    impact_level: "Low" | "Medium" | "High" | "Critical",
    description: String
}]->(t:TPO)

// Mitigation mitigates Risk
(m:Mitigation)-[:MITIGATES {
    id: String!,
    effectiveness: "Low" | "Medium" | "High" | "Critical",
    description: String,
    created_at: DateTime
}]->(r:Risk)
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
├── test_exposure_calculator.py
├── test_influence_analysis.py
├── test_filters.py
└── fixtures/
    └── sample_data.py
```

---

## Adding New Features

### Adding a New Entity Type

1. Create data model in `models/`
2. Create query module in `database/queries/`
3. Add methods to `RiskGraphManager`
4. Create node style in `visualization/node_styles.py`
5. Create tab in `ui/tabs/`
6. Wire into `app.py`

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

### Optimization Strategies

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

*Last updated: February 2026 | Version 2.2.0*
