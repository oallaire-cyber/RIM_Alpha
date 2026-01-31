# 🎯 Risk Influence Map (RIM)

A dynamic risk management visualization system built with Streamlit and Neo4j, designed for strategic and operational risk mapping in complex programs like SMR (Small Modular Reactor) nuclear projects.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Overview

The Risk Influence Map (RIM) is an innovative methodology for visualizing and managing the complex relationships between risks in large-scale programs. It transforms static risk registers into dynamic risk intelligence by distinguishing between:

- **Strategic Risks**: Consequence-oriented risks managed by program leadership
- **Operational Risks**: Cause-oriented risks managed by functional teams
- **Top Program Objectives (TPOs)**: Key program goals that risks may impact
- **Mitigations**: Actions and controls that address identified risks

## ✨ Features

### Risk Management

- Two-level risk architecture (Strategic/Operational)
- Multi-category classification (Programme, Produit, Industriel, Supply Chain)
- **Risk Origin tracking** (New vs Legacy):
  - **New**: Program-specific risks identified and managed within the program
  - **Legacy**: Inherited risks from other programs or Enterprise-level risk registers
- Contingent risk support with activation conditions and decision dates
- Probability × Impact exposure calculation

### Exposure Calculation

- **On-demand calculation** via dedicated button (not real-time for performance)
- **Base Exposure**: Likelihood × Impact (0-100 scale)
- **Mitigation Factor**: Multiplicative model with diminishing returns for multiple mitigations
- **Influence Limitation**: Upstream risks limit downstream mitigation effectiveness
  - Unmitigated upstream risks create a "floor" for downstream exposure
  - Models the reality that fixing symptoms without addressing causes has limited effect
- **Global Metrics**:
  - **Residual Risk %**: Percentage of base exposure remaining after all factors
  - **Weighted Risk Score**: Impact²-weighted score (0-100) for executive reporting
  - **Max Single Exposure**: Alert metric for worst-case individual risk
- **Health Status Indicator**: Color-coded status (Excellent → Critical)
- **Detailed Breakdown**: Per-risk exposure analysis with reduction percentages

### Influence Mapping

- Three types of influence links:
  - **Level 1**: Operational → Strategic (red, thick solid line)
  - **Level 2**: Strategic → Strategic (purple, medium solid line)
  - **Level 3**: Operational → Operational (blue, dashed line)
- Configurable strength (Weak/Moderate/Strong/Critical)
- Confidence scoring

### Top Program Objectives (TPOs)

- Link strategic risks to program objectives
- Cluster-based organization (Product Efficiency, Business Efficiency, Industrial Efficiency, Sustainability, Safety)
- Impact level tracking (Low/Medium/High/Critical)
- Gold hexagon visualization

### Mitigation Management

- **Mitigation Types**:
  - **Dedicated**: Program-owned mitigations created specifically for identified risks (teal, solid border)
  - **Inherited**: Mitigations inherited from other entities or programs (blue, dotted border)
  - **Baseline**: Standard controls from requirements, regulations, or industry standards (purple, thick border)
- **Mitigation Status tracking**: Proposed, In Progress, Implemented, Deferred
- **Effectiveness scoring**: Low, Medium, High, Critical
- **Many-to-many relationships**: One mitigation can address multiple risks
- Source entity tracking for inherited/baseline mitigations
- Shield-shaped visualization (🛡️) with bar-end arrows to risks

### Visualization

- Interactive graph powered by PyVis
- **Semantic shape system** for instant recognition:
  - **Diamonds (◆)** for Strategic Risks - pointed shape conveys danger
  - **Circles (●)** for Operational Risks - foundation/cause-oriented
  - **Rounded boxes (🛡️)** for Mitigations - shield-like protection
  - **Hexagons (⬡)** for TPOs - program objectives
- Color coding by level or exposure (heat map gradient)
- **Visual distinction for risk origins**:
  - New risks: Standard border
  - Legacy risks: Gray thick border with [L] prefix
