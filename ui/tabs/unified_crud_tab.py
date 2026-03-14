"""
Unified CRUD Management Tab.

Provides a completely generic schema-driven UI to manage any 
Context Nodes, Kernel Nodes (Risks, Mitigations), and Edges.
"""

import streamlit as st
from typing import Optional, Dict, Any, List, Union
from core import get_registry, EntityTypeDefinition, RelationshipTypeDefinition
from database import RiskGraphManager
from ui.dynamic_forms import build_entity_form, build_relationship_form
from ui.components import render_pagination
from config.settings import get_active_schema, get_active_schema_name
from config.schema_loader import save_schema


def render_unified_crud_tab(manager: RiskGraphManager, definition: Union[EntityTypeDefinition, RelationshipTypeDefinition]):
    """
    Render a dynamic CRUD manager for a given entity or relationship definition.
    Abstracts entirely whether it's a kernel type or a generic context type.
    """
    registry = get_registry()
    is_node = isinstance(definition, EntityTypeDefinition)
    type_id = definition.id
    
    st.subheader(f"Manage {definition.label}s")
    
    # Check Active Scope (only really relevant for Nodes right now)
    filter_mgr = st.session_state.get("filter_manager")
    active_scopes = filter_mgr.active_scopes if filter_mgr else None
    
    if is_node and active_scopes:
        st.info(f"📍 **Scope Active:** Displayed {definition.label.lower()}s are limited to the active scope.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search", key=f"search_{type_id}", placeholder=f"Search {definition.label.lower()}s...")
    with col2:
        if st.button(f"➕ New {definition.label}", use_container_width=True, key=f"btn_new_{type_id}"):
            st.session_state[f"show_add_{type_id}"] = True
            
    # --- ADD FORM ---
    if st.session_state.get(f"show_add_{type_id}"):
        with st.expander(f"Create New {definition.label}", expanded=True):
            if is_node:
                form_data = build_entity_form(definition, key_prefix=f"add_{type_id}")
            else:
                # Gather potential sources and targets for edges
                source_entities = _get_entities_by_types(manager, registry, definition.from_entity_types)
                target_entities = _get_entities_by_types(manager, registry, definition.to_entity_types)
                
                if not source_entities or not target_entities:
                    st.warning("Cannot manage relationships: Missing potential source or target nodes.")
                    form_data = None
                else:
                    form_data = build_relationship_form(
                        definition, source_entities, target_entities, key_prefix=f"add_{type_id}"
                    )
            
            if form_data is not None:
                # Scope awareness flag
                add_to_scope = False
                if is_node and active_scopes:
                    add_to_scope = st.checkbox("➕ Add to active scope upon creation", value=True, key=f"chk_scope_{type_id}")
                    
                cols = st.columns(2)
                with cols[0]:
                    if st.button("💾 Save", key=f"save_new_{type_id}"):
                        try:
                            if is_node:
                                new_item = manager.create_unified_entity(type_id, form_data)
                                
                                # Add to scope logic — use FilterManager so both the
                                # in-memory active_scopes AND the YAML file are updated.
                                if active_scopes and add_to_scope and new_item and "id" in new_item:
                                    if filter_mgr:
                                        filter_mgr.add_node_to_scope(
                                            active_scopes[0].id, new_item["id"]
                                        )
                                    else:
                                        _add_node_to_scope(new_item["id"], active_scopes[0].id)
                            else:
                                sid = form_data.pop("source_id", None)
                                tid = form_data.pop("target_id", None)
                                if not sid or not tid:
                                    st.error("Source and Target are required.")
                                    return
                                    
                                # Look up the specific types for the edge
                                s_type_id = _get_entity_type_id_from_id(manager, registry, definition.from_entity_types, sid)
                                t_type_id = _get_entity_type_id_from_id(manager, registry, definition.to_entity_types, tid)
                                
                                manager.create_unified_relationship(
                                    type_id, sid, tid, s_type_id, t_type_id, form_data
                                )
                                
                            st.success(f"{definition.label} created!")
                            st.session_state[f"show_add_{type_id}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating: {e}")
                with cols[1]:
                    if st.button("❌ Cancel", key=f"cancel_new_{type_id}"):
                        st.session_state[f"show_add_{type_id}"] = False
                        st.rerun()
                    
    st.markdown("---")
    
    # --- LIST VIEW ---
    try:
        if is_node:
            items = manager.get_unified_entities(type_id)
            
            # Apply scope filtering
            if active_scopes:
                scope_ids = set()
                for s in active_scopes:
                    scope_ids.update(s.node_ids)
                items = [n for n in items if n.get("id") in scope_ids]
        else:
            items = manager.get_unified_relationships(type_id)

            # Apply scope filtering for edges: only show edges where at least one
            # endpoint belongs to the active scope node set.
            if active_scopes:
                _scope_ids = set()
                for _s in active_scopes:
                    _scope_ids.update(_s.node_ids)
                items = [
                    i for i in items
                    if i.get("source_id") in _scope_ids or i.get("target_id") in _scope_ids
                ]

            # Fetch resolving dictionaries for display names
            source_entities = _get_entities_by_types(manager, registry, definition.from_entity_types)
            target_entities = _get_entities_by_types(manager, registry, definition.to_entity_types)
            s_map = {e["id"]: e.get("name", e["id"]) for e in source_entities}
            t_map = {e["id"]: e.get("name", e["id"]) for e in target_entities}
            
        # Apply search
        if search:
            search_low = search.lower()
            items = [
                i for i in items 
                if search_low in str(i.get("name", "")).lower() 
                or search_low in str(i.get("description", "")).lower()
            ]
            
        if not items:
            st.info(f"No {definition.label.lower()}s found.")
            return
            
        start_idx, end_idx = render_pagination(len(items), 20, f"list_{type_id}")
        
        for item in items[start_idx:end_idx]:
            if is_node:
                _render_node_card(manager, item, definition, active_scopes)
            else:
                _render_edge_card(manager, item, definition, s_map, t_map)
            
    except Exception as e:
        st.error(f"Error loading {definition.label.lower()}s: {e}")


