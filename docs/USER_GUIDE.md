# 📖 RIM User Guide

Complete documentation for the Risk Influence Map application.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Risk Management](#risk-management)
3. [Influence Mapping](#influence-mapping)
4. [Mitigation Management](#mitigation-management)
5. [Top Objective Management](#top-objective-management)
6. [Exposure Calculation](#exposure-calculation)
7. [Analysis Scopes](#analysis-scopes)
8. [Visualization](#visualization)
9. [Analysis Tools](#analysis-tools)
10. [What-If Analysis](#what-if-analysis)
11. [Mitigation Exposure View](#mitigation-exposure-view)
12. [Risk Lifecycle Engine](#risk-lifecycle-engine)
13. [Risk Templates](#risk-templates)
14. [Threshold Alerts](#threshold-alerts)
15. [Import/Export](#importexport)
16. [Filter System](#filter-system)

---

## Getting Started

### Connecting to Neo4j

1. Start the Neo4j database: `docker-compose up -d`
2. Open the RIM application: `streamlit run app.py`
3. The application now uses a **multi-page layout**:
   - **Home**: Dashboard and Graph Visualization
   - **Configuration**: Schema and Database Management
   - **Simulation**: Calibration Simulator
4. In the sidebar (on any page), verify connection settings:
   - **URI**: `bolt://localhost:7687`
   - **Username**: `neo4j`
   - **Password**: Your configured password
5. Click **Connect** (Connection persists across pages)

### Interface Overview

The application has four pages plus the main dashboard:

| Area | Location | Purpose |
|------|----------|---------|
| **Sidebar** | Left panel | UI Complexity Toggle, Connection, filters, legend, settings |
| **Data Management** | Sidebar Link | Navigate to the Data Management page to manage all graph entities |
| **Main Content** | Center | Forms, tables, visualization |

### UI Complexity Modes

RIM allows users to toggle the interface complexity from the **top of the sidebar**:

- **Advanced Mode**: The full experience. Shows all tabs, advanced filters, and renders every node/edge in the graph regardless of exposure. Intended for Risk Managers and Analysts.
- **Simple Mode**: A streamlined experience for non-technical stakeholders. Hides advanced tabs (Mitigations, Influences, Config, etc.), collapses complex filters, and brings focus to the graph by "ghosting" (making transparent) all nodes except the Top risks and TPOs.

### Navigation

The application uses a multi-page routing structure:

| Page | Purpose |
|------|---------|
| 📊 **Home** | Interactive risk visualization and analysis dashboard |
| 💾 **Data Management** | Full CRUD for all graph entities (Core Nodes/Edges, Context Nodes/Edges, Import/Export, Lifecycle Engine) |
| ⚙️ **Configuration** | Schema and database management |
| 🎲 **Simulation** | Monte Carlo calibration simulator (scope-based real-data mode) |
| 🔬 **What-If Analysis** | In-memory mitigation toggle with EL + TRI delta reporting |
| 📊 **Mitigation Exposure** | Counterfactual per-mitigation EL + TRI impact ranking |

### Loading Demo Data (Quick Start)

RIM includes a complete demo dataset covering the ODT New Space program and TC01-TC07 test scenarios:

1. Go to **⚙️ Configuration** → **📊 Data Management** tab
2. Tick the confirmation checkbox under **🔄 Reset Demo Data**
3. Click the **🔄 Reset Demo Data** button — wipes the database and reloads both datasets
4. Return to the Home page and activate any of the 8 pre-configured scopes from the sidebar

---


| Level | Description | Managed By |
|-------|-------------|------------|
| **Business** | Consequence-oriented risks with program-wide impact | Program leadership |
| **Operational** | Cause-oriented risks from specific functional areas | Functional teams |

### Risk Categories

- **Programme**: Schedule, budget, resources
- **Produit**: Technical performance, quality
- **Industriel**: Manufacturing, facilities
- **Supply Chain**: Suppliers, logistics

### Risk Origins

| Origin | Description | Visual Indicator |
|--------|-------------|------------------|
| **New** | Program-specific risk identified within this program | Standard border |
| **Legacy** | Inherited from enterprise risk register or other programs | Gray thick border, [L] prefix |

### Creating a Risk

1. Go to **Data Management** page → **Core Nodes** tab → Select **Risk**
2. Fill the form:
   - **Reference**: Unique identifier (e.g., SR-001, OR-015)
   - **Name**: Short descriptive name
   - **Description**: Detailed explanation
   - **Level**: Business or Operational
   - **Category**: Programme/Produit/Industriel/Supply Chain
   - **Likelihood**: 1-10 scale
   - **Severity**: 1-10 scale
   - **Origin**: New or Legacy
   - **Subtype**: Select the domain-specific subtype applicable to the risk level (e.g., Cyber, Supply Chain, Financial). Extension fields for the selected subtype appear automatically below.
3. Click **Save**

> **Subtype extension fields** are schema-defined per domain. They appear only when a non-Generic subtype is selected and differ by domain (e.g., CIA triad fields for IT Security, contract type for Supply Chain).

### Contingent Risks

Contingent risks are potential risks that may or may not materialize:

- Check **Is Contingent** when creating
- Set **Activation Condition**: What would trigger this risk
- Set **Decision Date**: When activation will be decided
- Visualized with dashed diamond outline

### Risk Status

| Status | Description |
|--------|-------------|
| **Active** | Currently relevant and being managed |
| **Archived** | No longer relevant, kept for history |

---

## Influence Mapping

### Influence Levels

Influence relationships describe how risks affect each other:

| Level | Direction | Description | Visual |
|-------|-----------|-------------|--------|
| **Level 1** | Operational → Business | Root cause creates consequence | Red, thick solid |
| **Level 2** | Business → Business | Consequence amplifies consequence | Purple, medium solid |
| **Level 3** | Operational → Operational | Cause contributes to cause | Blue, thin dashed |

### Influence Strength

| Strength | Weight | Description |
|----------|--------|-------------|
| **Critical** | 1.0 | Direct, unavoidable relationship |
| **Strong** | 0.75 | Significant, likely relationship |
| **Moderate** | 0.5 | Notable, possible relationship |
| **Weak** | 0.25 | Minor, occasional relationship |

### Confidence Scoring

Rate your confidence in the influence relationship (0.0 - 1.0):
- **1.0**: Documented, proven relationship
- **0.7-0.9**: Expert judgment with evidence
- **0.4-0.6**: Reasonable assumption
- **0.1-0.3**: Speculative

### Creating an Influence

1. Go to **Data Management** page → **Core Edges** tab → Select **Influence**
2. Select **Source Risk** (the risk that creates the influence)
3. Select **Target Risk** (the risk that is influenced)
4. Choose **Influence Type** (Level 1/2/3)
5. Set **Strength** and **Confidence**
6. Add optional **Description**
7. Click **Create Influence**

---

## Mitigation Management

### Mitigation Types

| Type | Description | Border Style | Color |
|------|-------------|--------------|-------|
| **Dedicated** | Program-specific mitigation created for identified risks | Solid, medium | Teal |
| **Inherited** | Imported from external sources (other programs, enterprise) | Dotted | Blue |
| **Baseline** | Standard controls from regulations, industry standards | Solid, thick | Purple |

### Mitigation Status

| Status | Border Style | Description |
|--------|--------------|-------------|
| **Implemented** | Solid | Active and operational |
| **In Progress** | Dash-dot (─∙─) | Currently being deployed |
| **Proposed** | Dashed (─ ─) | Planned, not started |
| **Deferred** | Dotted (∙∙∙) | On hold |

### Effectiveness Levels

| Level | Reduction | Description |
|-------|-----------|-------------|
| **Critical** | 90% | Highly effective, near-complete risk reduction |
| **High** | 70% | Strong protection |
| **Medium** | 50% | Moderate reduction |
| **Low** | 30% | Minimal impact |

### Creating a Mitigation

1. Go to **Data Management** page → **Core Nodes** tab → Select **Mitigation**
2. Fill the form:
   - **Reference**: Unique identifier (e.g., MIT-001)
   - **Name**: Short descriptive name
   - **Description**: Detailed explanation
   - **Type**: Dedicated/Inherited/Baseline
   - **Status**: Implementation status
   - **Source Entity**: For Inherited/Baseline, where it comes from
3. Click **Create Mitigation**

### Assigning Mitigations to Risks

1. Go to **Data Management** page → **Core Edges** tab → Select **Mitigates**
2. Select the source **Mitigation**
3. Select the target **Risk**
4. Set **Effectiveness** level
5. Add optional description
6. Click **Create Link**

> **Note**: One mitigation can address multiple risks (many-to-many relationship)

---

## Top Objective Management

### What are Top Objectives?

Top Objectives represent the key program goals that risks may threaten:

- **Product Efficiency**: Technical performance objectives
- **Business Efficiency**: Cost and schedule objectives
- **Industrial Efficiency**: Manufacturing objectives
- **Sustainability**: Environmental and social objectives
- **Safety**: Safety and regulatory objectives

### Creating a Top Objective

1. Go to **Data Management** page → **Context Nodes** tab → Select **Top Objective**
2. Fill the form:
   - **Reference**: Unique identifier (e.g., TPO-01)
   - **Name**: Objective description
   - **Cluster**: Category grouping
3. Click **Create**

### Linking Risks to Top Objectives

1. Go to **Data Management** page → **Context Edges** tab → Select **Impacts Top Objective**
2. Select the **Risk** (typically Business)
3. Select the **Top Objective** it threatens
4. Set **Impact Level** (Low/Medium/High/Critical)
5. Add optional description
6. Click **Create Impact**

---

## Exposure Calculation

### Overview

The exposure calculation quantifies risk severity considering:
- Base risk scores (likelihood × impact)
- Mitigation effectiveness
- Upstream influence limitations

### Calculation Steps

```
1. Base Exposure = Likelihood × Impact (scale 0-100)

2. Mitigation Factor = ∏(1 - Effectiveness_i)
   (multiplicative for diminishing returns)

3. Influence Limitation = Avg(Upstream_Residual × Strength)
   (unmitigated upstream risks limit downstream effectiveness)

4. Effective Factor = Mit_Factor + (1 - Mit_Factor) × Limitation

5. Final Exposure = Base × Effective_Factor
```

### Global Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Residual Risk %** | Σ(Final) / Σ(Base) × 100 | Overall mitigation effectiveness |
| **Weighted Risk Score** | Impact²-weighted aggregation | Executive summary (0-100) |
| **Max Single Exposure** | max(Final_Exposure) | Worst-case alert |

### Health Status

| Score Range | Status | Color |
|-------------|--------|-------|
| 0–10 | Excellent | Green |
| 11–30 | Good | Light green |
| 31–50 | Moderate | Orange |
| 51–70 | Concerning | Dark orange |
| 71–100 | Critical | Red |

### Using Exposure Calculation

1. In the **📊 Visualization** tab, find **⚡ Risk Exposure Analysis**
2. Click **Calculate Exposure**
3. View global metrics and detailed breakdown
4. Use results to prioritize mitigation efforts

---

## Analysis Scopes

### What Are Scopes?

Analysis scopes let you define **named subsets of your risk graph** for focused analysis. Instead of viewing the Full Graph, you can select a scope that contains only the nodes relevant to a specific area — for example, a particular supply chain, a functional domain, or a risk cluster.

Scopes are saved in `schema.yaml`, making them portable and shareable across team members.

### Creating a Scope

1. Open the **Configuration Manager** (`streamlit run app_config.py`)
2. Go to the **📐 Scopes** tab
3. Click **➕ Create New Scope**
4. Fill in:
   - **Scope ID**: Machine-readable identifier (e.g., `fuel_chain`)
   - **Display Name**: Human-readable label (e.g., "⛽ Fuel Supply Chain")
   - **Description**: Purpose of the scope
   - **Color**: Scope color for visual identification
   - **Nodes**: Select nodes from the database or paste UUIDs
5. Click **Create Scope**

### Selecting Scopes in the Main App

1. Open the main RIM app (`streamlit run app.py`)
2. In the sidebar, find the **📐 Analysis Scopes** expander
3. Select one or more scopes from the multiselect
4. Optionally check **Show connected neighbors** to include 1-hop risk neighbors
5. The visualization, statistics, CRUD tabs, and all analyses will reflect only the selected scope(s)
6. Click **🌐 Full Graph** to return to the unscoped view

### Multi-Scope Union

When you select multiple scopes, the displayed graph is the **union** of all selected scopes' node IDs. This lets you compare or combine related analysis areas.

### Smart Scope Expansion

When a scope is active, the system automatically includes:
- **Mitigations** connected to in-scope risks (via `MITIGATES` relationships)
- **TPOs** connected to in-scope risks (via `IMPACTS_TPO` relationships)
- **Risk neighbors** (optional, via "Show connected neighbors" toggle) — adds risks directly connected to scoped risks

This ensures you see the complete context for your scoped risks without manually adding every related node.

### Scoped Features

| Feature | Behavior When Scope Active |
|---------|----------------------------|
| **Statistics Dashboard** | Counts only scoped nodes and edges |
| **Exposure Calculation** | Only considers risks, mitigations, and influences within scope |
| **Influence Analysis** | Top propagators, convergence points, etc. computed on scoped data |
| **Mitigation Analysis** | Coverage gaps and effectiveness limited to scoped risks |
| **Data Management** (Risks, TPOs, Mitigations) | Lists only entities within the expanded scope |
| **Influence Explorer** | Node selector shows only scoped nodes |

### Scoped Exposure Calculation

When a scope is active, clicking **Calculate Exposure** only considers:
- **Risks** within the scope (and optionally their 1-hop neighbors)
- **Influences** between in-scope risks
- **Mitigations** connected to in-scope risks (found via relationships, not by ID membership)
- **Mitigates relationships** targeting in-scope risks

> **Note**: Scoped exposure percentages may differ from Full Graph results because influence chains that cross the scope boundary are excluded. This gives you an accurate picture of the risk within the focused area.

### Pre-built Demo Scopes

When using the bundled demo dataset, 8 scopes are pre-configured in `schemas/default/schema.yaml`:

| Scope ID | Description |
|---|---|
| `odt_demo` | Full ODT New Space program (RC-01–05, RH-01-07...) with connected mitigations and TPOs |
| `tc01_baseline` | TC01 — Simple 3-risk baseline scenario |
| `tc02_propagation` | TC02 — Influence propagation chain |
| `tc03_convergence` | TC03 — Multiple risks converging on one target |
| `tc04_mitigation` | TC04 — Mitigation effectiveness comparison |
| `tc05_tpo` | TC05 — TPO impact with multiple risk paths |
| `tc06_mixed` | TC06 — Mixed Business/Operational risk types |
| `tc07_influence_strengths` | TC07 — Influence strength gradation |

All TC scopes use deterministic UUIDs that match `demo_tc_dataset.cypher` — no post-import update step required.

### Tips

- Create scopes around **risk clusters** identified by the Influence Analysis panel
- Use scopes to prepare **focused briefings** for specific stakeholders
- Compare exposure metrics across scopes to identify the highest-risk areas
- Toggle **Show connected neighbors** to see how adjacent risks affect your scope

---

## Visualization

### Graph Layout Options

| Layout | Description | Best For |
|--------|-------------|----------|
| **🌳 Hierarchical (Sugiyama)** | Edge-crossing minimization, semantic layers | Understanding flow |
| **📶 Layered** | TPO → Business → Operational layers | Seeing hierarchy |
| **📊 Category Grid** | 2×2 grid by risk category | Category comparison |
| **🎯 TPO Cluster** | Group risks around their TPOs | TPO impact analysis |

### Node Visual Semantics

| Element | Shape | Meaning |
|---------|-------|---------|
| **◆ Diamond** | Business Risk | Pointed = danger, consequence |
| **● Circle** | Operational Risk | Foundation, cause |
| **🛡️ Rounded Box** | Mitigation | Shield = protection |
| **⬡ Hexagon** | TPO | Objective/goal |

### Color Modes

- **By Level**: Purple (Business), Blue (Operational)
- **By Exposure**: Gradient from Yellow (low) to Dark Red (critical)

### Edge Visual Semantics

| Relationship | Arrow Type | Color |
|--------------|------------|-------|
| Influence (Risk→Risk) | → Standard | Level-based |
| Mitigation (Mit→Risk) | ⊣ Bar end | Green |
| TPO Impact (Risk→TPO) | ▷ Vee | Orange |

### Interactive Features

- **Click node**: Select the node to open the **Contextual Property Panel** below the graph (6 sections: Identity, Exposure Metrics, Graph Position, Influence Analysis, Mitigation Summary, Edit). Also activates **Interactive Focus Mode**, fading out unrelated nodes to highlight the selected node's neighborhood. Use the "Full Chain Focus" toggle (top-left of map) to expand to the full connected chain. Click the empty canvas space to deselect.
- **Drag node**: Reposition (with physics off)
- **Scroll**: Zoom in/out
- **Right-click**: Context menu

### Saving Layouts

1. Arrange nodes as desired
2. Click **📸 Save Layout**
3. Enter a layout name
4. Load saved layouts from dropdown

---

## Analysis Tools

### Influence Analysis Panel

Access from **📈 Analysis** tab → **📊 Influence Analysis** expander.

| Analysis | Purpose | Key Insight |
|----------|---------|-------------|
| **🎯 Top Propagators** | Risks with highest downstream impact | "Address these first" |
| **⚠️ Convergence Points** | Nodes receiving multiple influences | "Monitor closely" |
| **🔥 Critical Paths** | Strongest influence chains to TPOs | "Key threat vectors" |
| **🚧 Bottlenecks** | Single points of failure | "Resilience risks" |
| **📦 Clusters** | Tightly interconnected groups | "Treat as a unit" |

### Mitigation Analysis Panel

Access from **📈 Analysis** tab → **🛡️ Mitigation Analysis** expander.

| Analysis | Purpose | Key Insight |
|----------|---------|-------------|
| **🎯 Risk Treatment** | Coverage per risk | "What's protecting this risk?" |
| **🛡️ Mitigation Impact** | Risks addressed by each mitigation | "Where is this control applied?" |
| **📊 Coverage Gaps** | Unmitigated risks | "What needs attention?" |

### Coverage Gap Prioritization

Coverage gaps are flagged if the unmitigated risk is also:
- A **Top Propagator** (high downstream impact)
- A **Convergence Point** (multiple influences)
- A **Bottleneck** (single point of failure)

### Monte Carlo Simulator

Access from the **🎲 Simulation** page.

| Mode | Data Source | Description |
|------|-------------|-------------|
| **Monte Carlo (Random)** | Synthetic | Random scenario generation for model validation |
| **Mitigation Path** | Synthetic | Progressive mitigation scenario analysis |
| **Scope-Based (Real Data)** | Live DB | Real graph topology; scope- and lifecycle-aware |
| **TRI α Calibration** | Live DB | Sweep TRI exponent α; calibration report + recommended α |

Scope-Based mode uses actual likelihood/severity values and respects the active scope.
Saved simulation results can be compared with Δ delta columns and exported to Excel.

#### Lifecycle-Aware Simulation — Worst-Case Canvas (F31c)

The **🧟 Worst-Case Canvas** toggle (available in Scope-Based and TRI α Calibration modes)
re-activates lifecycle-inactive risks (accepted / watching / suppressed / closed) to surface
latent tail exposure hidden by lifecycle decisions.

- A banner shows the count of re-activated risks
- Results are labelled `[Worst-Case]`; the `SimulationRecord` mode is `"Scope-Based (Worst-Case)"`
- Use to answer: *"What if we reversed all lifecycle decisions?"*

#### TRI α Calibration Mode (F31d)

The TRI exponent α controls tail amplification: `TRI = L × S^α`. The current schema
default is `α = 1.5`. The calibration mode validates this choice for each domain.

**Steps:**
1. Select **TRI α Calibration** in the mode radio
2. Configure α range (min / max / step) and runs per α
3. Optionally enable Worst-Case Canvas
4. Click **🚀 Run Calibration**
5. Select a **target quadrant profile** (Balanced / Tail-Heavy / Frequency-Heavy / Severity-Heavy)
6. The recommended α is highlighted in the calibration report table

**Outputs:**
- **Calibration Chart**: Mean TRI ±1σ band and P95 line vs α; stacked quadrant distribution bar
- **Calibration Report**: α → Mean/Std/P95 TRI + quadrant %s; recommended row highlighted
- **Raw Data**: CSV download of the full calibration DataFrame

To apply the calibrated α, update `tri_alpha` under `exposure_model` in
`schemas/[domain]/schema.yaml`.

---

## What-If Analysis

### Overview

The **What-If Analysis** page (`🔬 What-If Analysis` in the sidebar) lets you
explore mitigation scenarios **without touching the database**. All exploration
is session-local and reversible.

### Step-by-Step

1. Navigate to the **🔬 What-If Analysis** page
2. Verify the active scope shown in the sidebar (or leave it as Full Graph)
3. Optionally check **"Include inactive risks (worst-case)"** to include
   Accepted/Watching/Suppressed/Closed risks in the analysis
4. Click **🔄 Compute Baseline** — the page fetches live data and computes
   the reference exposure result
5. Uncheck any mitigation in the **Mitigation Toggles** panel to disable it
6. The **Portfolio Impact** summary and **Per-Risk Exposure Delta** table
   update immediately with Δ values
7. Click **↺ Reset Scenario** to re-enable all mitigations

> Changing the scope or the "Include inactive risks" setting requires
> re-running **Compute Baseline** to refresh the cached data.

### Portfolio Metrics

| Metric | Description |
|--------|-------------|
| **Residual Risk %** | Total final exposure / total base exposure × 100 |
| **Weighted Risk Score** | Severity²-weighted aggregate (0–100 scale) |
| **Total TRI** | Sum of Tail Risk Indicators (L × S^1.5) across all in-scope risks |

Each metric shows a delta indicator — **red = worse, green = better**.
A health status change banner appears when the scenario moves the portfolio
between bands (Excellent / Good / Moderate / Concerning / Critical).

### Per-Risk Delta Table

The table lists every in-scope risk with:
- **Baseline EL** and **Modified EL** (Final Exposure)
- **Δ EL** — sorted descending so the most-impacted risks appear first
- **Baseline TRI**, **Modified TRI**, **Δ TRI**
- **Quadrant** (critical / frequency / severity / marginal)

### Typical Use Cases

| Question | How to use What-If |
|----------|--------------------|
| "What if this mitigation is delayed?" | Disable the mitigation; read Δ EL for its target risks |
| "Which mitigation delivers the most coverage?" | Disable one at a time; compare Residual Risk % deltas |
| "Worst-case unmitigated exposure?" | Disable all mitigations + enable "Include inactive risks" |
| "Stakeholder briefing for a domain" | Activate a scope, compute baseline, toggle mitigations live |

---

## Mitigation Exposure View

### Overview

The **Mitigation Exposure View** (`📊 Mitigation Exposure` in the sidebar) answers:

> *Which mitigations are protecting the portfolio the most — and which are redundant?*

For each active mitigation, a **counterfactual** exposure is computed: what would the portfolio
look like without that mitigation? The **EL Delta** and **TRI Delta** show its individual
protective value, independent of other controls.

### Step-by-Step

1. Navigate to the **📊 Mitigation Exposure** page
2. Verify the active scope in the sidebar (or leave it as Full Graph)
3. Optionally check **"Include inactive risks (worst-case)"** to include
   Accepted/Watching/Suppressed/Closed risks
4. Optionally set the **Risk level** filter (All / Business / Operational)
5. Click **🔄 Compute Mitigation Impact** — each mitigation is evaluated in one pass
6. Review the ranked table — mitigations with the highest EL Delta ↑ are most critical

> Changing scope or lifecycle settings requires re-clicking **Compute Mitigation Impact**
> to refresh the cached results.

### Column Reference

| Column | Description |
|--------|-------------|
| **Mitigation** | Name of the mitigation control |
| **Type** | Dedicated / Inherited / Baseline |
| **Status** | Proposed / In Progress / Implemented / Deferred |
| **Level** | Risk level(s) the mitigation covers (Business / Operational / Mixed) |
| **Risks Covered** | Number of in-scope risks directly addressed by this mitigation |
| **EL Delta ↑** | Exposure increase if this mitigation were removed (marginal value) |
| **TRI Delta ↑** | Tail Risk Indicator increase if this mitigation were removed |
| **% Portfolio EL** | EL Delta as a percentage of total unmitigated base exposure |

### Interpreting Results

| Pattern | Interpretation |
|---------|----------------|
| High EL Delta + Implemented | Critical control — protect and monitor |
| High EL Delta + Proposed/Deferred | Unacceptable gap — prioritise implementation |
| Low EL Delta + any status | Limited measurable impact; check effectiveness data or control overlap |
| Zero EL Delta | Covers only risks with no likelihood/severity data, or fully redundant |

### Relationship to What-If Analysis

| Feature | Best for |
|---------|---------|
| **What-If Analysis** | Interactive multi-mitigation scenario exploration |
| **Mitigation Exposure View** | Objective single-mitigation ranking and prioritisation |

---

## Risk Lifecycle Engine

### Overview

The Lifecycle Engine manages the 6-state risk lifecycle:

| Status | Meaning |
|--------|---------|
| **Active** | Currently relevant, included in all analytics |
| **Watching** | Elevated monitoring; excluded from exposure by default |
| **Accepted** | Formally accepted by a decision-maker; excluded from exposure |
| **Suppressed** | Temporarily deprioritised; excluded from exposure |
| **Closed** | Risk has materialised or is no longer applicable |
| **Archived** | Historical record only |

### Using the Lifecycle Engine

Access from **💾 Data Management** → **Lifecycle Engine** expander.

- **Trigger Review**: lists risks whose `trigger_condition` text warrants human review
- **Auto-Acceptance**: flags risks eligible for formal acceptance (below threshold,
  not critical quadrant, not severity-ceiling) — includes a **🔓 Force Accept** button
  to override guards when reviewer intent is explicit
- **Archive Alerts**: lists risks with inactive status older than the configured
  `archive_retention_days` threshold

### Viewing Accepted Risks

Enable **"Show Accepted Risks"** toggle in Data Management to review the full list
of accepted risks and their acceptance metadata (date, owner).

---

## Risk Templates

### Overview

Generic Risk Templates allow you to define reusable risk archetypes that can be instantiated
into specific risks with pre-filled attributes.

| Property | Behaviour |
|----------|-----------|
| `is_template = true` | Excluded from exposure calculations |
| Canvas visibility | Hidden from graph canvas |
| Lifecycle | Not subject to lifecycle engine |
| INSTANTIATES rel | Links template → specific instance in Neo4j |

### Creating a Template

1. Go to **💾 Data Management → Risks** tab
2. In the **Create New Risk** form, check **☑ Mark as template (GenericRisk)**
3. Fill in likelihood, severity, subtype, categories, and description
4. Save — the risk appears in the **📋 Risk Templates** expander

### Instantiating a Template

1. Open **📋 Risk Templates** expander in Data Management → Risks
2. Find the template and click **➕ Instantiate**
3. Adjust the pre-filled form (name, description, etc.) and save
4. A new specific risk is created and linked to the template via `[:INSTANTIATES]`

### Viewing Template Relationships

In the **Node Property Panel** (click any risk on the canvas or in the list):
- Template risks show an instance count and list of instance names
- Instance risks show the parent template name

---

## Threshold Alerts

### Overview

Threshold Alerts automatically detect risks whose exposure scores exceed configured limits,
surfaced in the **⚡ Exposure** dashboard after each computation.

### Monitored Metrics

| Metric | Formula | Default Threshold |
|--------|---------|-------------------|
| Expected Loss (EL) | Likelihood × Severity × mitigation factor × influence limitation | 50.0 |
| Tail Risk Indicator (TRI) | Likelihood × Severity^1.5 | 25.0 |

### Reading the Alert Panel

After clicking **Compute** in the Exposure expander:
- **⚠️ Threshold Alerts** panel appears below the quadrant distribution widget
- Breach columns: **EL Breaches** and **TRI Breaches**, each listing risk name, level, and value
- When all risks are within thresholds: **✅ All risks within thresholds** success indicator

### Configuring Thresholds

Edit the active schema YAML (Configuration page → Schema Editor):

```yaml
analysis:
  alert_thresholds:
    expected_loss_threshold: 50.0
    tail_risk_indicator_threshold: 25.0
    enabled: true
```

Set `enabled: false` to suppress alerts without removing the configuration.

---

## Import/Export

### Excel Export

1. Go to **📥📤 Import/Export** tab
2. Click **Export to Excel**
3. Download the generated file

**Exported sheets**:
- Risks (all fields including Origin)
- TPOs
- Influences
- TPO_Impacts
- Mitigations
- Mitigates (mitigation-to-risk links)

### Excel Import

1. Prepare an Excel file with the required sheets
2. Go to **📥📤 Import/Export** tab
3. Upload the file
4. Review the import preview
5. Click **Import**
6. Check the import log for any warnings

**Import behavior**:
- Existing entities matched by name
- New entities created if not found
- Relationships recreated by name matching

---

## Filter System

### Quick Presets

| Preset | Shows |
|--------|-------|
| 🌐 Full View | Risks + TPOs (no mitigations) |
| 🟣 Business Focus | Business risks only |
| 🔵 Operational Focus | Operational risks only |
| ✅ Active Risks Only | Excludes contingent/archived |
| ⚠️ Contingent Risks | Potential risks only |
| 🎯 Risks Only | No TPOs or mitigations |
| 🆕 New Risks Only | Program-specific risks |
| 📜 Legacy Risks Only | Inherited risks |
| 🛡️ Risks + Mitigations | Risk-mitigation relationships |
| 🗺️ Full Map | Everything |

### Filter Categories

**⚡ Quick Presets**: One-click filter configurations

**🔷 Core Nodes & Edges**:

- **🎯 Risk Filters**: Level, Categories, Status, Origin, Exposure threshold
- **🛡️ Mitigation Filters**: Type (Dedicated/Inherited/Baseline), Status
- **🔗 Influences Filters**: Strength
- **🔗 Mitigates Filters**: Effectiveness

**🏆 TPO & Related**:

- **🏆 TPO Filters**: Show/hide TPOs, filter by cluster
- **🔗 TPO Impact Filters**: Impact level

**🎨 Color Options**:
- Color mode (by level/by exposure)

**🖼️ Graph Visual Behaviour** (F32):
- **Presets**: Clean / Analysis / Lifecycle Audit / Sandbox Edit — one-click bundles
- **Exposure Opacity**: High-exposure risks solid; low-exposure risks fade (configurable threshold)
- **Lifecycle Opacity**: Per-status transparency (Watching, Suppressed, Accepted, Closed)
- **Quadrant Border Encoding**: Coloured node borders show risk quadrant (Critical/High/Moderate/Low)
- **Save as Schema Default**: Persist settings to `graph_visual_config` in schema YAML

**🔍 Influence Explorer**:
- Show neighborhood of selected node
- Depth control

**⚙️ Graph Options**:
- Physics toggle
- Layout selection

**💾 Layout Management**:
- Save/load node positions

### All/None Buttons

Each multi-select filter has **All** and **None** buttons for quick selection.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `R` | Refresh visualization |
| `F` | Focus search box |
| `Esc` | Clear selection |

---

## Tips & Best Practices

### Risk Modeling

1. **Start with TPOs**: Define what you're protecting
2. **Map Business Risks**: What consequences threaten TPOs?
3. **Trace to Operational**: What causes create those consequences?
4. **Add Influences**: How do risks amplify each other?
5. **Layer Mitigations**: Cover high-exposure risks first

### Using Exposure Calculation

1. Run calculation after significant changes
2. Focus on **Residual Risk %** for overall health
3. Use **Max Single Exposure** to find outliers
4. Review **Influence Limitation** effects

### Visualization Best Practices

1. Use **Hierarchical layout** for understanding flow
2. Use **Exposure coloring** to spot hot spots
3. Save layouts for recurring views
4. Use filters to focus on specific areas

---

## Troubleshooting

### Connection Issues

**Problem**: Can't connect to Neo4j

**Solutions**:
1. Verify Docker is running: `docker ps`
2. Check Neo4j logs: `docker logs neo4j`
3. Verify credentials match docker-compose.yml
4. Try `bolt://localhost:7687` (not `neo4j://`)

### Visualization Issues

**Problem**: Graph doesn't display

**Solutions**:
1. Click **🔄 Refresh Graph**
2. Check filter settings (might be excluding everything)
3. Clear browser cache
4. Check console for JavaScript errors

### Import Issues

**Problem**: Import fails or misses data

**Solutions**:
1. Verify column names match expected format
2. Check for special characters in names
3. Review import log for specific errors
4. Ensure referenced entities exist

---

*Last updated: May 2026 | Version 2.32.0*
