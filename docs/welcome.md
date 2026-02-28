### What is RIM?

The **Risk Influence Map (RIM)** transforms static risk registers into **dynamic risk
intelligence** by modeling how risks influence each other, how mitigations reduce exposure,
and which program objectives are at stake.

---

### 🧩 Core Capabilities

**🎯 Two-Level Risk Architecture**
- **Business Risks** (◆ Diamond): Consequence-oriented, managed by program leadership
- **Operational Risks** (● Circle): Cause-oriented, managed by functional teams
- **Origin Tracking**: Distinguish New (program-specific) from Legacy (inherited) risks

> *Why two levels?* Business risks represent "what could go wrong" at the program level.
> Operational risks represent "why it could go wrong" at the team level.
> Influence links connect the two, creating a traceable causal network.*

**🔗 Influence Mapping**
- Level 1: Operational → Business *(causes consequence)*
- Level 2: Business → Business *(amplifies impact)*
- Level 3: Operational → Operational *(contributes to)*
- Each influence has strength and confidence scoring

> *Influences are the backbone of RIM. They model how addressing one risk
> can reduce exposure across the entire network.*

**⚡ Exposure Calculation**
- Base exposure = Likelihood × Impact (1-100 scale)
- Mitigation factor with **diminishing returns** (realistic stacking)
- Upstream **influence limitation** (unresolved causes limit downstream fixes)
- Weighted risk score for executive reporting

> *The influence limitation model captures a real-world truth: fixing symptoms
> without addressing root causes has limited effect.*

**📐 Analysis Scopes**
- Define named subsets of the risk graph for **focused analysis**
- Smart expansion: auto-includes connected mitigations, TPOs, and optional risk neighbors
- All features adapt: statistics, exposure, influence/mitigation analysis, CRUD tabs
- Multi-scope union for cross-area comparison

> *Scopes let you prepare focused briefings per stakeholder, domain, or risk cluster
> without losing the ability to analyze the full graph.*

**🛡️ Mitigation Management**
- **Dedicated** (teal): Program-specific controls
- **Inherited** (blue): From corporate or other programs
- **Baseline** (purple): Standards, regulations, best practices
- Coverage gap analysis with high-priority flagging

> *The mitigation analysis cross-references influence analysis to flag unmitigated
> risks that are also top propagators, convergence points, or bottlenecks.*

**🏆 Top Program Objectives (TPOs)**
- ⬡ Gold hexagon visualization
- Cluster-based organization
- Impact level tracking (Low → Critical)

**⚠️ Contingent Risk Support**
- ◇ Hollow diamond for potential/contingent risks
- Decision timeline and activation conditions

**📊 Import/Export**
- Full Excel import/export
- Layout save/load for presentations

---

### 🎨 Visual Quick Reference

| Element | Shape | Meaning |
|---------|-------|---------|
| ◆ Purple | Diamond | Business Risk |
| ● Blue | Circle | Operational Risk |
| ◇ Outlined | Diamond | Contingent Risk |
| 🛡️ Teal/Blue/Purple | Rounded Box | Mitigation |
| ⬡ Gold | Hexagon | TPO |
| → Standard arrow | Solid line | Influence (risk → risk) |
| ⊣ Bar-end arrow | Dashed line | Mitigation link (mit → risk) |
| ▷ Vee arrow | Dotted line | TPO Impact (risk → TPO) |

---

*See sidebar **❓ Help** for detailed feature documentation.*
