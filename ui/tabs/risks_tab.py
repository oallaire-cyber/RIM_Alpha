"""
Risks Tab for RIM Application.

Provides risk creation and management interface.
"""

from typing import Dict, Any, Optional, Callable, List
from config.settings import RISK_LEVELS, RISK_CATEGORIES, RISK_STATUSES, RISK_ORIGINS


def render_risks_tab(
    get_all_risks_fn: Callable[[], List[Dict]],
    create_risk_fn: Callable[..., bool],
    delete_risk_fn: Callable[[str], bool],
    update_risk_fn: Optional[Callable[..., bool]] = None
):
    """
    Render the Risks management tab.
    
    Args:
        get_all_risks_fn: Function to get all risks
        create_risk_fn: Function to create a new risk
        delete_risk_fn: Function to delete a risk
        update_risk_fn: Optional function to update a risk
    """
    import streamlit as st
    
    col_form, col_list = st.columns([1, 1])
    
    with col_form:
        _render_risk_form(create_risk_fn)
    
    with col_list:
        _render_risk_list(get_all_risks_fn, delete_risk_fn)


def _render_risk_form(create_risk_fn: Callable[..., bool]):
    """Render the risk creation form."""
    import streamlit as st
    
    st.markdown("### ➕ Create a Risk")
    
    with st.form("create_risk_form", clear_on_submit=True):
        name = st.text_input("Risk name *", placeholder="E.g.: Fuel delivery delay")
        
        col_level_origin = st.columns(2)
        with col_level_origin[0]:
            level = st.selectbox("Level *", RISK_LEVELS)
        with col_level_origin[1]:
            origin = st.selectbox(
                "Origin *", 
                RISK_ORIGINS,
                help="New: Program-specific risk | Legacy: Inherited/Enterprise level risk"
            )
        
        categories = st.multiselect(
            "Categories *",
            RISK_CATEGORIES,
            default=[RISK_CATEGORIES[0]] if RISK_CATEGORIES else []
        )
        
        description = st.text_area("Description", placeholder="Detailed risk description...")
        
        status = st.selectbox("Status", RISK_STATUSES)
        
        activation_condition = None
        activation_decision_date = None
        
        if status == "Contingent":
            activation_condition = st.text_area(
                "Activation condition",
                placeholder="E.g.: If fuel choice X, then..."
            )
            activation_decision_date = st.date_input("Decision date").isoformat()
        
        owner = st.text_input("Owner", placeholder="Risk owner")
        
        col_p, col_i = st.columns(2)
        with col_p:
            probability = st.slider("Probability (optional)", 0.0, 10.0, 5.0, 0.5)
        with col_i:
            impact = st.slider("Impact (optional)", 0.0, 10.0, 5.0, 0.5)
        
        if probability > 0 and impact > 0:
            st.info(f"**Calculated exposure:** {probability * impact:.1f}")
        
        # Scope addition
        filter_mgr = st.session_state.get("filter_manager")
        active_scopes = filter_mgr.active_scopes if filter_mgr else []
        add_to_scope = False
        if active_scopes:
            scope_names = [s.name for s in active_scopes]
            st.markdown("---")
            add_to_scope = st.checkbox(
                f"Add this new risk to active scope(s): {', '.join(scope_names)}",
                value=True,
                help="If checked, the new risk will be automatically added to the currently active scopes."
            )
        
        submitted = st.form_submit_button("Create risk", type="primary", use_container_width=True)
        
        if submitted:
            if name and categories:
                # We need the created ID to add to scope. Let's assume create_risk_fn returns the created node ID or True.
                # Currently it returns boolean. We'll need to fetch the ID or modify the manager function to return ID.
                # For now, we rely on a hook or re-fetching. Actually, manager.create_risk returns the ID currently? Let's check manager.py
                result_id = create_risk_fn(
                    name=name,
                    level=level,
                    categories=categories,
                    description=description,
                    status=status,
                    activation_condition=activation_condition,
                    activation_decision_date=activation_decision_date,
                    owner=owner,
                    probability=probability if probability > 0 else None,
                    impact=impact if impact > 0 else None,
                    origin=origin
                )
                if result_id:
                    if add_to_scope and filter_mgr:
                        for scope in filter_mgr.active_scopes:
                            filter_mgr.add_node_to_scope(scope.id, result_id)
                    
                    st.success(f"Risk '{name}' created successfully!")
                    st.rerun()
            else:
                st.error("Name and at least one category are required")


