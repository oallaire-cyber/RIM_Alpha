"""
Risk Influence Map (RIM) Application.

Main entry point that wires all modular components together.
"""

import streamlit as st
from datetime import datetime

# Configuration
from core import get_registry
from config import APP_TITLE, APP_ICON, LAYOUT_MODE, NEO4J_DEFAULT_URI, NEO4J_DEFAULT_USER, NEO4J_DEFAULT_PASSWORD, RISK_LEVEL_CONFIG
from config.schema_loader import SchemaLoader, AnalysisScopeConfig

# Database
from database import RiskGraphManager

# UI Components
from ui import (
    inject_styles,
    FilterManager,
    LayoutManager,
    render_influence_analysis_panel,
    render_mitigation_analysis_panel,
)

# Legend
from ui.legend import (
    render_graph_legend,
    render_compact_legend,
)

# Dynamic UI
from ui.dynamic_tabs import render_dynamic_tabs
from ui.dynamic_forms import build_entity_form

# CRUD Tabs
from ui.tabs import (
    render_risks_tab,
    render_tpos_tab,
    render_mitigations_tab,
    render_influences_tab,
    render_import_export_tab,
)

# Visualization
from visualization import (
    render_graph_streamlit,
)

# Layout generators
from ui.layouts import (
    generate_layered_layout,
    generate_category_layout,
    generate_tpo_cluster_layout,
    generate_auto_spread_layout,
)


def _compute_stats_from_graph(nodes, edges):
    """Compute statistics from pre-filtered graph data (used for scoped stats)."""
    registry = get_registry()
    risk_levels = registry.get_risk_levels()
    # DB stores level labels (e.g. "Business"), not IDs ("business")
    level1_label = risk_levels[0]["label"] if risk_levels else "Business"
    level2_label = risk_levels[1]["label"] if len(risk_levels) > 1 else "Operational"
    
    risk_nodes = [n for n in nodes if n.get("node_type") == "Risk"]
    tpo_nodes = [n for n in nodes if n.get("node_type") == "TPO"]
    mit_nodes = [n for n in nodes if n.get("node_type") == "Mitigation"]
    
    influence_edges = [e for e in edges if e.get("edge_type") == "INFLUENCES"]
    tpo_edges = [e for e in edges if e.get("edge_type") == "IMPACTS_TPO"]
    mit_edges = [e for e in edges if e.get("edge_type") == "MITIGATES"]
    
    return {
        "total_risks": len(risk_nodes),
        "level1_risks": len([n for n in risk_nodes if n.get("level") == level1_label]),
        "level2_risks": len([n for n in risk_nodes if n.get("level") == level2_label]),
        "new_risks": len([n for n in risk_nodes if n.get("origin") == "New"]),
        "legacy_risks": len([n for n in risk_nodes if n.get("origin") == "Legacy"]),
        "total_tpos": len(tpo_nodes),
        "total_mitigations": len(mit_nodes),
        "total_influences": len(influence_edges),
        "total_tpo_impacts": len(tpo_edges),
        "total_mitigates": len(mit_edges),
    }


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "manager" not in st.session_state:
        st.session_state.manager = None
    if "connected" not in st.session_state:
        st.session_state.connected = False
    if "filter_manager" not in st.session_state:
        st.session_state.filter_manager = FilterManager()
    if "layout_manager" not in st.session_state:
        st.session_state.layout_manager = LayoutManager()
    if "physics_enabled" not in st.session_state:
        st.session_state.physics_enabled = True
    if "color_by" not in st.session_state:
        st.session_state.color_by = "level"
    if "capture_mode" not in st.session_state:
        st.session_state.capture_mode = False
    if "influence_explorer_enabled" not in st.session_state:
        st.session_state.influence_explorer_enabled = False
    if "selected_node_id" not in st.session_state:
        st.session_state.selected_node_id = None


