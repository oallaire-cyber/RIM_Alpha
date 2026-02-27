# Risk Influence Map (RIM) - Development Roadmap & Agent Reference

**Context for Future AI Agents:**
This `ROADMAP.md` serves as the primary system reference and source of truth for all future development within the RIM repository. All features, architecture changes, and phase transitions must align with this document. The overarching philosophy is **simplicity, modularity, and strict validation** before implementing highly complex computational features. Each phase acts as a dependent foundation for the next.

Between every phase, there is a mandatory, exhaustive testing gateway (Automated and Manual) before progressing.

---

## Core Architectural Philosophy

The RIM application is built around two non-negotiable design principles:

**Principle 1 — Two Hardcoded Node Types, Everything Else Generic**

| Layer             | Node Types                        | Owner                         | Logic                                                   |
| ----------------- | --------------------------------- | ----------------------------- | ------------------------------------------------------- |
| **Risk Layer**    | `BusinessRisk`, `OperationalRisk` | Hardcoded in app              | Exposure engine, level deduction, influence propagation |
| **Context Layer** | All other node types              | Schema YAML (`context_nodes`) | Generic CRUD, display, and relationship traversal only  |

Adding a new node type to any domain requires only a YAML schema change — zero app code modification.

The only relationships that carry **computational weight** (exposure propagation) are `semantic: influence` relationships between risk nodes. All other relationships are `semantic: context` or `semantic: cluster` — traversable and displayed, but not in the exposure engine.

**Principle 2 — Scope Completeness: A Scope is a Full Graph**

When a user activates a scope, every operation in the application must behave as if the scoped subgraph _is_ the entire graph. This means:

- **Statistics** are computed for scoped nodes only — no global leakage
- **CRUD operations** are scope-aware — new nodes created while a scope is active are offered registration into that scope; deletion within scope distinguishes "remove from scope" vs. "delete globally"
- **Node selection dropdowns** (for influence creation, mitigation linking, etc.) show only scoped nodes
- **Exposure calculation**, **influence analysis**, **mitigation analysis**, and **critical path detection** all respect scope boundaries
- **ContextNodes** (upper/lower zone) are included in scope expansion alongside risk nodes, mitigations, and TPOs

This contract must be enforced end-to-end — any function that reads from or writes to the graph must accept and propagate a `scope_context` parameter. Partial scope-awareness (the current state) is worse than no scope at all, because it produces silently incorrect results.

---

## 1. Updates & Architectural Improvements

