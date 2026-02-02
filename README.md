# 🎯 Risk Influence Map (RIM)

A dynamic risk management visualization system built with Streamlit and Neo4j, designed for strategic and operational risk mapping in complex programs (SMR nuclear projects, aerospace, etc.).

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
| Strategic Risk | ◆ Diamond | Consequence-oriented, managed by leadership |
| Operational Risk | ● Circle | Cause-oriented, managed by functional teams |
| Mitigation | 🛡️ Rounded Box | Controls and protective actions |
| TPO | ⬡ Hexagon | Top Program Objectives at risk |

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
3. Load demo data via **Import/Export** tab
4. Explore the risk network in the **Visualization** tab

## ✨ Key Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Two-Level Risk Architecture** | Strategic (consequence) vs Operational (cause) risks |
| **Influence Mapping** | Three influence levels with strength/confidence scoring |
| **Mitigation Management** | Dedicated/Inherited/Baseline types with effectiveness tracking |
| **Exposure Calculation** | Quantitative scoring with influence limitation model |
| **TPO Impact Tracking** | Link risks to program objectives |

### Visualization

- **Semantic shapes**: Instant recognition without reading labels
- **Heat map coloring**: Exposure-based gradient (green → red)
- **Multiple layouts**: Hierarchical (Sugiyama), Layered, Category-based, Cluster
- **Interactive exploration**: Click nodes, filter by criteria, save layouts

### Analysis Tools

- **Influence Analysis**: Top propagators, convergence points, critical paths, bottlenecks, clusters
- **Mitigation Analysis**: Coverage gaps, treatment explorer, impact analysis
- **Monte Carlo Simulator**: Model validation and sensitivity analysis

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Complete feature documentation |
| [Architecture](docs/ARCHITECTURE.md) | Code structure and module design |
| [Methodology](docs/METHODOLOGY.md) | RIM methodology and formulas |
| [Visual Design](docs/VISUAL_DESIGN.md) | Shape/color semantics reference |
| [Changelog](CHANGELOG.md) | Version history |

## 🏗️ Project Structure

```
rim/
├── app.py                    # Main Streamlit application (1,193 lines)
├── calibration_simulator.py  # Monte Carlo validation tool
├── config/                   # Application settings
├── database/                 # Neo4j connection and queries
│   └── queries/              # Cypher query modules
├── models/                   # Data models and enumerations
├── services/                 # Business logic
│   ├── exposure_calculator.py
│   ├── influence_analysis.py
│   └── mitigation_analysis.py
├── ui/                       # Streamlit UI components
│   ├── panels/               # Analysis panels
│   └── tabs/                 # Tab page renderers
├── visualization/            # PyVis graph rendering
│   ├── node_styles.py        # Semantic shape system
│   ├── edge_styles.py        # Relationship visualization
│   └── colors.py             # Color palette
├── utils/                    # Helper functions
└── docs/                     # Documentation
```

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

Load the `Apex Nuclear Systems` demo dataset to explore:
- 15+ Strategic Risks
- 30+ Operational Risks
- Multiple influence chains
- Mitigation coverage scenarios
- TPO impact mappings

Import via **Import/Export** → **Import from Excel** using `demo_data_apex.xlsx`.

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

**Current Version**: v2.2.0 | See [CHANGELOG.md](CHANGELOG.md) for history