def render_help_section():
    """Render the help section in the sidebar."""
    with st.sidebar.expander("❓ Help & Documentation", expanded=False):
        help_tab = st.radio(
            "Select topic:",
            ["Overview", "Scopes", "Exposure", "Influence", "Mitigations", "Layouts"],
            label_visibility="collapsed",
            horizontal=True
        )
        
        if help_tab == "Overview":
            st.markdown("""
            ### 🎯 RIM Overview
            
            The **Risk Influence Map** transforms static risk registers into
            **dynamic risk intelligence** by modeling relationships between:
            
            - **Business Risks** (◆ Diamond): Consequence-oriented, managed by leadership
            - **Operational Risks** (● Circle): Cause-oriented, managed by teams  
            - **TPOs** (⬡ Hexagon): Top Program Objectives at risk
            - **Mitigations** (🛡️ Box): Controls and protective actions
            
            ---
            
            **Core Capabilities:**
            
            | Capability | What it does |
            |------------|--------------|
            | 🔗 Influence mapping | Models how risks amplify each other across the network |
            | ⚡ Exposure calculation | Quantifies composite risk score with mitigation diminishing returns |
            | 📐 Analysis scopes | Focus all analysis on a named subset of nodes |
            | 🛡️ Mitigation analysis | Coverage gaps, treatment effectiveness, high-priority flags |
            | 🎯 TPO tracking | Links risks to program objectives with impact levels |
            | 📊 Statistics | Live dashboard adapts to active scope |
            
            ---
            
            **Influence Types (auto-determined by node levels):**
            - **Level 1** (red): Operational → Business — *causal link*
            - **Level 2** (purple): Business → Business — *amplification*
            - **Level 3** (blue): Operational → Operational — *contribution*
            """)
        
        elif help_tab == "Scopes":
            st.markdown("""
            ### 📐 Analysis Scopes
            
            Scopes let you define **named subsets** of your risk graph
            for focused analysis. All features respect scope boundaries.
            
            ---
            
            **Creating a Scope:**
            1. Open Configuration Manager (`app_config.py`)
            2. Go to **📐 Scopes** tab
            3. Pick nodes, set name and color
            4. Scope is saved in `schema.yaml`
            
            ---
            
            **Selecting a Scope:**
            - Sidebar → **📐 Analysis Scopes** expander
            - Select one or more scopes (union of node IDs)
            - Click **🌐 Full Graph** to clear
            
            ---
            
            **Smart Expansion:**
            
            When a scope is active, the system automatically includes:
            - **Mitigations** connected to scoped risks
            - **TPOs** connected to scoped risks
            - **1-hop risk neighbors** (toggle "Show connected neighbors")
            
            ---
            
            **Scoped Features:**
            
            | Feature | When scope active |
            |---------|-------------------|
            | 📊 Statistics | Counts only scoped entities |
            | ⚡ Exposure | Risks + connected mitigations only |
            | 🔍 Influence Analysis | Scoped propagators, convergence, paths |
            | 🛡️ Mitigation Analysis | Coverage gaps within scope |
            | CRUD Tabs | List only scoped entities |
            | Influence Explorer | Node picker shows scoped nodes |
            
            > **Tip:** Scoped metrics may differ from Full Graph — this is
            > expected because cross-boundary chains are excluded.
            """)
        
        elif help_tab == "Exposure":
            st.markdown("""
            ### ⚡ Exposure Calculation
            
            Quantifies risk severity by combining base scores,
            mitigation effectiveness, and upstream influence limitation.
            
            ---
            
            **1️⃣ Base Exposure**
            ```
            Base = Likelihood × Impact
            ```
            *Scale: 1-10 each → Base ranges 1 to 100*
            
            ---
            
            **2️⃣ Mitigation Factor** *(diminishing returns)*
            ```
            Factor = ∏(1 - Effectiveness)
            ```
            
            | Effectiveness | Reduction | Description |
            |---------------|-----------|-------------|
            | Critical | 90% | Near-complete elimination |
            | High | 70% | Strong protection |
            | Medium | 50% | Moderate reduction |
            | Low | 30% | Minimal impact |
            
            *Example: High + Medium = 0.3 × 0.5 = 0.15 → 85% total reduction*
            
            ---
            
            **3️⃣ Influence Limitation**
            
            Upstream risks **limit** downstream mitigation effectiveness:
            ```
            Limitation = Avg(Upstream_Residual × Strength)
            ```
            
            *"Fixing symptoms without addressing root causes has limited effect"*
            
            | Strength | Weight | Interpretation |
            |----------|--------|----------------|
            | Critical | 1.0 | Direct, inevitable |
            | Strong | 0.75 | High probability |
            | Moderate | 0.50 | Likely contributes |
            | Weak | 0.25 | Minor contribution |
            
            ---
            
            **4️⃣ Final Exposure**
            ```
            Final = Base × Effective_Mitigation_Factor
            ```
            
            ---
            
            **📊 Global Metrics**
            
            | Metric | Purpose |
            |--------|---------|
            | Residual Risk % | How much risk remains after mitigations |
            | Weighted Risk Score | Impact²-weighted executive metric (0-100) |
            | Max Single Exposure | Worst-case individual risk alert |
            
            > **Scope-aware:** When a scope is active, exposure only
            > considers in-scope risks and their connected mitigations.
            > Toggle "Show connected neighbors" to include adjacent risks.
            """)
        
        elif help_tab == "Influence":
            st.markdown("""
            ### 🔗 Influence Model
            
            Models how risks propagate through the network.
            Source risk **causes or amplifies** target risk.
            
            ---
            
            **Influence Types (auto-determined):**
            
            | Type | From → To | Meaning |
            |------|-----------|---------|
            | Level 1 | Operational → Business | Causes consequence |
            | Level 2 | Business → Business | Amplifies impact |
            | Level 3 | Operational → Operational | Contributes to |
            
            ---
            
            **Strength Levels:**
            - **Critical**: Direct, inevitable causation
            - **Strong**: High probability of propagation
            - **Moderate**: Likely contributes
            - **Weak**: Possible minor contribution
            
            ---
            
            **Analysis Features** *(all scope-aware)*:
            
            | Analysis | What it reveals |
            |----------|-----------------|
            | 🔝 Top Propagators | Risks with highest downstream impact |
            | ⚠️ Convergence Points | Where multiple threats converge |
            | 🔥 Critical Paths | Strongest influence chains to TPOs |
            | 🚧 Bottlenecks | Single points of failure |
            | 📦 Clusters | Tightly interconnected risk groups |
            
            > **Tip:** Use the Influence Explorer to traverse the network
            > from any node. When a scope is active, only scoped nodes
            > appear in the selection dropdown.
            """)
        
        elif help_tab == "Mitigations":
            st.markdown("""
            ### 🛡️ Mitigation Model
            
            Mitigations represent controls, actions, or safeguards
            that reduce risk exposure. One mitigation can address
            multiple risks, and one risk can have multiple mitigations.
            
            ---
            
            **Mitigation Types:**
            
            | Type | Description | Visual |
            |------|-------------|--------|
            | Dedicated | Program-specific controls | Teal, solid border |
            | Inherited | From corporate or other programs | Blue, dotted border |
            | Baseline | Standards, regulations, best practices | Purple, thick border |
            
            ---
            
            **Status Levels:**
            - ✅ **Implemented** — Active protection
            - 🔄 **In Progress** — Being deployed
            - 📋 **Proposed** — Planned, not yet started
            - ⏸️ **Deferred** — On hold
            
            ---
            
            **Effectiveness Levels:**
            
            | Level | Reduction | When to use |
            |-------|-----------|-------------|
            | Critical | 90% | Eliminates root cause |
            | High | 70% | Significantly reduces probability or impact |
            | Medium | 50% | Moderate reduction |
            | Low | 30% | Minor reduction |
            
            ---
            
            **Mitigation Analysis** *(scope-aware)*:
            - **Coverage Overview**: Risks with/without mitigations
            - **Treatment Explorer**: Detailed per-risk mitigation status
            - **High-Priority Unmitigated**: Flags risks that are unmitigated
              AND are top propagators, convergence points, or bottlenecks
            
            **Strategic Advice:**
            - Mitigate upstream risks first (influence limitation principle)
            - Prioritize high-exposure, high-influence risks
            - Review coverage gaps regularly in the Analysis tab
            """)
        
        elif help_tab == "Layouts":
            st.markdown("""
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
            """)