- **U1. ~~Externalize Static Content~~** ✅ _(v2.9.0)_
- **U2. ~~Decouple Entry Point~~** ✅ _(v2.9.0)_
- **U3. ~~Centralized State Management~~** ✅ _(v2.10.0)_
- **U4. Strict Data Validation (Pydantic)**: Implement rigid validation for all incoming graph logic using `pydantic`. Models must cover both risk nodes and generic context nodes, with type enforcement driven by schema YAML property definitions.
- **U5. Mitigation Budget Attributes**: Extend the Mitigation schema with **CAPEX** and **OPEX** attributes. Foundation for cost-optimization algorithms.
- **U6. Generic ContextNode Architecture**: Refactor the graph schema and database layer to support a fully generic `ContextNode` type driven entirely by `context_nodes` entries in the schema YAML. The app renders, creates, edits, and deletes any context node type using a single generic form — no type-specific code. Each definition carries: `shape`, `color`, `zone` (`upper`/`lower`), and a typed `properties` list. Reserve `source` and `import_adapter` as base properties on all ContextNodes from the start (for F17). See _Architectural Note: ContextNode Schema_ below.
- **U7. ~~Computed Risk Level~~** ✅ _(v2.10.3)_: Replaced rigid `level` for visualization with dynamic BFS-computed distance to nearest TPO through `semantic: influence` relationships. Level 0 = TPO; Level N = shortest influence-path distance to any TPO. Orphan risks (no path to any TPO) are flagged in the UI. ContextNodes carry `zone` (upper/lower) from their schema definition — not a computed property.
- **U8. ~~Relationship Semantic Types~~** ✅ _(v2.10.4)_: Added a `semantic` field to all relationship type definitions. Three values: `influence` (participates in exposure propagation), `context` (structural/informational, feeds financial model), `cluster` (risk grouping only). The exposure engine routes exclusively on `semantic: influence` relationships.
- **U9. ~~Scope Completeness Enforcement~~** ✅ _(v2.10.6)_: Audited and repaired all functions that interact with the graph to ensure end-to-end scope propagation. Data fetching, UI CRUD dropdowns and lists, metrics, and network expansions respect strict active scope boundaries.
- **U10. ~~Schema-Driven Filter System (Full Dynamic Rebuild)~~** ✅ _(v2.10.1)_
  - **Problem resolved:** Three separate bugs existed in the filter layer:
    1. `ui/sidebar.py` (`render_filter_sidebar`) used the pre-schema-registry API (`filters["risks"]`, `select_all_levels()`, etc.) — methods that no longer exist in `FilterManager`. The function was still exported from `ui/__init__.py` but calling it would raise `AttributeError` immediately.
    2. `home.py` `render_visualization_filters` iterated hardcoded entity ID lists (`["risk", "mitigation"]`, `["tpo"]`) and relationship ID lists (`["influences", "mitigates"]`, `["impacts_tpo"]`) — not truly dynamic. Any new entity/relationship type added to a schema YAML would be silently ignored by the filter UI.
    3. `FilterManager.get_presets()` returned only 2 static presets; `apply_preset("risks_only")` hardcoded the string `"risk"` instead of using the registry's `is_risk_type` flag. `get_filters_for_query()` similarly hardcoded entity IDs `"risk"`, `"tpo"`, `"mitigation"` and relationship IDs `"influences"`, `"impacts_tpo"`, `"mitigates"`.
  - **Changes made:**
    - `ui/filters.py` — `get_presets()` rebuilt to be fully schema-driven: generates Full View, Risks Only, per-level presets (Business Only / Operational Only), Active Only (if schema defines an Active status), and Hide Mitigations — all derived from `registry.entity_types` and `registry.relationship_types` with zero hardcoded IDs. `apply_preset()` uses `entity_type.is_risk_type` / `entity_type.is_mitigation_type` flags. `get_filters_for_query()` iterates registry type flags for kernel types, then `get_additional_entity_types()` / `get_additional_relationship_types()` for all non-kernel types — adding `show_<entity_id>` / `show_<rel_id>` keys for any unknown types.
    - `ui/home.py` `render_visualization_filters` — replaced hardcoded ID lists with two inner helper functions `_render_entity_filter` / `_render_relationship_filter`, called via `registry.get_risk_type()`, `registry.get_mitigation_type()`, `registry.get_influence_type()`, `registry.get_mitigates_type()` for kernel types, then `registry.get_additional_entity_types()` / `registry.get_additional_relationship_types()` for all additional types. Added **All / None** quick-toggle buttons alongside every multiselect group.
    - `ui/sidebar.py` — fully rewritten using the same schema-driven approach (registry-first, no hardcoded IDs, All/None buttons). Removes the broken `config.settings` constant imports.

### Critical Scope Gaps (Current State as of v2.10.0)

The following gaps break the "scope as full graph" contract and must be resolved before Phase 2 work begins. They are documented here so future agents understand the full scope of required change:

| Component                             | Current Behavior                                                     | Required Behavior                                                                                            |
| ------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `get_statistics()`                    | Always returns global counts                                         | Accept `scope_node_ids`, return scoped counts only                                                           |
| CRUD forms (risks, mitigations, TPOs) | Create/update/delete against full graph                              | When scope active: offer "add to scope" on create; on delete offer "remove from scope" vs. "delete globally" |
| Node selection dropdowns              | Show all nodes in full graph                                         | When scope active: filter to scoped nodes only                                                               |
| `get_all_nodes_for_selection()`       | Returns all risks and TPOs globally                                  | Accept `scope_node_ids` parameter, return filtered list                                                      |
| `get_graph_data()` scope expansion    | Expands to connected mitigations and TPOs only                       | Must also expand to connected ContextNodes once U6 is implemented                                            |
| `get_influence_analysis()`            | Partially scoped (risks filtered, TPO connections not fully bounded) | Fully scope-bounded: all sub-analysis functions respect the same `scope_set`                                 |
| `get_mitigation_analysis()`           | Partially scoped                                                     | Fully scope-bounded                                                                                          |
| Cache keys (F2)                       | Not yet scope-keyed                                                  | Cache must be keyed by active scope — a full-graph cache hit must not serve a scoped view                    |
| `AnalysisScopeConfig`                 | Flat `node_ids` list, no hierarchy                                   | Add `scope_type` field (non-breaking, defaults to `"scope"`) for SubGraph promotion path (F16)               |

