"""
Reusable entity editor panel for seamless in-place modifications.
"""
import streamlit as st
from typing import Optional, Dict

from core import get_registry
from database import RiskGraphManager
from ui.dynamic_forms import build_entity_form

def get_entity_type_id(manager: RiskGraphManager, entity_id: str) -> Optional[str]:
    """Dynamically determine the schema type ID of a given node UUID."""
    if not manager._connection:
        return None
    
    # Check if we have the result cached in session state (e.g. from get_influence_network)
    # But usually doing a quick DB query is fine since it's just one node
    try:
        result = manager._connection.execute_query(
            "MATCH (n {id: $id}) RETURN labels(n)[0] as label, n.node_type as node_type",
            {"id": entity_id}
        )
        if not result:
            return None
            
        label = result[0]["label"]
        if label == "ContextNode":
            return result[0]["node_type"]
        else:
            # Schema uses lowercase for core entities: 'risk', 'tpo', 'mitigation'
            return label.lower()
    except Exception as e:
        st.error(f"Error determining entity type: {e}")
        return None

def render_inline_editor(manager: RiskGraphManager, entity_id: str, key_prefix: str = "inline_editor"):
    """
    Render a view of a node with an 'Edit' button that opens an inline form.
    """
    type_id = get_entity_type_id(manager, entity_id)
    if not type_id:
        st.warning(f"Could not determine entity type for ID: {entity_id} (or it does not exist)")
        return

    registry = get_registry()
    definition = registry.get_entity_type(type_id)
    if not definition:
        st.warning(f"Unknown schema type: {type_id}")
        return

    entity_data = manager.get_entity_by_id(type_id, entity_id)
    if not entity_data:
        st.warning("Entity not found in database.")
        return

    name = entity_data.get("name", "Unnamed")
    emoji = getattr(definition, "emoji", "📦")
    
    edit_state_key = f"edit_mode_{key_prefix}_{entity_id}"
    
    with st.expander(f"📝 {emoji} {name} (Properties)", expanded=True):
        if st.session_state.get(edit_state_key):
            st.markdown("### Edit Mode")
            edited_data = build_entity_form(definition, entity_data, key_prefix=f"form_{key_prefix}_{entity_id}", is_edit=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Save Changes", key=f"save_{key_prefix}_{entity_id}", type="primary"):
                    try:
                        manager.update_unified_entity(type_id, entity_id, edited_data)
                        st.success("Updated successfully!")
                        st.session_state[edit_state_key] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update: {e}")
            with c2:
                if st.button("❌ Cancel", key=f"cancel_{key_prefix}_{entity_id}"):
                    st.session_state[edit_state_key] = False
                    st.rerun()
        else:
            # View Mode
            st.markdown("### View Mode")
            
            # Show properties in a nice format
            for k, v in entity_data.items():
                # Skip internal fields
                if k in ("id", "_element_id", "name", "node_type") or not v:
                    continue
                display_k = k.replace("_", " ").title()
                st.markdown(f"**{display_k}:** {v}")
                
            st.markdown("---")
            if st.button("✏️ Edit Entity", key=f"btn_edit_{key_prefix}_{entity_id}"):
                st.session_state[edit_state_key] = True
                st.rerun()
