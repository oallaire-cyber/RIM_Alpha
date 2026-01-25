# 🎯 Risk Influence Map (RIM) - Phase 1

A dynamic risk management visualization system built with Streamlit and Neo4j, designed for strategic and operational risk mapping in complex programs like SMR (Small Modular Reactor) nuclear projects.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Overview

The Risk Influence Map (RIM) is an innovative methodology for visualizing and managing the complex relationships between risks in large-scale programs. It distinguishes between:

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
- Quick filter presets:
  - 🌐 Full View
  - 🟣 Strategic Focus
  - 🔵 Operational Focus
  - ✅ Active Risks Only
  - ⚠️ Contingent Risks
  - 🎯 Risks Only
  - 🆕 New Risks Only
  - 📜 Legacy Risks Only
  - 🛡️ Risks + Mitigations
  - 🗺️ Full Map (everything)
- Multi-select filters with All/None buttons
- **Origin filter** (New/Legacy)
- **Mitigation filters** (by type and status)
- Filter validation and summary display
- Persistent filter state

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
   streamlit run app_alpha.py
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
rim-alpha/
├── app_alpha.py             # Main Streamlit application
├── requirements.txt         # Python dependencies
├── demo_data_loader.cypher  # Cypher script to load demo data
├── bulk_import_template.cypher  # Template for bulk data imports
├── graph_layouts.json       # Saved layout positions (auto-generated)
└── README.md               # This file
```

## 🎮 Usage

### Creating Risks

1. Navigate to the **🎯 Risks** tab
2. Fill in the risk details:
   - Name (required)
   - Level: Strategic or Operational
   - **Origin: New (program-specific) or Legacy (inherited)**
   - Categories (multi-select)
   - Description
   - Status: Active, Contingent, or Archived
   - Probability and Impact (for exposure calculation)
3. Click "Create Risk"

### Creating Influences

1. Navigate to the **🔗 Influences** tab
2. Select source and target risks
3. Configure strength and confidence
4. Add description
5. Click "Create Influence"

### Creating TPOs

1. Navigate to the **🏆 TPOs** tab
2. Enter reference code (e.g., TPO-01)
3. Select cluster category
4. Add name and description
5. Click "Create TPO"

### Linking Risks to TPOs

1. Navigate to the **📌 TPO Impacts** tab
2. Select a strategic risk and a TPO
3. Set impact level
4. Click "Create Impact"

### Creating Mitigations

1. Navigate to the **🛡️ Mitigations** tab
2. Fill in mitigation details:
   - Name (required)
   - Type: Dedicated, Inherited, or Baseline
   - Status: Proposed, In Progress, Implemented, or Deferred
   - Owner
   - Source Entity (for Inherited/Baseline types)
   - Description
3. Click "Create Mitigation"

### Linking Mitigations to Risks

1. Navigate to the **💊 Risk Mitigations** tab
2. Select a mitigation and a risk
3. Set effectiveness level (Low/Medium/High/Critical)
4. Add description of how the mitigation addresses the risk
5. Click "Create Link"

### Visualizing Mitigations

1. In the **📊 Visualization** tab sidebar
2. Enable "🟢 Show Mitigations" checkbox
3. Optionally filter by mitigation type and status
4. Or use the "🛡️ Risks + Mitigations" or "🗺️ Full Map" preset

### Using Layouts

1. In the **📊 Visualization** tab, arrange nodes as desired
2. Disable physics to freeze positions
3. Enable "Position capture"
4. Click "📍 Capture Positions" on the graph
5. Click "📋 Copy to Clipboard"
6. Paste in the sidebar text area
7. Name and save your layout

### Import/Export

**Export:**
1. Go to **📥 Import/Export** tab
2. Click "Generate export"
3. Download the Excel file (now includes Mitigations and Mitigates sheets)

**Import:**
1. Prepare an Excel file with sheets: Risks, TPOs, Influences, TPO_Impacts, Mitigations, Mitigates
2. Upload the file
3. Review the detailed import log

## 🔧 Configuration

### Neo4j Connection

Default connection settings:
- URI: `bolt://localhost:7687`
- Username: `neo4j`
- Password: (your password)

### Filter Presets

Built-in presets:
| Preset | Description |
|--------|-------------|
| 🌐 Full View | All risks and TPOs |
| 🟣 Strategic Focus | Strategic risks + TPOs only |
| 🔵 Operational Focus | Operational risks only |
| ✅ Active Risks Only | Excludes contingent risks |
| ⚠️ Contingent Risks | Future/contingent risks only |
| 🎯 Risks Only | All risks, no TPOs |
| 🆕 New Risks Only | Program-specific new risks |
| 📜 Legacy Risks Only | Inherited/Enterprise level risks |
| 🛡️ Risks + Mitigations | Show risks with mitigations (no TPOs) |
| 🗺️ Full Map | Everything: Risks, TPOs, and Mitigations |

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

| Element | Shape | Color | Notes |
|---------|-------|-------|-------|
| Strategic Risk | Circle | Purple | Size varies by exposure |
| Operational Risk | Circle | Blue | Size varies by exposure |
| Contingent Risk | Square | Level color | Dashed border |
| Legacy Risk | Circle | Level color | Gray dashed border, [L] prefix |
| TPO | Hexagon | Yellow | Reference as label |
| Mitigation (Dedicated) | Rectangle | Green | 🛡️ prefix |
| Mitigation (Inherited) | Rectangle | Blue | 🛡️ prefix |
| Mitigation (Baseline) | Rectangle | Purple | 🛡️ prefix |

### Edge Types

| Relationship | Color | Style | Notes |
|--------------|-------|-------|-------|
| Level 1 (Op→Strat) | Red | Solid | Width by strength |
| Level 2 (Strat→Strat) | Purple | Solid | Width by strength |
| Level 3 (Op→Op) | Blue | Solid | Width by strength |
| TPO Impact | Blue | Dashed | Width by impact level |
| Mitigates | Green | Dashed | Width by effectiveness |

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
