"""
Risk Mitigations Tab for RIM Application.

Provides interface for linking mitigations to risks with effectiveness ratings.
"""

from typing import Dict, Any, Optional, Callable, List
from config.settings import MITIGATION_EFFECTIVENESS


def render_risk_mitigations_tab(
    get_all_risks_fn: Callable[[], List[Dict]],
    get_all_mitigations_fn: Callable[[], List[Dict]],
    get_all_mitigates_fn: Callable[[], List[Dict]],
    create_mitigates_fn: Callable[..., bool],
    delete_mitigates_fn: Callable[[str], bool]
):
    """
    Render the Risk Mitigations (links) management tab.
    
    Args:
        get_all_risks_fn: Function to get all risks
        get_all_mitigations_fn: Function to get all mitigations
        get_all_mitigates_fn: Function to get all mitigates relationships
        create_mitigates_fn: Function to create a new mitigates relationship
        delete_mitigates_fn: Function to delete a mitigates relationship
    """
    import streamlit as st
    
    col_form, col_list = st.columns([1, 1])
    
    # Get available mitigations and risks
    mitigations = get_all_mitigations_fn()
    mitigation_options = {f"🛡️ {m['name']} [{m.get('type', 'N/A')}]": m['id'] for m in mitigations}
    
    risks = get_all_risks_fn()
    risk_options = {f"{r['name']} [{r['level']}]": r['id'] for r in risks}
    
    with col_form:
        _render_mitigates_form(mitigation_options, risk_options, create_mitigates_fn)
    
    with col_list:
        _render_mitigates_list(get_all_mitigates_fn, delete_mitigates_fn)


def _render_mitigates_form(
    mitigation_options: Dict[str, str],
    risk_options: Dict[str, str],
    create_mitigates_fn: Callable[..., bool]
):
    """Render the mitigates relationship creation form."""
    import streamlit as st
    
    st.markdown("### ➕ Link Mitigation to Risk")
    st.markdown("*Define how a mitigation addresses a risk*")
    
    if len(mitigation_options) == 0:
        st.warning("You need at least 1 mitigation to create a link.")
        return
    
    if len(risk_options) == 0:
        st.warning("You need at least 1 risk to create a link.")
        return
    
    with st.form("create_mitigates_form", clear_on_submit=True):
        mitigation_name = st.selectbox("Mitigation", list(mitigation_options.keys()))
        risk_name = st.selectbox("Risk to mitigate", list(risk_options.keys()))
        
        effectiveness = st.selectbox(
            "Effectiveness",
            MITIGATION_EFFECTIVENESS,
            index=1,  # Default to Medium
            help="How effective is this mitigation against this risk?"
        )
        
        rel_description = st.text_area(
            "Description",
            placeholder="Describe how this mitigation addresses the risk..."
        )
        
        submitted = st.form_submit_button("Create Link", type="primary", use_container_width=True)
        
        if submitted:
            mitigation_id = mitigation_options[mitigation_name]
            risk_id = risk_options[risk_name]
            
            success = create_mitigates_fn(
                mitigation_id=mitigation_id,
                risk_id=risk_id,
                effectiveness=effectiveness,
                description=rel_description
            )
            if success:
                st.success("Mitigation link created!")
                st.rerun()


def _render_mitigates_list(
    get_all_mitigates_fn: Callable[[], List[Dict]],
    delete_mitigates_fn: Callable[[str], bool]
):
    """Render the existing mitigates relationships list."""
    import streamlit as st
    
    st.markdown("### 📋 Existing Mitigation Links")
    
    mitigates_rels = get_all_mitigates_fn()
    
    if not mitigates_rels:
        st.info("No mitigation links created.")
        return
    
    effectiveness_icons = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢"
    }
    
    for rel in mitigates_rels:
        eff_icon = effectiveness_icons.get(rel['effectiveness'], "⚪")
        
        with st.expander(f"{eff_icon} {rel['mitigation_name']} → {rel['risk_name']}"):
            st.markdown(f"**Mitigation:** {rel['mitigation_name']} ({rel.get('mitigation_type', 'N/A')})")
            st.markdown(f"**Risk:** {rel['risk_name']} ({rel.get('risk_level', 'N/A')})")
            st.markdown(f"**Effectiveness:** {rel['effectiveness']}")
            
            if rel.get('description'):
                st.markdown(f"**Description:** {rel['description']}")
            
            if st.button("🗑️ Delete", key=f"del_mit_rel_{rel['id']}", use_container_width=True):
                if delete_mitigates_fn(rel['id']):
                    st.success("Mitigation link deleted")
                    st.rerun()
