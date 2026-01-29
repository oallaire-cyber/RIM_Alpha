"""
TPO Impacts Tab for RIM Application.

Provides TPO impact relationship creation and management interface.
Links Strategic Risks to Top Program Objectives.
"""

from typing import Dict, Any, Optional, Callable, List
from config.settings import IMPACT_LEVELS


def render_tpo_impacts_tab(
    get_all_risks_fn: Callable[[], List[Dict]],
    get_all_tpos_fn: Callable[[], List[Dict]],
    get_all_tpo_impacts_fn: Callable[[], List[Dict]],
    create_tpo_impact_fn: Callable[..., bool],
    delete_tpo_impact_fn: Callable[[str], bool]
):
    """
    Render the TPO Impacts management tab.
    
    Args:
        get_all_risks_fn: Function to get all risks
        get_all_tpos_fn: Function to get all TPOs
        get_all_tpo_impacts_fn: Function to get all TPO impacts
        create_tpo_impact_fn: Function to create a new TPO impact
        delete_tpo_impact_fn: Function to delete a TPO impact
    """
    import streamlit as st
    
    col_form, col_list = st.columns([1, 1])
    
    # Get strategic risks and TPOs
    all_risks = get_all_risks_fn()
    strategic_risks = [r for r in all_risks if r['level'] == 'Strategic']
    strategic_options = {f"{r['name']}": r['id'] for r in strategic_risks}
    
    tpos = get_all_tpos_fn()
    tpo_options = {f"{t['reference']}: {t['name']}": t['id'] for t in tpos}
    
    with col_form:
        _render_tpo_impact_form(strategic_options, tpo_options, create_tpo_impact_fn)
    
    with col_list:
        _render_tpo_impact_list(get_all_tpo_impacts_fn, delete_tpo_impact_fn)


def _render_tpo_impact_form(
    strategic_options: Dict[str, str],
    tpo_options: Dict[str, str],
    create_tpo_impact_fn: Callable[..., bool]
):
    """Render the TPO impact creation form."""
    import streamlit as st
    
    st.markdown("### ➕ Create a TPO Impact")
    st.markdown("*Link a Strategic Risk to a Top Program Objective*")
    
    if len(strategic_options) == 0:
        st.warning("You need at least 1 Strategic risk to create a TPO impact.")
        return
    
    if len(tpo_options) == 0:
        st.warning("You need at least 1 TPO to create a TPO impact.")
        return
    
    with st.form("create_tpo_impact_form", clear_on_submit=True):
        risk_name = st.selectbox("Strategic Risk", list(strategic_options.keys()))
        tpo_name = st.selectbox("Target TPO", list(tpo_options.keys()))
        
        impact_level = st.selectbox(
            "Impact Level",
            IMPACT_LEVELS,
            index=1  # Default to Medium
        )
        
        description = st.text_area(
            "Description",
            placeholder="Describe how this risk impacts the TPO..."
        )
        
        submitted = st.form_submit_button("Create TPO Impact", type="primary", use_container_width=True)
        
        if submitted:
            risk_id = strategic_options[risk_name]
            tpo_id = tpo_options[tpo_name]
            
            success = create_tpo_impact_fn(
                risk_id=risk_id,
                tpo_id=tpo_id,
                impact_level=impact_level,
                description=description
            )
            if success:
                st.success("TPO Impact created!")
                st.rerun()


def _render_tpo_impact_list(
    get_all_tpo_impacts_fn: Callable[[], List[Dict]],
    delete_tpo_impact_fn: Callable[[str], bool]
):
    """Render the existing TPO impacts list."""
    import streamlit as st
    
    st.markdown("### 📋 Existing TPO Impacts")
    
    impacts = get_all_tpo_impacts_fn()
    
    if not impacts:
        st.info("No TPO impacts created.")
        return
    
    level_colors = {
        "Low": "🟢",
        "Medium": "🟡",
        "High": "🟠",
        "Critical": "🔴"
    }
    
    for imp in impacts:
        emoji = level_colors.get(imp['impact_level'], "⚪")
        
        with st.expander(f"{emoji} {imp['risk_name']} → {imp['tpo_reference']}"):
            st.markdown(f"**Risk:** {imp['risk_name']}")
            st.markdown(f"**TPO:** {imp['tpo_reference']}: {imp['tpo_name']}")
            st.markdown(f"**Impact Level:** {imp['impact_level']}")
            
            if imp.get('description'):
                st.markdown(f"**Description:** {imp['description']}")
            
            if st.button("🗑️ Delete", key=f"del_tpo_imp_{imp['id']}", use_container_width=True):
                if delete_tpo_impact_fn(imp['id']):
                    st.success("TPO Impact deleted")
                    st.rerun()