- **Mitigation visualization**:
  - Rounded boxes with shield emoji (🛡️)
  - Bar-end arrows (⊣) showing "blocking" effect
  - Border style indicates status (solid=implemented, dashed=proposed)
- **Edge differentiation by relationship type**:
  - Standard arrows (→) for influence relationships
  - Bar-end arrows (⊣) for mitigation relationships
  - Vee arrows (▷) for TPO impact relationships
- Multiple layout algorithms:
  - **Hierarchical (Sugiyama)**: Edge-crossing minimization with semantic layer constraints
  - Layered (TPO → Strategic → Operational)
  - Category-based (2×2 grid)
  - TPO Cluster grouping
- Manual layout save/load with position capture
- Physics toggle for node arrangement

### Filter System

- **Collapsible filter sections** for a cleaner interface:
  - ⚡ Quick Presets
  - 🎯 Risk Filters (Level, Categories, Status, Origin)
  - 🏆 TPO Filters
  - 🛡️ Mitigation Filters
  - 🎨 Display Options
  - 🔍 Influence Explorer
  - ⚙️ Graph Options
  - 💾 Layout Management
- Quick filter presets:
  - 🌐 Full View (risks + TPOs, no mitigations)
  - 🟣 Strategic Focus
  - 🔵 Operational Focus
  - ✅ Active Risks Only
  - ⚠️ Contingent Risks
  - 🎯 Risks Only
  - 🆕 New Risks Only
  - 📜 Legacy Risks Only
  - 🛡️ Risks + Mitigations
  - 🗺️ Full Map (everything)
- **All/None buttons** for quick multi-select control
- **Origin filter** (New/Legacy)
- **Mitigation filters** (by type and status)
- Filter validation and summary display
- **Refresh button** for visualization updates
- Persistent filter state

### User Interface

- **Collapsible Statistics Dashboard** at the top of the main view
- **Risk Exposure Analysis Dashboard** with calculation button and metrics display
- **Comprehensive Legend** in sidebar with collapsible sections:
  - Node Types (risks, TPOs, mitigations)
  - Link Types (influences, impacts, mitigates)
  - Edge Thickness meanings
- **Analysis Panels** in the visualization area:
  - 📊 Influence Analysis (Top Propagators, Convergence Points, Critical Paths, Bottlenecks, Clusters)
  - 🛡️ Mitigation Analysis (Risk Treatment, Mitigation Impact, Coverage Gaps)
- **Default view shows all elements** (risks, TPOs, and mitigations)
- Responsive layout with filter panel on left, visualization on right

### Import/Export

- Excel import/export with detailed logging
- **Sheets exported/imported**:
  - Risks (including origin)
  - TPOs
  - Influences
  - TPO_Impacts
  - Mitigations
  - Mitigates (mitigation-to-risk links)
- Name-based relationship matching for re-import capability
- Comprehensive error reporting and warnings
- Cypher templates for bulk database operations

### Influence Analysis

- **Top Propagators**: Risks with highest downstream impact on the network
- **Convergence Points**: Risks/TPOs where multiple influences converge
- **Critical Paths**: Strongest influence chains from operational risks to TPOs
- **Bottlenecks**: Nodes appearing in many paths (single points of failure)
- **Risk Clusters**: Tightly interconnected risk groups
- Interactive exploration with "Explore in Graph" buttons

### Mitigation Analysis

- **Three analysis modes** accessible from the Visualization tab:
  - **🎯 Risk Treatment Explorer**: Risk-centric view showing mitigation coverage per risk
  - **🛡️ Mitigation Impact Explorer**: Mitigation-centric view showing all risks addressed
  - **📊 Coverage Gap Analysis**: Transverse view identifying gaps in mitigation strategy
