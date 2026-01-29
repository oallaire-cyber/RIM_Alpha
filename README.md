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

### Influence Mapping

- Three types of influence links:
  - **Level 1**: Operational → Strategic (red)
  - **Level 2**: Strategic → Strategic (purple)
  - **Level 3**: Operational → Operational (blue)
- Configurable strength (Weak/Moderate/Strong/Critical)
- Confidence scoring

### Top Program Objectives (TPOs)

- Link strategic risks to program objectives
- Cluster-based organization (Product Efficiency, Business Efficiency, Industrial Efficiency, Sustainability, Safety)
- Impact level tracking (Low/Medium/High/Critical)
- Yellow hexagon visualization

### Mitigation Management

- **Mitigation Types**:
  - **Dedicated**: Program-owned mitigations created specifically for identified risks
  - **Inherited**: Mitigations inherited from other entities or programs
  - **Baseline**: Standard controls from requirements, regulations, or industry standards
- **Mitigation Status tracking**: Proposed, In Progress, Implemented, Deferred
- **Effectiveness scoring**: Low, Medium, High, Critical
- **Many-to-many relationships**: One mitigation can address multiple risks
- Source entity tracking for inherited/baseline mitigations
- Green rectangle visualization with dashed edges to risks

### Visualization

- Interactive graph powered by PyVis
- Color coding by level or exposure
- **Visual distinction for risk origins**:
  - New risks: Standard border
  - Legacy risks: Gray dashed border with [L] prefix
- **Mitigation visualization**:
  - Green rectangles (color varies by type)
  - Dashed green edges showing mitigation relationships
  - Edge thickness indicates effectiveness
- Multiple layout algorithms:
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

The application has been refactored from a monolithic design to a modular architecture for improved maintainability, testability, and code organization.

```
rim-app/
├── app.py                      # Main application entry point (823 lines)
├── app_alpha.py                # Legacy monolithic version (deprecated)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── config/                     # Configuration
│   ├── __init__.py
│   └── settings.py             # App settings and constants
│
├── models/                     # Data models
│   ├── __init__.py
│   ├── enums.py                # Enumeration types
│   ├── risk.py                 # Risk model
│   ├── tpo.py                  # TPO model
│   ├── mitigation.py           # Mitigation model
│   └── relationships.py        # Relationship models
│
├── database/                   # Database layer
│   ├── __init__.py
│   ├── connection.py           # Neo4j connection management
│   ├── manager.py              # RiskGraphManager facade
│   └── queries/                # Cypher query modules
│       ├── __init__.py
│       ├── risks.py            # Risk CRUD queries
│       ├── tpos.py             # TPO CRUD queries
│       ├── mitigations.py      # Mitigation CRUD queries
│       ├── influences.py       # Influence queries
│       └── analysis.py         # Analysis queries
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── influence_analysis.py   # Influence network analysis
│   ├── mitigation_analysis.py  # Mitigation coverage analysis
│   ├── export_service.py       # Excel export
│   └── import_service.py       # Excel import
│
├── ui/                         # UI components
│   ├── __init__.py
│   ├── styles.py               # CSS styles and badges
│   ├── filters.py              # Filter management
│   ├── layouts.py              # Graph layout generators
│   ├── components.py           # Reusable UI components
│   ├── sidebar.py              # Sidebar rendering
│   ├── panels/                 # Analysis panels
│   │   ├── __init__.py
│   │   ├── influence_panel.py
│   │   └── mitigation_panel.py
│   └── tabs/                   # Tab pages
│       ├── __init__.py
│       ├── risks_tab.py
│       ├── tpos_tab.py
│       ├── mitigations_tab.py
│       ├── influences_tab.py
│       ├── tpo_impacts_tab.py
│       ├── risk_mitigations_tab.py
│       └── import_export_tab.py
│
├── visualization/              # Graph visualization
│   ├── __init__.py
│   ├── colors.py               # Color schemes
│   ├── node_styles.py          # Node styling
│   ├── edge_styles.py          # Edge styling
│   ├── graph_options.py        # PyVis configuration
│   └── graph_renderer.py       # Main render functions
│
├── utils/                      # Utilities
│   ├── __init__.py
│   └── helpers.py              # Helper functions
│
├── tests/                      # Test suite
│   └── __init__.py
│
├── demo_data_loader.cypher     # Cypher script to load demo data
└── bulk_import_template.cypher # Template for bulk data imports
```

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        app.py                                   │
│                   (Main Entry Point)                            │
└─────────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│       UI        │ │   Visualization │ │    Services     │
│  (Streamlit)    │ │    (PyVis)      │ │ (Analysis/IO)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            ▼
              ┌─────────────────────────┐
              │   Database (Neo4j)      │
              │   RiskGraphManager      │
              └─────────────────────────┘
                            │
              ┌─────────────────────────┐
              │      Neo4j Graph        │
              └─────────────────────────┘