def _render_risk_list(
    get_all_risks_fn: Callable[[], List[Dict]],
    delete_risk_fn: Callable[[str], bool]
):
    """Render the existing risks list."""
    import streamlit as st
    
    st.markdown("### 📋 Existing Risks")
    
    risks = get_all_risks_fn()
    
    if not risks:
        st.info("No risks created.")
        return
    
    from ui.components import render_pagination
    start_idx, end_idx = render_pagination(len(risks), 20, "risks_list")
    paginated_risks = risks[start_idx:end_idx]
    
    for risk in paginated_risks:
        level_icon = "🟣" if risk['level'] == 'Strategic' or risk['level'] == 'Business' else "🔵"
        origin = risk.get('origin', 'New')
        origin_icon = "📜" if origin == "Legacy" else "🆕"
        
        dist = risk.get('computed_distance', -1)
        is_orphan = risk.get('is_orphan', False)
        
        orphan_badge = " ⚠️ Orphan" if is_orphan else ""
        dist_badge = f" [Dist {dist}]" if dist > 0 else ""
        
        with st.expander(f"{level_icon} {origin_icon} {risk['name']}{dist_badge}{orphan_badge}", expanded=False):
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Stored Level:** {risk['level']}")
                st.markdown(f"**Computed Dist:** {dist if dist > 0 else 'Orphan (-1)'}")
                st.markdown(f"**Origin:** {origin}")
            with col_info2:
                st.markdown(f"**Status:** {risk['status']}")
                if risk.get('exposure'):
                    st.markdown(f"**Exposure:** {risk['exposure']:.2f}")
            
            st.markdown(f"**Categories:** {', '.join(risk.get('categories', []))}")
            
            if risk['status'] == "Contingent":
                st.markdown(f"**Condition:** {risk.get('activation_condition', 'N/A')}")
                st.markdown(f"**Decision:** {risk.get('activation_decision_date', 'N/A')}")
            
            st.markdown(f"**Owner:** {risk.get('owner', 'Not defined')}")
            
            if risk.get('description'):
                st.markdown(f"**Description:** {risk['description']}")
            
            col_edit, col_del = st.columns(2)
            
            with col_del:
                filter_mgr = st.session_state.get("filter_manager")
                active_scopes = filter_mgr.active_scopes if filter_mgr else []
                
                # If we are in a scoped view, default to "Remove from scope(s)" rather than global delete
                if active_scopes:
                    if st.button("➖ Remove from Scopes", key=f"rm_scope_{risk['id']}", use_container_width=True):
                        removed = False
                        for scope in filter_mgr.active_scopes:
                            if filter_mgr.remove_node_from_scope(scope.id, risk['id']):
                                removed = True
                        if removed:
                            st.success("Risk removed from active scopes")
                            st.rerun()
                    
                    st.markdown("<div style='text-align: center; font-size: 0.8em; color: gray;'>or</div>", unsafe_allow_html=True)
                    
                    if st.button("🗑️ Delete Globally", key=f"del_global_{risk['id']}", use_container_width=True, type="secondary"):
                        if delete_risk_fn(risk['id']):
                            st.success("Risk deleted from database")
                            st.rerun()
                else:
                    if st.button("🗑️ Delete", key=f"del_{risk['id']}", use_container_width=True):
                        if delete_risk_fn(risk['id']):
                            st.success("Risk deleted")
                            st.rerun()