### Architectural Note: ContextNode Schema Structure

```yaml
# In schema YAML — illustrative entries
context_nodes:
  # Upper zone — anchors above BusinessRisk layer
  business_perimeter:
    shape: "box"
    color: "#8E44AD"
    border: "double"
    zone: "upper"
    properties:
      - { name: "ebit_absolute", type: "float", unit: "EUR", required: true }
      - { name: "ebit_margin", type: "float", label: "EBIT Margin %" }
      - { name: "fcf_annual", type: "float", unit: "EUR" }
      - { name: "p_and_l_owner", type: "string" }

  scenario:
    shape: "hexagon_small"
    color: "#F39C12"
    zone: "upper"
    properties:
      - { name: "annual_probability", type: "float", required: true }
      - { name: "ebit_impact_min", type: "float", unit: "EUR" }
      - {
          name: "ebit_impact_expected",
          type: "float",
          unit: "EUR",
          required: true,
        }
      - { name: "ebit_impact_max", type: "float", unit: "EUR" }
      - { name: "fcf_impact_expected", type: "float", unit: "EUR" }
      - { name: "recovery_days", type: "int" }
      - { name: "fair_calibration_flag", type: "bool", default: false }
      - {
          name: "fair_tef_source",
          type: "enum",
          values: ["historical", "expert", "threat_intel"],
        }
      - {
          name: "fair_lm_distribution",
          type: "enum",
          values: ["lognormal", "pert", "uniform"],
        }

  # Lower zone — anchors below OperationalRisk layer
  entry_point:
    shape: "box"
    color: "#E67E22"
    zone: "lower"
    properties:
      - { name: "exploitability", type: "int", min: 1, max: 10 }
      - {
          name: "entry_type",
          type: "enum",
          values: ["credential", "network", "physical", "supply_chain"],
        }

  attacker:
    shape: "box"
    color: "#922B21"
    zone: "lower"
    properties:
      - {
          name: "actor_type",
          type: "enum",
          values: ["nation_state", "criminal", "insider", "hacktivist"],
        }
      - { name: "capability_level", type: "int", min: 1, max: 10 }

relationship_types:
  # Existing influence types retain semantic: influence unchanged
  # New context relationships
  impact_financially:
    semantic: "context"
    valid_from: ["BusinessRisk"]
    valid_to: ["business_perimeter"]
    properties:
      - { name: "impact_fraction", type: "float" }
      - {
          name: "impact_type",
          type: "enum",
          values: ["revenue_loss", "direct_cost", "fine", "recovery"],
        }
  scenario_illustrates:
    semantic: "context"
    valid_from: ["scenario"]
    valid_to: ["BusinessRisk", "OperationalRisk"]
  enable:
    semantic: "context"
    valid_from: ["entry_point"]
    valid_to: ["OperationalRisk"]
  is_member:
    semantic: "cluster"
    valid_from: ["OperationalRisk"]
    valid_to: ["BusinessRisk"]
```

---

## 2. Planned Features

### Simple / Medium Workload

- **F1. Progressive UI Loading**: Pagination or virtual scrolling for CRUD tables on large scopes.
- **F2. Intelligent Caching**: Apply `@st.cache_data` to expensive queries and layout algorithms. Cache must be keyed by active scope — a cache hit on a full-graph query must never serve a scoped view.
- **F3. Complexity Toggle (Simple vs. Advanced Mode)**: Streamlined UI hiding advanced tabs for non-technical stakeholders.
- **F4. One-Click Visualization Export**: Export the active styled graph view to PNG or PDF.
- **F5. Automated Risk Threshold Alerts**: Visual flags when computed exposure exceeds predefined thresholds. Must be scope-aware.
- **F6. Mitigation Exposure View (Business Focus)**: Dedicated view showing mitigations contributing to exposure reduction for selected Business Risks, filterable by lifecycle status. Must be scope-aware.
- **F12. Generic Context Node and Context Edge CRUD UI**: A schema-driven UI to manage custom context nodes and context edges in the main app exactly how risks and influences are managed. Field types, labels, enums, units, and required markers driven entirely by property definitions. No type-specific code. Must be scope-aware — new ContextNodes/Edges created while a scope is active are offered registration into that scope.
- **F18. Extend Data Management for Context Data**: Extend the existing Excel import/export and JSON backup/restore capabilities in the main app to fully handle ContextNode and ContextEdge data alongside core entities.
- **F13. Zone-Aware 4-Layer Visual Layout**: Extend the layout engine with a zone-aware hierarchical mode positioning nodes across four visual bands: `[Lower Context Zone] → [Operational Risks] → [Business Risks] → [Upper Context Zone]`. Y-axis position within risk bands is determined by computed level (U7). Togglable alongside existing layout options.

