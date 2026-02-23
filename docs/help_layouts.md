### 📐 Graph Layouts

Choose a layout algorithm to organize the risk network
visualization. Each layout emphasizes different relationships.

---

**Predefined Layouts:**

| Layout | Best for |
|--------|----------|
| 🌳 Hierarchical (Sugiyama) | Understanding flow, presentations |
| 📶 Layered | Seeing the TPO → Business → Operational hierarchy |
| 📊 Category Grid | Comparing risk categories (2×2 grid) |
| 🎯 TPO Cluster | Analyzing TPO impact groupings |

---

**Sugiyama Algorithm:**
1. Layer assignment based on RIM hierarchy
2. Crossing minimization (barycenter heuristic)
3. Coordinate assignment with connected-node alignment

---

**Manual Layout:**
1. Disable physics (⚙️ Graph Options)
2. Drag nodes to desired positions
3. Enable "📍 Position capture"
4. Click capture button on graph
5. Save in 💾 Layout Management

> **Tip:** Saved layouts persist across sessions.
> Use Hierarchical for stakeholder presentations.
