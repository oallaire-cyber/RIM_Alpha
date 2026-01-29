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
        
        submitted = st.form_submit_button("Create TPO", type="primary", use_container_width=True)
        
        if submitted:
            if reference and name and cluster:
                success = create_tpo_fn(
                    reference=reference,
                    name=name,
                    cluster=cluster,
                    description=description
                )
                if success:
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
    
    # Group by cluster
    clusters_data = {}
    for tpo in tpos:
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
                        if st.button("🗑️ Delete", key=f"del_tpo_{tpo['id']}", use_container_width=True):
                            if delete_tpo_fn(tpo['id']):
                                st.success("TPO deleted")
                                st.rerun()
