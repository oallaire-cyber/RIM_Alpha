# Risk Influence Map - Quick Reference Card

## 🚀 Quick Start

```bash
# Start everything (Windows)
start.bat

# Start everything (Linux/Mac)
./start.sh

# Access application
http://localhost:8501

# Access Neo4j Browser
http://localhost:7474
Username: neo4j
Password: risk2024secure
```

## 🎯 Core Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **Risk** | Potential event with probability & impact | "Data Breach" (P:7, I:9) |
| **Influence** | How one risk affects another | "Phishing → Credential Compromise" |
| **Score** | Risk severity (P × I) | 7 × 9 = 63 |

## 🔗 Influence Types

| Type | Meaning | Example |
|------|---------|---------|
| **TRIGGERS** | Causes another risk | Phishing → Data Breach |
| **AMPLIFIES** | Increases impact/probability | Downtime → Reputation Damage |
| **MITIGATES** | Reduces impact/probability | Training → Phishing Risk |
| **CORRELATES** | Occurs together | Economic Crisis ↔ Budget Cuts |

## 🎨 Risk Categories

- 🔴 **Cyber**: Technical security risks
- 🔵 **Operational**: Business operations
- 🟣 **Strategic**: Long-term planning
- 🟠 **Financial**: Money & resources
- 🟢 **Compliance**: Legal & regulatory
- 🟡 **Reputation**: Public perception
- 🟤 **HR**: People & culture
- 🔷 **Environmental**: Ecological impact

## 📊 Navigation

| Tab | Purpose | Key Actions |
|-----|---------|-------------|
| **Dashboard** | Overview & metrics | View stats, quick viz |
| **Visualization** | Interactive graph | Color by category/score, explore network |
| **Risks** | Manage risks | Create, edit, delete risks |
| **Influences** | Manage relationships | Create, view, delete influences |
| **Analytics** | Insights & stats | Top risks, distribution |

## 🎮 Visualization Controls

| Action | How To |
|--------|--------|
| **Pan** | Click + drag background |
| **Zoom** | Mouse wheel |
| **Select Node** | Click on risk |
| **Move Node** | Drag individual risk |
| **Details** | Hover over node/edge |
| **Color Mode** | Toggle "Color by" option |

## 🎯 Scoring Guide

### Probability Scale (1-10)
- **1-2**: Very unlikely (<5%)
- **3-4**: Unlikely (5-25%)
- **5-6**: Possible (25-50%)
- **7-8**: Likely (50-75%)
- **9-10**: Very likely (>75%)

### Impact Scale (1-10)
- **1-2**: Negligible
- **3-4**: Minor
- **5-6**: Moderate
- **7-8**: Major
- **9-10**: Critical

### Risk Severity (Score)
- **🟢 <40**: Low risk
- **🟠 40-69**: Medium risk
- **🔴 ≥70**: High risk

## 💡 Best Practices

### Naming Risks
✅ **Good**: "Ransomware Attack on Production Systems"  
❌ **Bad**: "Cyber Risk #1"

### Influence Strength
- **1-3**: Weak connection
- **4-6**: Moderate connection
- **7-9**: Strong connection
- **10**: Near-certain connection

### Demo Tips
1. Start with 5-10 risks for clarity
2. Create a logical attack chain
3. Use contrasting categories
4. Highlight cascade effects
5. Show both AMPLIFIES and MITIGATES

## 🔍 Common Cypher Queries

### View All Risks
```cypher
MATCH (r:Risk)
RETURN r
ORDER BY r.score DESC
```

### Find Attack Chains
```cypher
MATCH path = (a:Risk)-[:INFLUENCES*1..3]->(b:Risk)
WHERE a.category = 'Cyber'
RETURN path
```

### Calculate Total Risk Exposure
```cypher
MATCH (r:Risk)
RETURN sum(r.score) as total_exposure,
       avg(r.score) as avg_risk,
       count(r) as risk_count
```

### Find Most Connected Risks
```cypher
MATCH (r:Risk)
OPTIONAL MATCH (r)-[out:INFLUENCES]->()
OPTIONAL MATCH ()-[in:INFLUENCES]->(r)
RETURN r.name,
       count(out) as influences_out,
       count(in) as influences_in,
       count(out) + count(in) as total_connections
ORDER BY total_connections DESC
LIMIT 5
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to Neo4j | Check Docker is running, wait 15s after start |
| Blank graph | Ensure risks exist, refresh page |
| Port 8501 in use | Close other Streamlit apps or change port |
| "Neo4j auth failed" | Verify password in docker-compose.yml |

## 📁 File Structure

```
RIM_Alpha/
├── app.py              # Main application
├── demo_data.cypher    # Sample data
├── docker-compose.yml  # Neo4j config
├── requirements.txt    # Python deps
├── start.sh / .bat     # Startup scripts
├── README.md           # Overview
├── USER_GUIDE.md       # Detailed docs
└── SETUP.md            # Installation
```

## 🎬 Demo Workflow

1. **Introduction** (2 min)
   - What is RIM
   - Why graph databases
   - Use cases

2. **Dashboard** (1 min)
   - Show statistics
   - Overview of risk landscape

3. **Create Risks** (3 min)
   - Add 2-3 risks live
   - Explain scoring
   - Show different categories

4. **Create Influences** (3 min)
   - Connect risks
   - Show different types
   - Explain strength

5. **Visualization** (5 min)
   - Show full graph
   - Highlight cascade effects
   - Toggle color modes
   - Demonstrate interaction

6. **Analytics** (2 min)
   - Top influencing risks
   - Category distribution
   - Strategic insights

7. **Q&A** (5 min)
   - Answer questions
   - Discuss applications
   - Next steps

## 🎯 Key Messages for Demo

- **Dynamic vs Static**: Traditional registers vs living model
- **Relationships Matter**: Not just individual risks
- **Cascade Analysis**: See ripple effects
- **Strategic Tool**: Supports decision-making
- **Flexible**: Adaptable to any risk domain

## 📞 Quick Support

**Neo4j Issues**: http://localhost:7474  
**Application Issues**: Check terminal output  
**Data Issues**: Use Neo4j Browser to query directly  
**Performance**: Limit to <100 nodes for demos

---

**💡 Pro Tip**: Have demo_data.cypher ready to reload if needed during demo!

**🎯 Remember**: It's about relationships, not just individual risks!
