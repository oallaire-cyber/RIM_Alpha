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
from ui.panels.scope_filter_panel import render_scope_filter_panel
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

    # F28: Advanced Scope Filter Panel (risks only, scope active)
    if is_node and type_id == "risk" and active_scopes and filter_mgr:
        with st.expander("🔍 Scope Definition — Add / Remove Risks", expanded=False):
            render_scope_filter_panel(manager, filter_mgr, active_scopes[0])
        st.markdown("---")

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
                if type_id == "risk":
                    _render_risk_subtype_fields(form_data, {}, key_prefix=f"add_{type_id}")
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
                                # NOTE: create_unified_entity returns a raw str (UUID) for
                                # risk/mitigation, but a dict with an "id" key for context
                                # nodes — handle both.
                                if active_scopes and add_to_scope and new_item:
                                    if isinstance(new_item, str):
                                        _new_node_id = new_item
                                    elif isinstance(new_item, dict):
                                        _new_node_id = new_item.get("id")
                                    else:
                                        _new_node_id = None
                                    if _new_node_id:
                                        if filter_mgr:
                                            filter_mgr.add_node_to_scope(
                                                active_scopes[0].id, _new_node_id
                                            )
                                        else:
                                            _add_node_to_scope(_new_node_id, active_scopes[0].id)
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

    # --- RISK TEMPLATE LIBRARY (U14) ---
    if is_node and type_id == "risk":
        _render_template_library(manager)
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


def _render_risk_subtype_fields(form_data: dict, existing_data: dict, key_prefix: str) -> None:
    """
    Render subtype selector and extension fields for a risk form.
    Mutates form_data in place, adding 'subtype' and 'ext_fields'.
    Must be called after build_entity_form so form_data['level'] is populated.
    """
    schema = get_active_schema()
    if schema is None:
        form_data["subtype"] = "generic"
        form_data["ext_fields"] = {}
        return

    level_id = (form_data.get("level") or "").lower()
    subtypes = schema.risk.get_subtypes_for_level(level_id)

    # Build option list: Generic always first, then level-specific subtypes
    options = [{"id": "generic", "label": "Generic (no subtype)"}] + [
        {"id": s.id, "label": s.label} for s in subtypes
    ]
    option_labels = [o["label"] for o in options]

    # Resolve current selection (edit mode pre-fill)
    current_id = existing_data.get("subtype") or "generic"
    current_label = next((o["label"] for o in options if o["id"] == current_id), option_labels[0])
    current_index = option_labels.index(current_label) if current_label in option_labels else 0

    selected_label = st.selectbox(
        "Subtype",
        options=option_labels,
        index=current_index,
        key=f"{key_prefix}_subtype"
    )
    selected_id = next((o["id"] for o in options if o["label"] == selected_label), "generic")
    form_data["subtype"] = selected_id

    # Extension fields for the selected subtype
    selected_subtype = next((s for s in subtypes if s.id == selected_id), None)
    ext_fields = {}
    if selected_subtype and selected_subtype.extension_fields:
        st.markdown(f"**{selected_label} fields:**")
        existing_ext = existing_data.get("ext_fields") or {}
        for ef in selected_subtype.extension_fields:
            ftype = ef.type.lower()
            current_val = existing_ext.get(ef.name, "")
            label = ef.name.replace("_", " ").title() + (" *" if ef.required else "")
            help_text = ef.description or None
            widget_key = f"{key_prefix}_ext_{ef.name}"

            if ftype == "enum" and ef.values:
                idx = ef.values.index(current_val) if current_val in ef.values else 0
                val = st.selectbox(label, options=ef.values, index=idx, help=help_text, key=widget_key)
            elif ftype in ("boolean", "bool"):
                val = st.checkbox(label, value=bool(current_val), help=help_text, key=widget_key)
            elif ftype in ("integer", "int"):
                val = st.number_input(label, value=int(current_val) if current_val else 0,
                                      step=1, help=help_text, key=widget_key)
            elif ftype == "float":
                val = st.number_input(label, value=float(current_val) if current_val else 0.0,
                                      step=0.1, help=help_text, key=widget_key)
            else:
                val = st.text_input(label, value=str(current_val) if current_val else "",
                                    help=help_text, key=widget_key)
            ext_fields[ef.name] = val

    form_data["ext_fields"] = ext_fields