def _render_node_card(manager: RiskGraphManager, node: Dict, definition: EntityTypeDefinition, active_scopes: List):
    """Render an individual node CRUD card."""
    node_id = node.get("id", "")
    name = node.get("name", "Unnamed")
    emoji = getattr(definition, "emoji", "📦")
    
    with st.expander(f"{emoji} **{name}**"):
        if st.session_state.get(f"edit_{definition.id}_{node_id}"):
            # Edit Mode
            st.markdown("### Edit Mode")
            edited_data = build_entity_form(definition, node, key_prefix=f"edit_form_{definition.id}_{node_id}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Save Changes", key=f"save_{definition.id}_{node_id}"):
                    try:
                        manager.update_unified_entity(definition.id, node_id, edited_data)
                        st.success("Updated!")
                        st.session_state[f"edit_{definition.id}_{node_id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with c2:
                if st.button("❌ Cancel", key=f"cancel_{definition.id}_{node_id}"):
                    st.session_state[f"edit_{definition.id}_{node_id}"] = False
                    st.rerun()
        else:
            # View Mode
            for k, v in node.items():
                if k in ("id", "_element_id", "name") or not v:
                    continue
                display_k = k.replace("_", " ").title()
                st.markdown(f"**{display_k}:** {v}")
                
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("✏️ Edit", key=f"btn_edit_{definition.id}_{node_id}"):
                    st.session_state[f"edit_{definition.id}_{node_id}"] = True
                    st.rerun()
            with c2:
                # Scope logic: if active scope, offer "Remove from scope" instead of pure "Delete"
                if active_scopes:
                    if st.button("📤 Remove from Scope", key=f"btn_rem_scope_{definition.id}_{node_id}"):
                        fm = st.session_state.get("filter_manager")
                        scope_id = active_scopes[0].id
                        if node_id in active_scopes[0].node_ids:
                            active_scopes[0].node_ids.remove(node_id)
                            _remove_node_from_scope(node_id, scope_id)
                            st.success("Removed from scope.")
                            st.rerun()
                else:
                    st.empty()
            with c3:
                # Global delete requires confirmation or clear text
                if st.button("🗑️ Delete Globally", key=f"btn_del_{definition.id}_{node_id}"):
                    manager.delete_unified_entity(definition.id, node_id)
                    st.success("Deleted from database.")
                    st.rerun()


def _render_edge_card(manager: RiskGraphManager, edge: Dict, definition: RelationshipTypeDefinition, s_map: dict, t_map: dict):
    """Render an individual edge CRUD card."""
    # Handle different ID names returned by different queries (id vs relationship_id)
    edge_id = edge.get("id") or edge.get("relationship_id") or edge.get("_element_id", "")
    source_id = edge.get("source_id", "")
    target_id = edge.get("target_id", "")
    
    s_name = s_map.get(source_id, source_id)
    t_name = t_map.get(target_id, target_id)
    
    label = f"🔗 {s_name} ➔ {t_name}"
    
    with st.expander(label):
        if st.session_state.get(f"edit_{definition.id}_{edge_id}"):
            # Edit Mode
            st.markdown("### Edit Mode")
            edited_data = build_relationship_form(
                definition, [], [], key_prefix=f"edit_form_{definition.id}_{edge_id}", default_values=edge, is_edit=True
            )
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Save Changes", key=f"save_{definition.id}_{edge_id}"):
                    try:
                        manager.update_unified_relationship(definition.id, edge_id, edited_data)
                        st.success("Updated!")
                        st.session_state[f"edit_{definition.id}_{edge_id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with c2:
                if st.button("❌ Cancel", key=f"cancel_{definition.id}_{edge_id}"):
                    st.session_state[f"edit_{definition.id}_{edge_id}"] = False
                    st.rerun()
        else:
            # View Mode
            for k, v in edge.items():
                if k in ("id", "relationship_id", "_element_id", "source_id", "target_id") or not v:
                    continue
                display_k = k.replace("_", " ").title()
                st.markdown(f"**{display_k}:** {v}")
                
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Edit", key=f"btn_edit_{definition.id}_{edge_id}"):
                    st.session_state[f"edit_{definition.id}_{edge_id}"] = True
                    st.rerun()
            with c2:
                if st.button("🗑️ Delete Globally", key=f"btn_del_{definition.id}_{edge_id}"):
                    manager.delete_unified_relationship(definition.id, edge_id)
                    st.success("Deleted from database.")
                    st.rerun()


# --- HELPER FUNCTIONS ---

def _get_entities_by_types(manager: RiskGraphManager, registry, type_ids: List[str]) -> List[Dict]:
    """Helper to fetch entities of multiple types for dropdowns."""
    entities = []
    for tid in type_ids:
        try:
            items = manager.get_unified_entities(tid)
            # Add type marker to help routing
            for x in items:
                x["_entity_type_id"] = tid
            entities.extend(items)
        except Exception:
            pass
    return entities


def _get_entity_type_id_from_id(manager: RiskGraphManager, registry, type_ids: List[str], entity_id: str) -> Optional[str]:
    """Helper to figure out the schema type of a node just from its UUID by checking the lists."""
    for tid in type_ids:
        try:
            items = manager.get_unified_entities(tid)
            if any(x.get("id") == entity_id for x in items):
                return tid
        except Exception:
            pass
    return None


def _add_node_to_scope(node_id: str, scope_id: str):
    """Helper to update the schema scope persistently."""
    schema = get_active_schema()
    for s in schema.scopes:
        if s.id == scope_id and node_id not in s.node_ids:
            s.node_ids.append(node_id)
            break
    save_schema(schema, get_active_schema_name())

def _remove_node_from_scope(node_id: str, scope_id: str):
    """Helper to update the schema scope persistently."""
    schema = get_active_schema()
    for s in schema.scopes:
        if s.id == scope_id and node_id in s.node_ids:
            s.node_ids.remove(node_id)
            break
    save_schema(schema, get_active_schema_name())