def render_connection_sidebar():
    """Render the Neo4j connection sidebar."""
    st.sidebar.markdown("## 🔌 Neo4j Connection")
    
    with st.sidebar.expander("Connection Settings", expanded=not st.session_state.connected):
        uri = st.text_input("URI", value=NEO4J_DEFAULT_URI, key="neo4j_uri")
        user = st.text_input("User", value=NEO4J_DEFAULT_USER, key="neo4j_user")
        password = st.text_input("Password", type="password", key="neo4j_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", type="primary", use_container_width=True):
                manager = RiskGraphManager(uri, user, password)
                if manager.connect():
                    st.session_state.manager = manager
                    st.session_state.connected = True
                    st.success("Connected!")
                    st.rerun()
        
        with col2:
            if st.button("Disconnect", use_container_width=True, disabled=not st.session_state.connected):
                if st.session_state.manager:
                    st.session_state.manager.close()
                st.session_state.manager = None
                st.session_state.connected = False
                st.rerun()
    
    if st.session_state.connected:
        st.sidebar.success("✅ Connected to Neo4j")
    else:
        st.sidebar.warning("⚠️ Not connected")
        
    if st.session_state.connected:
        st.sidebar.markdown("---")
        render_graph_legend(expanded=False)
        st.sidebar.markdown("---")
        render_help_section()


def render_welcome_page():
    """Render the welcome page when not connected."""
    st.info("👈 Please connect to Neo4j via the sidebar to get started.")
    
    with st.expander("📖 About Risk Influence Map", expanded=True):
        st.markdown("""
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
        
        *Version 2.6.1 — See sidebar **❓ Help** for detailed feature documentation.*
        """)


def render_statistics_dashboard(stats: dict):
    """Render the statistics dashboard."""
    with st.expander("📊 Statistics Dashboard", expanded=True):
        # First row of metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Total Risks", stats.get("total_risks", 0))
        with col2:
            # Schema-driven level 1 display
            registry = get_registry()
            risk_levels = registry.get_risk_levels()
            level1_name = risk_levels[0]["id"] if risk_levels else "Strategic"
            level1_label = risk_levels[0]["label"] if risk_levels else "Strategic"
            level1_emoji = risk_levels[0].get("emoji", "◆")
            st.metric(f"{level1_emoji} {level1_label}", stats.get("level1_risks", 0))
        with col3:
            # Schema-driven level 2 display
            level2_name = risk_levels[1]["id"] if len(risk_levels) > 1 else "Operational"
            level2_label = risk_levels[1]["label"] if len(risk_levels) > 1 else "Operational"
            level2_emoji = risk_levels[1].get("emoji", "●")
            st.metric(f"{level2_emoji} {level2_label}", stats.get("level2_risks", 0))
        with col4:
            st.metric("🆕 New", stats.get("new_risks", 0))
        with col5:
            st.metric("📜 Legacy", stats.get("legacy_risks", 0))
        
        # Second row of metrics
        col6, col7, col8, col9, col10 = st.columns(5)
        
        with col6:
            st.metric("🟡 TPOs", stats.get("total_tpos", 0))
        with col7:
            st.metric("🛡️ Mitigations", stats.get("total_mitigations", 0))
        with col8:
            st.metric("🔗 Influences", stats.get("total_influences", 0))
        with col9:
            st.metric("📌 TPO Impacts", stats.get("total_tpo_impacts", 0))
        with col10:
            st.metric("💊 Mitigates", stats.get("total_mitigates", 0))