### Complex Workload

- **F7. "What-If" Analysis Sandbox**: Toggle mitigations ON/OFF to live-preview downstream exposure changes without committing to the DB. Must operate fully within the active scope — the sandbox must never produce results including out-of-scope nodes.
- **F8. SPICE Scenario Manager**: Full UI for creating, editing, and linking `scenario` context nodes to risks via `SCENARIO_ILLUSTRATES` relationships. Multiple scenarios per risk; one scenario can illustrate multiple risks. Financial aggregation by linked `business_perimeter` nodes where present. Scenario nodes are pure ContextNodes defined in schema YAML — no hardcoded logic in the app.
- **F9. Resilience State Modeling**: Track aggregated exposure of a scope against financial thresholds to classify into **Robust** / **Resilient** / **Fragile** states. Inherently scope-bounded — this state is meaningless without a defined scope boundary.
- **F10. Mitigation Budget Management**: Optimization engine for CAPEX/OPEX-constrained mitigation selection using FAIR ALE as the objective function.
- **F11. Historical Timeline / Versioning**: Traverse back in time to render the graph state "as it was" on previous dates. Scope + version is a valid combination — "show me scope X as it was 3 months ago."
- **F14. FAIR Financial Quantification — SPICE-Calibrated**: FAIR ALE engine deriving all three primary inputs from the graph:

  | FAIR Input                           | Source                                    | Method                                                                                                                |
  | ------------------------------------ | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
  | **Threat Event Frequency (TEF)**     | `Scenario.annual_probability`             | Weighted average across SPICE scenarios flagged `fair_calibration_flag = true`                                        |
  | **Loss Magnitude (LM) distribution** | `Scenario.ebit_impact_[min/expected/max]` | PERT or lognormal distribution fitted to SPICE range                                                                  |
  | **Vulnerability (V)**                | RIM mitigation engine                     | `V = 1 − Effective_Mitigation_Factor` — reuses existing exposure calculation output directly; no re-estimation needed |

  SPICE calibrates financial magnitude inputs; RIM provides vulnerability; FAIR structures the ALE output. Three methodologies, one graph, no parameter duplication.

- **F15. P&L Exposure Dashboard**: Aggregate EBIT-at-risk and FCF-at-risk per `business_perimeter` context node from SPICE scenarios and FAIR ALE outputs. Cross-perimeter portfolio-level financial risk view. Requires F8 and F14.
- **F16. SubGraph Promotion and System of Systems** — see dedicated section below.
- **F17. External Graph Ingestion (Import Adapters)** — see dedicated section below.

---

## 3. SubGraph Architecture and System of Systems (F16)

This is the long-horizon architectural evolution of the scope system. It must be designed now as an extension target, even though full implementation is Phase 5+.

### From Scope to SubGraph

`AnalysisScopeConfig` is the architectural seed. A SubGraph is a scope that has been **promoted** to first-class status with its own identity, ownership, and analytical context.

The promotion path is:

```
Named Scope (current) → SubGraph (Phase 5) → System of Systems (future)
```

**SubGraph adds to Scope:**

```python
@dataclass
class SubGraphConfig(AnalysisScopeConfig):
    # Identity
    scope_type: str = "scope"          # "scope" | "subgraph" | "external"
    version: str = ""                  # semantic version of this subgraph definition
    team_owner: str = ""               # team responsible for this subgraph

    # Boundary policy
    boundary_policy: str = "permeable"
    # "isolated"    — no cross-boundary edges shown or computed
    # "permeable"   — boundary edges displayed but computed separately
    # "transparent" — full graph visible, subgraph highlights a region

    # Hierarchy
    parent_scope_id: str = ""
    child_scope_ids: list = field(default_factory=list)

    # Local analytical context
    local_tpo_ids: list = field(default_factory=list)   # TPOs scoped to this subgraph only
    local_schema_overrides: dict = field(default_factory=dict)
```

### Nested SubGraph Rules

