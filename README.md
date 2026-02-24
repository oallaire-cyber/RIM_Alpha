# 🎯 Risk Influence Map (RIM)

A dynamic risk management visualization system built with Streamlit and Neo4j, designed for business and operational risk mapping in complex programs (SMR nuclear projects, aerospace, etc.).

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 What is RIM?

The Risk Influence Map transforms static risk registers into **dynamic risk intelligence** by modeling:

- **Influence relationships** between risks (how one risk amplifies another)
- **Mitigation effectiveness** with diminishing returns and upstream limitations
- **Quantitative exposure calculation** that considers the entire risk network
- **Visual semantics** where shapes and colors convey meaning instantly

| Entity | Shape | Purpose |
|--------|-------|---------|
| Business Risk | ◆ Diamond | Consequence-oriented, managed by leadership |
| Operational Risk | ● Circle | Cause-oriented, managed by functional teams |
| Mitigation | 🛡️ Rounded Box | Controls and protective actions |
| TPO | ⬡ Hexagon | Top Program Objectives at risk |
| Custom Entities | 📦 Configurable | User-defined types (e.g., Asset, Threat Actor) |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker (for Neo4j)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/rim.git
cd rim

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Neo4j
docker-compose up -d

# Run the application
streamlit run app.py
```

### First Steps

1. Open http://localhost:8501 in your browser
2. Connect to Neo4j (default credentials: neo4j/password)
3. Navigate between **Home**, **Configuration**, and **Simulation** via the sidebar
4. Load demo data via **Import/Export** tab on the Home page
5. Explore the risk network in the **Visualization** tab

## ✨ Key Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Two-Level Risk Architecture** | Business (consequence) vs Operational (cause) risks |
| **Influence Mapping** | Three influence levels with strength/confidence scoring |
| **Mitigation Management** | Dedicated/Inherited/Baseline types with effectiveness tracking |
| **Exposure Calculation** | Quantitative scoring with influence limitation model |
| **TPO Impact Tracking** | Link risks to program objectives |
| **Analysis Scopes** | Define named node subsets for focused analysis with neighbor expansion, scoped statistics, exposure, influence and mitigation analysis |

### Visualization

- **Semantic shapes**: Instant recognition without reading labels
- **Heat map coloring**: Exposure-based gradient (green → red)
- **Multiple layouts**: Hierarchical (Sugiyama), Layered, Category-based, Cluster
- **Interactive exploration**: Click nodes, filter by criteria, save layouts

### Analysis Tools

- **Influence Analysis**: Top propagators, convergence points, critical paths, bottlenecks, clusters (scope-aware)
- **Mitigation Analysis**: Coverage gaps, treatment explorer, impact analysis (scope-aware)
- **Exposure Calculation**: Quantitative scoring with influence limitation model (scope-aware with neighbor expansion)
- **Monte Carlo Simulator**: Model validation and sensitivity analysis

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Complete feature documentation |
| [Architecture](docs/ARCHITECTURE.md) | Code structure and module design |
| [Methodology](docs/METHODOLOGY.md) | RIM methodology and formulas |
| [Visual Design](docs/VISUAL_DESIGN.md) | Shape/color semantics reference |
| [Configuration Manager](docs/CONFIGURATION_MANAGER.md) | Schema management app |
| [Calibration Simulator](docs/CALIBRATION_SIMULATOR.md) | Monte Carlo validation tool |
| [Changelog](CHANGELOG.md) | Version history |

## 🏗️ Project Structure

```
rim/
├── app.py                    # Thin entry point (~60 lines)
├── config/                   # Application settings
│   ├── settings.py           # Hardcoded defaults
│   └── schema_loader.py      # YAML schema system
├── schemas/                  # Schema configurations
│   ├── default/              # SMR nuclear schema
│   └── it_security/          # Cybersecurity schema
├── database/                 # Neo4j connection and queries
│   └── queries/              # Cypher query modules
├── models/                   # Data models and enumerations
├── services/                 # Business logic
│   ├── exposure_calculator.py
│   ├── influence_analysis.py
│   └── mitigation_analysis.py
├── ui/                       # Streamlit UI components
│   ├── home.py               # Home page rendering (dashboard, viz, analysis)
│   ├── panels/               # Analysis panels
│   └── tabs/                 # Tab page renderers
├── visualization/            # PyVis graph rendering
│   ├── node_styles.py        # Semantic shape system
│   ├── edge_styles.py        # Relationship visualization
│   └── colors.py             # Color palette
├── pages/                    # Streamlit multi-page navigation
│   ├── 1_⚙️_Configuration.py # Schema and data management
│   └── 2_🎲_Simulation.py    # Monte Carlo calibration
├── utils/                    # Helper functions
│   ├── state_manager.py      # Centralized session state management
│   ├── db_manager.py         # Shared singleton connection
│   └── markdown_loader.py    # Cached docs/*.md file loader
├── docs/                     # Documentation (loaded at runtime for help section)
├── tests/                    # Test suite
└── requirements.txt
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=models --cov=utils --cov=services