def _render_template_library(manager: RiskGraphManager):
    """U14 — Render the GenericRisk template library expander."""
    templates = manager.get_all_templates()
    count_label = f" ({len(templates)})" if templates else ""
    with st.expander(f"📋 Risk Templates{count_label}", expanded=False):
        if not templates:
            st.info("No risk templates defined. Mark a risk as a template when creating it.")
            return

        for tmpl in templates:
            tmpl_id = tmpl.get("id", "")
            tmpl_name = tmpl.get("name", "Unnamed")
            tmpl_level = tmpl.get("level", "")
            tmpl_prob = tmpl.get("probability")
            tmpl_sev = tmpl.get("severity")
            score_str = f" | L={tmpl_prob} S={tmpl_sev}" if (tmpl_prob and tmpl_sev) else ""
            instances = manager.get_instances_of_template(tmpl_id)
            inst_str = f" — {len(instances)} instance(s)" if instances else " — no instances yet"

            with st.expander(f"📋 **{tmpl_name}** [{tmpl_level}]{score_str}{inst_str}"):
                desc = tmpl.get("description", "")
                if desc:
                    st.markdown(f"*{desc}*")

                # Show existing instances
                if instances:
                    st.markdown("**Instances:**")
                    for inst in instances:
                        st.markdown(
                            f"- {inst.get('name', '?')} [{inst.get('level', '')}] "
                            f"— {inst.get('status', 'Active')}"
                        )

                st.markdown("---")
                col_inst, col_del = st.columns(2)

                with col_inst:
                    if st.button("➕ Instantiate", key=f"btn_instantiate_{tmpl_id}"):
                        st.session_state[f"instantiate_tmpl_{tmpl_id}"] = True

                with col_del:
                    if st.button("🗑️ Delete Template", key=f"btn_del_tmpl_{tmpl_id}"):
                        manager.delete_risk(tmpl_id)
                        st.success("Template deleted.")
                        st.rerun()

                # Instantiation inline form
                if st.session_state.get(f"instantiate_tmpl_{tmpl_id}"):
                    st.markdown("#### Create Instance from Template")
                    inst_name = st.text_input(
                        "Instance name", value=f"{tmpl_name} (Instance)",
                        key=f"inst_name_{tmpl_id}"
                    )
                    inst_prob = st.number_input(
                        "Likelihood (0–10)", min_value=0.0, max_value=10.0,
                        value=float(tmpl_prob or 5.0), step=0.5,
                        key=f"inst_prob_{tmpl_id}"
                    )
                    inst_sev = st.number_input(
                        "Severity (0–10)", min_value=0.0, max_value=10.0,
                        value=float(tmpl_sev or 5.0), step=0.5,
                        key=f"inst_sev_{tmpl_id}"
                    )
                    inst_owner = st.text_input(
                        "Owner", value=tmpl.get("owner", ""),
                        key=f"inst_owner_{tmpl_id}"
                    )

                    ic1, ic2 = st.columns(2)
                    with ic1:
                        if st.button("💾 Create Instance", key=f"save_inst_{tmpl_id}"):
                            new_id = manager.create_risk(
                                name=inst_name,
                                level=tmpl_level,
                                categories=tmpl.get("categories", []),
                                description=tmpl.get("description", ""),
                                status="Active",
                                owner=inst_owner,
                                probability=inst_prob,
                                severity=inst_sev,
                                origin=tmpl.get("origin", "New"),
                                subtype=tmpl.get("subtype"),
                                is_template=False,
                            )
                            if new_id:
                                manager.create_instantiates_rel(tmpl_id, new_id)
                                st.success(f"Instance '{inst_name}' created and linked to template.")
                                st.session_state[f"instantiate_tmpl_{tmpl_id}"] = False
                                st.rerun()
                            else:
                                st.error("Failed to create instance.")
                    with ic2:
                        if st.button("❌ Cancel", key=f"cancel_inst_{tmpl_id}"):
                            st.session_state[f"instantiate_tmpl_{tmpl_id}"] = False
                            st.rerun()


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
            if definition.id == "risk":
                _render_risk_subtype_fields(edited_data, node, key_prefix=f"edit_form_{definition.id}_{node_id}")

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
                definition, [], [], key_prefix=f"edit_form_{definition.id}_{edge_id}", existing_data=edge
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
