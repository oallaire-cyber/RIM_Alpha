"""
Risk Influence Map (RIM) Application.

Main entry point that wires all modular components together.
"""

import streamlit as st
from datetime import datetime

# Configuration
from config import (
    APP_TITLE,
    APP_ICON,
    LAYOUT_MODE,
    NEO4J_DEFAULT_URI,
    NEO4J_DEFAULT_USER,
    RISK_LEVELS,
    RISK_CATEGORIES,
    TPO_CLUSTERS,
    RISK_LEVEL_CONFIG,
)

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

# Tab Pages
from ui.tabs import (
    render_risks_tab,
    render_tpos_tab,
    render_mitigations_tab,
    render_influences_tab,
    render_tpo_impacts_tab,
    render_risk_mitigations_tab,
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
            ["Overview", "Exposure Calculation", "Influence Model", "Mitigations", "Layouts"],
            label_visibility="collapsed",
            horizontal=True
        )
        
        if help_tab == "Overview":
            st.markdown("""
            ### 🎯 RIM Overview
            
            The **Risk Influence Map** visualizes relationships between:
            
            - **Business Risks** (◆): Consequence-oriented, managed by leadership
            - **Operational Risks** (●): Cause-oriented, managed by teams  
            - **TPOs** (⬡): Top Program Objectives
            - **Mitigations** (🛡️): Risk treatments
            
            **Influence Types:**
            - **Level 1** (red): Operational → Business
            - **Level 2** (purple): Business → Business
            - **Level 3** (blue): Operational → Operational
            """)
        
        elif help_tab == "Exposure Calculation":
            st.markdown("""
            ### ⚡ Exposure Calculation
            
            The exposure model quantifies risk considering three factors:
            
            ---
            
            **1️⃣ Base Exposure**
            ```
            Base = Likelihood × Impact
            ```
            Scale: 1-10 each, so Base ranges 1-100
            
            ---
            
            **2️⃣ Mitigation Factor**
            
            Multiple mitigations combine with **diminishing returns**:
            ```
            Factor = ∏(1 - Effectiveness)
            ```
            
            | Effectiveness | Reduction |
            |---------------|-----------|
            | Critical | 90% |
            | High | 70% |
            | Medium | 50% |
            | Low | 30% |
            
            *Example: High + Medium = 0.3 × 0.5 = 0.15 (85% reduction)*
            
            ---
            
            **3️⃣ Influence Limitation**
            
            Upstream risks **limit** how effective downstream mitigations can be:
            ```
            Limitation = Avg(Upstream_Residual × Strength)
            ```
            
            | Strength | Weight |
            |----------|--------|
            | Critical | 1.0 |
            | Strong | 0.75 |
            | Moderate | 0.50 |
            | Weak | 0.25 |
            
            The effective mitigation becomes:
            ```
            Effective = Mit_Factor + (1 - Mit_Factor) × Limitation
            ```
            
            *This models: "fixing symptoms without addressing causes has limited effect"*
            
            ---
            
            **4️⃣ Final Exposure**
            ```
            Final = Base × Effective_Mitigation_Factor
            ```
            
            ---
            
            **📊 Global Metrics**
            
            | Metric | Formula | Purpose |
            |--------|---------|---------|
            | Residual % | Σ(Final)/Σ(Base)×100 | Overall effectiveness |
            | Risk Score | Impact²-weighted (0-100) | Executive metric |
            | Max Exposure | max(Final) | Hotspot alert |
            """)
        
        elif help_tab == "Influence Model":
            st.markdown("""
            ### 🔗 Influence Model
            
            Influences represent how risks affect each other:
            
            **Direction Matters:**
            - Source risk **causes or contributes to** target risk
            - Operational risks typically influence Business risks
            
            **Influence Types (Auto-determined):**
            
            | Type | From → To | Meaning |
            |------|-----------|---------|
            | Level 1 | Op → Strat | Causes consequence |
            | Level 2 | Strat → Strat | Amplifies impact |
            | Level 3 | Op → Op | Contributes to |
            
            **Strength Levels:**
            - **Critical**: Direct, inevitable causation
            - **Strong**: High probability of propagation
            - **Moderate**: Likely contributes
            - **Weak**: Possible minor contribution
            
            **Analysis Features:**
            - **Top Propagators**: Risks with highest downstream impact
            - **Convergence Points**: Where multiple influences meet
            - **Critical Paths**: Strongest chains to TPOs
            - **Bottlenecks**: Single points of failure
            """)
        
        elif help_tab == "Mitigations":
            st.markdown("""
            ### 🛡️ Mitigation Model
            
            **Mitigation Types:**
            
            | Type | Description | Visual |
            |------|-------------|--------|
            | Dedicated | Program-specific | Teal, solid |
            | Inherited | From other sources | Blue, dotted |
            | Baseline | Standards/regulations | Purple, thick |
            
            **Status Levels:**
            - **Implemented**: Active protection ✅
            - **In Progress**: Being deployed 🔄
            - **Proposed**: Planned 📋
            - **Deferred**: On hold ⏸️
            
            **Effectiveness Levels:**
            
            | Level | Reduction | When to use |
            |-------|-----------|-------------|
            | Critical | 90% | Eliminates root cause |
            | High | 70% | Significantly reduces |
            | Medium | 50% | Moderate reduction |
            | Low | 30% | Minor reduction |
            
            **Key Principle:**
            One mitigation can address multiple risks, and one risk can have multiple mitigations.
            
            **Strategic Advice:**
            - Mitigate upstream risks first (influence limitation)
            - Prioritize high-exposure, high-influence risks
            - Check coverage gaps regularly
            """)
        
        elif help_tab == "Layouts":
            st.markdown("""
            ### 📐 Graph Layouts
            
            **Predefined Layouts:**
            
            | Layout | Description |
            |--------|-------------|
            | 🌳 Hierarchical | Sugiyama algorithm, minimizes edge crossings |
            | 📊 Layered | TPO → Strategic → Operational rows |
            | 🗂️ Categories | 2×2 grid by category |
            | 🏆 TPO Clusters | Grouped by TPO associations |
            
            **Hierarchical (Sugiyama) Algorithm:**
            
            1. **Layer Assignment**: Nodes assigned to layers based on RIM hierarchy
            2. **Crossing Minimization**: Barycenter heuristic orders nodes to reduce edge crossings
            3. **Coordinate Assignment**: Positions nodes with connected nodes aligned
            
            **Manual Layout:**
            1. Disable physics (⚙️ Graph Options)
            2. Drag nodes to desired positions
            3. Enable "📍 Position capture"
            4. Click capture button on graph
            5. Save layout in 💾 Layout Management
            
            **Tips:**
            - Use Hierarchical for presentations
            - Disable physics for stable manual layouts
            - Saved layouts persist across sessions
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
        
        The **Risk Influence Map (RIM)** is an innovative methodology for visualizing and managing 
        complex relationships between risks in large-scale programs. It transforms static risk registers 
        into dynamic risk intelligence.
        
        ---
        
        ### ✨ Key Features
        
        **🎯 Two-Level Risk Architecture**
        - **Business Risks** (◆ Diamond): Consequence-oriented, managed by program leadership
        - **Operational Risks** (● Circle): Cause-oriented, managed by functional teams
        - **Origin Tracking**: Distinguish between New (program-specific) and Legacy (inherited) risks
        
        **🔗 Influence Mapping**
        - Level 1: Operational → Business influences (red, thick)
        - Level 2: Business → Business influences (purple, medium)
        - Level 3: Operational → Operational influences (blue, dashed)
        - Configurable strength and confidence scoring
        
        **🏆 Top Program Objectives (TPOs)**
        - ⬡ Gold hexagon visualization
        - Cluster-based organization (Product, Business, Industrial, Safety, Sustainability)
        - Impact level tracking with visual indicators
        
        **🛡️ Mitigation Management**
        - **Dedicated** (teal, solid): Program-owned mitigations
        - **Inherited** (blue, dotted): From corporate or other programs
        - **Baseline** (purple, thick): Standards, regulations, best practices
        - Shield-shaped nodes (🛡️) with bar-end arrows showing "blocking" effect
        
        **⚠️ Contingent Risk Support**
        - ◇ Hollow diamond shape for potential/contingent risks
        - Decision timeline and activation conditions
        - Visual distinction with dashed borders
        
        **🔍 Advanced Analysis**
        - Influence Explorer for network traversal
        - Top propagators and convergence points identification
        - Critical path analysis
        - Risk clustering by category
        
        **📊 Import/Export**
        - Full Excel import/export capability
        - Layout save/load for presentations
        
        ---
        
        ### 🎨 Visual Legend Quick Reference
        
        | Element | Shape | Meaning |
        |---------|-------|---------|
        | ◆ Purple | Diamond | Strategic Risk |
        | ● Blue | Circle | Operational Risk |
        | 🛡️ Teal/Blue/Purple | Rounded Box | Mitigation |
        | ⬡ Gold | Hexagon | TPO |
        | → | Standard Arrow | Influence |
        | ⊣ | Bar-end Arrow | Mitigation link |
        | ▷ | Vee Arrow | TPO Impact |
        """)


