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
- All features adapt: statistics, exposure, influence/mitigation analysis, Data Management UI
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

**🏆 Top Objectives (TPOs)**
- ⬡ Gold hexagon visualization
- Cluster-based organization
- Impact level tracking (Low → Critical)

**⚠️ Contingent Risk Support**
- ◇ Hollow diamond for potential/contingent risks
- Decision timeline and activation conditions

**🔬 What-If Analysis**
- Toggle any mitigation ON/OFF in-memory — no database changes
- Instantly see EL + TRI deltas at portfolio and per-risk level
- Scope-constrained and lifecycle-aware
- "Include inactive risks" option for worst-case scenario exploration

> *Use What-If to answer "what if this control fails?" or to explore multi-mitigation scenarios in a live briefing.*

**📊 Mitigation Exposure View**
- Rank every in-scope mitigation by its **marginal EL and TRI contribution**
- Counterfactual computation: for each mitigation, calculates what the portfolio would look like without it
- Business-focused: filter by risk level, scope-aware, lifecycle-filtered by default
- Instantly surfaces critical controls and coverage gaps

> *Use Mitigation Exposure to prioritise control investment and identify single points of failure in your mitigation portfolio.*

**📋 Risk Templates**
- Define Generic Risk archetypes as reusable templates
- Instantiate a template to create a specific risk pre-filled with standard attributes
- Templates are excluded from exposure calculations and the graph canvas
- Traceable via `[:INSTANTIATES]` relationship in Neo4j

**⚠️ Threshold Alerts**
- Configurable EL and TRI thresholds per domain (set in schema YAML)
- Breach panel surfaced in the Exposure dashboard after each computation
- Scope-aware and lifecycle-aware — only active in-scope risks are evaluated

**🖼️ Graph Visual Behaviour**
- Four presets: Clean / Analysis / Lifecycle Audit / Sandbox Edit
- Per-status lifecycle opacity sliders (Watching, Suppressed, Accepted, Closed)
- Quadrant border encoding: coloured borders by risk quadrant (Critical / Frequency / Severity / Marginal)
- Save as Schema Default — persists settings to `graph_visual_config` in schema YAML

**🎲 Lifecycle-Aware Simulation (Worst-Case Canvas)**
- Re-activates accepted / watching / suppressed / closed risks in-memory to reveal latent tail exposure
- Shows count of re-activated risks; results labelled `[Worst-Case]` in Saved Results
- Available in both Scope-Based and TRI α Calibration modes

**📐 TRI α Calibration**
- Sweeps TRI exponent α over a configurable range (default 1.0 → 3.0)
- Monte Carlo per α value: computes TRI = L × S^α and classifies into quadrants
- Output: calibration chart (Mean TRI ±1σ, P95), stacked quadrant distribution, calibration report
- Recommends domain-appropriate α based on selected target quadrant profile

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
