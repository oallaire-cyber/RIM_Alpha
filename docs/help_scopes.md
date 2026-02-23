### 📐 Analysis Scopes

Scopes let you define **named subsets** of your risk graph
for focused analysis. All features respect scope boundaries.

---

**Creating a Scope:**
1. Open Configuration Manager (⚙️ Configuration page)
2. Go to **📐 Scopes** tab
3. Pick nodes, set name and color
4. Scope is saved in `schema.yaml`

---

**Selecting a Scope:**
- Sidebar → **📐 Analysis Scopes** expander
- Select one or more scopes (union of node IDs)
- Click **🌐 Full Graph** to clear

---

**Smart Expansion:**

When a scope is active, the system automatically includes:
- **Mitigations** connected to scoped risks
- **TPOs** connected to scoped risks
- **1-hop risk neighbors** (toggle "Show connected neighbors")

---

**Scoped Features:**

| Feature | When scope active |
|---------|-------------------|
| 📊 Statistics | Counts only scoped entities |
| ⚡ Exposure | Risks + connected mitigations only |
| 🔍 Influence Analysis | Scoped propagators, convergence, paths |
| 🛡️ Mitigation Analysis | Coverage gaps within scope |
| CRUD Tabs | List only scoped entities |
| Influence Explorer | Node picker shows scoped nodes |

> **Tip:** Scoped metrics may differ from Full Graph — this is
> expected because cross-boundary chains are excluded.
