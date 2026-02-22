# Risk Influence Map (RIM) - Development Roadmap & Agent Reference

**Context for Future AI Agents:** 
This `ROADMAP.md` serves as the primary system reference and source of truth for all future development within the RIM repository. All features, architecture changes, and phase transitions must align with this document. The overarching philosophy is **simplicity, modularity, and strict validation** before implementing highly complex computational features. Each phase acts as a dependent foundation for the next. 

Between every phase, there is a mandatory, exhaustive testing gateway (Automated and Manual) before progressing.

---

## 1. Updates & Architectural Improvements

These foundational changes are required to ensure the application remains stable, readable, and easy to extend as complex simulation features are added.

*   **U1. Externalize Static Content**: Move hardcoded documentation from `app.py` into separate `.md` files in a `docs/` folder, loading them efficiently at runtime (e.g., via `st.markdown`).
*   **U2. Decouple Entry Point**: Split the monolithic `app.py` into smaller, focused pages (e.g., `pages/0_🏠_Home.py`). Let `app.py` only handle Streamlit configuration and primary routing.
*   **U3. Centralized State Management**: Introduce a dedicated state manager module (`utils/state_manager.py`) to standardize `st.session_state` initialization and simplify type hinting across the app.
*   **U4. Strict Data Validation (Pydantic)**: Implement rigid data validation schemas for all incoming graph logic (nodes, edges, budgets, exposure configurations) using `pydantic`. This guarantees that downstream algorithms (like budget optimization) won't fail due to malformed data configurations.

## 2. Planned Features

Features are categorized by their expected technical complexity.

### Simple Workload Features
*   **F1. Progressive UI Loading**: Add pagination or virtual scrolling to the CRUD tables (Risks, TPOs, Mitigations tabs) to maintain snappy browser performance on extremely large graphing scopes.
*   **F2. Intelligent Caching**: Utilize Streamlit `@st.cache_data` heavily around expensive database queries and graph layout algorithms (e.g., Sugiyama) to prevent redundant UI re-renders.
*   **F3. One-Click Visualization Export**: Add functionality to export the active, styled graph view directly to PNG or PDF for stakeholder presentations.
*   **F4. Automated Risk Threshold Alerts**: Configure simple visual indicators in the UI to flag nodes if their computed exposure score dynamically exceeds a predefined operational threshold.

### Complex Workload Features
*   **F5. "What-If" Analysis Sandbox**: A simulation mode where users can toggle mitigations ON/OFF to live-preview the downstream exposure drop across the network *without* committing changes to the production Neo4j database. Target: Visual proof of mitigation value.
*   **F6. Mitigation Budget Management**: An optimization engine to calculate the most effective set of mitigation implementations given a fixed financial or resource budget. 
    *   *Implementation Strategy*: Start locally (Scope 1) to identify maximum risk reduction per budget unit. Scale up by comparing Scope 1 to an extended Scope 2. This visually demonstrates to stakeholders where budget increases yield diminishing returns across the broader graph.
*   **F7. Historical Timeline / Versioning**: Allow the system to traverse back in time and render the complete graph state "as it was" on previous dates, helping prove risk remediation progress to executive leadership.

---

## 3. Coherent Roadmap (Phased Approach)

To ensure smooth delivery and maintain a modular architecture, development is scheduled in strict sequential phases. **A phase cannot be considered complete until its Testing Gateway is fully passed.**

### Phase 1: Foundation & Refactoring (Near-Term)
*Goal: Prepare the application for heavy computational features by simplifying the codebase.*
1. **[U1 & U2]** Clean up `app.py` and modularize the page structure.
2. **[U3]** Establish Centralized State Management.
3. **[F1 & F2]** Implement Intelligent Caching and Progressive UI Loading.

> 🛑 **GATEWAY 1: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Validate that refactored UI elements and state variables do not break existing Streamlit behaviors. All existing unit tests pass.
> *   **Manual:** Execute User Acceptance Testing via the **Phase 1 Acceptance Document** (to be designed). Verify that page transitions, state retention, and baseline graph loading are noticeably faster.

### Phase 2: Quality of Life & Data Integrity (Mid-Term)
*Goal: Solidify the data pipeline and provide immediate value to users.*
1. **[U4]** Implement rigid Pydantic Data Validation (Crucial precursor to optimization).
2. **[F3]** Build the One-Click Visualization Export feature.
3. **[F4]** Add Automated Risk Threshold Alerts.
4. **[F5]** Build the "What-If" Sandbox (Serves as UI groundwork for the Budget Manager).

> 🛑 **GATEWAY 2: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Implement unit test suite verifying Pydantic schema rejection of bad network data, and formula parity for the Sandbox exposure calculations.
> *   **Manual:** Execute User Acceptance Testing via the **Phase 2 Acceptance Document**. Validate the What-If simulation changes exposure correctly *without* altering the DB. Confirm PDF/PNG exports render accurately.

### Phase 3: Advanced Optimization & Analytics (Long-Term)
*Goal: Introduce powerful analytical capabilities built on stable foundations.*
1. **[F6] Mitigation Budget Management**: Implement the scoped budget optimization engine leveraging the What-If architecture.
2. **[F7] Historical Timeline**: Finalize the analytical suite by adding temporal graph state comparisons.

> 🛑 **GATEWAY 3: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Budget optimization algorithms must have dedicated parameterized testing covering edge cases (zero budget, infinite budget, disconnected subgraphs). 
> *   **Manual:** Execute User Acceptance Testing via the **Phase 3 Acceptance Document**. Validate that Scope 1 vs Scope 2 dynamic budget comparisons display accurately to the end user.