def render_statistics_dashboard(stats: dict):
    """Render the statistics dashboard."""
    with st.expander("📊 Statistics Dashboard", expanded=True):
        # First row of metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🎯 Total Risks", stats.get("total_risks", 0))
        with col2:
            # Schema-driven level 1 display
            level1_name = stats.get("level1_name", RISK_LEVELS[0] if RISK_LEVELS else "Business")
            level1_cfg = RISK_LEVEL_CONFIG.get(level1_name, {})
            st.metric(f"{level1_cfg.get('emoji', '◆')} {level1_name}", stats.get("level1_risks", 0))
        with col3:
            # Schema-driven level 2 display
            level2_name = stats.get("level2_name", RISK_LEVELS[1] if len(RISK_LEVELS) > 1 else "Operational")
            level2_cfg = RISK_LEVEL_CONFIG.get(level2_name, {})
            st.metric(f"{level2_cfg.get('emoji', '●')} {level2_name}", stats.get("level2_risks", 0))
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
                        help="Run exposure calculation for all risks"):
                with st.spinner("Calculating exposure scores..."):
                    try:
                        results = manager.calculate_exposure()
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
    from config import RISK_STATUSES, RISK_ORIGINS, MITIGATION_TYPES, MITIGATION_STATUSES
    
    filter_mgr = st.session_state.filter_manager
    
    st.markdown("### 🎛️ Filters")
    
    # Refresh button
    if st.button("🔄 Refresh Visualization", use_container_width=True, type="primary"):
        st.rerun()
    
    st.markdown("---")
    
    # Filter Presets
    with st.expander("⚡ Quick Presets", expanded=False):
        preset_cols = st.columns(2)
        col_idx = 0
        for preset_key, preset_data in FilterManager.PRESETS.items():
            with preset_cols[col_idx % 2]:
                if st.button(
                    preset_data.name,
                    key=f"preset_{preset_key}",
                    use_container_width=True,
                    help=preset_data.description
                ):
                    filter_mgr.apply_preset(preset_key)
                    st.rerun()
            col_idx += 1
    
    # Risk Filters
    with st.expander("🎯 Risk Filters", expanded=True):
        # Level filter
        st.markdown("**Level**")
        col_level_btns = st.columns([1, 1])
        with col_level_btns[0]:
            if st.button("All", key="level_all", use_container_width=True):
                filter_mgr.select_all_levels()
                st.rerun()
        with col_level_btns[1]:
            if st.button("None", key="level_none", use_container_width=True):
                filter_mgr.deselect_all_levels()
                st.rerun()
        
        level_filter = st.multiselect(
            "Level",
            RISK_LEVELS,
            default=filter_mgr.filters["risks"]["levels"],
            key="level_filter",
            label_visibility="collapsed"
        )
        filter_mgr.set_risk_levels(level_filter)
        
        st.markdown("---")
        
        # Status filter
        st.markdown("**Status**")
        status_filter = st.multiselect(
            "Status",
            RISK_STATUSES,
            default=filter_mgr.filters["risks"].get("statuses", ["Active", "Contingent"]),
            key="status_filter",
            label_visibility="collapsed"
        )
        filter_mgr.filters["risks"]["statuses"] = status_filter
        
        st.markdown("---")
        
        # Origin filter
        st.markdown("**Origin**")
        origin_filter = st.multiselect(
            "Origin",
            RISK_ORIGINS,
            default=filter_mgr.filters["risks"].get("origins", RISK_ORIGINS.copy()),
            key="origin_filter",
            label_visibility="collapsed"
        )
        filter_mgr.filters["risks"]["origins"] = origin_filter
        
        st.markdown("---")
        
        # Category filter
        st.markdown("**Categories**")
        col_cat_btns = st.columns([1, 1])
        with col_cat_btns[0]:
            if st.button("All", key="cat_all", use_container_width=True):
                filter_mgr.select_all_categories()
                st.rerun()
        with col_cat_btns[1]:
            if st.button("None", key="cat_none", use_container_width=True):
                filter_mgr.deselect_all_categories()
                st.rerun()
        
        category_filter = st.multiselect(
            "Categories",
            RISK_CATEGORIES,
            default=filter_mgr.filters["risks"]["categories"],
            key="category_filter",
            label_visibility="collapsed"
        )
        filter_mgr.set_risk_categories(category_filter)
        
        st.markdown("---")
        
        # Exposure threshold filter
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
    
    # TPO Filters
    with st.expander("🏆 TPO Filters", expanded=False):
        show_tpos = st.checkbox(
            "Show TPOs",
            value=filter_mgr.filters["tpos"]["enabled"],
            key="show_tpos"
        )
        filter_mgr.set_tpo_enabled(show_tpos)
        
        if show_tpos:
            tpo_clusters = st.multiselect(
                "TPO Clusters",
                TPO_CLUSTERS,
                default=filter_mgr.filters["tpos"]["clusters"],
                key="tpo_cluster_filter"
            )
            filter_mgr.set_tpo_clusters(tpo_clusters)
    
    # Mitigation Filters
    with st.expander("🛡️ Mitigation Filters", expanded=False):
        show_mitigations = st.checkbox(
            "Show Mitigations",
            value=filter_mgr.filters["mitigations"]["enabled"],
            key="show_mitigations"
        )
        filter_mgr.set_mitigations_enabled(show_mitigations)
        
        if show_mitigations:
            st.markdown("**Mitigation Types**")
            mit_types = st.multiselect(
                "Types",
                MITIGATION_TYPES,
                default=filter_mgr.filters["mitigations"].get("types", MITIGATION_TYPES.copy()),
                key="mit_type_filter",
                label_visibility="collapsed"
            )
            filter_mgr.filters["mitigations"]["types"] = mit_types
            
            st.markdown("**Mitigation Status**")
            mit_statuses = st.multiselect(
                "Status",
                MITIGATION_STATUSES,
                default=filter_mgr.filters["mitigations"].get("statuses", MITIGATION_STATUSES.copy()),
                key="mit_status_filter",
                label_visibility="collapsed"
            )
            filter_mgr.filters["mitigations"]["statuses"] = mit_statuses
    
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
            # Node selection
            all_nodes = manager.get_all_nodes_for_selection()
            
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