- A SubGraph can contain other SubGraphs via `parent_scope_id` / `child_scope_ids`
- **Exposure calculation** within a child SubGraph uses only its scoped nodes + boundary connections per `boundary_policy`
- **Cross-boundary influence edges** are tagged `boundary: true` so the engine can optionally treat them with attenuated strength or separate confidence
- **Statistics aggregation** flows upward: a parent SubGraph can aggregate child stats or recompute from the union of their node sets (no double-counting)

### System of Systems

When multiple SubGraphs each have their own TPOs, teams, and boundary policies:

- Each SubGraph is a "system" with its own risk posture
- Cross-SubGraph influence edges represent inter-system dependencies
- A dedicated "System of Systems" view renders SubGraph-level composite nodes with inter-system edges
- This requires no new database concepts — it is entirely scope hierarchy + aggregation logic on the existing graph model

### Preparation Required Now (Phase 1)

`AnalysisScopeConfig` must gain a `scope_type` field in Phase 1 (U9). This is a non-breaking addition (defaults to `"scope"`) that flags scopes intended for SubGraph promotion. It costs nothing now and prevents a forced migration later.

---

## 4. External Graph Ingestion (F17)

The ContextNode architecture makes it possible to enrich the RIM graph with externally-sourced graph data — IT architecture maps, supply chain graphs, organizational charts — without any changes to the core application.

### The Import Adapter Pattern

An Import Adapter is a YAML mapping file translating external node/edge types into RIM ContextNode and relationship types:

```yaml
# Example: IT architecture import adapter
adapter_name: "IT Architecture Import"
source_format: "json" # or "csv", "graphml", "neo4j_export", "stix"
zone_default: "lower" # all imported nodes land in lower zone by default

node_mappings:
  - source_type: "Server"
    target_context_node: "technical_target"
    property_mappings:
      - { source: "hostname", target: "name" }
      - { source: "criticality", target: "vulnerability_score" }

  - source_type: "Application"
    target_context_node: "functional_target"
    property_mappings:
      - { source: "app_name", target: "name" }
      - { source: "data_sensitivity", target: "business_value" }

edge_mappings:
  - source_type: "CONNECTS_TO"
    target_relationship: "enable"
    semantic: "context"

post_import_link_rule: "prompt_user"
# "prompt_user" — show unlinked ContextNodes in a review panel
# "auto_by_name" — fuzzy match names to existing OperationalRisk names
# "none" — import as orphan ContextNodes for manual wiring
```

### Supported External Sources (Target)

| Source                                          | Format         | Zone  | Primary Use                                         |
| ----------------------------------------------- | -------------- | ----- | --------------------------------------------------- |
| IT Architecture (CMDB, Cartography, BloodHound) | JSON / GraphML | Lower | Enrich attack chain (TechnicalTarget, EntryPoint)   |
| Supply Chain Map                                | CSV / JSON     | Lower | Enrich operational risks with supplier nodes        |
| Organizational Chart                            | CSV            | Upper | Connect business perimeters to org units            |
| Financial System (ERP export)                   | CSV            | Upper | Pre-populate BusinessPerimeter financial attributes |
| Threat Intelligence Feed (STIX/TAXII)           | STIX JSON      | Lower | Import Attacker / SponsorOfAttack nodes             |

### Key Architectural Constraints

- Imported nodes **always** land as ContextNodes — they never bypass the risk layer
- Imported nodes carry `source: "imported"` and `import_adapter: "<adapter_name>"` base properties (reserved from U6), enabling reverse identification and re-import on refresh
- Imported edges are always `semantic: context` — they never participate in exposure propagation until a risk node is manually linked
- An imported subgraph can be auto-assigned to a named SubGraph (F16), enabling "IT Architecture" or "Supply Chain" to appear as dedicated SubGraphs in the System of Systems view
- Re-importing is **idempotent**: nodes are matched by `(import_adapter, source_id)` composite key and updated in place rather than duplicated

### Preparation Required Now (Phase 1)

ContextNodes (U6) must exist before Import Adapters (F17) can function. Reserve `source` and `import_adapter` in the ContextNode base definition from the start.

---

## 5. Coherent Roadmap (Phased Approach)

Development is scheduled across five sequential phases. **A phase cannot be considered complete until its Testing Gateway is fully passed.**

---

### Phase 1: Foundation, Architecture & Scope Completeness

_Goal: Establish the generic ContextNode architecture, computed level logic, relationship semantics, and — critically — full scope completeness. Every operation in the app must respect the active scope before any new analytical feature is added._

