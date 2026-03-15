### 📐 Analysis Scopes

Scopes let you define **named subsets** of your risk graph
for focused analysis. All features respect scope boundaries.

---

**Creating a Scope:**
1. Open Configuration Manager (⚙️ Configuration page)
2. Go to **📐 Scopes** tab
3. Fill in Scope ID, Display Name, color, and description
4. Use the **Advanced Filter Panel** to find and select risks:
   - 🔍 Search by partial name
   - Filter by **Level** (Business / Operational)
   - Filter by **Subtype** (schema-driven)
   - Use **✅ Select All Filtered** / **🔲 Deselect All Filtered** for bulk actions
5. Scope is saved in `schema.yaml`

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
| Data Management UI | List only scoped entities; 🔍 Scope Definition panel to add/remove risks |
| Influence Explorer | Node picker shows scoped nodes |

> **Tip:** Scoped metrics may differ from Full Graph — this is
> expected because cross-boundary chains are excluded.
