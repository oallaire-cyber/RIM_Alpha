# 📝 Changelog

All notable changes to the Risk Influence Map (RIM) application.

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
