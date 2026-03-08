"""
Data Management Page for RIM Application.

Provides a 4-tab unified interface for managing all nodes and edges:
- Core Nodes (Risks, Mitigations)
- Core Edges (Influences, Mitigates)
- Context Nodes (TPOs, Business Units, etc)
- Context Edges
"""

import streamlit as st
from config import APP_TITLE, APP_ICON, LAYOUT_MODE
from ui import inject_styles
from ui.sidebar import render_filter_sidebar
from ui.home import init_session_state, render_connection_sidebar, render_welcome_page, render_complexity_toggle, render_scope_selector
from ui.tabs import render_unified_crud_tab, render_import_export_tab
from core import get_registry

def render_data_management_page():
    """Render the dedicated Data Management page."""
    # Check connection
    if not st.session_state.connected:
        st.warning("Please connect to the database on the Home page first.")
        return
        
    manager = st.session_state.manager
    registry = get_registry()
    
    st.title("💾 Data Management")
    st.markdown("Easily adapt and modify the structural objects powering the Risk Graph visualization and Exposure Engine calculation.")
    
    # ── Sidebar Configuration ───────────────────────────────────────────────
    render_complexity_toggle()
    render_scope_selector()
    
    # Render unified attribute filters (so we can filter the list in the CRUD tabs)
    render_filter_sidebar(st.session_state.filter_manager)
    
    # ── 4 Tabs Configuration ────────────────────────────────────────────────
    tab_names = [
        "🔵 Core Nodes", 
        "🔗 Core Edges", 
        "🟡 Context Nodes", 
        "🔗 Context Edges",
        "📥 Import / Export"
    ]
    
    tabs = st.tabs(tab_names)
    
    # 1. Core Nodes
    with tabs[0]:
        st.markdown("Manage hardcoded algorithmic objects required by the Exposure Engine.")
        core_node_subtabs = st.tabs(["🔥 Risks", "🛡️ Mitigations"])
        
        with core_node_subtabs[0]:
            render_unified_crud_tab(manager, registry.get_entity_type("risk"))
            
        with core_node_subtabs[1]:
            render_unified_crud_tab(manager, registry.get_entity_type("mitigation"))
            
    # 2. Core Edges
    with tabs[1]:
        st.markdown("Manage mathematical relationships used for propagation calculations.")
        core_edge_subtabs = st.tabs(["➡️ Influences", "🛡️ Mitigates"])
        
        with core_edge_subtabs[0]:
            render_unified_crud_tab(manager, registry.get_relationship_type("influences"))
            
        with core_edge_subtabs[1]:
            render_unified_crud_tab(manager, registry.get_relationship_type("mitigates"))
            
    # 3. Context Nodes
    with tabs[2]:
        st.markdown("Manage schema-driven organizational elements.")
        
        # Filter for custom context nodes
        context_node_defs = [
            d for d in registry.entity_types.values() 
            if d.id not in ("risk", "mitigation")
        ]
        
        if not context_node_defs:
            st.info("No custom Context Nodes defined in schema.yaml.")
        else:
            cn_tabs = st.tabs([f"{d.emoji or '📦'} {d.label}s" for d in context_node_defs])
            for i, d in enumerate(context_node_defs):
                with cn_tabs[i]:
                    render_unified_crud_tab(manager, d)
                    
    # 4. Context Edges
    with tabs[3]:
        st.markdown("Manage custom organizational links.")
        
        # Filter for custom context edges
        context_edge_defs = [
            d for d in registry.relationship_types.values() 
            if d.id not in ("influences", "mitigates")
        ]
        
        if not context_edge_defs:
            st.info("No custom Context Edges defined in schema.yaml.")
        else:
            ce_tabs = st.tabs([f"🔗 {d.label}" for d in context_edge_defs])
            for i, d in enumerate(context_edge_defs):
                with ce_tabs[i]:
                    render_unified_crud_tab(manager, d)
                    
    # 5. Import / Export
    with tabs[4]:
        st.markdown("Bulk manage graph definitions via Excel.")
        render_import_export_tab(manager.export_to_excel, manager.import_from_excel)


def main():
    """Page execution."""
    # Page configuration
    st.set_page_config(
        page_title=f"{APP_TITLE} - Data",
        page_icon="💾",
        layout=LAYOUT_MODE,
        initial_sidebar_state="expanded"
    )
    
    inject_styles()
    init_session_state()
    render_connection_sidebar()
    
    if not st.session_state.connected:
        render_welcome_page()
    else:
        render_data_management_page()

if __name__ == "__main__":
    main()