0. **~~[U10]~~** Schema-Driven Filter System ✅ — fully dynamic `FilterManager`, `render_visualization_filters`, and `render_filter_sidebar`. All filter UI now iterates registry types; no hardcoded entity/relationship IDs. Preset buttons are schema-derived. All/None quick-toggle buttons added to every multiselect group.
1. **~~[U6]~~** Generic ContextNode Architecture — YAML `context_nodes` section, generic Neo4j label strategy (`ContextNode` + `node_type` + `zone` properties), schema loader updates. Reserve `source` and `import_adapter` base properties on all ContextNodes.
2. **~~[U7]~~** Computed Risk Level — replace stored `level` with BFS-computed level. Update all queries and display logic.
3. **~~[U8]~~** Relationship Semantic Types ✅ — added `semantic` to all relationship definitions. Exposure engine routes exclusively on `semantic: influence`.
4. **~~[U9]~~ Scope Completeness Enforcement** ✅ — audited and repaired all scope gaps:
   - `get_statistics()` → added `scope_node_ids` parameter
   - `get_all_nodes_for_selection()` → added `scope_node_ids` parameter
   - All CRUD forms → scope-aware create/delete behavior with 'Add to scope' and 'Remove from scope' logic
   - `get_graph_data()` scope expansion → extended ContextNodes
   - `AnalysisScopeConfig` → added non-breaking `scope_type` field (default `"scope"`)
   - Cache key strategy → scope-keyed from the start
5. **[F1 & F2]** Intelligent Caching (scope-keyed) and Progressive UI Loading.
6. **[F3]** Complexity Toggle.
7. **[U5]** Mitigation CAPEX / OPEX attributes.

> 🛑 **GATEWAY 1: Extensive Code Review & Testing Pass**
>
> - **Automatic:** Verify computed levels match previously stored levels on all demo datasets. Confirm exposure engine produces identical results before/after semantic routing change. Confirm `get_statistics()` with a scope returns counts that sum to the scoped subset only — not the full graph. Confirm generic ContextNode CRUD requires zero type-specific code paths. Confirm `AnalysisScopeConfig` loads/saves `scope_type` without breaking existing scope data.
> - **Manual:** UAT via Phase 1 Document. Activate a scope and verify that ALL of the following reflect scoped data only: statistics panel, node selection dropdowns, influence analysis, mitigation analysis, and exposure calculations. Add a new `context_node` type to the YAML and verify it appears in the UI with no code change. Verify Simple Mode hides advanced tabs correctly. Confirm CAPEX/OPEX fields persist correctly.

---

### Phase 2: ContextNode UI, Zone Layout & Quality of Life

_Goal: Expose ContextNode infrastructure through working UI. Introduce zone-aware visualization. Solidify the data pipeline with Pydantic._

1. **[U4]** Pydantic Data Validation — schemas for both risk nodes and generic ContextNodes (type enforcement from YAML property definitions).
2. **[F12]** Generic Context Node and Context Edge CRUD UI — scope-aware single form component to manage custom nodes and edges.
3. **[F18]** Extend Data Management — update Excel import/export and JSON backup/restore to handle ContextData.
4. **[F13]** Zone-Aware 4-Layer Visual Layout — zone-anchored hierarchical layout mode.
5. **[F4]** One-Click Visualization Export.
6. **[F5]** Automated Risk Threshold Alerts (scope-aware).
7. **[F6]** Mitigation Exposure View (scope-aware).
8. **[F7]** "What-If" Analysis Sandbox (scope-bounded — must never produce out-of-scope results).

> 🛑 **GATEWAY 2: Extensive Code Review & Testing Pass**
>
> - **Automatic:** Pydantic rejection tests for malformed ContextNode property types. Mathematical parity tests for What-If sandbox vs. committed DB state. **Critical scope test:** confirm that sandbox exposure calculations for a scoped graph are identical whether the full graph contains 20 or 200 nodes outside the active scope. Zone layout tests verifying upper/lower node placement matches schema zone definitions.
> - **Manual:** UAT via Phase 2 Document. Add a new `context_node` type mid-sprint and verify zero code changes needed. Confirm zone-aware layout on both SMR nuclear and cybersecurity demo datasets. Activate a scope, run What-If, confirm only scoped nodes appear in the sandbox preview. Validate What-If does not alter DB state.

---

### Phase 3: SPICE Scenarios & Financial Anchoring