def render_exposure_dashboard(manager):
    """Render the exposure calculation dashboard."""
    with st.expander("⚡ Risk Exposure Analysis", expanded=True):
        # Check if we have cached results
        exposure_results = st.session_state.get("exposure_results")
        
        col_btn, col_info = st.columns([1, 3])
        
        with col_btn:
            if st.button("🔄 Calculate Exposure", type="primary", use_container_width=True,
                        help="Run exposure calculation for all risks (or scoped risks)"):
                with st.spinner("Calculating exposure scores..."):
                    try:
                        # Pass scope node IDs if scope is active
                        filter_mgr = st.session_state.get("filter_manager")
                        scope_ids = filter_mgr.get_scope_node_ids() if filter_mgr else None
                        include_neighbors = st.session_state.get("scope_include_neighbors", False)
                        results = manager.calculate_exposure(
                            scope_node_ids=scope_ids,
                            include_neighbors=include_neighbors,
                        )
                        st.session_state.exposure_results = results
                        st.success("✅ Calculation complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Calculation error: {e}")
        
        with col_info:
            if exposure_results:
                calc_time = exposure_results.get("calculated_at", "")
                if calc_time:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(calc_time)
                        st.caption(f"Last calculated: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        pass
            else:
                st.caption("Click 'Calculate Exposure' to compute risk scores")
        
        if exposure_results:
            st.markdown("---")
            
            # Main metrics row
            col1, col2, col3 = st.columns(3)
            
            with col1:
                residual_pct = exposure_results.get("residual_risk_percentage", 0)
                st.metric(
                    "📉 Residual Risk",
                    f"{residual_pct:.1f}%",
                    help="Percentage of base exposure remaining after mitigations and considering influences"
                )
            
            with col2:
                weighted_score = exposure_results.get("weighted_risk_score", 0)
                # Determine health status color
                if weighted_score <= 10:
                    health_label, health_color = "Excellent", "🟢"
                elif weighted_score <= 30:
                    health_label, health_color = "Good", "🟢"
                elif weighted_score <= 50:
                    health_label, health_color = "Moderate", "🟡"
                elif weighted_score <= 70:
                    health_label, health_color = "Concerning", "🟠"
                else:
                    health_label, health_color = "Critical", "🔴"
                
                st.metric(
                    f"{health_color} Risk Score",
                    f"{weighted_score:.1f}/100",
                    help=f"Impact-weighted risk score. Status: {health_label}"
                )
            
            with col3:
                max_exp = exposure_results.get("max_single_exposure", 0)
                max_name = exposure_results.get("max_exposure_risk_name", "N/A")
                st.metric(
                    "⚠️ Max Exposure",
                    f"{max_exp:.1f}",
                    help=f"Highest single risk exposure: {max_name}"
                )
            
            # Secondary metrics row
            col4, col5, col6, col7 = st.columns(4)
            
            with col4:
                total_base = exposure_results.get("total_base_exposure", 0)
                st.metric("📊 Total Base", f"{total_base:.0f}")
            
            with col5:
                total_final = exposure_results.get("total_final_exposure", 0)
                st.metric("📉 Total Final", f"{total_final:.0f}")
            
            with col6:
                mitigated = exposure_results.get("mitigated_risks_count", 0)
                unmitigated = exposure_results.get("unmitigated_risks_count", 0)
                st.metric("🛡️ Mitigated", f"{mitigated}/{mitigated + unmitigated}")
            
            with col7:
                risks_with_data = exposure_results.get("risks_with_data", 0)
                total_risks = exposure_results.get("total_risks", 0)
                st.metric("📋 With Data", f"{risks_with_data}/{total_risks}")
            
            # Details expander
            with st.expander("📋 Detailed Risk Exposures", expanded=False):
                risk_results = exposure_results.get("risk_results", [])
                if risk_results:
                    # Sort by final exposure descending
                    sorted_results = sorted(risk_results, key=lambda x: x.get("final_exposure", 0), reverse=True)
                    
                    # Create a simple table
                    st.markdown("**Top Risks by Final Exposure:**")
                    
                    for i, r in enumerate(sorted_results[:10]):
                        # Schema-driven level icon
                        risk_level = r.get("level", "")
                        level_cfg = RISK_LEVEL_CONFIG.get(risk_level, {})
                        level_icon = level_cfg.get("emoji", "●")
                        mit_info = f"🛡️×{r.get('mitigation_count', 0)}" if r.get('mitigation_count', 0) > 0 else "⚠️ No mit"
                        inf_info = f"↑{r.get('upstream_risk_count', 0)}" if r.get('upstream_risk_count', 0) > 0 else ""
                        
                        base = r.get("base_exposure", 0)
                        final = r.get("final_exposure", 0)
                        reduction = ((base - final) / base * 100) if base > 0 else 0
                        
                        st.markdown(
                            f"{i+1}. {level_icon} **{r.get('risk_name', 'Unknown')}**: "
                            f"Base={base:.0f} → Final={final:.1f} "
                            f"({reduction:.0f}% ↓) {mit_info} {inf_info}"
                        )
                else:
                    st.info("No risk exposure data available.")


def render_visualization_filters(manager: RiskGraphManager):
    """Render the visualization filters sidebar."""
    registry = get_registry()
    filter_mgr = st.session_state.filter_manager
    
    st.markdown("### 🎛️ Filters")
    
    # Refresh button
    if st.button("🔄 Refresh Visualization", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    
    # Filter Presets
    with st.expander("⚡ Quick Presets", expanded=False):
        presets = filter_mgr.get_presets()
        preset_cols = st.columns(2)
        for i, preset in enumerate(presets):
            with preset_cols[i % 2]:
                if st.button(
                    preset.name,
                    key=f"preset_{preset.key}",
                    use_container_width=True,
                    help=preset.description
                ):
                    filter_mgr.apply_preset(preset.key)
                    st.rerun()
    
    # ==========================================================
    # CORE NODES & EDGES
    # ==========================================================
    st.markdown("#### 🔷 Core Nodes & Edges")
    
    # Core entity filters: risk and mitigation
    for entity_id in ["risk", "mitigation"]:
        entity_type = registry.entity_types.get(entity_id)
        if not entity_type:
            continue
        with st.expander(f"{entity_type.emoji} {entity_type.label} Filters", expanded=(entity_id == "risk")):
            # Enable/Disable toggle
            is_enabled = st.checkbox(
                f"Show {entity_type.label}s",
                value=filter_mgr.filters["entities"].get(entity_id, {}).get("enabled", True),
                key=f"enabled_{entity_id}"
            )
            filter_mgr.set_entity_enabled(entity_id, is_enabled)
            
            if is_enabled:
                # Add filters for categorical groups (levels, categories, statuses, origins, etc.)
                for group_name, group_items in entity_type.categorical_groups.items():
                    if group_items:
                        choices = [item.get("label", item.get("id", "")) for item in group_items]
                        if choices:
                            st.markdown(f"**{group_name.replace('_', ' ').title()}**")
                            current_selection = filter_mgr.filters["entities"][entity_id]["attributes"].get(group_name, choices)
                            selected = st.multiselect(
                                group_name.replace('_', ' ').title(),
                                choices,
                                default=current_selection if isinstance(current_selection, list) else choices,
                                key=f"filter_{entity_id}_{group_name}",
                                label_visibility="collapsed"
                            )
                            filter_mgr.set_entity_attribute_filter(entity_id, group_name, selected)
                
                # Special case: Exposure threshold for risks
                if entity_id == "risk":
                    st.markdown("**Exposure Threshold**")
                    exposure_threshold = st.slider(
                        "Min Exposure",
                        min_value=0.0,
                        max_value=16.0,
                        value=st.session_state.get("exposure_threshold", 0.0),
                        step=0.5,
                        key="exposure_threshold_slider",
                        help="Show only risks with exposure >= this value"
                    )
                    st.session_state.exposure_threshold = exposure_threshold
    
    # Core relationship filters: influences and mitigates
    for rel_id in ["influences", "mitigates"]:
        rel_type = registry.relationship_types.get(rel_id)
        if not rel_type:
            continue
        with st.expander(f"🔗 {rel_type.label} Filters", expanded=False):
            is_enabled = st.checkbox(
                f"Show {rel_type.label}",
                value=filter_mgr.filters["relationships"].get(rel_id, {}).get("enabled", True),
                key=f"enabled_rel_{rel_id}"
            )
            filter_mgr.set_relationship_enabled(rel_id, is_enabled)
            
            if is_enabled:
                for group_name, group_items in rel_type.categorical_groups.items():
                    if group_items:
                        choices = [item.get("label", item.get("id", "")) for item in group_items]
                        if choices:
                            st.markdown(f"**{group_name.replace('_', ' ').title()}**")
                            current_selection = filter_mgr.filters["relationships"][rel_id]["attributes"].get(group_name, choices)
                            selected = st.multiselect(
                                group_name.replace('_', ' ').title(),
                                choices,
                                default=current_selection if isinstance(current_selection, list) else choices,
                                key=f"filter_rel_{rel_id}_{group_name}",
                                label_visibility="collapsed"
                            )
                            filter_mgr.set_relationship_attribute_filter(rel_id, group_name, selected)
    
    st.markdown("---")
    
    # ==========================================================
    # TPO & RELATED
    # ==========================================================
    st.markdown("#### 🏆 TPO & Related")
    
    # TPO entity filter
    for entity_id in ["tpo"]:
        entity_type = registry.entity_types.get(entity_id)
        if not entity_type:
            continue
        with st.expander(f"{entity_type.emoji} {entity_type.label} Filters", expanded=False):
            is_enabled = st.checkbox(
                f"Show {entity_type.label}s",
                value=filter_mgr.filters["entities"].get(entity_id, {}).get("enabled", True),
                key=f"enabled_{entity_id}"
            )
            filter_mgr.set_entity_enabled(entity_id, is_enabled)
            
            if is_enabled:
                for group_name, group_items in entity_type.categorical_groups.items():
                    if group_items:
                        choices = [item.get("label", item.get("id", "")) for item in group_items]
                        if choices:
                            st.markdown(f"**{group_name.replace('_', ' ').title()}**")
                            current_selection = filter_mgr.filters["entities"][entity_id]["attributes"].get(group_name, choices)
                            selected = st.multiselect(
                                group_name.replace('_', ' ').title(),
                                choices,
                                default=current_selection if isinstance(current_selection, list) else choices,
                                key=f"filter_{entity_id}_{group_name}",
                                label_visibility="collapsed"
                            )
                            filter_mgr.set_entity_attribute_filter(entity_id, group_name, selected)
    
    # TPO-related relationship filters: impacts_tpo
    for rel_id in ["impacts_tpo"]:
        rel_type = registry.relationship_types.get(rel_id)
        if not rel_type:
            continue
        with st.expander(f"🔗 {rel_type.label} Filters", expanded=False):
            is_enabled = st.checkbox(
                f"Show {rel_type.label}",
                value=filter_mgr.filters["relationships"].get(rel_id, {}).get("enabled", True),
                key=f"enabled_rel_{rel_id}"
            )
            filter_mgr.set_relationship_enabled(rel_id, is_enabled)
            
            if is_enabled:
                for group_name, group_items in rel_type.categorical_groups.items():
                    if group_items:
                        choices = [item.get("label", item.get("id", "")) for item in group_items]
                        if choices:
                            st.markdown(f"**{group_name.replace('_', ' ').title()}**")
                            current_selection = filter_mgr.filters["relationships"][rel_id]["attributes"].get(group_name, choices)
                            selected = st.multiselect(
                                group_name.replace('_', ' ').title(),
                                choices,
                                default=current_selection if isinstance(current_selection, list) else choices,
                                key=f"filter_rel_{rel_id}_{group_name}",
                                label_visibility="collapsed"
                            )
                            filter_mgr.set_relationship_attribute_filter(rel_id, group_name, selected)

    # Color mode
    with st.expander("🎨 Display Options", expanded=False):
        color_by = st.radio(
            "Color by",
            ["level", "exposure"],
            format_func=lambda x: "Risk Level" if x == "level" else "Exposure",
            horizontal=True,
            key="color_by_radio"
        )
        st.session_state.color_by = color_by
    
    return filter_mgr


def render_influence_explorer(manager: RiskGraphManager):
    """Render the influence explorer controls."""
    with st.expander("🔍 Influence Explorer", expanded=st.session_state.influence_explorer_enabled):
        explorer_enabled = st.checkbox(
            "Enable Influence Explorer",
            value=st.session_state.influence_explorer_enabled,
            key="influence_explorer_toggle"
        )
        st.session_state.influence_explorer_enabled = explorer_enabled
        
        if explorer_enabled:
            # Node selection — scope-limited when active
            all_nodes = manager.get_all_nodes_for_selection()
            
            # Filter to scope nodes if a scope is active
            _filter_mgr = st.session_state.get("filter_manager")
            _scope_ids = _filter_mgr.get_scope_node_ids() if _filter_mgr else None
            if _scope_ids is not None:
                _scope_set = set(_scope_ids)
                all_nodes = [n for n in all_nodes if n["id"] in _scope_set]
            
            if all_nodes:
                node_options = {n["id"]: n["label"] for n in all_nodes}
                node_ids = [""] + list(node_options.keys())
                node_labels = ["-- Select a node --"] + [node_options[nid] for nid in node_ids[1:]]
                
                # Find current selection index
                current_idx = 0
                if st.session_state.selected_node_id and st.session_state.selected_node_id in node_ids:
                    current_idx = node_ids.index(st.session_state.selected_node_id)
                
                selected_idx = st.selectbox(
                    "Select node to explore",
                    range(len(node_labels)),
                    index=current_idx,
                    format_func=lambda i: node_labels[i],
                    key="node_selector"
                )
                
                if selected_idx > 0:
                    st.session_state.selected_node_id = node_ids[selected_idx]
                else:
                    st.session_state.selected_node_id = None
                
                if st.session_state.selected_node_id:
                    # Direction control
                    direction = st.radio(
                        "Direction",
                        ["both", "upstream", "downstream"],
                        format_func=lambda x: {
                            "upstream": "⬆️ Upstream",
                            "downstream": "⬇️ Downstream",
                            "both": "↕️ Both"
                        }[x],
                        horizontal=True,
                        key="influence_direction"
                    )
                    
                    # Depth control
                    col_depth1, col_depth2 = st.columns([2, 1])
                    with col_depth1:
                        max_depth = st.slider(
                            "Max depth",
                            min_value=1,
                            max_value=10,
                            value=5,
                            key="influence_depth"
                        )
                    with col_depth2:
                        unlimited = st.checkbox("Unlimited", value=False, key="unlimited_depth")
                    
                    # Include TPOs
                    include_tpos = st.checkbox(
                        "🟡 Include TPOs",
                        value=True,
                        key="influence_include_tpos"
                    )
                    
                    # Clear selection button
                    if st.button("🔄 Clear selection", use_container_width=True):
                        st.session_state.selected_node_id = None
                        st.rerun()
            else:
                st.info("No nodes available. Create some risks first!")


def render_graph_options():
    """Render graph display options."""
    with st.expander("⚙️ Graph Options", expanded=False):
        physics_enabled = st.checkbox(
            "🔄 Physics enabled",
            value=st.session_state.physics_enabled,
            help="Uncheck to freeze nodes after positioning"
        )
        st.session_state.physics_enabled = physics_enabled
        
        st.markdown("---")
        
        # Edge visibility
        st.markdown("**📊 Edge Visibility**")
        edge_mode = st.radio(
            "Display mode",
            ["all", "progressive"],
            format_func=lambda x: "Show all edges" if x == "all" else "Progressive disclosure",
            horizontal=True,
            key="edge_visibility_mode"
        )
        
        if edge_mode == "progressive":
            st.slider(
                "Edge visibility %",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                key="edge_visibility_slider"
            )
        
        st.markdown("---")
        
        # Capture mode
        capture_mode = st.checkbox(
            "📍 Enable position capture",
            value=st.session_state.capture_mode,
            help="Enable to capture node positions"
        )
        st.session_state.capture_mode = capture_mode


def render_layout_management(manager: RiskGraphManager):
    """Render layout management controls."""
    layout_mgr = st.session_state.layout_manager
    
    with st.expander("💾 Layout Management", expanded=False):
        # Save current layout
        st.markdown("**💾 Save Current Layout**")
        col_name_input, col_save_btn = st.columns([2, 1])
        with col_name_input:
            layout_name_input = st.text_input(
                "Layout name",
                placeholder="my_layout",
                key="new_layout_name",
                label_visibility="collapsed"
            )
        with col_save_btn:
            if st.button("💾 Save", key="save_layout_btn", use_container_width=True):
                if layout_name_input:
                    st.info("📍 Use 'Capture Positions' in Graph Options, then paste JSON here")
        
        # Manual position paste area
        position_data = st.text_area(
            "Position Data (JSON)",
            height=100,
            key="position_data_input",
            help="Paste position data captured from the graph",
            placeholder='{"risk_id_1": {"x": 100, "y": 200}, ...}'
        )
        
        if st.button("💾 Save Layout from JSON", key="save_json_layout", use_container_width=True):
            if layout_name_input and position_data:
                try:
                    import json
                    positions = json.loads(position_data)
                    layout_mgr.save_layout(layout_name_input, positions)
                    st.session_state.selected_layout_name = layout_name_input
                    st.success(f"✅ Layout '{layout_name_input}' saved!")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
            else:
                st.warning("Please enter a layout name and paste position data")
        
        st.markdown("---")
        
        # Predefined layouts
        st.markdown("**🎨 Predefined Layouts**")
        col_preset_1, col_preset_2 = st.columns(2)
        
        with col_preset_1:
            if st.button("📊 Layered", key="preset_layered", use_container_width=True):
                nodes, _ = manager.get_graph_data({"show_tpos": True})
                positions = generate_layered_layout(nodes)
                auto_name = f"layered_{datetime.now().strftime('%Y%m%d_%H%M')}"
                layout_mgr.save_layout(auto_name, positions)
                st.session_state.selected_layout_name = auto_name
                st.rerun()
        
        with col_preset_2:
            if st.button("🗂️ Categories", key="preset_categories", use_container_width=True):
                nodes, _ = manager.get_graph_data({"show_tpos": True})
                positions = generate_category_layout(nodes)
                auto_name = f"categories_{datetime.now().strftime('%Y%m%d_%H%M')}"
                layout_mgr.save_layout(auto_name, positions)
                st.session_state.selected_layout_name = auto_name
                st.rerun()
        
        col_preset_3, col_preset_4 = st.columns(2)
        
        with col_preset_3:
            if st.button("🏆 TPO Clusters", key="preset_tpo_clusters", use_container_width=True):
                nodes, _ = manager.get_graph_data({"show_tpos": True})
                positions = generate_tpo_cluster_layout(nodes)
                auto_name = f"tpo_clusters_{datetime.now().strftime('%Y%m%d_%H%M')}"
                layout_mgr.save_layout(auto_name, positions)
                st.session_state.selected_layout_name = auto_name
                st.rerun()
        
        with col_preset_4:
            if st.button("🌳 Hierarchical", key="preset_sugiyama", use_container_width=True,
                        help="Sugiyama algorithm - minimizes edge crossings"):
                nodes, edges = manager.get_graph_data({"show_tpos": True})
                positions = generate_auto_spread_layout(nodes, edges)
                auto_name = f"hierarchical_{datetime.now().strftime('%Y%m%d_%H%M')}"
                layout_mgr.save_layout(auto_name, positions)
                st.session_state.selected_layout_name = auto_name
                st.rerun()
        
        col_preset_5, _ = st.columns(2)
        
        with col_preset_5:
            if st.button("🔄 Reset Layout", key="reset_layout", use_container_width=True):
                if "selected_layout_name" in st.session_state:
                    del st.session_state.selected_layout_name
                st.rerun()
        
        # Saved layouts
        st.markdown("---")
        st.markdown("**📁 Saved Layouts**")
        
        saved_layouts = layout_mgr.list_layouts()
        if saved_layouts:
            for name in saved_layouts:
                col_name, col_load, col_del = st.columns([2, 1, 1])
                with col_name:
                    st.text(name)
                with col_load:
                    if st.button("📂", key=f"load_{name}"):
                        st.session_state.selected_layout_name = name
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{name}"):
                        layout_mgr.delete_layout(name)
                        if st.session_state.get("selected_layout_name") == name:
                            del st.session_state.selected_layout_name
                        st.rerun()
        else:
            st.info("No saved layouts.")


def render_visualization_tab(manager: RiskGraphManager, config: dict = None):
    """Render the visualization tab content."""
    col_filters, col_display = st.columns([1, 3])
    
    with col_filters:
        filter_mgr = render_visualization_filters(manager)
        render_influence_explorer(manager)
        render_graph_options()
        render_layout_management(manager)
    
    with col_display:
        # Define node selection callback for influence explorer
        def on_node_select(node_id: str, direction: str):
            st.session_state.influence_explorer_enabled = True
            st.session_state.selected_node_id = node_id
            st.session_state.influence_direction = direction
        
        # Prepare graph data
        if (st.session_state.influence_explorer_enabled and 
            st.session_state.selected_node_id):
            # Influence explorer mode
            direction = st.session_state.get("influence_direction", "both")
            max_depth = None if st.session_state.get("unlimited_depth") else st.session_state.get("influence_depth", 5)
            include_tpos = st.session_state.get("influence_include_tpos", True)
            
            nodes, edges, selected_info = manager.get_influence_network(
                node_id=st.session_state.selected_node_id,
                direction=direction,
                max_depth=max_depth,
                include_tpos=include_tpos
            )
            
            if selected_info:
                node_type = selected_info.get("node_type", "Risk")
                if node_type == "TPO":
                    st.success(f"🔍 **Exploring:** {selected_info.get('reference')}: {selected_info.get('name')} (TPO)")
                else:
                    st.success(f"🔍 **Exploring:** {selected_info.get('name')} ({selected_info.get('level')} Risk)")
            
            positions = None
            highlighted_node_id = st.session_state.selected_node_id
        else:
            # Normal mode
            filters = filter_mgr.get_filters_for_query()
            nodes, edges = manager.get_graph_data(filters)
            highlighted_node_id = None
            
            # Load positions if layout selected
            positions = None
            if "selected_layout_name" in st.session_state:
                layout_name = st.session_state.selected_layout_name
                positions = st.session_state.layout_manager.load_layout(layout_name)
                if positions:
                    st.info(f"📍 Active layout: **{layout_name}**")
        
        # Handle edge filtering
        max_edges = None
        edge_scores = None
        if st.session_state.get("edge_visibility_mode") == "progressive":
            edge_pct = st.session_state.get("edge_visibility_slider", 100)
            try:
                all_scored = manager.get_all_edges_scored()
                max_edges = max(1, int(len(all_scored) * edge_pct / 100))
                edge_scores = {(e["source"], e["target"]): e["score"] for e in all_scored}
            except:
                pass
        
        # Add compact legend above graph
        render_compact_legend()
        
        # Render graph
        render_graph_streamlit(
            nodes=nodes,
            edges=edges,
            color_by=st.session_state.color_by,
            physics_enabled=st.session_state.physics_enabled,
            positions=positions,
            capture_positions=st.session_state.capture_mode,
            highlighted_node_id=highlighted_node_id,
            max_edges=max_edges,
            edge_scores=edge_scores
        )


def _render_scope_selector():
    """Render the scope selector in the sidebar."""
    # Load scopes from schema config
    try:
        loader = SchemaLoader()
        schema_name = st.session_state.get("active_schema_name", "default")
        schema = loader.load_schema(schema_name)
        available_scopes = schema.scopes
    except Exception:
        available_scopes = []
    
    if not available_scopes:
        return  # No scopes defined, skip rendering
    
    with st.sidebar.expander("📐 Analysis Scopes", expanded=False):
        filter_mgr = st.session_state.filter_manager
        
        # Build options: list of scope names
        scope_map = {s.name: s for s in available_scopes}
        scope_names = list(scope_map.keys())
        
        # Current selection
        current_names = [s.name for s in filter_mgr.active_scopes]
        
        selected_names = st.multiselect(
            "Select scope(s)",
            options=scope_names,
            default=[n for n in current_names if n in scope_names],
            key="scope_selector",
            help="Select one or more scopes. Nodes are shown as the union of all selected scopes.",
        )
        
        # Update FilterManager
        selected_scopes = [scope_map[name] for name in selected_names if name in scope_map]
        filter_mgr.set_active_scopes(selected_scopes)
        
        if selected_scopes:
            total_nodes = len(set().union(*(s.node_ids for s in selected_scopes)))
            scope_colors = " ".join(
                f'<span style="color:{s.color}">●</span>' for s in selected_scopes
            )
            st.markdown(
                f"{scope_colors} **{total_nodes}** nodes in scope",
                unsafe_allow_html=True,
            )
            
            # Neighbor expansion toggle
            st.checkbox(
                "Show connected neighbors",
                value=st.session_state.get("scope_include_neighbors", False),
                key="scope_include_neighbors",
                help="Also display risks directly connected to the scoped nodes.",
            )
        
        if st.button("🌐 Full Graph", use_container_width=True, key="clear_scopes"):
            filter_mgr.clear_scopes()
            st.session_state.scope_include_neighbors = False
            st.rerun()


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=LAYOUT_MODE,
        initial_sidebar_state="expanded"
    )
    
    # Inject custom styles
    inject_styles()
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown(f'<p class="main-header">{APP_ICON} {APP_TITLE}</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Dynamic visualization system for business and operational risk management</p>', unsafe_allow_html=True)
    
    # Connection sidebar
    render_connection_sidebar()
    
    # Check connection
    if not st.session_state.connected:
        render_welcome_page()
        return
    
    manager = st.session_state.manager
    
    # ── Scope selector in sidebar ────────────────────────────────────────
    _render_scope_selector()
    
    # Scope-aware statistics
    filter_mgr = st.session_state.filter_manager
    scope_ids = filter_mgr.get_scope_node_ids()
    
    if scope_ids is not None:
        scope_names = [s.name for s in filter_mgr.active_scopes]
        st.info(f"📐 Active scope{'s' if len(scope_names) > 1 else ''}: **{', '.join(scope_names)}** — showing {len(scope_ids)} scoped risk nodes")
        
        # Build scoped filters and compute stats from filtered graph data
        scoped_filters = filter_mgr.get_filters_for_query()
        scoped_filters["scope_include_neighbors"] = st.session_state.get("scope_include_neighbors", False)
        scoped_nodes, scoped_edges = manager.get_graph_data(scoped_filters)
        scoped_stats = _compute_stats_from_graph(scoped_nodes, scoped_edges)
        render_statistics_dashboard(scoped_stats)
    else:
        stats = manager.get_statistics()
        render_statistics_dashboard(stats)
    
    # Exposure analysis dashboard (scope-aware)
    render_exposure_dashboard(manager)
    
    st.markdown("---")
    
    # Custom renderers for complex tabs
    def render_analysis_tab(manager_inst, config):
        """Render the analysis tab content."""
        # Pass scope filter to influence analysis, with optional neighbor expansion
        _scope_ids = filter_mgr.get_scope_node_ids()
        _include_nbrs = st.session_state.get("scope_include_neighbors", False)
        # If neighbors enabled, expand scope IDs for analysis
        if _scope_ids is not None and _include_nbrs:
            _expanded_scope = set(_scope_ids)
            _inf_list = manager_inst.get_all_influences()
            for _inf in _inf_list:
                _s, _t = _inf.get("source_id"), _inf.get("target_id")
                if _s in _expanded_scope:
                    _expanded_scope.add(_t)
                if _t in _expanded_scope:
                    _expanded_scope.add(_s)
            _scope_ids = list(_expanded_scope)
        render_influence_analysis_panel(
            get_analysis_fn=lambda: manager_inst.get_influence_analysis(scope_node_ids=_scope_ids),
            on_node_select=lambda node_id, direction: None
        )
        render_mitigation_analysis_panel(
            get_analysis_fn=lambda: manager_inst.get_mitigation_analysis(scope_node_ids=_scope_ids),
            get_coverage_gaps_fn=manager_inst.get_coverage_gap_analysis,
            get_all_risks_fn=_scoped_getter(manager_inst.get_all_risks, _scope_ids if _scope_ids is None else _expanded_crud_ids),
            get_all_mitigations_fn=_scoped_getter(manager_inst.get_all_mitigations, _scope_ids if _scope_ids is None else _expanded_crud_ids),
            get_risk_details_fn=manager_inst.get_risk_mitigation_details,
            get_mitigation_details_fn=manager_inst.get_mitigation_impact_details,
            get_mitigation_by_id_fn=manager_inst.get_mitigation_by_id,
            get_risks_for_mitigation_fn=manager_inst.get_risks_for_mitigation,
        )
    
    # ── Scope-aware CRUD helpers ──────────────────────────────────────────
    def _scoped_getter(getter_fn, scope_ids, id_field="id"):
        """Wrap a getter to filter results by scope."""
        def wrapped(*args, **kwargs):
            results = getter_fn(*args, **kwargs)
            if scope_ids is None:
                return results
            _scope_set = set(scope_ids)
            return [r for r in results if r.get(id_field) in _scope_set]
        return wrapped

    def _scoped_edge_getter(getter_fn, scope_ids, src_field, tgt_field):
        """Wrap an edge getter to filter by scope."""
        def wrapped(*args, **kwargs):
            results = getter_fn(*args, **kwargs)
            if scope_ids is None:
                return results
            _scope_set = set(scope_ids)
            return [r for r in results if r.get(src_field) in _scope_set or r.get(tgt_field) in _scope_set]
        return wrapped

    # Build the expanded scope set (risks + connected mits/tpos) for CRUD
    _crud_scope_ids = filter_mgr.get_scope_node_ids()
    _expanded_crud_ids = None
    if _crud_scope_ids is not None:
        _expanded = set(_crud_scope_ids)
        # Optionally expand 1-hop risk neighbors
        if st.session_state.get("scope_include_neighbors", False):
            _all_influences = manager.get_all_influences()
            for inf in _all_influences:
                src, tgt = inf.get("source_id"), inf.get("target_id")
                if src in _expanded:
                    _expanded.add(tgt)
                if tgt in _expanded:
                    _expanded.add(src)
        # Add connected mitigations
        _all_mitigates = manager.get_all_mitigates_relationships()
        _connected_mit_ids = {mr["mitigation_id"] for mr in _all_mitigates if mr.get("risk_id") in _expanded}
        # Add connected TPOs
        _all_tpo_impacts = manager.get_all_tpo_impacts()
        _connected_tpo_ids = {i["tpo_id"] for i in _all_tpo_impacts if i.get("risk_id") in _expanded}
        _expanded_crud_ids = list(_expanded | _connected_mit_ids | _connected_tpo_ids)

    tab_renderers = {
        "visualization": render_visualization_tab,
        "risks": lambda m, c: render_risks_tab(
            get_all_risks_fn=_scoped_getter(m.get_all_risks, _expanded_crud_ids),
            create_risk_fn=m.create_risk,
            delete_risk_fn=m.delete_risk,
        ),
        "tpos": lambda m, c: render_tpos_tab(
            get_all_tpos_fn=_scoped_getter(m.get_all_tpos, _expanded_crud_ids),
            create_tpo_fn=m.create_tpo,
            delete_tpo_fn=m.delete_tpo,
        ),
        "mitigations": lambda m, c: render_mitigations_tab(
            get_all_mitigations_fn=_scoped_getter(m.get_all_mitigations, _expanded_crud_ids),
            create_mitigation_fn=m.create_mitigation,
            delete_mitigation_fn=m.delete_mitigation,
            get_risks_for_mitigation_fn=m.get_risks_for_mitigation,
        ),
        "influences": lambda m, c: render_influences_tab(
            get_all_risks_fn=_scoped_getter(m.get_all_risks, _expanded_crud_ids),
            get_all_influences_fn=_scoped_edge_getter(m.get_all_influences, _expanded_crud_ids, "source_id", "target_id"),
            create_influence_fn=m.create_influence,
            delete_influence_fn=m.delete_influence,
        ),
        "analysis": render_analysis_tab,
        "import_export": lambda m, c: render_import_export_tab(m.export_to_excel, m.import_from_excel),
    }
    
    # Render main tabs dynamically from schema
    render_dynamic_tabs(manager, tab_renderers)


if __name__ == "__main__":
    main()
