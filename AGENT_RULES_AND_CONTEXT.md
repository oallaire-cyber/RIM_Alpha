# RIM Project: Agent Rules and Context

This document provides the foundational rules, architectural context, and operating procedures for all AI agents contributing to the Risk Influence Map (RIM) project.

## 1. Core Architectural Philosophy
**Simplicity, Modularity, and Strict Validation**
- **No unauthorized complexity**: Do not implement highly complex computational features without ensuring the fundamental architecture (Phase 1) is rock-solid.
- **Testing Gateways**: A phase or feature is NEVER considered complete until rigorous automated and manual testing is executed and passed.
- **Schema-Driven Adaptability**: The platform is domain-agnostic. All domain-specific logic must reside in the `schema YAML`, NOT in the application code.

## 2. The Golden Rules of the Graph Engine
Agents working on the backend or database layer must strictly adhere to these principles:

### A. The Computational Engine Boundary (Core Types vs. Context)
- **The Risk/Computational Layer**: `BusinessRisk`, `OperationalRisk`, and `Mitigation` are the **ONLY** core node types that carry computational weight. They own and execute the exposure engine, level deduction, mitigation effectiveness, and influence propagation algorithms.
  - *Note for the future*: If a future requirement demands a new node or edge type that *must* participate mathematically in exposure calculations, it must be carefully added to this core layer.
- **Context Layer**: All other node types (e.g., Scenarios, Targets, Attackers) are generic `ContextNodes`.
- **Enforcement**: Adding a new `ContextNode` type requires **zero app code modification**. Agents must only update the YAML schema. Any attempt to hardcode a type-specific `if/else` block for a ContextNode will be rejected.

### B. The Scope Completeness Contract
- **Rule**: When a scope is active, the scoped subgraph IS the entire graph.
- **Enforcement**: All operations must accept and propagate a `scope_context` or `scope_node_ids`.
- **Checklist**: If you are writing a query, computation, or UI component, you must ensure:
  - Statistics compute ONLY scoped nodes.
  - Node dropdowns show ONLY scoped nodes.
  - Exposure propagation explicitly stops at the scope boundary.
  - Partial scope-awareness is considered a critical bug.

### C. Relationship Semantics
- Only `semantic: influence` relationships participate in exposure propagation.
- `semantic: context` and `semantic: cluster` are traversable and displayable but carry **no computational weight**.

### D. Computed, Not Stored
- Risk Level (e.g., distance to Top Programme Objective) is **dynamically computed** via Breadth-First Search at read time. Do not attempt to store or cache it as a static property on the node in the DB.

## 3. Parallel Multi-Agent Execution Rules
The `ROADMAPv2.md` defines parallel work streams to prevent agent collisions.
- **Stream A (Visual/UI)**: Focus strictly on Streamlit, PyVis, and CSS. Do not alter database logic.
- **Stream B (Schema/Data)**: Focus on Pydantic validation, CRUD forms, and state management.
- **Stream C (Analytical/Algorithmic)**: Focus on the exposure engine, math, and graph algorithms.
- **Cross-Stream Dependency**: If an agent in Stream A needs a backend data change, they must explicitly document the dependency or pause until Stream B completes the prerequisite. Do not perform "out-of-lane" refactoring.

## 4. Understanding the 3-Tier Architecture
When working on data ingestion or display, keep the hierarchy pristine:
1. **Top Tier**: Business Objectives (measurable strategic goals).
2. **Middle Tier**: Business Risks (consequences, owned by C-suite).
3. **Bottom Tier**: Operational Risks (causes, owned by functional teams).
Agents must never collapse this hierarchy by treating causes and consequences interchangeably.

## 5. Development Workflow for Agents
1. **Read `task.md` & `ROADMAPv2.md`**: Understand your specific assignment stream.
2. **Consult Schema YAML**: Before writing code to handle entities, read the YAML definitions.
3. **Validate Scope**: If your feature touches the graph, write a test ensuring it respects isolation boundaries.
4. **Pydantic First**: Any new data inflow must pass through strict Pydantic models.
5. **Verify and Walkthrough**: Generate a `walkthrough.md` with proof of testing upon completion.
