"""
Sidebar Components for RIM Application.

Provides sidebar rendering for filters, presets, and controls.
"""

from typing import Dict, List, Any, Optional, Callable
from ui.filters import FilterManager, FILTER_PRESETS, get_preset_names
from config.settings import (
    RISK_LEVELS, RISK_CATEGORIES, RISK_STATUSES, RISK_ORIGINS,
    TPO_CLUSTERS, MITIGATION_TYPES, MITIGATION_STATUSES
)


def render_filter_sidebar(
    filter_manager: FilterManager,
    on_filter_change: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Render the complete filter sidebar using Streamlit.
    
    Args:
        filter_manager: FilterManager instance to update
        on_filter_change: Optional callback when filters change
    
    Returns:
        Dictionary with current filter state
    """
    import streamlit as st
    
    st.sidebar.header("🎛️ Filters")
    
    # Preset selector
    preset_names = get_preset_names()
    preset_options = ["Custom"] + list(preset_names.keys())
    preset_labels = ["Custom"] + [preset_names[k] for k in preset_names.keys()]
    
    selected_preset = st.sidebar.selectbox(
        "Quick Preset",
        options=preset_options,
        format_func=lambda x: preset_names.get(x, x),
        key="filter_preset"
    )
    
    if selected_preset != "Custom":
        if st.sidebar.button("Apply Preset"):
            filter_manager.apply_preset(selected_preset)
            if on_filter_change:
                on_filter_change()
            st.rerun()
    
    st.sidebar.divider()
    
    # Risk Filters
    with st.sidebar.expander("📊 Risk Filters", expanded=True):
        # Levels
        st.write("**Levels**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("All", key="all_levels", use_container_width=True):
                filter_manager.select_all_levels()
        with col2:
            if st.button("None", key="no_levels", use_container_width=True):
                filter_manager.deselect_all_levels()
        
        selected_levels = st.multiselect(
            "Select levels",
            options=RISK_LEVELS,
            default=filter_manager.filters["risks"]["levels"],
            key="risk_levels",
            label_visibility="collapsed"
        )
        filter_manager.set_risk_levels(selected_levels)
        
        # Categories
        st.write("**Categories**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("All", key="all_cats", use_container_width=True):
                filter_manager.select_all_categories()
        with col2:
            if st.button("None", key="no_cats", use_container_width=True):
                filter_manager.deselect_all_categories()
        
        selected_categories = st.multiselect(
            "Select categories",
            options=RISK_CATEGORIES,
            default=filter_manager.filters["risks"]["categories"],
            key="risk_categories",
            label_visibility="collapsed"
        )
        filter_manager.set_risk_categories(selected_categories)
        
        # Statuses
        st.write("**Status**")
        selected_statuses = st.multiselect(
            "Select statuses",
            options=RISK_STATUSES,
            default=filter_manager.filters["risks"]["statuses"],
            key="risk_statuses",
            label_visibility="collapsed"
        )
        filter_manager.set_risk_statuses(selected_statuses)
        
        # Origins
        st.write("**Origin**")
        selected_origins = st.multiselect(
            "Select origins",
            options=RISK_ORIGINS,
            default=filter_manager.filters["risks"]["origins"],
            key="risk_origins",
            label_visibility="collapsed"
        )
        filter_manager.set_risk_origins(selected_origins)
    
    # TPO Filters
    with st.sidebar.expander("🎯 TPO Filters", expanded=True):
        show_tpos = st.checkbox(
            "Show TPOs",
            value=filter_manager.filters["tpos"]["enabled"],
            key="show_tpos"
        )
        filter_manager.set_tpo_enabled(show_tpos)
        
        if show_tpos:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("All", key="all_clusters", use_container_width=True):
                    filter_manager.select_all_clusters()
            with col2:
                if st.button("None", key="no_clusters", use_container_width=True):
                    filter_manager.deselect_all_clusters()
            
            selected_clusters = st.multiselect(
                "TPO Clusters",
                options=TPO_CLUSTERS,
                default=filter_manager.filters["tpos"]["clusters"],
                key="tpo_clusters",
                label_visibility="collapsed"
            )
            filter_manager.set_tpo_clusters(selected_clusters)
    
    # Mitigation Filters
    with st.sidebar.expander("🛡️ Mitigation Filters", expanded=False):
        show_mitigations = st.checkbox(
            "Show Mitigations",
            value=filter_manager.filters["mitigations"]["enabled"],
            key="show_mitigations"
        )
        filter_manager.set_mitigations_enabled(show_mitigations)
        
        if show_mitigations:
            st.write("**Types**")
            selected_types = st.multiselect(
                "Mitigation types",
                options=MITIGATION_TYPES,
                default=filter_manager.filters["mitigations"]["types"],
                key="mit_types",
                label_visibility="collapsed"
            )
            filter_manager.set_mitigation_types(selected_types)
            
            st.write("**Statuses**")
            selected_mit_statuses = st.multiselect(
                "Mitigation statuses",
                options=MITIGATION_STATUSES,
                default=filter_manager.filters["mitigations"]["statuses"],
                key="mit_statuses",
                label_visibility="collapsed"
            )
            filter_manager.set_mitigation_statuses(selected_mit_statuses)
    
    # Validation
    is_valid, message = filter_manager.validate()
    if not is_valid:
        st.sidebar.error(message)
    elif message:
        st.sidebar.warning(message)
    
    # Filter summary
    st.sidebar.divider()
    st.sidebar.caption(f"**Current filters:** {filter_manager.get_filter_summary()}")
    
    return filter_manager.get_filters_for_query()


def render_graph_controls(
    current_physics: bool = True,
    current_layout: str = "auto",
    available_layouts: List[str] = None
) -> Dict[str, Any]:
    """
    Render graph visualization controls in sidebar.
    
    Args:
        current_physics: Current physics enabled state
        current_layout: Current layout type
        available_layouts: List of available layout options
    
    Returns:
        Dictionary with control values
    """
    import streamlit as st
    
    if available_layouts is None:
        available_layouts = ["auto", "layered", "category", "tpo_cluster"]
    
    st.sidebar.header("🎨 Graph Controls")
    
    # Physics toggle
    physics_enabled = st.sidebar.checkbox(
        "Enable Physics",
        value=current_physics,
        help="Enable/disable physics simulation for node positioning"
    )
    
    # Layout selector
    layout_type = st.sidebar.selectbox(
        "Layout",
        options=available_layouts,
        index=available_layouts.index(current_layout) if current_layout in available_layouts else 0,
        help="Select graph layout algorithm"
    )
    
    # Edge display
    st.sidebar.write("**Edge Display**")
    show_all_edges = st.sidebar.checkbox("Show all edges", value=True)
    edge_threshold = 0
    if not show_all_edges:
        edge_threshold = st.sidebar.slider(
            "Minimum edge score",
            min_value=0.0,
            max_value=4.0,
            value=1.0,
            step=0.5
        )
    
    # Node sizing
    scale_by_exposure = st.sidebar.checkbox(
        "Scale nodes by exposure",
        value=True,
        help="Make higher-exposure risks appear larger"
    )
    
    return {
        "physics_enabled": physics_enabled,
        "layout_type": layout_type,
        "show_all_edges": show_all_edges,
        "edge_threshold": edge_threshold,
        "scale_by_exposure": scale_by_exposure
    }


def render_layout_manager_sidebar(layout_manager) -> Optional[str]:
    """
    Render layout save/load controls in sidebar.
    
    Args:
        layout_manager: LayoutManager instance
    
    Returns:
        Action to perform: "save", "load", "delete", or None
    """
    import streamlit as st
    
    with st.sidebar.expander("💾 Layout Management"):
        # List existing layouts
        layouts = layout_manager.list_layouts()
        
        if layouts:
            st.write("**Saved Layouts:**")
            for name, meta in layouts.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"{name} ({meta['node_count']} nodes)")
                with col2:
                    if st.button("🗑️", key=f"del_{name}"):
                        layout_manager.delete_layout(name)
                        st.rerun()
            
            selected_layout = st.selectbox(
                "Load layout",
                options=[""] + list(layouts.keys()),
                key="load_layout_select"
            )
            
            if selected_layout and st.button("Load Selected"):
                return ("load", selected_layout)
        else:
            st.caption("No saved layouts")
        
        # Save new layout
        st.divider()
        new_layout_name = st.text_input("New layout name", key="new_layout_name")
        if new_layout_name and st.button("Save Current Layout"):
            return ("save", new_layout_name)
    
    return None


def render_database_controls() -> Optional[str]:
    """
    Render database connection controls in sidebar.
    
    Returns:
        Action to perform: "connect", "disconnect", or None
    """
    import streamlit as st
    
    with st.sidebar.expander("🔌 Database Connection"):
        uri = st.text_input(
            "Neo4j URI",
            value="bolt://localhost:7687",
            key="neo4j_uri"
        )
        user = st.text_input(
            "Username",
            value="neo4j",
            key="neo4j_user"
        )
        password = st.text_input(
            "Password",
            type="password",
            key="neo4j_password"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", use_container_width=True):
                return ("connect", {"uri": uri, "user": user, "password": password})
        with col2:
            if st.button("Disconnect", use_container_width=True):
                return ("disconnect", None)
    
    return None


def render_export_import_sidebar() -> Optional[tuple]:
    """
    Render export/import controls in sidebar.
    
    Returns:
        Tuple of (action, data) or None
    """
    import streamlit as st
    
    with st.sidebar.expander("📁 Import/Export"):
        st.write("**Export**")
        if st.button("Export to Excel", use_container_width=True):
            return ("export", None)
        
        st.divider()
        
        st.write("**Import**")
        uploaded_file = st.file_uploader(
            "Upload Excel file",
            type=["xlsx"],
            key="import_file"
        )
        
        if uploaded_file is not None:
            if st.button("Import Data", use_container_width=True):
                return ("import", uploaded_file)
    
    return None
