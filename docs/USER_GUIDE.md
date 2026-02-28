# 📖 RIM User Guide

Complete documentation for the Risk Influence Map application.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Risk Management](#risk-management)
3. [Influence Mapping](#influence-mapping)
4. [Mitigation Management](#mitigation-management)
5. [TPO Management](#tpo-management)
6. [Exposure Calculation](#exposure-calculation)
7. [Analysis Scopes](#analysis-scopes)
8. [Visualization](#visualization)
9. [Analysis Tools](#analysis-tools)
10. [Import/Export](#importexport)
11. [Filter System](#filter-system)

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

The application has three main areas:

| Area | Location | Purpose |
|------|----------|---------|
| **Sidebar** | Left panel | UI Complexity Toggle, Connection, filters, legend, settings |
| **Tab Bar** | Top center | Navigate between management tabs |
| **Main Content** | Center | Forms, tables, visualization |

### UI Complexity Modes

RIM allows users to toggle the interface complexity from the **top of the sidebar**:

- **Advanced Mode**: The full experience. Shows all tabs, advanced filters, and renders every node/edge in the graph regardless of exposure. Intended for Risk Managers and Analysts.
- **Simple Mode**: A streamlined experience for non-technical stakeholders. Hides advanced tabs (Mitigations, Influences, Config, etc.), collapses complex filters, and brings focus to the graph by "ghosting" (making transparent) all nodes except the Top risks and TPOs.

### Navigation Tabs

| Tab | Purpose |
|-----|---------|
| 📊 Visualization | Interactive risk network graph |
| ⚠️ Risks | Create and edit risks |
| 🎯 TPOs | Define program objectives |
| 🛡️ Mitigations | Manage mitigation actions |
| 🔗 Influences | Map risk relationships |
| 📌 TPO Impacts | Link risks to objectives |
| 🛡️↔⚠️ Risk Mitigations | Assign mitigations to risks |
| 📥📤 Import/Export | Data exchange |

### Loading Demo Data (Quick Start)

RIM includes a complete demo dataset covering the SNR nuclear program and TC01-TC07 test scenarios:

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

1. Go to **⚠️ Risks** tab
2. Fill the form:
   - **Reference**: Unique identifier (e.g., SR-001, OR-015)
   - **Name**: Short descriptive name
   - **Description**: Detailed explanation
   - **Level**: Business or Operational
   - **Category**: Programme/Produit/Industriel/Supply Chain
   - **Likelihood**: 1-10 scale
   - **Impact**: 1-10 scale
   - **Origin**: New or Legacy
3. Click **Create Risk**

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

1. Go to **🔗 Influences** tab
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

1. Go to **🛡️ Mitigations** tab
2. Fill the form:
   - **Reference**: Unique identifier (e.g., MIT-001)
   - **Name**: Short descriptive name
   - **Description**: Detailed explanation
   - **Type**: Dedicated/Inherited/Baseline
   - **Status**: Implementation status
   - **Source Entity**: For Inherited/Baseline, where it comes from
3. Click **Create Mitigation**

### Assigning Mitigations to Risks

1. Go to **🛡️↔⚠️ Risk Mitigations** tab
2. Select the **Mitigation**
3. Select the target **Risk**
4. Set **Effectiveness** level
5. Add optional description
6. Click **Create Link**

> **Note**: One mitigation can address multiple risks (many-to-many relationship)

---

## TPO Management

### What are TPOs?

Top Program Objectives (TPOs) represent the key goals that risks may threaten:

- **Product Efficiency**: Technical performance objectives
- **Business Efficiency**: Cost and schedule objectives
- **Industrial Efficiency**: Manufacturing objectives
- **Sustainability**: Environmental and social objectives
- **Safety**: Safety and regulatory objectives

### Creating a TPO

1. Go to **🎯 TPOs** tab
2. Fill the form:
   - **Reference**: Unique identifier (e.g., TPO-01)
   - **Name**: Objective description
   - **Cluster**: Category grouping
3. Click **Create TPO**

### Linking Risks to TPOs

1. Go to **📌 TPO Impacts** tab
2. Select the **Risk** (typically Business)
3. Select the **TPO** it threatens
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
| 0-25 | Excellent | Green |
| 26-50 | Good | Blue |
| 51-75 | Attention Needed | Orange |
| 76-100 | Critical | Red |

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
| **CRUD Tabs** (Risks, TPOs, Mitigations, Influences) | List only entities within the expanded scope |
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
| `snr_demo` | Full SNR nuclear program (RS-01–08, RO-01–07) with connected mitigations and TPOs |
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

- **Click node**: View details
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

**🎨 Display Options**:
- Color mode (by level/by exposure)
- Label options
- Edge visibility

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

*Last updated: February 2026 | Version 2.10.9*