# Run specific module tests
python -m pytest tests/test_enums.py -v
python -m pytest tests/test_risk.py -v
```

### Test Coverage

| Module | Test File | Coverage |
|--------|-----------|----------|
| `models/enums.py` | `test_enums.py` | ✓ Complete |
| `models/risk.py` | `test_risk.py` | ✓ Complete |
| `models/mitigation.py` | `test_mitigation.py` | ✓ Complete |
| `models/tpo.py` | `test_tpo.py` | ✓ Complete |
| `models/relationships.py` | `test_relationships.py` | ✓ Complete |
| `utils/helpers.py` | `test_helpers.py` | ✓ Complete |
| `utils/state_manager.py` | `test_state_manager.py` | ✓ Complete |
| `services/exposure_calculator.py` | `test_exposure_calculator.py` | Partial |
| `services/influence_analysis.py` | `test_influence_analysis.py` | Partial |
| `services/mitigation_analysis.py` | `test_mitigation_analysis.py` | Partial |
| `config/schema_loader.py` (scopes) | `test_scopes.py` | ✓ Complete |
| `ui/filters.py` (scopes) | `test_scopes.py` | ✓ Complete |
| `database/manager.py` (scoped exposure) | `test_scopes.py` | ✓ Complete |

## 🔧 Configuration

### Neo4j Connection

Default connection (can be changed in sidebar):
- URI: `bolt://localhost:7687`
- User: `neo4j`
- Password: Set in docker-compose.yml

### Environment Variables

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## 📊 Demo Data

RIM ships with a fully integrated demo package combining two datasets:

### SNR Nuclear Program (`demo_data_loader_en.cypher`)
- 15 Business Risks (RS-01–08) + Operational Risks (RO-01–07)
- Multiple influence chains, mitigation scenarios, and TPO impact mappings
- Pre-configured `snr_demo` scope in `schemas/default/schema.yaml`

### TC01-TC07 Test Cases (`demo_tc_dataset.cypher`)
- **37 risks**, **25 mitigations**, **18 influences**, **2 TPOs**, **3 TPO impacts**
- 7 scenarios (baseline, propagation, convergence, mitigation effectiveness, etc.)
- UUID v5 deterministic IDs — stable across reloads, no post-import fix-up needed
- Entities prefixed `[TCxx]` to coexist with SNR data
- 7 pre-configured scopes (`tc01_baseline` … `tc07_influence_strengths`)

### Loading the Demo

**Option A — Reset Demo Data button (recommended)**
1. Go to **⚙️ Configuration** → **📊 Data Management** tab
2. Tick the confirmation checkbox
3. Click **🔄 Reset Demo Data** — wipes the database and reloads both datasets

**Option B — Manual Excel import**
Import `test_datasets/DEMO_Complete.xlsx` via **Import/Export** → **Import from Excel**.

After loading, activate any of the 8 pre-configured scopes in the sidebar **📐 Analysis Scopes** expander, or select all 8 to view the full combined graph.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Application framework
- [Neo4j](https://neo4j.com/) - Graph database
- [PyVis](https://pyvis.readthedocs.io/) - Network visualization

## 📞 Contact

For questions about the RIM methodology, open an issue on GitHub.

---

**Current Version**: v2.10.0 | See [CHANGELOG.md](CHANGELOG.md) for history