- **Coverage statistics**: Real-time metrics on mitigated vs unmitigated risks
- **Cross-reference with Influence Analysis**:
  - Flags unmitigated risks that are Top Propagators, Convergence Points, or Bottlenecks
  - Prioritizes high-impact risks for mitigation decisions
- **Risk coverage status indicators**:
  - ⚠️ No Mitigations
  - 📋 Only Proposed (no implemented)
  - 🔶 Partially Covered
  - ✅ Well Covered
- **Gap analysis views**:
  - High Priority: Unmitigated risks with high influence scores
  - Critical Unmitigated: High-exposure risks without mitigations
  - Proposed Only: Risks awaiting mitigation implementation
  - Strategic Gaps: Strategic risks without adequate coverage
  - Coverage by Category: Visual breakdown per risk category

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Neo4j Database (local or cloud instance)
- Git (for cloning)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/oallaire-cyber/RIM_Alpha
   cd rim-alpha
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Neo4j**
   - Install [Neo4j Desktop](https://neo4j.com/download/) or use [Neo4j Aura](https://neo4j.com/cloud/aura/) (cloud)
   - Create a new database
   - Note your connection URI, username, and password

5. **Run the application**

   ```bash
   streamlit run app.py
   ```

6. **Connect to Neo4j**
   - Enter your Neo4j credentials in the sidebar
   - Click "Connect"

### Migration for Existing Data

If you have existing risks without the `origin` property, run this Cypher query to set a default:

```cypher
MATCH (r:Risk)
WHERE r.origin IS NULL
SET r.origin = 'New'
RETURN count(r) as updated_risks
```

## 📁 Project Structure

```
rim/
├── app.py                  # Main application entry point
├── config/
│   ├── __init__.py
│   └── settings.py         # Application settings and constants
├── database/
│   ├── __init__.py
│   ├── connection.py       # Neo4j connection management
│   ├── manager.py          # RiskGraphManager facade
│   └── queries/
│       ├── analysis.py     # Influence analysis queries
│       ├── influences.py   # Influence CRUD operations
│       ├── mitigations.py  # Mitigation CRUD operations
│       ├── risks.py        # Risk CRUD operations
│       └── tpos.py         # TPO CRUD operations
├── models/
│   ├── __init__.py
│   ├── enums.py            # Enumeration types
│   ├── mitigation.py       # Mitigation data model
│   ├── relationships.py    # Relationship data models
│   ├── risk.py             # Risk data model
│   └── tpo.py              # TPO data model
├── services/
│   ├── __init__.py
│   ├── export_service.py   # Excel export functionality
│   ├── import_service.py   # Excel import functionality
│   ├── influence_analysis.py  # InfluenceAnalyzer class
│   ├── mitigation_analysis.py # Mitigation coverage analysis
│   └── exposure_calculator.py # Risk exposure calculation engine
├── ui/
│   ├── __init__.py
│   ├── components.py       # Reusable UI components
│   ├── filters.py          # FilterManager class
│   ├── layouts.py          # LayoutManager and layout generators
│   ├── panels/
│   │   ├── influence_panel.py   # Influence analysis panel
│   │   └── mitigation_panel.py  # Mitigation analysis panel
│   ├── sidebar.py          # Sidebar rendering
│   ├── styles.py           # CSS styles and badge generators
│   └── tabs/
│       ├── import_export_tab.py
│       ├── influences_tab.py
│       ├── mitigations_tab.py
│       ├── risks_tab.py
│       ├── risk_mitigations_tab.py
│       ├── tpos_tab.py
│       └── tpo_impacts_tab.py
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Utility functions
├── visualization/
│   ├── __init__.py
│   ├── colors.py           # Color schemes and utilities
│   ├── edge_styles.py      # Edge styling configuration
│   ├── graph_options.py    # Graph physics and options
│   ├── graph_renderer.py   # PyVis graph rendering
│   └── node_styles.py      # Node styling configuration
└── requirements.txt
```

## 📖 Usage Guide

### Creating Risks

1. Go to the **🎯 Risks** tab
2. Expand "➕ Create New Risk"
3. Fill in the details:
   - **Name**: Descriptive risk name
   - **Level**: Strategic (consequence-oriented) or Operational (cause-oriented)
   - **Origin**: New (program-specific) or Legacy (inherited)
   - **Categories**: One or more domain categories
   - **Status**: Active, Contingent, or Archived
   - **Probability/Impact**: For exposure calculation
4. Click "Create Risk"

### Creating Influences

1. Go to the **🔗 Influences** tab
2. Expand "➕ Create New Influence"
3. Select source and target risks
4. The influence type is automatically determined:
   - Level 1: Operational → Strategic
   - Level 2: Strategic → Strategic
   - Level 3: Operational → Operational
5. Set strength and optional description
6. Click "Create Influence"

### Creating TPOs

1. Go to the **🏆 TPOs** tab
2. Expand "➕ Create New TPO"
3. Enter reference, name, cluster, and description
4. Click "Create TPO"

### Linking Risks to TPOs

1. Go to the **🔗 TPO Impacts** tab
2. Select a strategic risk and TPO
3. Set the impact level
4. Click "Create Impact"

### Creating Mitigations

1. Go to the **🛡️ Mitigations** tab
2. Expand "➕ Create New Mitigation"
3. Fill in the details:
   - **Name**: Mitigation action name
   - **Type**: Dedicated, Inherited, or Baseline
   - **Status**: Proposed, In Progress, Implemented, or Deferred
   - **Owner**: Responsible party
   - **Source Entity**: For Inherited/Baseline types
4. Click "Create Mitigation"

### Linking Mitigations to Risks

1. Go to the **🔗 Risk Mitigations** tab
2. Expand "➕ Link Mitigation to Risk"
3. Select a mitigation and risk
4. Set the effectiveness level
5. Click "Create Mitigation Link"

Note: One mitigation can be linked to multiple risks, and one risk can have multiple mitigations.

### Viewing Mitigations

1. Go to the **📊 Visualization** tab
2. Toggle "🟢 Show Mitigations" checkbox to show/hide
3. Optionally filter by mitigation type and status
4. Or use Quick Presets:
   - 🗺️ Full Map: Shows everything
   - 🛡️ Risks + Mitigations: Risks and mitigations without TPOs
   - 🌐 Full View: Risks and TPOs without mitigations

### Using Layouts

1. In the **📊 Visualization** tab, expand the **⚙️ Graph Options** section
2. Disable physics to freeze positions
3. Arrange nodes as desired by dragging
4. Enable "📍 Enable position capture"
5. Click "📍 Capture Positions" on the graph
6. Click "📋 Copy to Clipboard"
7. Expand the **💾 Layout Management** section
8. Paste in the Position Data text area
9. Name and save your layout

Predefined layouts available:

- **Hierarchical**: Sugiyama algorithm with edge-crossing minimization
- **Layered**: TPO at top, Strategic middle, Operational bottom
- **Categories**: 2×2 grid grouping by category
- **TPO Clusters**: Group risks by their TPO cluster associations

### Import/Export

**Export:**

1. Go to **📥 Import/Export** tab
2. Click "Generate export"
3. Download the Excel file (now includes Mitigations and Mitigates sheets)

**Import:**

1. Prepare an Excel file with sheets: Risks, TPOs, Influences, TPO_Impacts, Mitigations, Mitigates
2. Upload the file
3. Review the detailed import log

### Using Influence Analysis

1. In the **📊 Visualization** tab, expand the **📊 Influence Analysis** panel
2. Click "🔄 Refresh Analysis" to compute/update the analysis
3. Navigate through the analysis tabs:
   - **🎯 Top Propagators**: See which risks have the highest downstream impact
   - **⚠️ Convergence Points**: Identify risks/TPOs where multiple influences converge
   - **🔥 Critical Paths**: View the strongest influence chains to TPOs
   - **🚧 Bottlenecks**: Find single points of failure in the risk network
   - **📦 Risk Clusters**: Discover tightly interconnected risk groups
4. Click the **🔍** button next to any risk to explore it in the graph

### Using Mitigation Analysis

The Mitigation Analysis panel provides decision support for risk treatment strategies by combining mitigation coverage data with influence analysis insights.

1. In the **📊 Visualization** tab, expand the **🛡️ Mitigation Analysis** panel
2. Review the coverage overview metrics at the top
3. Select an analysis mode:

**Mode 1: Risk Treatment Explorer** 🎯

- Select a risk from the dropdown to see its mitigation coverage
- Status indicators show coverage level (⚠️ None, 📋 Proposed, 🔶 Partial, ✅ Well covered)
- View influence analysis flags (Top Propagator, Convergence Point, Bottleneck)
- See all mitigations with their type, status, and effectiveness
- Click "🔍 Visualize in Graph" to explore the risk in context

**Mode 2: Mitigation Impact Explorer** 🛡️

- Select a mitigation to see all risks it addresses
- View strategic vs operational risk breakdown
- See total exposure covered by the mitigation
- Identify if the mitigation addresses high-priority risks (propagators, convergence points)

**Mode 3: Coverage Gap Analysis** 📊

- **🚨 High Priority**: Unmitigated risks that are Top Propagators, Convergence Points, or Bottlenecks
- **⚠️ Unmitigated**: High-exposure risks without any mitigations
- **📋 Proposed Only**: High-exposure risks with only proposed (not implemented) mitigations
- **🟣 Strategic Gaps**: Strategic risks without adequate mitigation coverage
- **📊 By Category**: Visual progress bars showing coverage percentage per risk category

**Best Practices:**

- Prioritize mitigating risks flagged as "High Priority" first
- Ensure all Strategic risks have at least one implemented mitigation
- Monitor category coverage to identify systematic gaps
- Use the "Visualize in Graph" feature to understand risk context before deciding on mitigation approach

### Using Exposure Calculation

The Exposure Calculation feature provides quantitative risk scoring that accounts for mitigations and influence relationships.

1. In the **⚡ Risk Exposure Analysis** dashboard (below Statistics)
2. Click **🔄 Calculate Exposure** to run the calculation
3. Review the three key metrics:
   - **📉 Residual Risk %**: Overall mitigation effectiveness (lower is better)
   - **🟢/🟡/🔴 Risk Score**: Impact-weighted score with health status
   - **⚠️ Max Exposure**: Highest single risk exposure (identifies hotspots)
4. Expand **📋 Detailed Risk Exposures** to see per-risk breakdown

**Understanding the Calculation:**

The exposure model considers three factors:

1. **Base Exposure** = Likelihood × Impact (0-100 scale)
2. **Mitigation Effect**: Each mitigation reduces exposure multiplicatively
   - Critical: 90% reduction, High: 70%, Medium: 50%, Low: 30%
   - Multiple mitigations have diminishing returns: Factor = ∏(1 - Effectiveness)
3. **Influence Limitation**: Upstream risks limit downstream mitigation effectiveness
   - If upstream risks are unmitigated, downstream mitigations are less effective
   - This models "you can't fully solve symptoms without addressing causes"

**Example:**
- Risk A (upstream): Base=12, no mitigation → Residual=12 (100%)
- Risk B (downstream): Base=15, Medium mitigation (50%)
  - Without influence: Final = 15 × 0.5 = 7.5
  - With unmitigated upstream: Final ≈ 15 × 0.68 = 10.2 (limitation reduces effectiveness)

**Best Practices:**

- Run calculation after significant data changes (new risks, mitigations, influences)
- Address high-influence upstream risks before downstream risks
- Monitor the Max Exposure metric to identify critical hotspots
- Use the detailed breakdown to prioritize mitigation efforts

## 📊 Data Model

### Nodes

**Risk**

- `id`: UUID
- `name`: String
- `level`: "Strategic" | "Operational"
- `origin`: "New" | "Legacy"
- `categories`: List of strings
- `status`: "Active" | "Contingent" | "Archived"
- `probability`: Float (0-1)
- `impact`: Float (1-10)
- `exposure`: Float (calculated)
- `owner`: String
- `description`: String
- `activation_condition`: String (for contingent)
- `activation_decision_date`: Date (for contingent)

**TPO**

- `id`: UUID
- `reference`: String (e.g., "TPO-01")
- `name`: String
- `cluster`: String
- `description`: String

**Mitigation**

- `id`: UUID
- `name`: String
- `type`: "Dedicated" | "Inherited" | "Baseline"
- `status`: "Proposed" | "In Progress" | "Implemented" | "Deferred"
- `description`: String
- `owner`: String
- `source_entity`: String (for inherited/baseline mitigations)
- `created_at`: DateTime
- `updated_at`: DateTime

### Relationships

**INFLUENCES** (Risk → Risk)

- `influence_type`: "Level_1" | "Level_2" | "Level_3"
- `strength`: "Weak" | "Moderate" | "Strong" | "Critical"
- `confidence`: Float (0-1)
- `description`: String

**IMPACTS_TPO** (Risk → TPO)

- `impact_level`: "Low" | "Medium" | "High" | "Critical"
- `description`: String

**MITIGATES** (Mitigation → Risk)

- `id`: UUID
- `effectiveness`: "Low" | "Medium" | "High" | "Critical"
- `description`: String
- `created_at`: DateTime

## 🎨 Visual Legend

### Node Shapes & Colors

| Element                | Shape              | Color            | Border Style      | Notes                                         |
| ---------------------- | ------------------ | ---------------- | ----------------- | --------------------------------------------- |
| Strategic Risk         | ◆ Diamond          | Purple (#8E44AD) | Solid             | Consequence-oriented, size varies by exposure |
| Operational Risk       | ● Circle           | Blue (#2980B9)   | Solid             | Cause-oriented, size varies by exposure       |
| Contingent Risk        | ◇ Diamond (hollow) | Level color      | Dashed            | Potential risk, not yet materialized          |
| Legacy Risk            | ● or ◆             | Level color      | Gray thick border | Inherited risk, [L] prefix in label           |
| TPO                    | ⬡ Hexagon          | Gold (#F1C40F)   | Solid             | Program objective, reference as label         |
| Mitigation (Dedicated) | 🛡️ Rounded Box     | Teal (#1ABC9C)   | Solid, medium     | Program-specific mitigation                   |
| Mitigation (Inherited) | 🛡️ Rounded Box     | Blue (#3498DB)   | Dotted            | Inherited from external source                |
| Mitigation (Baseline)  | 🛡️ Rounded Box     | Purple (#9B59B6) | Solid, thick      | Standard practice/regulation                  |

### Risk Exposure Gradient (when coloring by exposure)

| Exposure Level | Color              | Description                  |
| -------------- | ------------------ | ---------------------------- |
| Critical (≥7)  | Dark Red (#C0392B) | Immediate attention required |
| High (≥4)      | Red (#E74C3C)      | Significant concern          |
| Medium (≥2)    | Orange (#F39C12)   | Attention needed             |
| Low (<2)       | Yellow (#F1C40F)   | Manageable                   |

### Mitigation Status Indicators (Border Style)

| Status      | Border Style   | Description                |
| ----------- | -------------- | -------------------------- |
| Implemented | Solid          | Active protection in place |
| In Progress | Dash-dot (─∙─) | Being deployed             |
| Proposed    | Dashed (─ ─)   | Planned but not started    |
| Deferred    | Dotted (∙∙∙)   | On hold                    |

### Edge Types

| Relationship          | Color            | Style        | Arrow Type | Notes               |
| --------------------- | ---------------- | ------------ | ---------- | ------------------- |
| Level 1 (Op→Strat)    | Red (#E74C3C)    | Thick solid  | → Standard | Causes consequence  |
| Level 2 (Strat→Strat) | Purple (#8E44AD) | Medium solid | → Standard | Amplifies impact    |
| Level 3 (Op→Op)       | Blue (#2980B9)   | Thin dashed  | → Standard | Contributes to      |
| TPO Impact            | Orange (#E67E22) | Dash-dot     | ▷ Vee      | Threatens objective |
| Mitigates             | Green (#1ABC9C)  | Variable     | ⊣ Bar      | Blocks/reduces risk |

### Mitigation Edge Thickness (by Effectiveness)

| Effectiveness | Width | Description              |
| ------------- | ----- | ------------------------ |
| Critical      | 5px   | Highly effective control |
| High          | 4px   | Strong protection        |
| Medium        | 3px   | Moderate reduction       |
| Low           | 2px   | Minimal impact           |

## 📝 Version History

### v2.2.0 - Exposure Calculation & Hierarchical Layout (January 2025)

**Major Changes:**

- **Exposure Calculation Engine**: New quantitative risk scoring system
  - Calculates risk exposure considering mitigations and influence relationships
  - Influence Limitation model: upstream risks limit downstream mitigation effectiveness
  - Three global metrics: Residual Risk %, Weighted Risk Score, Max Exposure
  - Health status indicator with color coding
  - Detailed per-risk breakdown with reduction percentages
  - On-demand calculation via button (not real-time for performance)

- **Hierarchical Layout (Sugiyama Algorithm)**: New graph layout option
  - Minimizes edge crossings using barycenter heuristic
  - Respects RIM semantic hierarchy (TPO → Strategic → Operational)
  - Connected nodes are vertically aligned for better readability
  - Mitigations positioned alongside their target risks
  - Available as "🌳 Hierarchical" in predefined layouts

**New Files:**
- `services/exposure_calculator.py`: Exposure calculation engine

**UI Enhancements:**
- New "⚡ Risk Exposure Analysis" dashboard section
- Calculate Exposure button with cached results
- Detailed exposure breakdown expandable panel

### v2.1.0 - Enhanced Visualization (January 2025)

**Major Changes:**

- New semantic shape system for instant visual recognition
- Diamonds for strategic risks (pointed = danger)
- Circles for operational risks (foundation)
- Rounded shield-like boxes for mitigations
- Different arrow types for relationship categories
- Heat map gradient for exposure coloring
- Border styles encode mitigation status

### v2.0.0 - Modular Refactoring (January 2025)

**Major Changes:**

- Refactored from monolithic `app_alpha.py` (6,521 lines) to modular architecture
- Separated concerns into logical packages: `config`, `database`, `models`, `services`, `ui`, `visualization`, `utils`
- Improved code maintainability and testability
- No functional changes - 100% backward compatible

**Architecture Improvements:**

- `RiskGraphManager` as a facade for all database operations
- Dedicated query modules for each entity type
- `InfluenceAnalyzer` class for influence network analysis
- `ExcelImporter` class for structured import operations
- `FilterManager` with validation and summary features

**Files:**

- Main entry: `app.py` (823 lines)
- Legacy (deprecated): `app_alpha.py`

### v1.x - Monolithic Version

- Full feature implementation in single file
- Mitigation management with many-to-many relationships
- Influence and Mitigation analysis panels
- Excel import/export with detailed logging
- Filter presets and layout management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Graph database powered by [Neo4j](https://neo4j.com/)
- Visualization using [PyVis](https://pyvis.readthedocs.io/)

## 📞 Contact

For questions or feedback about the RIM methodology, please open an issue on GitHub.

---
