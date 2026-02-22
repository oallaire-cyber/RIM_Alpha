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
*   **U5. Mitigation Budget Attributes**: Extend the Mitigation data schema to include specific financial attributes: **CAPEX** (Capital Expenditure) and **OPEX** (Operational Expenditure). This provides the foundation for cost-optimization algorithms.

## 2. Planned Features

Features are categorized by their expected technical complexity to ensure a balanced workload across development phases.

### Simple / Medium Workload Features
*   **F1. Progressive UI Loading**: Add pagination or virtual scrolling to the CRUD tables (Risks, TPOs, Mitigations tabs) to maintain snappy browser performance on extremely large graphing scopes.
*   **F2. Intelligent Caching**: Utilize Streamlit `@st.cache_data` heavily around expensive database queries and graph layout algorithms (e.g., Sugiyama) to prevent redundant UI re-renders.
*   **F3. Complexity Toggle (Simple vs. Advanced Mode)**: Implement a streamlined "New User" UI mode that hides advanced analytical tabs (like deep influence explorers or budget optimizers) via Streamlit's page mechanism and session state. This lowers the barrier to entry for non-technical stakeholders.
*   **F4. One-Click Visualization Export**: Add functionality to export the active, styled graph view directly to PNG or PDF for stakeholder presentations.
*   **F5. Automated Risk Threshold Alerts**: Configure simple visual indicators in the UI to flag nodes if their computed exposure score dynamically exceeds a predefined operational threshold.
*   **F6. Mitigation Exposure View (Business Focus)**: Introduce a dedicated analytical view highlighting all mitigations contributing to the exposure reduction for selected **Business Risks**, with filtering by lifecycle status (Active, Planned, Proposed).

### Complex Workload Features
*   **F7. "What-If" Analysis Sandbox**: A simulation mode where users can toggle mitigations ON/OFF to live-preview the downstream exposure drop across the network *without* committing changes to the production Neo4j database. 
*   **F8. Risk Financial Quantification (FAIR)**: Implement a simplified version of the FAIR (Factor Analysis of Information Risk) methodology to assign tangible financial loss values to risks. This translates abstract exposure scores into specific monetary risk (e.g., Value at Risk).
*   **F9. Resilience State Modeling**: Track the aggregated exposure of a scope against defined financial thresholds to categorize the operational reality into three strategic states:
    1.  **Robust**: Incidents can be managed with existing resources/OPEX without severe day-to-day perturbation (just delayed projects).
    2.  **Resilient**: Incidents trigger crisis protocols (BCP/DR). Day-to-day operations are degraded with extra costs, but the entity has the budget/means to recover internally.
    3.  **Fragile**: Massive impact. Survival depends on external stakeholder decisions or structural business model pivots. 
    *This state model serves as the ultimate executive output bridging risk engineering with C-Suite strategy.*
*   **F10. Mitigation Budget Management**: An optimization engine to calculate the most financially effective set of mitigation implementations given fixed CAPEX/OPEX constraints. Validated by viewing Scope 1 vs. Scope 2 ROI differences.
*   **F11. Historical Timeline / Versioning**: Allow the system to traverse back in time and render the complete graph state "as it was" on previous dates, helping prove risk remediation progress.

---

## 3. Coherent Roadmap (Phased Approach)

To ensure manageable workloads and maintain code quality, development is scheduled across four strict sequential phases. **A phase cannot be considered complete until its Testing Gateway is fully passed.**

### Phase 1: Foundation & UX Simplification 
*Goal: Prepare the application architecture, extend core data models, and improve baseline usability.*
1. **[U1 & U2]** Clean up `app.py` and modularize the page structure.
2. **[U3]** Establish Centralized State Management.
3. **[F1 & F2]** Implement Intelligent Caching and Progressive UI Loading.
4. **[F3]** Complexity Toggle (Simple vs Advanced UI modes).
5. **[U5]** Extend the Mitigation schema to include CAPEX and OPEX budget attributes.

> 🛑 **GATEWAY 1: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Validate refactored UI elements and state variables do not break existing routing. Schema updates (CAPEX/OPEX) successfully save/load without data loss.
> *   **Manual:** UAT via Phase 1 Document. Verify page transitions, state retention, baseline graph loading speed, and ensure the "Simple Mode" accurately hides advanced tabs.

### Phase 2: Quality of Life & Tactical Business Views 
*Goal: Solidify the data pipeline and introduce mid-tier analytical views.*
1. **[U4]** Implement rigid Pydantic Data Validation (Crucial precursor to optimization).
2. **[F4]** Build the One-Click Visualization Export feature.
3. **[F5]** Add Automated Risk Threshold Alerts.
4. **[F6]** Build the Mitigation Exposure View (Business Focus) with active/planned/proposed filtering.
5. **[F7]** Build the "What-If" Sandbox (Serves as UI groundwork for the Budget Manager).

> 🛑 **GATEWAY 2: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Unit test suite verifying Pydantic schema rejection of bad network data, and mathematical parity for Sandbox exposure calculations.
> *   **Manual:** UAT via Phase 2 Document. Validate What-If simulation changes exposure correctly *without* altering the DB. Confirm Mitigation Exposure views map connections accurately.

### Phase 3: FAIR Financials & Resilience Modeling 
*Goal: Introduce quantitative financial risk modeling and executive resilience reporting.*
1. **[F8] FAIR Financial Quantification**: Transcribe abstract risk scores into financial loss models.
2. **[F9] Resilience State Modeling**: Calculate and display "Robust/Resilient/Fragile" states based on aggregated FAIR financial thresholds and exposure levels. 

> 🛑 **GATEWAY 3: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Data science testing of the FAIR math logic to ensure monetary calculations do not break under extreme edge cases (e.g., chained likelihoods).
> *   **Manual:** UAT via Phase 3 Document. Present executive views on dummy data. Validate that the aggregation of financial impact properly triggers the transitions between the three Resilience states.

### Phase 4: Advanced Budget Optimization & History
*Goal: Deliver full financial optimization planning and time-series progress tracking.*
1. **[F10] Mitigation Budget Management**: Implement the scoped budget optimization engine leveraging the FAIR dollar values against CAPEX/OPEX limits.
2. **[F11] Historical Timeline / Versioning**: Finish the analytical suite by adding temporal graph state comparisons linked to financial risk reductions over time.

> 🛑 **GATEWAY 4: Extensive Code Review & Testing Pass** 
> *   **Automatic:** Optimization engine parameterized testing covering constraint boundary limits (zero budget vs infinite budget, conflicting mitigation prerequisites).
> *   **Manual:** UAT via Phase 4 Document. Validate that Scope 1 vs Scope 2 dynamic budget comparisons display accurately, generating strategic, executive-ready mitigation plans.
