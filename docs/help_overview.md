### 🎯 RIM Overview

The **Risk Influence Map** transforms static risk registers into
**dynamic risk intelligence** by modeling relationships between:

- **Business Risks** (◆ Diamond): Consequence-oriented, managed by leadership
- **Operational Risks** (● Circle): Cause-oriented, managed by teams  
- **TPOs** (⬡ Hexagon): Top Program Objectives at risk
- **Mitigations** (🛡️ Box): Controls and protective actions

---

**Core Capabilities:**

| Capability | What it does |
|------------|--------------|
| 🔗 Influence mapping | Models how risks amplify each other across the network |
| ⚡ Exposure calculation | Quantifies composite risk score with mitigation diminishing returns |
| 📐 Analysis scopes | Focus all analysis on a named subset of nodes |
| 🛡️ Mitigation analysis | Coverage gaps, treatment effectiveness, high-priority flags |
| 🎯 TPO tracking | Links risks to program objectives with impact levels |
| 📊 Statistics | Live dashboard adapts to active scope |
| ♻️ Lifecycle engine | 6-state risk lifecycle with auto-acceptance, trigger review, and archive alerts |
| 🔬 What-If Analysis | Toggle mitigations ON/OFF in-memory; observe EL + TRI deltas without DB writes |

---

**Influence Types (auto-determined by node levels):**
- **Level 1** (red): Operational → Business — *causal link*
- **Level 2** (purple): Business → Business — *amplification*
- **Level 3** (blue): Operational → Operational — *contribution*