```

### Module Responsibilities

| Module           | Purpose                                                        |
| ---------------- | -------------------------------------------------------------- |
| `config/`        | Application settings, constants, and default values            |
| `models/`        | Data models, enumerations, and type definitions                |
| `database/`      | Neo4j connection, query execution, and RiskGraphManager facade |
| `services/`      | Business logic for analysis, import/export operations          |
| `ui/`            | Streamlit UI components, filters, panels, and tab pages        |
| `visualization/` | PyVis graph rendering, styling, and layout                     |
| `utils/`         | Helper functions and utilities                                 |

## 🔧 Configuration

### Neo4j Connection

Default connection settings (in `config/settings.py`):

- URI: `bolt://localhost:7687`
- Username: `neo4j`
- Password: (your password)

### Application Settings

Edit `config/settings.py` to customize:

- Risk levels, categories, statuses
- TPO clusters
- Mitigation types and effectiveness levels
- Influence strengths
- Visualization colors and node sizes
- Analysis parameters (propagation decay, max depth, etc.)

### Filter Presets

Built-in presets:
| Preset | Description |
|--------|-------------|
| 🌐 Full View | All risks and TPOs (no mitigations) |
| 🟣 Strategic Focus | Strategic risks + TPOs only |
| 🔵 Operational Focus | Operational risks only |
| ✅ Active Risks Only | Excludes contingent risks |
| ⚠️ Contingent Risks | Future/contingent risks only |
| 🎯 Risks Only | All risks, no TPOs |
| 🆕 New Risks Only | Program-specific new risks |
| 📜 Legacy Risks Only | Inherited/Enterprise level risks |
| 🛡️ Risks + Mitigations | Show risks with mitigations (no TPOs) |
| 🗺️ Full Map | Everything: Risks, TPOs, and Mitigations |

**Note:** At application startup, the default view displays all elements (equivalent to 🗺️ Full Map).

## 📖 Usage Guide

### Connecting to Neo4j

1. Enter your Neo4j connection details in the sidebar
2. Click "Connect"

### Creating Risks

1. Navigate to the "🎯 Risks" tab
2. Fill in the risk form (name, level, categories, etc.)
3. Click "Create risk"

### Creating Influences

1. Navigate to the "🔗 Influences" tab
2. Select source and target risks
3. Set strength and confidence
4. Click "Create influence"

### Creating TPO Impacts

1. Navigate to the "📌 TPO Impacts" tab
2. Select a Strategic risk and a TPO
3. Set impact level
4. Click "Create TPO Impact"

### Creating Mitigations

1. Navigate to the "🛡️ Mitigations" tab
2. Enter name, type, and status
3. Click "Create Mitigation"

### Linking Mitigations to Risks

1. Navigate to the "💊 Risk Mitigations" tab
2. Select a mitigation and a risk
3. Set effectiveness level (Low/Medium/High/Critical)
4. Add description of how the mitigation addresses the risk
5. Click "Create Link"

### Visualizing Mitigations

By default, the application displays all elements including mitigations. To customize:

1. In the **📊 Visualization** tab, expand the **🛡️ Mitigation Filters** section
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

| Element                | Shape     | Color       | Notes                          |
| ---------------------- | --------- | ----------- | ------------------------------ |
| Strategic Risk         | Circle    | Purple      | Size varies by exposure        |
| Operational Risk       | Circle    | Blue        | Size varies by exposure        |
| Contingent Risk        | Square    | Level color | Dashed border                  |
| Legacy Risk            | Circle    | Level color | Gray dashed border, [L] prefix |
| TPO                    | Hexagon   | Yellow      | Reference as label             |
| Mitigation (Dedicated) | Rectangle | Green       | 🛡️ prefix                      |
| Mitigation (Inherited) | Rectangle | Blue        | 🛡️ prefix                      |
| Mitigation (Baseline)  | Rectangle | Purple      | 🛡️ prefix                      |

### Edge Types

| Relationship          | Color  | Style  | Notes                  |
| --------------------- | ------ | ------ | ---------------------- |
| Level 1 (Op→Strat)    | Red    | Solid  | Width by strength      |
| Level 2 (Strat→Strat) | Purple | Solid  | Width by strength      |
| Level 3 (Op→Op)       | Blue   | Solid  | Width by strength      |
| TPO Impact            | Blue   | Dashed | Width by impact level  |
| Mitigates             | Green  | Dashed | Width by effectiveness |

## 📝 Version History

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
