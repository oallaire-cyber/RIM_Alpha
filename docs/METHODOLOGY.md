# 📐 RIM Methodology

The Risk Influence Map (RIM) methodology documentation, including concepts, formulas, and rationale.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Risk Architecture](#risk-architecture)
3. [Influence Model](#influence-model)
4. [Mitigation Model](#mitigation-model)
5. [Exposure Calculation](#exposure-calculation)
6. [Scoped Exposure Calculation](#scoped-exposure-calculation)
7. [Analysis Algorithms](#analysis-algorithms)
8. [Calibration & Validation](#calibration--validation)

---

## Core Concepts

### The Problem with Traditional Risk Registers

Traditional risk registers treat risks as **isolated items** in a spreadsheet:

```
| ID | Risk | Likelihood | Impact | Score |
|----|------|------------|--------|-------|
| R1 | Supply delay | 3 | 4 | 12 |
| R2 | Cost overrun | 2 | 5 | 10 |
```

**Problems**:
1. **No relationships**: Doesn't show R1 might cause R2
2. **Static scores**: Doesn't reflect how mitigations affect connected risks
3. **No hierarchy**: Mixes causes and consequences
4. **Siloed management**: Everyone manages "their" risks independently

### The RIM Solution

RIM transforms risk registers into **dynamic risk intelligence**:

```
   [OR-001: Supplier bankruptcy]
           │
           │ Level 1 (causes)
           ▼
   [SR-001: Supply chain disruption]──────► [TPO: Schedule]
           │
           │ Level 2 (amplifies)
           ▼
   [SR-002: Cost overrun]────────────────► [TPO: Budget]
```

**Benefits**:
1. **Visible relationships**: See how risks connect and amplify
2. **Dynamic scoring**: Mitigations affect entire chains
3. **Clear hierarchy**: Causes vs consequences
4. **Coordinated management**: Business vs operational ownership

---

## Risk Architecture

### Two-Level Hierarchy

| Level | Orientation | Focus | Managed By |
|-------|-------------|-------|------------|
| **Business** | Consequence | What could go wrong for the program | Program leadership |
| **Operational** | Cause | What activities could fail | Functional teams |

### Why Two Levels?

1. **Different management approaches**:
   - Business: Portfolio-level decisions, resource allocation
   - Operational: Process controls, technical mitigations

2. **Clear accountability**:
   - Leadership owns consequences
   - Teams own causes

3. **Reduced cognitive load**:
   - ~10-20 business risks for leadership
   - ~50-100 operational risks across teams

### Risk Categories

| Category | Scope | Examples |
|----------|-------|----------|
| **Programme** | Schedule, budget, resources | Delays, cost overruns, staffing |
| **Produit** | Technical performance | Design flaws, quality issues |
| **Industriel** | Manufacturing, facilities | Production capacity, tooling |
| **Supply Chain** | Suppliers, logistics | Vendor risks, material shortages |

### Risk Origins

| Origin | Definition | Management Approach |
|--------|------------|---------------------|
| **New** | Identified specifically for this program | Full ownership, active management |
| **Legacy** | Inherited from enterprise register or other programs | Acknowledge, may have limited control |

---

## Influence Model

### Influence Types

```
                    ┌──────────────┐
                    │     TPO      │
                    └──────▲───────┘
                           │ IMPACTS_TPO
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
┌────┴─────┐         ┌─────┴────┐         ┌─────┴────┐
│ Business│◄────────│ Business│◄────────│ Business│
│  Risk 1  │ Level 2 │  Risk 2  │ Level 2 │  Risk 3  │
└────▲─────┘         └──────────┘         └────▲─────┘
     │                                         │
     │ Level 1                                 │ Level 1
     │                                         │
┌────┴─────┐                            ┌─────┴────┐
│Operational│                            │Operational│
│  Risk A  │◄───── Level 3 ─────────────│  Risk B  │
└──────────┘                            └──────────┘
```

| Level | Direction | Meaning | Example |
|-------|-----------|---------|---------|
| **Level 1** | Operational → Business | Cause creates consequence | "Supplier bankruptcy causes supply disruption" |
| **Level 2** | Business → Business | Consequence amplifies consequence | "Supply disruption causes schedule delay" |
| **Level 3** | Operational → Operational | Cause contributes to cause | "Quality issue contributes to rework" |

### Influence Strength

| Strength | Score | Meaning |
|----------|-------|---------|
| **Critical** | 1.0 | Direct, unavoidable impact |
| **Strong** | 0.75 | Significant, likely impact |
| **Moderate** | 0.5 | Notable, possible impact |
| **Weak** | 0.25 | Minor, occasional impact |

### Confidence

How certain are we about this influence?

| Confidence | When to Use |
|------------|-------------|
| 0.9 - 1.0 | Documented, proven relationship |
| 0.7 - 0.8 | Expert judgment with evidence |
| 0.5 - 0.6 | Reasonable assumption |
| 0.3 - 0.4 | Speculative but plausible |

---

## Mitigation Model

### Mitigation Types

| Type | Source | Ownership | Example |
|------|--------|-----------|---------|
| **Dedicated** | Created for this program | Full | "Dual-source supplier strategy" |
| **Inherited** | From other programs/entities | Partial | "Enterprise vendor management process" |
| **Baseline** | Industry standards, regulations | External | "ISO 9001 quality system" |

### Why Multiple Types?

1. **Realistic coverage**: Not all controls are program-specific
2. **Dependency awareness**: Inherited/baseline may change without notice
3. **Effort allocation**: Focus effort on dedicated mitigations

### Effectiveness Model

Mitigations reduce risk exposure multiplicatively:

```
If Risk has mitigations M1 (70% effective) and M2 (50% effective):

Mitigation Factor = (1 - 0.70) × (1 - 0.50)
                  = 0.30 × 0.50
                  = 0.15

Residual = 15% of base exposure
```

**Why multiplicative?**
- **Diminishing returns**: Each additional mitigation has less marginal impact
- **Independence**: Mitigations work on different aspects
- **Realism**: You can't reduce to zero, asymptotic approach

### Effectiveness Scores

| Level | Reduction | Interpretation |
|-------|-----------|----------------|
| **Critical** | 90% | Near-complete risk elimination |
| **High** | 70% | Strong protection |
| **Medium** | 50% | Moderate reduction |
| **Low** | 30% | Minimal impact |

---

## Exposure Calculation

### Overview

The exposure calculation quantifies risk severity considering the entire network:

1. **Base Exposure**: Raw risk score
2. **Mitigation Factor**: How much mitigations reduce it
3. **Influence Limitation**: How upstream risks limit mitigation effectiveness
4. **Final Exposure**: Net risk after all factors

### Step-by-Step Formulas

#### 1. Base Exposure

```
Base Exposure = Likelihood × Impact

Where:
- Likelihood: 1-10 scale (1 = rare, 10 = certain)
- Impact: 1-10 scale (1 = negligible, 10 = catastrophic)
- Result: 1-100 scale
```

#### 2. Mitigation Factor

```
Mitigation Factor = ∏(1 - Effectiveness_i)

Where:
- Effectiveness_i: Reduction from each mitigation (0.3, 0.5, 0.7, or 0.9)
- Product of all (1 - Effectiveness) values
```

**Example**:
```
Risk with High (0.7) and Medium (0.5) mitigations:
Factor = (1 - 0.7) × (1 - 0.5) = 0.3 × 0.5 = 0.15
```

#### 3. Influence Limitation

**Core insight**: If upstream risks are unmitigated, downstream mitigations have limited effect.

```
Influence Limitation = Σ(Upstream_Residual_i × Strength_i) / Count

Where:
- Upstream_Residual_i: (0-1) how much of upstream risk remains
- Strength_i: Influence strength score (0.25, 0.5, 0.75, 1.0)
- Count: Number of upstream influences
```

**Example**:
```
Risk R2 influenced by R1 (Strong, 0.75 strength)
R1 has no mitigation, so Upstream_Residual = 1.0

Limitation = (1.0 × 0.75) / 1 = 0.75
```

#### 4. Effective Mitigation Factor

```
Effective Factor = Mit_Factor + (1 - Mit_Factor) × Limitation
```

**Interpretation**: 
- If Limitation = 0 (all upstream fully mitigated): Effective = Mit_Factor
- If Limitation = 1 (all upstream unmitigated): Effective = 1 (no benefit)

**Example**:
```
Mit_Factor = 0.15 (85% reduction from mitigations)
Limitation = 0.75 (upstream mostly unmitigated)

Effective = 0.15 + (1 - 0.15) × 0.75
         = 0.15 + 0.85 × 0.75
         = 0.15 + 0.6375
         = 0.7875 (only 21% effective reduction!)
```

#### 5. Final Exposure

```
Final Exposure = Base Exposure × Effective Factor
```

**Example**:
```
Base = 70 (Likelihood 7 × Impact 10)
Effective Factor = 0.7875

Final = 70 × 0.7875 = 55.125
```

### Global Metrics

#### Residual Risk Percentage

```
Residual Risk % = (Σ Final Exposures / Σ Base Exposures) × 100
```

**Interpretation**: "Overall, we've reduced risk to X% of what it would be without any mitigations."

#### Weighted Risk Score

```
Weighted Score = Σ(Final_i × Impact_i²) / Σ(Impact_i²)
```

**Why impact-squared weighting?**
- High-impact risks matter more
- Prevents low-impact risks from dominating the average
- Aligns with executive focus on severe outcomes

#### Max Single Exposure

```
Max Exposure = max(Final_i)
```

**Purpose**: Alert metric for worst-case individual risk

### Health Status Thresholds

| Weighted Score | Status | Action |
|----------------|--------|--------|
| 0-25 | Excellent | Maintain current controls |
| 26-50 | Good | Monitor for changes |
| 51-75 | Attention Needed | Review mitigation strategy |
| 76-100 | Critical | Immediate intervention required |

---

## Scoped Exposure Calculation

### Overview

When an **Analysis Scope** is active, the exposure calculation only considers entities within the scope boundary. This allows focused analysis of specific risk clusters without interference from unrelated parts of the graph.

### Pre-Filtering Logic

Before the exposure engine runs, all input data is filtered:

```
1. Risks       → Keep only risks whose id ∈ scope_node_ids
2. (Optional)  → Expand to 1-hop risk neighbors if "include_neighbors" enabled
3. Influences  → Keep only if source_id ∈ scope AND target_id ∈ scope
4. Mitigates   → Keep only if risk_id ∈ scope (find connected mitigations by relationship)
5. Mitigations → Keep only mitigations referenced by kept mitigates relationships
```

> **Important**: Mitigations are discovered via their `MITIGATES` relationships to scoped risks, not by checking if the mitigation ID is in the scope set. This ensures that mitigations linked to in-scope risks are always included.

### Neighbor Expansion

When "Show connected neighbors" is enabled:
- Risks directly connected to scoped risks via influence relationships are added
- This applies to the visualization, statistics, exposure, and all analysis panels
- Creates a more complete picture of the risk environment around the focused scope

### Implications

| Scenario | Effect |
|----------|--------|
| Risk has upstream influence from **outside** scope | Influence is **excluded** (unless neighbor expansion is on) |
| Mitigation connected to in-scope risk | Mitigation is **automatically included** via relationship discovery |
| Risk is in scope but has no mitigations | Risk appears **unmitigated** in scoped calculation |
| Two connected risks split across scopes | Their influence is **invisible** in either scope (unless neighbors enabled) |
| Neighbor expansion enabled | 1-hop risks and their mitigations are included in all calculations |

### Interpreting Scoped Metrics

> **Important**: Scoped **Residual Risk %** and **Weighted Risk Score** may differ from Full Graph values. This is expected and intentional.

- A **higher** scoped residual risk may indicate that the scope contains under-mitigated risks
- A **lower** scoped residual risk may indicate the scope is well-covered by internal mitigations
- For accurate cross-scope comparison, ensure scopes do not split tightly-coupled risk clusters

### Cross-Scope Mitigation Considerations

When a mitigation addresses risks in multiple scopes:

```
Scope A: [R1, R2]     ← M1 mitigates R1 → M1 auto-included
Scope B: [R3, R4]     ← M1 also mitigates R3 → M1 auto-included
Full Graph: [R1..R4]  ← M1 visible for both
```

- In **Scope A**, M1 only shows its effect on R1
- In **Scope B**, M1 only shows its effect on R3
- In **Full Graph**, M1 covers both R1 and R3

This ensures each scope's metrics are self-consistent.

---

## Analysis Algorithms

### Top Propagators

**Definition**: Risks with highest downstream impact on the network.

```
Propagation Score = Σ(Reachable_Downstream × Path_Weight)

Where:
- Reachable_Downstream: Number of risks reachable from this node
- Path_Weight: Product of influence strengths along path
```

**Use case**: "Which risks should we address first to reduce overall network exposure?"

### Convergence Points

**Definition**: Nodes receiving influences from multiple sources.

```
Convergence Score = Σ(Upstream_Paths) × Avg(Path_Strengths)
```

**Use case**: "Which risks are at the intersection of multiple threat vectors?"

### Critical Paths

**Definition**: Strongest influence chains from operational risks to TPOs.

**Algorithm**:
1. Find all paths from operational risks to TPOs
2. Calculate path strength = Π(Influence_Strengths)
3. Return top N strongest paths

**Use case**: "What are the most threatening paths to our objectives?"

### Bottlenecks

**Definition**: Nodes that appear in many critical paths.

```
Bottleneck Score = (Paths_Through_Node / Total_Paths) × Avg_Path_Strength
```

**Use case**: "Which nodes are single points of failure?"

### Risk Clusters

**Definition**: Tightly interconnected risk groups.

**Algorithm**:
1. Build undirected graph from influences
2. Find connected components
3. For each component, calculate density
4. Return high-density groups

**Use case**: "Which risks should be managed together as a unit?"

---

## Calibration & Validation

### Monte Carlo Simulator

The `calibration_simulator.py` tool validates the exposure model:

**Monte Carlo Mode**:
1. Generate N random risk networks
2. Calculate exposure for each
3. Analyze distribution of outcomes

**Mitigation Path Mode**:
1. Start with unmitigated network
2. Add mitigations progressively
3. Track exposure reduction curve

### Key Validation Questions

1. **Sensitivity**: How much does influence strength affect outcomes?
2. **Diminishing Returns**: Does the mitigation model show realistic diminishing returns?
3. **Influence Limitation**: Does upstream risk appropriately limit downstream effectiveness?

### Expected Behaviors

| Scenario | Expected Outcome |
|----------|------------------|
| Add mitigation to upstream risk | Downstream exposure should decrease |
| Increase influence strength | Target risk exposure should increase |
| Add multiple weak mitigations | Less effective than one strong mitigation |
| Fully mitigate all upstream | Downstream mitigations become fully effective |

### Model Limitations

1. **Linear influence**: Real relationships may be non-linear
2. **Independent mitigations**: Some may have dependencies
3. **Static analysis**: Doesn't model time dynamics
4. **Simplified strengths**: 4-level discrete scale

---

## References

### Industry Frameworks

- ISO 31000: Risk Management Guidelines
- PMI PMBOK: Project Risk Management
- COSO ERM: Enterprise Risk Management

### Academic Foundations

- Graph theory: Network centrality measures
- Decision analysis: Multi-criteria decision making
- Reliability engineering: Fault tree analysis

---

*Last updated: February 2026 | Version 2.6.1*
