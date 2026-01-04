# 🎯 Risk Influence Map (RIM) - POC & Demo

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29+-red.svg)](https://streamlit.io)
[![Neo4j](https://img.shields.io/badge/neo4j-5.0+-green.svg)](https://neo4j.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A dynamic risk management application that visualizes risks and their interdependencies using graph theory and Neo4j.

## 🎯 Overview

The Risk Influence Map (RIM) is a proof-of-concept application designed for strategic risk management in complex programs, particularly in the nuclear energy sector. It enables:

- **Dynamic visualization** of risks and their relationships
- **Influence modeling** between risks (amplification, triggering, mitigation, correlation)
- **Complete risk lifecycle management** (CRUD operations)
- **Cascade impact analysis** through graph traversal
- **Strategic vs. operational risk differentiation**

## ✨ Key Features

### Risk Management
- Create, read, update, and delete risks
- Multi-dimensional risk attributes (category, probability, impact, status)
- Automatic risk scoring calculation
- Support for 8 risk categories (Cyber, Operational, Strategic, Financial, Compliance, Reputation, HR, Environmental)

### Influence Mapping
- Model four types of influences: Amplifies, Triggers, Mitigates, Correlates
- Weighted influence strength (1-10 scale)
- Bidirectional and cascade influence analysis
- Visual representation of influence chains

### Visualization
- Interactive graph visualization using PyVis
- Dynamic node sizing based on risk score
- Color-coded nodes by category or risk score
- Edge thickness proportional to influence strength
- Zoom, pan, and node selection capabilities

### Analytics
- Risk distribution by category
- Influence network statistics
- Top influencing and influenced risks
- Critical path identification

## 🚀 Quick Start

### Prerequisites

- **Docker** (for Neo4j database)
- **Python 3.9+**
- No admin rights required
- No external web server needed

### Installation

1. **Start Neo4j with Docker**

```bash
docker-compose up -d
```

Or manually:

```bash
docker run -d \
    --name neo4j-rim \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/risk2024secure \
    -v neo4j_rim_data:/data \
    neo4j:latest
```

2. **Install Python dependencies**

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Load demo data** (optional)

Access Neo4j Browser at `http://localhost:7474` and load `demo_data.cypher`

4. **Launch the application**

```bash
streamlit run app.py
```

Or use the startup scripts:
- Windows: `start.bat`
- Linux/Mac: `./start.sh`

The application opens automatically at `http://localhost:8501`

## 📊 Data Model

### Risk Node Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | String | Unique risk identifier |
| `category` | Enum | Risk category (Cyber, Operational, Strategic, etc.) |
| `probability` | Integer (1-10) | Likelihood of occurrence |
| `impact` | Integer (1-10) | Severity if occurs |
| `score` | Integer | Auto-calculated (probability × impact) |
| `status` | Enum | Active, Monitored, Mitigated, Closed |
| `description` | Text | Detailed risk description |

### Influence Relationship Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | Enum | AMPLIFIES, TRIGGERS, MITIGATES, CORRELATES |
| `strength` | Integer (1-10) | Influence intensity |
| `description` | Text | Explanation of the influence |

## 📈 Use Cases

### Cybersecurity Risk Analysis

Model attack chains and cascading impacts:

```
[Phishing Success] --TRIGGERS--> [Credential Compromise]
         |                              |
         |                              v
         +-------AMPLIFIES-------> [Lateral Movement]
                                        |
                                        v
                                 [Data Exfiltration]
                                        |
                                        v
                                 [Reputation Impact]
```

### Nuclear Program Risk Management

- Differentiate strategic vs. operational risks
- Model contingent risks dependent on Q3 2026 decisions
- Visualize risk dependencies across program phases
- Support governance decision-making

### Enterprise Risk Management

- Map business continuity risks
- Analyze supply chain vulnerabilities
- Track compliance and regulatory risks
- Identify risk concentration areas

## 🛠️ Configuration

### Neo4j Connection

Default configuration (modify in `app.py` if needed):

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "risk2024secure"
```

### Environment Variables (Optional)

```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password
```

## 📁 Project Structure

```
RIM_Alpha/
├── app.py                  # Main Streamlit application
├── demo_data.cypher        # Sample data for demonstration
├── docker-compose.yml      # Docker configuration for Neo4j
├── requirements.txt        # Python dependencies
├── start.sh               # Linux/Mac startup script
├── start.bat              # Windows startup script
├── README.md              # This file
├── USER_GUIDE.md          # Detailed user documentation
├── SETUP.md               # Installation and setup guide
└── .gitignore             # Git ignore file
```

## 🔍 Useful Cypher Queries

### Find Top Influencing Risks

```cypher
MATCH (r:Risk)-[i:INFLUENCES]->()
RETURN r.name, count(i) as outgoing_influences
ORDER BY outgoing_influences DESC
LIMIT 5
```

### Find Most Influenced Risks

```cypher
MATCH ()-[i:INFLUENCES]->(r:Risk)
RETURN r.name, count(i) as incoming_influences
ORDER BY incoming_influences DESC
LIMIT 5
```

### Identify Influence Chains

```cypher
MATCH path = (a:Risk)-[:INFLUENCES*1..3]->(b:Risk)
WHERE a <> b
RETURN path
LIMIT 20
```

### Calculate Cumulative Influence Score

```cypher
MATCH (r:Risk)
OPTIONAL MATCH (r)-[out:INFLUENCES]->()
OPTIONAL MATCH ()-[in:INFLUENCES]->(r)
RETURN r.name, 
       r.score as risk_score,
       sum(out.strength) as outgoing_influence,
       sum(in.strength) as incoming_influence
ORDER BY r.score DESC
```

## 🎓 Documentation

- [User Guide](USER_GUIDE.md) - Comprehensive usage documentation
- [Setup Guide](SETUP.md) - Detailed installation instructions
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute

## 🔮 Future Enhancements

- [ ] Import/Export CSV for risks and influences
- [ ] Impact propagation simulation
- [ ] Change history tracking
- [ ] Automatic residual risk calculation
- [ ] Integration with risk frameworks (EBIOS RM, ISO 27005)
- [ ] REST API for SIEM/SOAR integration
- [ ] Multi-user authentication and authorization
- [ ] Advanced analytics and reporting
- [ ] Layout persistence for graph visualization
- [ ] Risk scenario modeling

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📧 Contact

For questions or feedback about this POC:
- Open an issue in this repository
- Contact: [Your contact information]

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Powered by [Neo4j](https://neo4j.com)
- Graph visualization using [PyVis](https://pyvis.readthedocs.io)

---

**Note**: This is a proof-of-concept application. For production use, additional security, scalability, and governance features would be required.
