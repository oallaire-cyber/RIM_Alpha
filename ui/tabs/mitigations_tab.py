"""
Mitigations Tab for RIM Application.

Provides mitigation creation and management interface.
"""

from typing import Dict, Any, Optional, Callable, List
from config.settings import MITIGATION_TYPES, MITIGATION_STATUSES


def render_mitigations_tab(
    get_all_mitigations_fn: Callable[[], List[Dict]],
    create_mitigation_fn: Callable[..., bool],
    delete_mitigation_fn: Callable[[str], bool],
    get_risks_for_mitigation_fn: Optional[Callable[[str], List[Dict]]] = None,
    update_mitigation_fn: Optional[Callable[..., bool]] = None
):
    """
    Render the Mitigations management tab.
    
    Args:
        get_all_mitigations_fn: Function to get all mitigations
        create_mitigation_fn: Function to create a new mitigation
        delete_mitigation_fn: Function to delete a mitigation
        get_risks_for_mitigation_fn: Optional function to get risks for a mitigation
        update_mitigation_fn: Optional function to update a mitigation
    """
    import streamlit as st
    
    col_form, col_list = st.columns([1, 1])
    
    with col_form:
        _render_mitigation_form(create_mitigation_fn)
    
    with col_list:
        _render_mitigation_list(
            get_all_mitigations_fn,
            delete_mitigation_fn,
            get_risks_for_mitigation_fn
        )


def _render_mitigation_form(create_mitigation_fn: Callable[..., bool]):
    """Render the mitigation creation form."""
    import streamlit as st
    
    st.markdown("### ➕ Create a Mitigation")
    
    with st.form("create_mitigation_form", clear_on_submit=True):
        mit_name = st.text_input("Mitigation name *", placeholder="E.g.: Dual sourcing strategy")
        
        col_type_status = st.columns(2)
        with col_type_status[0]:
            mit_type = st.selectbox(
                "Type *", 
                MITIGATION_TYPES,
                help="Dedicated: Program-owned | Inherited: From other entities | Baseline: Standards/Requirements"
            )
        with col_type_status[1]:
            mit_status = st.selectbox("Status *", MITIGATION_STATUSES)
        
        mit_description = st.text_area("Description", placeholder="Detailed mitigation description...")
        
        mit_owner = st.text_input("Owner", placeholder="Mitigation owner")
        
        # Show source entity field for Inherited and Baseline types
        mit_source_entity = ""
        if mit_type in ["Inherited", "Baseline"]:
            mit_source_entity = st.text_input(
                "Source Entity" if mit_type == "Inherited" else "Standard/Requirement Reference",
                placeholder="E.g.: Corporate ERM" if mit_type == "Inherited" else "E.g.: ISO 27001 A.12.3"
            )
        
        submitted = st.form_submit_button("Create Mitigation", type="primary", use_container_width=True)
        
        if submitted:
            if mit_name and mit_type and mit_status:
                success = create_mitigation_fn(
                    name=mit_name,
                    mitigation_type=mit_type,
                    status=mit_status,
                    description=mit_description,
                    owner=mit_owner,
                    source_entity=mit_source_entity
                )
                if success:
                    st.success(f"Mitigation '{mit_name}' created successfully!")
                    st.rerun()
            else:
                st.error("Name, type, and status are required")


def _render_mitigation_list(
    get_all_mitigations_fn: Callable[[], List[Dict]],
    delete_mitigation_fn: Callable[[str], bool],
    get_risks_for_mitigation_fn: Optional[Callable[[str], List[Dict]]] = None
):
    """Render the existing mitigations list."""
    import streamlit as st
    
    st.markdown("### 📋 Existing Mitigations")
    
    mitigations = get_all_mitigations_fn()
    
    if not mitigations:
        st.info("No mitigations created.")
        return
    
    # Icons for types and statuses
    type_icons = {
        "Dedicated": "🎯",
        "Inherited": "📥",
        "Baseline": "📐"
    }
    status_icons = {
        "Proposed": "📋",
        "In Progress": "🔄",
        "Implemented": "✅",
        "Deferred": "⏸️"
    }
    
    for mit in mitigations:
        type_icon = type_icons.get(mit.get('type', 'Dedicated'), '🛡️')
        status_icon = status_icons.get(mit.get('status', 'Proposed'), '❓')
        
        with st.expander(f"{type_icon} {mit['name']} {status_icon}", expanded=False):
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Type:** {mit.get('type', 'N/A')}")
                st.markdown(f"**Status:** {mit.get('status', 'N/A')}")
            with col_info2:
                st.markdown(f"**Owner:** {mit.get('owner', 'Not defined')}")
                if mit.get('source_entity'):
                    st.markdown(f"**Source:** {mit['source_entity']}")
            
            if mit.get('description'):
                st.markdown(f"**Description:** {mit['description']}")
            
            # Show risks this mitigation addresses
            if get_risks_for_mitigation_fn:
                mitigated_risks = get_risks_for_mitigation_fn(mit['id'])
                if mitigated_risks:
                    st.markdown(f"**Mitigates {len(mitigated_risks)} risk(s):**")
                    for risk in mitigated_risks[:5]:  # Show first 5
                        st.caption(f"  • {risk['name']} ({risk.get('effectiveness', 'N/A')})")
                    if len(mitigated_risks) > 5:
                        st.caption(f"  ... and {len(mitigated_risks) - 5} more")
            
            col_edit, col_del = st.columns(2)
            
            with col_del:
                if st.button("🗑️ Delete", key=f"del_mit_{mit['id']}", use_container_width=True):
                    if delete_mitigation_fn(mit['id']):
                        st.success("Mitigation deleted")
                        st.rerun()
