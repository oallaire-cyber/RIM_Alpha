"""
Dynamic Tab Generation - Schema-driven Streamlit tabs.

Generates tabs dynamically based on the schema's ui.tabs configuration.
"""

from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from core import get_registry, SchemaRegistry


def get_tab_config(registry: Optional[SchemaRegistry] = None) -> List[Dict[str, Any]]:
    """
    Get tab configuration from schema.
    
    Args:
        registry: SchemaRegistry instance (uses global if not provided)
        
    Returns:
        List of tab configuration dictionaries
    """
    reg = registry or get_registry()
    ui_config = reg.get_ui_config()
    tabs_config = ui_config.get("tabs", [])
    
    if not tabs_config:
        # Default tabs if not specified
        tabs_config = [
            {"id": "visualization", "label": "Visualization", "icon": "📊"},
            {"id": "risks", "label": "Risks", "entity_type": "risk", "icon": "🎯"},
            {"id": "mitigations", "label": "Mitigations", "entity_type": "mitigation", "icon": "🛡️"},
            {"id": "influences", "label": "Influences", "relationship_type": "influences", "icon": "🔗"},
        ]
    
    return tabs_config


def build_tabs(
    registry: Optional[SchemaRegistry] = None
) -> List[str]:
    """
    Build Streamlit tabs based on schema configuration.
    
    Args:
        registry: SchemaRegistry instance
        
    Returns:
        List of tab names for st.tabs()
    """
    config = get_tab_config(registry)
    return [f"{tab.get('icon', '📋')} {tab.get('label', tab.get('id'))}" for tab in config]


def get_tab_by_index(index: int, registry: Optional[SchemaRegistry] = None) -> Dict[str, Any]:
    """
    Get tab configuration by index.
    
    Args:
        index: Tab index
        registry: SchemaRegistry instance
        
    Returns:
        Tab configuration dictionary
    """
    config = get_tab_config(registry)
    if 0 <= index < len(config):
        return config[index]
    return {}


def render_dynamic_tabs(
    manager,
    tab_renderers: Dict[str, Callable[[Any, Dict[str, Any]], None]],
    registry: Optional[SchemaRegistry] = None
) -> None:
    """
    Render all tabs dynamically.
    
    Args:
        manager: RiskGraphManager instance
        tab_renderers: Dict mapping tab type -> render function
                      Example: {"visualization": render_viz_tab, "entity": render_entity_tab}
        registry: SchemaRegistry instance
    """
    reg = registry or get_registry()
    tab_config = get_tab_config(reg)
    tab_names = build_tabs(reg)
    
    tabs = st.tabs(tab_names)
    
    for idx, tab_obj in enumerate(tabs):
        config = tab_config[idx]
        tab_type = _determine_tab_type(config)
        
        with tab_obj:
            renderer = tab_renderers.get(tab_type)
            if renderer:
                renderer(manager, config)
            else:
                # Fallback: try to auto-render based on config
                _auto_render_tab(manager, config, reg)


def _determine_tab_type(config: Dict[str, Any]) -> str:
    """Determine the tab type from configuration."""
    tab_id = config.get("id", "")
    # Check for specific well-known tab IDs first
    if tab_id in ("visualization", "analysis", "import_export"):
        return tab_id
    if config.get("entity_type"):
        return "entity"
    if config.get("relationship_type"):
        return "relationship"
    # Fallback: use explicit type, then tab ID, then 'custom'
    return config.get("type", tab_id or "custom")


def _auto_render_tab(
    manager,
    config: Dict[str, Any],
    registry: SchemaRegistry
) -> None:
    """
    Auto-render a tab based on configuration.
    
    For entity types, shows a list with CRUD.
    For relationship types, shows relationships with CRUD.
    """
    tab_id = config.get("id", "")
    entity_type_id = config.get("entity_type")
    rel_type_id = config.get("relationship_type")
    
    if entity_type_id:
        _render_entity_tab_content(manager, entity_type_id, registry)
    elif rel_type_id:
        _render_relationship_tab_content(manager, rel_type_id, registry)
    else:
        st.info(f"No renderer for tab '{tab_id}'")