_Goal: Introduce SPICE scenario management. Build P&L exposure view. Lay the complete data foundation for FAIR._

1. **[F8] SPICE Scenario Manager** — ContextNode-based scenario create/edit/link, scope-aware, entirely schema-driven.
2. **[F9] Resilience State Modeling** — Robust/Resilient/Fragile classification from aggregated SPICE exposure against scope thresholds. Inherently scope-bounded.
3. **[F15] P&L Exposure Dashboard** — cross-perimeter financial risk view from SPICE scenarios.

> 🛑 **GATEWAY 3: Extensive Code Review & Testing Pass**
>
> - **Automatic:** SPICE financial aggregation math vs. manually computed expected values. Resilience State threshold transition tests at boundary values (exposure exactly at threshold, zero scenarios, scenarios with no perimeter link). Verify `scenario` ContextNodes created via generic CRUD (F12) are correctly recognized by the SPICE Scenario Manager without special-casing.
> - **Manual:** UAT via Phase 3 Document. Validate on SMR nuclear demo dataset. Verify Resilience State responds correctly to probability and impact parameter changes. Confirm P&L dashboard aggregates correctly across multiple perimeters within a scope.

---

### Phase 4: FAIR Financials & Advanced Analysis

_Goal: Deliver the SPICE→FAIR pipeline. Produce monetized ALE outputs grounded entirely in graph data._

1. **[F14] FAIR Financial Quantification — SPICE-Calibrated** — ALE engine using TEF from SPICE, LM distribution from SPICE impact ranges, Vulnerability from `1 − Effective_Mitigation_Factor`. No manual parameter entry. Scope-aware.
2. **[F10] Mitigation Budget Management** — CAPEX/OPEX-constrained optimization using FAIR ALE as objective function.

> 🛑 **GATEWAY 4: Extensive Code Review & Testing Pass**
>
> - **Automatic:** FAIR math validation against known reference values. Budget optimization parameterized tests at constraint boundaries (zero budget, unconstrained, conflicting prerequisites). Validate `V = 1 − Effective_Mitigation_Factor` across varied mitigation configurations. **Critical isolation test:** verify ALE output does not change when out-of-scope nodes are added to the full graph.
> - **Manual:** UAT via Phase 4 Document. ALE sanity check with a risk practitioner on SMR demo dataset. Scope 1 vs. Scope 2 budget optimization comparison produces differentiated, strategically meaningful recommendations.

---

### Phase 5: SubGraph Promotion, External Ingestion & History

_Goal: Elevate scopes to first-class SubGraphs. Enable external graph import. Add temporal tracking._

1. **[F16] SubGraph Promotion and System of Systems** — promote `AnalysisScopeConfig` to `SubGraphConfig` with `boundary_policy`, parent/child hierarchy, and local TPOs. Implement nested exposure aggregation. Implement System of Systems composite view showing SubGraph-level nodes with inter-system edges.
2. **[F17] External Graph Ingestion (Import Adapters)** — YAML-defined adapters mapping external node/edge types to ContextNode types. Idempotent re-import by `(import_adapter, source_id)` key. Support for IT architecture (CMDB), supply chain maps, organizational charts, and STIX threat intelligence. Post-import review panel for unlinked ContextNodes.
3. **[F11] Historical Timeline / Versioning** — render graph state "as it was" at any previous date. Scope + version is a valid combination. Link financial risk reductions to mitigation implementation events.

> 🛑 **GATEWAY 5: Extensive Code Review & Testing Pass**
>
> - **Automatic:** SubGraph boundary policy tests — `isolated` produces zero cross-boundary edges in exposure calculation; `permeable` includes them. Nested SubGraph aggregation tests — parent stats equal union of child stats with no double-counting. Import adapter idempotency test — import the same external file twice and verify no duplicate nodes (matched by composite key). Historical snapshot consistency test — restored state reproduces identical exposure as original.
> - **Manual:** UAT via Phase 5 Document. Demonstrate a 3-level nested SubGraph hierarchy on SMR demo dataset. Import a sample IT architecture JSON via adapter and verify nodes land as ContextNodes in the lower zone, correctly linked to existing OperationalRisks. Show a full remediation timeline with FAIR ALE delta across 6+ monthly snapshots.

---

## 6. Feature Dependency Map

