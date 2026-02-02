# 📝 Changelog

All notable changes to the Risk Influence Map (RIM) application.

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
  - Respects RIM semantic hierarchy (TPO → Strategic → Operational)
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
  - ◆ Diamonds for Strategic Risks (pointed = danger)
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
  - 🟣 Strategic Focus
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
  - Link strategic risks to TPOs
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
  - Two-level architecture (Strategic/Operational)
  - Four categories (Programme/Produit/Industriel/Supply Chain)
  - Likelihood × Impact scoring
  - Active/Archived status

- **Influence Mapping**
  - Three influence levels (L1: Op→Strat, L2: Strat→Strat, L3: Op→Op)
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

1. Node shapes changed: Diamond for strategic, circle for operational
2. Edge arrows changed: Bar-end for mitigations, vee for TPO impacts
3. No data migration needed

### v2.1.0 → v2.2.0

1. New exposure calculation: Run "Calculate Exposure" to use new feature
2. New layout option: "Hierarchical" added to layout dropdown
3. No data migration needed

---

*For questions or issues, please open a GitHub issue.*