def _render_entity_tab_content(
    manager,
    entity_type_id: str,
    registry: SchemaRegistry
) -> None:
    """Render content for an entity type tab."""
    entity_type = registry.get_entity_type(entity_type_id)
    
    if not entity_type:
        st.warning(f"Entity type '{entity_type_id}' not found in schema")
        return
    
    st.subheader(f"{entity_type.emoji} {entity_type.label}s")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Search
        search = st.text_input(
            "🔍 Search",
            key=f"search_{entity_type_id}",
            placeholder=f"Search {entity_type.label.lower()}s..."
        )
    
    with col2:
        # Add button
        if st.button(f"➕ Add {entity_type.label}", key=f"add_{entity_type_id}"):
            st.session_state[f"show_add_form_{entity_type_id}"] = True
    
    # Add form (collapsible)
    if st.session_state.get(f"show_add_form_{entity_type_id}"):
        with st.expander(f"Add New {entity_type.label}", expanded=True):
            from ui.dynamic_forms import build_entity_form
            form_data = build_entity_form(
                entity_type,
                key_prefix=f"add_{entity_type_id}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", key=f"save_add_{entity_type_id}"):
                    try:
                        # Use generic create
                        manager.create_entity(entity_type_id, form_data)
                        st.success(f"{entity_type.label} created!")
                        st.session_state[f"show_add_form_{entity_type_id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col2:
                if st.button("❌ Cancel", key=f"cancel_add_{entity_type_id}"):
                    st.session_state[f"show_add_form_{entity_type_id}"] = False
                    st.rerun()
    
    st.markdown("---")
    
    # Entity list
    try:
        if hasattr(manager, "get_entities"):
            entities = manager.get_entities(entity_type_id)
        else:
            # Fallback for older manager
            if entity_type_id == "risk":
                entities = manager.get_all_risks()
            elif entity_type_id == "mitigation":
                entities = manager.get_all_mitigations()
            elif entity_type_id == "tpo":
                entities = manager.get_all_tpos()
            else:
                entities = []
        
        # Filter by search
        if search:
            search_lower = search.lower()
            entities = [
                e for e in entities
                if search_lower in str(e.get("name", "")).lower()
                or search_lower in str(e.get("description", "")).lower()
            ]
        
        if not entities:
            st.info(f"No {entity_type.label.lower()}s found")
        else:
            from ui.components import render_pagination
            start_idx, end_idx = render_pagination(len(entities), 20, f"entities_{entity_type_id}")
            paginated_entities = entities[start_idx:end_idx]
            
            for entity in paginated_entities:
                _render_entity_card(entity, entity_type, manager)
    
    except Exception as e:
        st.error(f"Error loading {entity_type.label.lower()}s: {e}")


def _render_entity_card(
    entity: Dict[str, Any],
    entity_type,
    manager
) -> None:
    """Render a single entity as an expandable card."""
    name = entity.get("name", "Unnamed")
    entity_id = entity.get("id", "")
    
    with st.expander(f"{entity_type.emoji} **{name}**"):
        # Display key attributes
        for key, value in entity.items():
            if key in ("id", "_element_id", "name"):
                continue
            if value:
                display_key = key.replace("_", " ").title()
                st.write(f"**{display_key}:** {value}")
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit", key=f"edit_{entity_id}"):
                st.session_state[f"editing_{entity_id}"] = True
        
        with col2:
            if st.button("🗑️ Delete", key=f"delete_{entity_id}"):
                if hasattr(manager, "delete_entity"):
                    manager.delete_entity(entity_type.id, entity_id)
                st.success("Deleted!")
                st.rerun()


def _render_relationship_tab_content(
    manager,
    rel_type_id: str,
    registry: SchemaRegistry
) -> None:
    """Render content for a relationship type tab."""
    rel_type = registry.get_relationship_type(rel_type_id)
    
    if not rel_type:
        st.warning(f"Relationship type '{rel_type_id}' not found in schema")
        return
    
    st.subheader(f"🔗 {rel_type.label}")
    
    # Add button
    if st.button(f"➕ Add {rel_type.label}", key=f"add_{rel_type_id}"):
        st.session_state[f"show_add_form_{rel_type_id}"] = True
    
    st.markdown("---")
    
    # Relationship list
    try:
        if hasattr(manager, "get_relationships"):
            relationships = manager.get_relationships(rel_type_id)
        else:
            # Fallback
            if rel_type_id == "influences":
                relationships = manager.get_all_influences()
            elif rel_type_id == "mitigates":
                relationships = manager.get_all_mitigates() if hasattr(manager, "get_all_mitigates") else []
            else:
                relationships = []
        
        if not relationships:
            st.info(f"No {rel_type.label.lower()} relationships found")
        else:
            from ui.components import render_pagination
            start_idx, end_idx = render_pagination(len(relationships), 20, f"rels_{rel_type_id}")
            paginated_relationships = relationships[start_idx:end_idx]
            
            for rel in paginated_relationships:
                _render_relationship_card(rel, rel_type, manager)
    
    except Exception as e:
        st.error(f"Error loading {rel_type.label.lower()}: {e}")


def _render_relationship_card(
    rel: Dict[str, Any],
    rel_type,
    manager
) -> None:
    """Render a single relationship as an expandable card."""
    source = rel.get("_source", {})
    target = rel.get("_target", {})
    source_name = source.get("name", rel.get("source_id", "?")[:8])
    target_name = target.get("name", rel.get("target_id", "?")[:8])
    rel_id = rel.get("id", "")
    
    with st.expander(f"**{source_name}** → **{target_name}**"):
        for key, value in rel.items():
            if key.startswith("_") or key in ("id", "source_id", "target_id"):
                continue
            if value:
                display_key = key.replace("_", " ").title()
                st.write(f"**{display_key}:** {value}")
        
        if st.button("🗑️ Delete", key=f"delete_rel_{rel_id}"):
            if hasattr(manager, "delete_relationship"):
                manager.delete_relationship(rel_type.id, rel_id)
            st.success("Deleted!")
            st.rerun()
