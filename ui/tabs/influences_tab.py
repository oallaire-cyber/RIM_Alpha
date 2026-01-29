"""
Influences Tab for RIM Application.

Provides influence relationship creation and management interface.
"""

from typing import Dict, Any, Optional, Callable, List
from config.settings import INFLUENCE_STRENGTHS


def render_influences_tab(
    get_all_risks_fn: Callable[[], List[Dict]],
    get_all_influences_fn: Callable[[], List[Dict]],
    create_influence_fn: Callable[..., bool],
    delete_influence_fn: Callable[[str], bool]
):
    """
    Render the Influences management tab.
    
    Args:
        get_all_risks_fn: Function to get all risks
        get_all_influences_fn: Function to get all influences
        create_influence_fn: Function to create a new influence
        delete_influence_fn: Function to delete an influence
    """
    import streamlit as st
    
    col_form, col_list = st.columns([1, 1])
    
    risks = get_all_risks_fn()
    risk_options = {f"{r['name']} [{r['level']}]": r['id'] for r in risks}
    
    with col_form:
        _render_influence_form(risk_options, create_influence_fn)
    
    with col_list:
        _render_influence_list(get_all_influences_fn, delete_influence_fn)


def _render_influence_form(
    risk_options: Dict[str, str],
    create_influence_fn: Callable[..., bool]
):
    """Render the influence creation form."""
    import streamlit as st
    
    st.markdown("### ➕ Create an Influence")
    
    if len(risk_options) < 2:
        st.warning("You need at least 2 risks to create an influence.")
        return
    
    with st.form("create_influence_form", clear_on_submit=True):
        source_name = st.selectbox("Source risk", list(risk_options.keys()))
        target_name = st.selectbox(
            "Target risk",
            [n for n in risk_options.keys() if n != source_name]
        )
        
        st.info("ℹ️ The influence type (Level 1/2/3) is determined automatically based on source/target levels")
        
        strength = st.selectbox("Influence strength", INFLUENCE_STRENGTHS)
        
        confidence = st.slider("Confidence level", 0.0, 1.0, 0.8, 0.1)
        
        description = st.text_area(
            "Description",
            placeholder="Describe how this risk influences the other..."
        )
        
        submitted = st.form_submit_button("Create influence", type="primary", use_container_width=True)
        
        if submitted:
            source_id = risk_options[source_name]
            target_id = risk_options[target_name]
            
            success = create_influence_fn(
                source_id=source_id,
                target_id=target_id,
                influence_type="",  # Auto-determined
                strength=strength,
                description=description,
                confidence=confidence
            )
            if success:
                st.success("Influence created!")
                st.rerun()


def _render_influence_list(
    get_all_influences_fn: Callable[[], List[Dict]],
    delete_influence_fn: Callable[[str], bool]
):
    """Render the existing influences list."""
    import streamlit as st
    
    st.markdown("### 📋 Existing Influences")
    
    influences = get_all_influences_fn()
    
    if not influences:
        st.info("No influences created.")
        return
    
    for inf in influences:
        # Type emoji based on influence level
        inf_type = inf.get('influence_type', '')
        if "Level1" in inf_type:
            type_emoji = "🔴"
        elif "Level2" in inf_type:
            type_emoji = "🟣"
        else:
            type_emoji = "🔵"
        
        with st.expander(f"{type_emoji} {inf['source_name']} → {inf['target_name']}"):
            st.markdown(f"**Type:** {inf['influence_type']}")
            st.markdown(f"**Strength:** {inf['strength']}")
            st.markdown(f"**Confidence:** {inf['confidence']:.0%}")
            
            if inf.get('description'):
                st.markdown(f"**Description:** {inf['description']}")
            
            if st.button("🗑️ Delete", key=f"del_inf_{inf['id']}", use_container_width=True):
                if delete_influence_fn(inf['id']):
                    st.success("Influence deleted")
                    st.rerun()
