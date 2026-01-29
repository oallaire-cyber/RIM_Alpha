"""
Influence Analysis Panel for RIM Application.

Renders the influence analysis panel with:
- Top Propagators
- Convergence Points
- Critical Paths
- Bottlenecks
- Risk Clusters
"""

from typing import Dict, Any, Optional, Callable, List
import time


def render_influence_analysis_panel(
    analysis_data: Optional[Dict[str, Any]] = None,
    get_analysis_fn: Optional[Callable] = None,
    on_node_select: Optional[Callable[[str, str], None]] = None,
    cache_timeout: int = 30
):
    """
    Render the influence analysis panel.
    
    Args:
        analysis_data: Pre-computed analysis data (if None, will use get_analysis_fn)
        get_analysis_fn: Function to call to get analysis data
        on_node_select: Callback when user selects a node to explore.
                       Called with (node_id, direction) where direction is
                       "upstream", "downstream", or "both"
        cache_timeout: Seconds before cache expires
    """
    import streamlit as st
    
    # Initialize cache
    if "influence_analysis_cache" not in st.session_state:
        st.session_state.influence_analysis_cache = None
        st.session_state.influence_analysis_timestamp = None
    
    # Handle pending node selection
    if "pending_explore_node" in st.session_state and st.session_state.pending_explore_node:
        pending = st.session_state.pending_explore_node
        st.session_state.pending_explore_node = None
        if on_node_select:
            on_node_select(pending["node_id"], pending.get("direction", "both"))
        st.rerun()
    
    # Check cache validity
    current_time = time.time()
    cache_valid = (
        st.session_state.influence_analysis_cache is not None and
        st.session_state.influence_analysis_timestamp is not None and
        (current_time - st.session_state.influence_analysis_timestamp) < cache_timeout
    )
    
    with st.expander("📊 Influence Analysis", expanded=False):
        # Refresh button
        col_refresh, col_spacer = st.columns([1, 4])
        with col_refresh:
            if st.button("🔄 Refresh Analysis", key="refresh_influence_analysis", use_container_width=True):
                st.session_state.influence_analysis_cache = None
                cache_valid = False
        
        # Get or compute analysis
        analysis = analysis_data
        
        if analysis is None:
            if not cache_valid and get_analysis_fn:
                with st.spinner("Analyzing influence network..."):
                    try:
                        analysis = get_analysis_fn()
                        st.session_state.influence_analysis_cache = analysis
                        st.session_state.influence_analysis_timestamp = current_time
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
                        return
            else:
                analysis = st.session_state.influence_analysis_cache
        
        if not analysis:
            st.info("No data available for analysis. Create some risks and influences first.")
            return
        
        # Create tabs for different analysis views
        analysis_tabs = st.tabs([
            "🎯 Top Propagators",
            "⚠️ Convergence Points",
            "🔥 Critical Paths",
            "🚧 Bottlenecks",
            "📦 Risk Clusters"
        ])
        
        # Tab 1: Top Propagators
        with analysis_tabs[0]:
            _render_propagators_tab(analysis.get("top_propagators", []), on_node_select)
        
        # Tab 2: Convergence Points
        with analysis_tabs[1]:
            _render_convergence_tab(analysis.get("convergence_points", []), on_node_select)
        
        # Tab 3: Critical Paths
        with analysis_tabs[2]:
            _render_critical_paths_tab(analysis.get("critical_paths", []))
        
        # Tab 4: Bottlenecks
        with analysis_tabs[3]:
            _render_bottlenecks_tab(analysis.get("bottlenecks", []), on_node_select)
        
        # Tab 5: Risk Clusters
        with analysis_tabs[4]:
            _render_clusters_tab(analysis.get("risk_clusters", []))


def _render_propagators_tab(
    propagators: List[Dict[str, Any]],
    on_node_select: Optional[Callable] = None,
    limit: int = 3
):
    """Render the Top Propagators tab content."""
    import streamlit as st
    
    st.markdown("**Risks with highest downstream impact** - Mitigate here for global effect")
    
    if not propagators:
        st.info("No propagation data available.")
        return
    
    for i, prop in enumerate(propagators[:limit], 1):
        level_icon = "🟣" if prop.get("level") == "Strategic" else "🔵"
        node_id = prop.get("id")
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{i}. {level_icon} {prop.get('name', 'Unknown')}**")
            
            # Handle both full analysis format and simple database format
            if "score" in prop:
                # Full analysis format
                st.caption(
                    f"Propagation Score: **{prop['score']}** | "
                    f"Reaches: {prop.get('tpos_reached', 0)} TPOs, {prop.get('risks_reached', 0)} Risks"
                )
            elif "influence_count" in prop:
                # Simple database format
                st.caption(
                    f"Outgoing Influences: **{prop['influence_count']}** | "
                    f"Exposure: {prop.get('exposure', 'N/A')}"
                )
            else:
                st.caption("Analysis data not available")
        
        with col_btn:
            if node_id and st.button("🔍", key=f"btn_propagator_{node_id}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": node_id,
                    "direction": "downstream"
                }
                st.rerun()


