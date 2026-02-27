"""
TPOs Tab for RIM Application.

Provides TPO (Top Program Objectives) creation and management interface.
"""

from typing import Dict, Any, Optional, Callable, List
from config.settings import TPO_CLUSTERS


def render_tpos_tab(
    get_all_tpos_fn: Callable[[], List[Dict]],
    create_tpo_fn: Callable[..., bool],
    delete_tpo_fn: Callable[[str], bool],
    update_tpo_fn: Optional[Callable[..., bool]] = None
):
    """
    Render the TPOs management tab.
    
    Args:
        get_all_tpos_fn: Function to get all TPOs
        create_tpo_fn: Function to create a new TPO
        delete_tpo_fn: Function to delete a TPO
        update_tpo_fn: Optional function to update a TPO
    """
    import streamlit as st
    
    col_form, col_list = st.columns([1, 1])
    
    with col_form:
        _render_tpo_form(create_tpo_fn)
    
    with col_list:
        _render_tpo_list(get_all_tpos_fn, delete_tpo_fn)


def _render_tpo_form(create_tpo_fn: Callable[..., bool]):
    """Render the TPO creation form."""
    import streamlit as st
    
    st.markdown("### ➕ Create a TPO")
    
    with st.form("create_tpo_form", clear_on_submit=True):
        reference = st.text_input("Reference *", placeholder="E.g.: TPO-01")
        
        name = st.text_input("Name *", placeholder="E.g.: Reduce production costs by 15%")
        
        cluster = st.selectbox("Cluster *", TPO_CLUSTERS)
        
        description = st.text_area("Description", placeholder="Detailed TPO description...")
        
        # Scope addition
        filter_mgr = st.session_state.get("filter_manager")
        active_scopes = filter_mgr.active_scopes if filter_mgr else []
        add_to_scope = False
        if active_scopes:
            scope_names = [s.name for s in active_scopes]
            st.markdown("---")
            add_to_scope = st.checkbox(
                f"Add this new TPO to active scope(s): {', '.join(scope_names)}",
                value=True,
                help="If checked, the new TPO will be automatically added to the currently active scopes."
            )
        
        submitted = st.form_submit_button("Create TPO", type="primary", use_container_width=True)
        
        if submitted:
            if reference and name and cluster:
                result_id = create_tpo_fn(
                    reference=reference,
                    name=name,
                    cluster=cluster,
                    description=description
                )
                if result_id:
                    if add_to_scope and filter_mgr:
                        for scope in filter_mgr.active_scopes:
                            filter_mgr.add_node_to_scope(scope.id, result_id)
                    
                    st.success(f"TPO '{reference}' created successfully!")
                    st.rerun()
            else:
                st.error("Reference, name and cluster are required")


def _render_tpo_list(
    get_all_tpos_fn: Callable[[], List[Dict]],
    delete_tpo_fn: Callable[[str], bool]
):
    """Render the existing TPOs list, grouped by cluster."""
    import streamlit as st
    
    st.markdown("### 📋 Existing TPOs")
    
    tpos = get_all_tpos_fn()
    
    if not tpos:
        st.info("No TPOs created.")
        return
        
    tpos = sorted(tpos, key=lambda x: (x.get('cluster', 'Unknown'), x.get('reference', '')))
    
    from ui.components import render_pagination
    start_idx, end_idx = render_pagination(len(tpos), 20, "tpos_list")
    paginated_tpos = tpos[start_idx:end_idx]
    
    # Group by cluster
    clusters_data = {}
    for tpo in paginated_tpos:
        cluster = tpo.get('cluster', 'Unknown')
        if cluster not in clusters_data:
            clusters_data[cluster] = []
        clusters_data[cluster].append(tpo)
    
    # Display by cluster in defined order
    for cluster in TPO_CLUSTERS:
        if cluster in clusters_data:
            st.markdown(f"#### 📁 {cluster}")
            for tpo in clusters_data[cluster]:
                with st.expander(f"🟡 {tpo['reference']}: {tpo['name']}", expanded=False):
                    st.markdown(f"**Reference:** {tpo['reference']}")
                    st.markdown(f"**Name:** {tpo['name']}")
                    st.markdown(f"**Cluster:** {tpo['cluster']}")
                    
                    if tpo.get('description'):
                        st.markdown(f"**Description:** {tpo['description']}")
                    
                    col_edit, col_del = st.columns(2)
                    
                    with col_del:
                        filter_mgr = st.session_state.get("filter_manager")
                        active_scopes = filter_mgr.active_scopes if filter_mgr else []
                        
                        if active_scopes:
                            if st.button("➖ Remove from Scopes", key=f"rm_scope_tpo_{tpo['id']}", use_container_width=True):
                                removed = False
                                for scope in filter_mgr.active_scopes:
                                    if filter_mgr.remove_node_from_scope(scope.id, tpo['id']):
                                        removed = True
                                if removed:
                                    st.success("TPO removed from active scopes")
                                    st.rerun()
                            
                            st.markdown("<div style='text-align: center; font-size: 0.8em; color: gray;'>or</div>", unsafe_allow_html=True)
                            
                            if st.button("🗑️ Delete Globally", key=f"del_global_tpo_{tpo['id']}", use_container_width=True, type="secondary"):
                                if delete_tpo_fn(tpo['id']):
                                    st.success("TPO deleted from database")
                                    st.rerun()
                        else:
                            if st.button("🗑️ Delete", key=f"del_tpo_{tpo['id']}", use_container_width=True):
                                if delete_tpo_fn(tpo['id']):
                                    st.success("TPO deleted")
                                    st.rerun()
