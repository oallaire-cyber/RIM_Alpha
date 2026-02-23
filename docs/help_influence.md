### 🔗 Influence Model

Models how risks propagate through the network.
Source risk **causes or amplifies** target risk.

---

**Influence Types (auto-determined):**

| Type | From → To | Meaning |
|------|-----------|---------|
| Level 1 | Operational → Business | Causes consequence |
| Level 2 | Business → Business | Amplifies impact |
| Level 3 | Operational → Operational | Contributes to |

---

**Strength Levels:**
- **Critical**: Direct, inevitable causation
- **Strong**: High probability of propagation
- **Moderate**: Likely contributes
- **Weak**: Possible minor contribution

---

**Analysis Features** *(all scope-aware)*:

| Analysis | What it reveals |
|----------|-----------------|
| 🔝 Top Propagators | Risks with highest downstream impact |
| ⚠️ Convergence Points | Where multiple threats converge |
| 🔥 Critical Paths | Strongest influence chains to TPOs |
| 🚧 Bottlenecks | Single points of failure |
| 📦 Clusters | Tightly interconnected risk groups |

> **Tip:** Use the Influence Explorer to traverse the network
> from any node. When a scope is active, only scoped nodes
> appear in the selection dropdown.