def _render_convergence_tab(
    convergence_points: List[Dict[str, Any]],
    on_node_select: Optional[Callable] = None,
    limit: int = 3
):
    """Render the Convergence Points tab content."""
    import streamlit as st
    
    st.markdown("**Risks/TPOs where multiple influences converge** - Require transverse management")
    
    if not convergence_points:
        st.info("No convergence data available.")
        return
    
    for i, conv in enumerate(convergence_points[:limit], 1):
        node_type = conv.get("node_type", "Risk")
        if node_type == "TPO":
            level_icon = "🟡"
        elif conv.get("level") == "Strategic":
            level_icon = "🟣"
        else:
            level_icon = "🔵"
        
        node_id = conv.get("id")
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{i}. {level_icon} {conv.get('name', 'Unknown')}**")
            
            # Handle both full analysis format and simple database format
            if "score" in conv:
                # Full analysis format
                convergence_warning = " ⚡ High convergence" if conv.get("is_high_convergence") else ""
                st.caption(
                    f"Influence Score: **{conv['score']}** | "
                    f"Sources: {conv.get('source_count', 0)} risks ({conv.get('path_count', 0)} paths)"
                    f"{convergence_warning}"
                )
                if conv.get("is_high_convergence"):
                    st.caption("💡 *Mitigate upstream rather than directly*")
            elif "influenced_by_count" in conv:
                # Simple database format
                st.caption(
                    f"Incoming Influences: **{conv['influenced_by_count']}** | "
                    f"Exposure: {conv.get('exposure', 'N/A')}"
                )
            else:
                st.caption("Analysis data not available")
        
        with col_btn:
            if node_id and st.button("🔍", key=f"btn_convergence_{node_id}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": node_id,
                    "direction": "upstream"
                }
                st.rerun()


def _render_critical_paths_tab(
    critical_paths: List[Dict[str, Any]],
    limit: int = 3
):
    """Render the Critical Paths tab content."""
    import streamlit as st
    
    st.markdown("**Strongest influence chains from operational risks to TPOs**")
    
    if not critical_paths:
        st.info("No critical paths found. Ensure risks are connected to TPOs.")
        return
    
    for i, path in enumerate(critical_paths[:limit], 1):
        # Build path string
        path_parts = []
        for node in path["path"]:
            if node["type"] == "TPO":
                icon = "🟡"
            elif node["type"] == "Strategic":
                icon = "🟣"
            else:
                icon = "🔵"
            path_parts.append(f"{icon} {node['name']}")
        
        path_str = " → ".join(path_parts)
        
        st.markdown(f"**{i}. Path Strength: {path['strength']:.2f}**")
        st.caption(path_str)
        st.markdown("---")


def _render_bottlenecks_tab(
    bottlenecks: List[Dict[str, Any]],
    on_node_select: Optional[Callable] = None,
    limit: int = 3
):
    """Render the Bottlenecks tab content."""
    import streamlit as st
    
    st.markdown("**Nodes appearing in many paths to TPOs** - Single points of failure")
    
    if not bottlenecks:
        st.info("No bottlenecks identified.")
        return
    
    for i, bn in enumerate(bottlenecks[:limit], 1):
        level_icon = "🟣" if bn["level"] == "Strategic" else "🔵"
        node_id = bn["id"]
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{i}. {level_icon} {bn['name']}**")
            st.caption(
                f"Appears in **{bn['path_count']}** of {bn['total_paths']} paths to TPOs "
                f"({bn['percentage']}%)"
            )
            if bn["percentage"] > 50:
                st.caption("🚨 *Critical bottleneck - high impact if this risk materializes*")
        with col_btn:
            if st.button("🔍", key=f"btn_bottleneck_{node_id}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": node_id,
                    "direction": "both"
                }
                st.rerun()


def _render_clusters_tab(
    clusters: List[Dict[str, Any]],
    limit: int = 3
):
    """Render the Risk Clusters tab content."""
    import streamlit as st
    
    st.markdown("**Tightly interconnected risk groups** - Consider managing as units")
    
    if not clusters:
        st.info("No risk clusters identified.")
        return
    
    for i, cluster in enumerate(clusters[:limit], 1):
        st.markdown(f"**{i}. Cluster: {cluster['primary_category']}** ({cluster['size']} risks)")
        
        # Show level breakdown
        levels = cluster.get("levels", {})
        level_str = f"🟣 {levels.get('Strategic', 0)} Strategic, 🔵 {levels.get('Operational', 0)} Operational"
        st.caption(f"{level_str} | {cluster['internal_edges']} internal links | Density: {cluster['density']}")
        
        # Show node names (truncated)
        node_names = cluster.get("node_names", [])[:5]
        if len(cluster.get("node_names", [])) > 5:
            node_names.append(f"... +{len(cluster['node_names']) - 5} more")
        st.caption("Includes: " + ", ".join(node_names))
        st.markdown("---")


def get_level_icon(level: str, node_type: str = "Risk") -> str:
    """Get the appropriate icon for a node's level/type."""
    if node_type == "TPO":
        return "🟡"
    elif level == "Strategic":
        return "🟣"
    else:
        return "🔵"
