"""
Context Data Management Tab.

Provides schema-driven UI to manage generic Context Nodes 
and Context Edges, matching exactly how risks and influences are managed.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from core import get_registry, EntityTypeDefinition, RelationshipTypeDefinition
from database import RiskGraphManager
from ui.dynamic_forms import build_entity_form, build_relationship_form
from ui.components import render_pagination


def render_context_data_tab(manager: RiskGraphManager):
    """Render the contextual data management tab."""
    st.markdown("## 🧩 Context Data Management")
    st.markdown(
        "Manage domain-specific context nodes and their relationships. "
        "These elements provide context but do not computationally affect risk exposure paths."
    )
    
    registry = get_registry()
    context_node_types = registry.get_context_node_types()
    context_edge_types = registry.get_additional_relationship_types()
    
    if not context_node_types and not context_edge_types:
        st.info("No context nodes or edges defined in the current schema.")
        return
        
    # Build options for selector
    options = []
    
    # 1. Add context nodes
    for nid, node_def in context_node_types.items():
        options.append({
            "id": nid,
            "type": "node",
            "label": f"{node_def.emoji} {node_def.label} (Node)",
            "def": node_def
        })
        
    # 2. Add context edges
    for eid, edge_def in context_edge_types.items():
        options.append({
            "id": eid,
            "type": "edge",
            "label": f"🔗 {edge_def.label} (Edge)",
            "def": edge_def
        })
        
    if not options:
        return
        
    # Type Selector
    selected_option_idx = st.selectbox(
        "Select Type to Manage",
        range(len(options)),
        format_func=lambda i: options[i]["label"]
    )
    
    selected_option = options[selected_option_idx]
    st.markdown("---")
    
    if selected_option["type"] == "node":
        _render_context_node_manager(manager, selected_option["def"])
    else:
        _render_context_edge_manager(manager, selected_option["def"], registry)


def _render_context_node_manager(manager: RiskGraphManager, node_def: EntityTypeDefinition):
    """Render the manager for a specific context node type."""
    st.subheader(f"Manage {node_def.label}s")
    
    # Check Active Scope
    filter_mgr = st.session_state.get("filter_manager")
    active_scopes = filter_mgr.active_scopes if filter_mgr else None
    
    if active_scopes:
        st.info(f"📍 **Scope Active:** Displayed {node_def.label.lower()}s are limited to the active scope.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search", key=f"search_cn_{node_def.id}", placeholder=f"Search {node_def.label.lower()}s...")
    with col2:
        if st.button(f"➕ New {node_def.label}", use_container_width=True):
            st.session_state[f"show_add_cn_{node_def.id}"] = True
            
    # Add Form
    if st.session_state.get(f"show_add_cn_{node_def.id}"):
        with st.expander(f"Create New {node_def.label}", expanded=True):
            form_data = build_entity_form(node_def, key_prefix=f"add_cn_{node_def.id}")
            
            # Scope awareness flag
            add_to_scope = False
            if active_scopes:
                add_to_scope = st.checkbox("➕ Add to active scope upon creation", value=True)
                
            cols = st.columns(2)
            with cols[0]:
                if st.button("💾 Save Node"):
                    try:
                        new_node = manager.create_generic_entity(node_def, form_data)
                        
                        # Add to scope logic
                        if active_scopes and add_to_scope and new_node:
                            # Modify scope config
                            scope_config = active_scopes[0]  # Take first for now
                            if "id" in new_node:
                                scope_config.node_ids.append(new_node["id"])
                                filter_mgr.save_scope(scope_config)
                                
                        st.success(f"{node_def.label} created!")
                        st.session_state[f"show_add_cn_{node_def.id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating node: {e}")
            with cols[1]:
                if st.button("❌ Cancel"):
                    st.session_state[f"show_add_cn_{node_def.id}"] = False
                    st.rerun()
                    
    st.markdown("---")
    
    # List Existing Nodes
    try:
        nodes = manager.get_generic_entities(node_def)
        
        # Apply scope filtering
        if active_scopes:
            scope_ids = set()
            for s in active_scopes:
                scope_ids.update(s.node_ids)
            nodes = [n for n in nodes if n.get("id") in scope_ids]
            
        # Apply search
        if search:
            search_low = search.lower()
            nodes = [
                n for n in nodes 
                if search_low in str(n.get("name", "")).lower() 
                or search_low in str(n.get("description", "")).lower()
            ]
            
        if not nodes:
            st.info(f"No {node_def.label.lower()}s found.")
            return
            
        start_idx, end_idx = render_pagination(len(nodes), 20, f"cn_list_{node_def.id}")
        
        for node in nodes[start_idx:end_idx]:
            _render_context_node_card(manager, node, node_def, active_scopes)
            
    except Exception as e:
        st.error(f"Error loading {node_def.label.lower()}s: {e}")


def _render_context_node_card(manager: RiskGraphManager, node: Dict, node_def: EntityTypeDefinition, active_scopes: List):
    """Render an individual context node card."""
    node_id = node.get("id", "")
    name = node.get("name", "Unnamed")
    
    with st.expander(f"{node_def.emoji} **{name}**"):
        if st.session_state.get(f"edit_cn_{node_id}"):
            # Edit Mode
            st.markdown("### Edit Mode")
            edited_data = build_entity_form(node_def, node, key_prefix=f"edit_form_{node_id}")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Setup Changes", key=f"save_cn_{node_id}"):
                    try:
                        manager.update_generic_entity(node_def, node_id, edited_data)
                        st.success("Updated!")
                        st.session_state[f"edit_cn_{node_id}"] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with c2:
                if st.button("❌ Cancel Cancel", key=f"cancel_cn_{node_id}"):
                    st.session_state[f"edit_cn_{node_id}"] = False
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
                if st.button("✏️ Edit", key=f"btn_edit_{node_id}"):
                    st.session_state[f"edit_cn_{node_id}"] = True
                    st.rerun()
            with c2:
                # Scope logic: if active scope, offer "Remove from scope" instead of pure "Delete"
                if active_scopes:
                    if st.button("📤 Remove from Scope", key=f"btn_rem_scope_{node_id}"):
                        fm = st.session_state.get("filter_manager")
                        scope = active_scopes[0]
                        if node_id in scope.node_ids:
                            scope.node_ids.remove(node_id)
                            fm.save_scope(scope)
                            st.success("Removed from scope.")
                            st.rerun()
                else:
                    st.empty()
            with c3:
                # Global delete requires confirmation or clear text
                if st.button("🗑️ Delete Globally", key=f"btn_del_{node_id}"):
                    manager.delete_generic_entity(node_def, node_id, cascade=True)
                    st.success("Deleted from database.")
                    st.rerun()


def _render_context_edge_manager(manager: RiskGraphManager, edge_def: RelationshipTypeDefinition, registry):
    """Render the manager for a specific generic context edge."""
    st.subheader(f"Manage '{edge_def.label}' Edges")
    
    # Gather potential sources and targets
    source_entities = []
    target_entities = []
    
    for stype in edge_def.from_entity_types:
        ent_def = registry.get_entity_type(stype)
        if ent_def:
            try:
                # Use standard specific functions if they are kernel types...
                if stype == "risk":
                    source_entities.extend(manager.get_all_risks())
                elif stype == "mitigation":
                    source_entities.extend(manager.get_all_mitigations())
                elif stype == "tpo":
                    source_entities.extend(manager.get_all_tpos())
                else:
                    # Generic type
                    source_entities.extend(manager.get_generic_entities(ent_def))
            except Exception:
                pass
                
    for ttype in edge_def.to_entity_types:
        ent_def = registry.get_entity_type(ttype)
        if ent_def:
            try:
                if ttype == "risk":
                    target_entities.extend(manager.get_all_risks())
                elif ttype == "mitigation":
                    target_entities.extend(manager.get_all_mitigations())
                elif ttype == "tpo":
                    target_entities.extend(manager.get_all_tpos())
                else:
                    target_entities.extend(manager.get_generic_entities(ent_def))
            except Exception:
                pass
                
    if not source_entities or not target_entities:
        st.warning("Cannot manage relationships: Missing potential source or target nodes.")
        return
        
    if st.button(f"➕ New {edge_def.label} Edge"):
        st.session_state[f"show_add_ce_{edge_def.id}"] = True
        
    if st.session_state.get(f"show_add_ce_{edge_def.id}"):
        with st.expander(f"Create New {edge_def.label}", expanded=True):
            form_data = build_relationship_form(
                edge_def, source_entities, target_entities, key_prefix=f"add_ce_{edge_def.id}"
            )
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Link Nodes"):
                    sid = form_data.pop("source_id", None)
                    tid = form_data.pop("target_id", None)
                    
                    if not sid or not tid:
                        st.error("Source and Target are required.")
                    else:
                        try:
                            # We don't have the explicit entity def here easily, 
                            # generic_relationship.py only enforces it via the def object properties
                            manager.create_generic_relationship(
                                edge_def, sid, tid, None, None, form_data
                            )
                            st.success("Edge created successfully!")
                            st.session_state[f"show_add_ce_{edge_def.id}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Creation failed: {e}")
                            
            with c2:
                if st.button("❌ Cancel"):
                    st.session_state[f"show_add_ce_{edge_def.id}"] = False
                    st.rerun()
                    
    st.markdown("---")
    
    # List Existing Edges
    try:
        edges = manager.get_generic_relationships(edge_def)
        if not edges:
            st.info(f"No {edge_def.label.lower()} relationships found.")
            return
            
        start_idx, end_idx = render_pagination(len(edges), 20, f"ce_list_{edge_def.id}")
        
        for edge in edges[start_idx:end_idx]:
            eid = edge.get("id", "")
            src_node = edge.get("_source", {})
            tgt_node = edge.get("_target", {})
            sname = src_node.get("name", "Unknown")
            tname = tgt_node.get("name", "Unknown")
            
            with st.expander(f"**{sname}** ➔ **{tname}**"):
                if st.session_state.get(f"edit_ce_{eid}"):
                    edited = build_relationship_form(
                        edge_def, [src_node], [tgt_node], edge, key_prefix=f"edit_ce_form_{eid}"
                    )
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("💾 Save", key=f"sa_ce_{eid}"):
                            edited.pop("source_id", None)
                            edited.pop("target_id", None)
                            manager.update_generic_relationship(edge_def, eid, edited)
                            st.success("Edge Updated!")
                            st.session_state[f"edit_ce_{eid}"] = False
                            st.rerun()
                    with cc2:
                        if st.button("❌ Cancel", key=f"ca_ce_{eid}"):
                            st.session_state[f"edit_ce_{eid}"] = False
                            st.rerun()
                else:
                    for k, v in edge.items():
                        if k.startswith("_") or k in ("id", "source_id", "target_id") or not v:
                            continue
                        st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                        
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✏️ Edit", key=f"btn_e_ce_{eid}"):
                            st.session_state[f"edit_ce_{eid}"] = True
                            st.rerun()
                    with c2:
                        if st.button("🗑️ Delete Globally", key=f"btn_d_ce_{eid}"):
                            manager.delete_generic_relationship(edge_def, eid)
                            st.success("Deleted!")
                            st.rerun()
                            
    except Exception as e:
        st.error(f"Failed to load edges: {e}")