def render_visualization_tab(manager: RiskGraphManager):
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
        
        # Analysis panels
        render_influence_analysis_panel(
            get_analysis_fn=manager.get_influence_analysis,
            on_node_select=on_node_select
        )
        render_mitigation_analysis_panel(
            get_analysis_fn=manager.get_mitigation_analysis,
            get_coverage_gaps_fn=manager.get_coverage_gap_analysis,
            get_all_risks_fn=manager.get_all_risks,
            get_all_mitigations_fn=manager.get_all_mitigations,
            get_risk_details_fn=manager.get_risk_mitigation_details,
            get_mitigation_details_fn=manager.get_mitigation_impact_details,
            get_mitigation_by_id_fn=manager.get_mitigation_by_id,
            get_risks_for_mitigation_fn=manager.get_risks_for_mitigation,
        )
        
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
    
    # Statistics dashboard
    stats = manager.get_statistics()
    render_statistics_dashboard(stats)
    
    # Exposure analysis dashboard
    render_exposure_dashboard(manager)
    
    st.markdown("---")
    
    # Main tabs
    tab_viz, tab_risks, tab_tpos, tab_mitigations, tab_influences, tab_tpo_impacts, tab_risk_mitigations, tab_import = st.tabs([
        "📊 Visualization",
        "🎯 Risks",
        "🏆 TPOs",
        "🛡️ Mitigations",
        "🔗 Influences",
        "📌 TPO Impacts",
        "💊 Risk Mitigations",
        "📥 Import/Export"
    ])
    
    # Visualization Tab
    with tab_viz:
        render_visualization_tab(manager)
    
    # Risks Tab
    with tab_risks:
        render_risks_tab(
            get_all_risks_fn=manager.get_all_risks,
            create_risk_fn=manager.create_risk,
            delete_risk_fn=manager.delete_risk
        )
    
    # TPOs Tab
    with tab_tpos:
        render_tpos_tab(
            get_all_tpos_fn=manager.get_all_tpos,
            create_tpo_fn=manager.create_tpo,
            delete_tpo_fn=manager.delete_tpo
        )
    
    # Mitigations Tab
    with tab_mitigations:
        render_mitigations_tab(
            get_all_mitigations_fn=manager.get_all_mitigations,
            create_mitigation_fn=manager.create_mitigation,
            delete_mitigation_fn=manager.delete_mitigation,
            get_risks_for_mitigation_fn=manager.get_risks_for_mitigation
        )
    
    # Influences Tab
    with tab_influences:
        render_influences_tab(
            get_all_risks_fn=manager.get_all_risks,
            get_all_influences_fn=manager.get_all_influences,
            create_influence_fn=manager.create_influence,
            delete_influence_fn=manager.delete_influence
        )
    
    # TPO Impacts Tab
    with tab_tpo_impacts:
        render_tpo_impacts_tab(
            get_all_risks_fn=manager.get_all_risks,
            get_all_tpos_fn=manager.get_all_tpos,
            get_all_tpo_impacts_fn=manager.get_all_tpo_impacts,
            create_tpo_impact_fn=manager.create_tpo_impact,
            delete_tpo_impact_fn=manager.delete_tpo_impact
        )
    
    # Risk Mitigations Tab
    with tab_risk_mitigations:
        render_risk_mitigations_tab(
            get_all_risks_fn=manager.get_all_risks,
            get_all_mitigations_fn=manager.get_all_mitigations,
            get_all_mitigates_fn=manager.get_all_mitigates_relationships,
            create_mitigates_fn=manager.create_mitigates_relationship,
            delete_mitigates_fn=manager.delete_mitigates_relationship
        )
    
    # Import/Export Tab
    with tab_import:
        render_import_export_tab(
            export_fn=manager.export_to_excel,
            import_fn=manager.import_from_excel
        )


if __name__ == "__main__":
    main()