```
                       ──► F12 (Generic CRUD UI for Nodes & Edges)
                       ──► F18 (Data Management extensions)
                       ──► F13 (Zone layout)
                       ──► F8  (SPICE Manager — scenario is a ContextNode)
                       ──► F17 (Import Adapters — imported nodes are ContextNodes)

U7 (Computed levels)  ──► F13 (Zone layout — Y-axis positioning within risk bands)

U8 (Rel. semantics)   ──► U4  (Pydantic — type-aware validation)
                      ──► F14 (FAIR — exposure engine reuse via semantic routing)

U9 (Scope complete)   ──► ALL analytical features (F7, F8, F9, F14, F15, F16)
                         Partial scope-awareness silently corrupts all downstream analytics.
                         This MUST be resolved before any new analytical feature is added.

F2  (Caching)         ──► Must be scope-keyed from initial implementation (U9 dependency)

F8  (SPICE)           ──► F9  (Resilience State — financial thresholds)
                      ──► F15 (P&L Dashboard)
                      ──► F14 (FAIR — TEF and LM calibration)

F14 (FAIR)            ──► F10 (Budget Optimization — ALE as objective function)
                      ──► F15 (P&L Dashboard — ALE layer)
                      ──► F11 (Versioning — ALE delta per snapshot)

U5  (CAPEX/OPEX)      ──► F10 (Budget Optimization — cost constraints)

F7  (What-If)         ──► F10 (Budget Optimization — UI groundwork)

F9  (Resilience)      ──► F11 (Versioning — state transitions over time)

U9 + AnalysisScopeConfig.scope_type ──► F16 (SubGraph — non-breaking prep in Phase 1)

F16 (SubGraph)        ──► F17 (External Ingestion — imported subgraphs auto-assign to SubGraph)
```

---

## 7. Domain Adaptability Matrix

The schema-driven ContextNode architecture makes the platform deployable across domains with YAML-only changes:

| Domain                 | Upper Zone Nodes                       | Lower Zone Nodes                                                         | Key Relationship Types                   |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| **Nuclear SMR**        | Company, BusinessPerimeter, Scenario   | —                                                                        | IMPACT_FINANCIALLY, SCENARIO_ILLUSTRATES |
| **Cybersecurity**      | Company, BusinessPerimeter, Scenario   | FunctionalTarget, TechnicalTarget, EntryPoint, Attacker, SponsorOfAttack | ENABLE, TARGET, USE, MANAGE              |
| **Aerospace**          | Programme, BusinessPerimeter, Scenario | SubSystem, Component, Supplier                                           | DEPENDS_ON, SUPPLIED_BY                  |
| **Financial Services** | Entity, RegulatoryPerimeter, Scenario  | CounterParty, Instrument                                                 | EXPOSES_TO, COLLATERALIZES               |

All domains share the same Risk Layer, exposure engine, SPICE/FAIR pipeline, and Resilience State model. Domain differentiation lives entirely in the schema YAML.

---

## 8. Open Questions — Design Decisions Pending

The following questions should be resolved before Phase 5 implementation begins:

**Q1 — SubGraph Boundary Policy and Exposure Calculation**
When `boundary_policy: "permeable"`, cross-boundary influence edges are shown. Do they participate in exposure calculation at full strength, attenuated strength, or via a separate confidence-weighted computation? The answer has significant implications for the exposure engine's scope handling.

**Q2 — Local TPOs in SubGraphs**
Should a SubGraph be allowed to define its own local TPOs not present in the parent graph? This enables team-level risk management with team-specific objectives, but affects how computed levels work for risks whose TPOs are local vs. inherited from the parent.

**Q3 — Import Adapter Versioning and Staleness**
When an external graph source updates (e.g., CMDB changes daily), how should deleted nodes be handled? Options: mark as `archived`, hard delete, or keep with `stale: true` flag. The choice affects data integrity and the utility of historical analysis (F11).

**Q4 — SPICE Scenario Ownership in SubGraphs**
If a Scenario ContextNode is linked to a BusinessRisk in SubGraph A, should it be visible in the parent graph's P&L Dashboard? Or should Scenarios be contained within their SubGraph? This is a scope containment question with financial reporting implications.

**Q5 — System of Systems Composite Exposure Score**
At the System of Systems level, each SubGraph appears as a composite node. What is that node's exposure score? Candidate options: max exposure of any child node, impact²-weighted average (consistent with existing Weighted Risk Score formula), or FAIR ALE sum of children. The answer determines what executives see at portfolio level.
