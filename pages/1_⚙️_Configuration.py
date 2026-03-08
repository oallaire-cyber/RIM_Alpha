"""
RIM Configuration Manager - Streamlit Application

A standalone configuration tool for managing RIM application settings through
YAML schemas without modifying code.
"""


import streamlit as st
import yaml
import json
import copy
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import sys

# Add parent directory to path to allow imports from root
sys.path.append(str(Path(__file__).parent.parent))

# Internal imports
from config.schema_loader import (
    SchemaLoader, SchemaConfig, get_schema, reload_schema, list_schemas,
    LevelConfig, CategoryConfig, ClusterConfig, TypeConfig, StatusConfig,
    StrengthConfig, EffectivenessConfig, ImpactLevelConfig, CustomAttributeConfig,
    AttributeConfig, ContextNodeConfig, ContextEdgeConfig,
    RiskSubtypeConfig, RiskSubtypeFieldConfig,
    validate_schema, save_schema, get_loader
)
from database.connection import Neo4jConnection
from utils.db_manager import get_active_manager, init_connection_state



# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================


def init_session_state():
    """Initialize Streamlit session state variables.

    Delegates to the centralized state manager so that all key
    definitions and default values live in one place.
    """
    from utils.state_manager import init_config_page_state
    init_config_page_state()



def load_active_schema():
    """Load the active schema from disk."""
    try:
        schema = get_schema(st.session_state.active_schema_name)
        st.session_state.active_schema = schema
        st.session_state.schema_modified = False
        return schema
    except Exception as e:
        st.error(f"Failed to load schema: {e}")
        return None


# =============================================================================
# SIDEBAR COMPONENTS
# =============================================================================


def render_connection_panel():
    """Render Neo4j connection settings in sidebar."""
    st.sidebar.markdown("## 🔌 Database Connection")
    
    # Check shared connection
    manager = get_active_manager()
    if manager:
        st.session_state.config_connected = True
        st.session_state.config_connection = manager._connection
    
    if st.session_state.get("connected", False) and manager:
         st.sidebar.success(f"✅ Connected (Shared)")
         if st.sidebar.button("Disconnect Shared"):
             if st.session_state.manager:
                 st.session_state.manager.close()
             st.session_state.manager = None
             st.session_state.connected = False
             st.session_state.config_connected = False
             st.session_state.config_connection = None
             st.rerun()
    else:
        with st.sidebar.expander("Connection Settings", expanded=not st.session_state.get("connected", False)):
            uri = st.text_input("URI", value="bolt://localhost:7687", key="cfg_neo4j_uri")
            user = st.text_input("User", value="neo4j", key="cfg_neo4j_user")
            password = st.text_input("Password", type="password", key="cfg_neo4j_password")
            
            if st.button("Connect", type="primary", use_container_width=True):
                from database import RiskGraphManager
                try:
                    manager = RiskGraphManager(uri, user, password)
                    if manager.connect():
                        st.session_state.manager = manager
                        st.session_state.connected = True
                        st.session_state.config_connection = manager._connection
                        st.session_state.config_connected = True
                        st.success("Connected!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {e}")
    
    if st.session_state.config_connected:
        st.sidebar.success("✅ Connected to Neo4j")
    else:
        st.sidebar.warning("⚠️ Not connected")



def render_active_schema_selector():
    """Render schema selector in sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📋 Active Schema")
    
    available_schemas = list_schemas()
    
    if not available_schemas:
        st.sidebar.warning("No schemas found in schemas/ directory")
        return
    
    current_idx = 0
    if st.session_state.active_schema_name in available_schemas:
        current_idx = available_schemas.index(st.session_state.active_schema_name)
    
    selected = st.sidebar.selectbox(
        "Select Schema",
        available_schemas,
        index=current_idx,
        key="schema_selector"
    )
    
    if selected != st.session_state.active_schema_name:
        if st.session_state.schema_modified:
            st.sidebar.warning("⚠️ Unsaved changes will be lost!")
        st.session_state.active_schema_name = selected
        load_active_schema()
        st.rerun()
    
    # Load schema if not loaded
    if st.session_state.active_schema is None:
        load_active_schema()
    
    # Show schema info
    if st.session_state.active_schema:
        schema = st.session_state.active_schema
        st.sidebar.markdown(f"**{schema.name}** v{schema.version}")
        if schema.description:
            st.sidebar.caption(schema.description)
        
        # Quick stats
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Levels", len(schema.risk.levels))
            st.metric("Categories", len(schema.risk.categories))
        with col2:
            st.metric("TPO Clusters", len(schema.tpo.clusters))
            st.metric("Mit. Types", len(schema.mitigation.types))
    
    if st.session_state.schema_modified:
        st.sidebar.warning("📝 Unsaved changes")
    
    # Set as default for main app
    st.sidebar.markdown("---")
    
    # Check current default
    project_root = Path(__file__).parent
    rim_schema_file = project_root / ".rim_schema"
    current_default = None
    if rim_schema_file.exists():
        try:
            current_default = rim_schema_file.read_text().strip()
        except Exception:
            pass
    
    is_current_default = current_default == st.session_state.active_schema_name
    
    if is_current_default:
        st.sidebar.success(f"✅ '{st.session_state.active_schema_name}' is the default schema for the main RIM app")
    else:
        if st.sidebar.button("🎯 Set as Default for Main App", use_container_width=True):
            try:
                rim_schema_file.write_text(st.session_state.active_schema_name)
                st.sidebar.success(f"Set '{st.session_state.active_schema_name}' as default. Restart main app to apply.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to set default: {e}")


# =============================================================================
# GENERIC EDITOR COMPONENTS
# =============================================================================

def render_attribute_editor(attributes: List[AttributeConfig], prefix: str):
    """Generic editor for a list of attributes."""
    if attributes:
        for j, attr in enumerate(attributes):
            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.text(attr.name)
            with cols[1]:
                st.text(attr.type)
            with cols[2]:
                st.text("Required" if attr.required else "Optional")
            with cols[3]:
                if st.button("🗑️", key=f"{prefix}_attr_del_{j}"):
                    attributes.pop(j)
                    st.session_state.schema_modified = True
                    st.rerun()
    else:
        st.caption("No attributes defined.")

    # Add attribute popover
    with st.popover("➕ Add Attribute"):
        attr_name = st.text_input("Attribute Name", key=f"{prefix}_new_attr_name")
        attr_type = st.selectbox("Type", ["string", "int", "float", "boolean", "date"], key=f"{prefix}_new_attr_type")
        attr_required = st.checkbox("Required", key=f"{prefix}_new_attr_req")
        attr_desc = st.text_input("Description", key=f"{prefix}_new_attr_desc")
        
        if st.button("Add", key=f"{prefix}_add_attr_btn") and attr_name:
            attributes.append(AttributeConfig(
                name=attr_name,
                type=attr_type,
                required=attr_required,
                description=attr_desc
            ))
            st.session_state.schema_modified = True
            st.rerun()


def render_generic_entity_config(entity_type: Any, prefix: str, is_kernel: bool = False):
    """Generic editor for an entity type configuration."""
    col1, col2 = st.columns(2)
    
    with col1:
        if not is_kernel:
            new_id = st.text_input("ID", value=entity_type.id, key=f"{prefix}_id")
            if new_id != entity_type.id:
                entity_type.id = new_id
                st.session_state.schema_modified = True
        
        # label is common
        label_val = getattr(entity_type, 'label', '')
        new_label = st.text_input("Label", value=label_val, key=f"{prefix}_label")
        if new_label != label_val:
            entity_type.label = new_label
            st.session_state.schema_modified = True
        
        new_neo4j = st.text_input("Neo4j Label", value=entity_type.neo4j_label, key=f"{prefix}_neo4j")
        if new_neo4j != entity_type.neo4j_label:
            entity_type.neo4j_label = new_neo4j
            st.session_state.schema_modified = True
        
        desc_val = getattr(entity_type, 'description', '')
        new_desc = st.text_area("Description", value=desc_val, key=f"{prefix}_desc", height=80)
        if new_desc != desc_val:
            entity_type.description = new_desc
            st.session_state.schema_modified = True
    
    with col2:
        color_val = getattr(entity_type, 'color', '#808080')
        new_color = st.color_picker("Color", value=color_val, key=f"{prefix}_color")
        if new_color != color_val:
            entity_type.color = new_color
            st.session_state.schema_modified = True
        
        shape_options = ["dot", "box", "diamond", "hexagon", "star", "triangle", "triangleDown", "square"]
        shape_val = getattr(entity_type, 'shape', 'dot')
        current_shape_idx = shape_options.index(shape_val) if shape_val in shape_options else 0
        new_shape = st.selectbox("Shape", shape_options, index=current_shape_idx, key=f"{prefix}_shape")
        if new_shape != shape_val:
            entity_type.shape = new_shape
            st.session_state.schema_modified = True
        
        emoji_val = getattr(entity_type, 'emoji', '📦')
        new_emoji = st.text_input("Emoji", value=emoji_val, key=f"{prefix}_emoji")
        if new_emoji != emoji_val:
            entity_type.emoji = new_emoji
            st.session_state.schema_modified = True
        
        size_val = getattr(entity_type, 'size', 30)
        new_size = st.number_input("Size", value=size_val, min_value=10, max_value=100, key=f"{prefix}_size")
        if new_size != size_val:
            entity_type.size = new_size
            st.session_state.schema_modified = True
    
    # Generic Attributes editor
    st.markdown("##### Standard Attributes")
    render_attribute_editor(entity_type.attributes, f"{prefix}_std")
    
    # Custom Attributes editor (if applicable)
    if hasattr(entity_type, 'custom_attributes'):
        st.markdown("##### Custom Attributes")
        render_attribute_editor(entity_type.custom_attributes, f"{prefix}_cust")


# =============================================================================
# SCHEMA MANAGEMENT TAB
# =============================================================================

def render_schema_management():
    """Render schema management tab content."""
    schema = st.session_state.active_schema
    
    if not schema:
        st.warning("No schema loaded. Select a schema from the sidebar.")
        return
    
    # Sub-tabs for different schema sections
    subtab1, subtab2, subtab3, subtab4, subtab5, subtab6, subtab7 = st.tabs([
        "⚙️ General",
        "🎯 Risk Config",
        "🛡️ Mitigation Config",
        "🔗 Relationships",
        "🧩 Context Nodes",
        "🔗 Context Edges",
        "📄 YAML Preview"
    ])
    
    with subtab1:
        render_general_settings(schema)
    
    with subtab2:
        render_risk_config(schema)
    
    with subtab3:
        render_mitigation_config(schema)
    
    with subtab4:
        render_relationship_config(schema)
    
    with subtab5:
        render_context_nodes_config(schema)
    
    with subtab6:
        render_context_edges_config(schema)
    
    with subtab7:
        render_yaml_preview(schema)


def render_general_settings(schema: SchemaConfig):
    """Render general schema settings."""
    st.subheader("⚙️ General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_name = st.text_input("Schema Name", value=schema.name, key="schema_name")
        if new_name != schema.name:
            schema.name = new_name
            st.session_state.schema_modified = True
        
        new_version = st.text_input("Version", value=schema.version, key="schema_version")
        if new_version != schema.version:
            schema.version = new_version
            st.session_state.schema_modified = True
    
    with col2:
        new_desc = st.text_area("Description", value=schema.description, key="schema_desc", height=100)
        if new_desc != schema.description:
            schema.description = new_desc
            st.session_state.schema_modified = True
    
    st.markdown("---")
    st.subheader("🎨 UI Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_title = st.text_input("App Title", value=schema.ui.app_title, key="ui_title")
        if new_title != schema.ui.app_title:
            schema.ui.app_title = new_title
            st.session_state.schema_modified = True
    
    with col2:
        new_icon = st.text_input("App Icon", value=schema.ui.app_icon, key="ui_icon")
        if new_icon != schema.ui.app_icon:
            schema.ui.app_icon = new_icon
            st.session_state.schema_modified = True
    
    with col3:
        new_layout = st.selectbox("Layout", ["wide", "centered"], 
                                  index=0 if schema.ui.layout == "wide" else 1,
                                  key="ui_layout")
        if new_layout != schema.ui.layout:
            schema.ui.layout = new_layout
            st.session_state.schema_modified = True
    
    st.markdown("---")
    
    # Save and actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Save Schema", type="primary", use_container_width=True):
            errors = validate_schema(schema)
            if errors:
                for err in errors:
                    st.error(err)
            else:
                try:
                    save_schema(schema, st.session_state.active_schema_name)
                    st.session_state.schema_modified = False
                    st.success("Schema saved successfully!")
                except Exception as e:
                    st.error(f"Failed to save: {e}")
    
    with col2:
        if st.button("🔄 Reload", use_container_width=True):
            load_active_schema()
            st.success("Schema reloaded from disk")
            st.rerun()
    
    with col3:
        if st.button("📋 Duplicate", use_container_width=True):
            st.session_state.show_duplicate_dialog = True
    
    with col4:
        if st.button("➕ New Schema", use_container_width=True):
            st.session_state.show_new_schema_dialog = True
    
    # Dialogs
    if st.session_state.get("show_duplicate_dialog"):
        render_duplicate_schema_dialog(schema)
    
    if st.session_state.get("show_new_schema_dialog"):
        render_new_schema_dialog()


def render_duplicate_schema_dialog(schema: SchemaConfig):
    """Render duplicate schema dialog."""
    with st.expander("📋 Duplicate Schema", expanded=True):
        new_name = st.text_input("New Schema Directory Name", key="dup_schema_name")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Copy", type="primary"):
                if new_name:
                    existing = list_schemas()
                    if new_name in existing:
                        st.error("Schema already exists!")
                    else:
                        try:
                            new_schema = copy.deepcopy(schema)
                            new_schema.name = new_name.replace("_", " ").title()
                            save_schema(new_schema, new_name)
                            st.success(f"Created schema: {new_name}")
                            st.session_state.show_duplicate_dialog = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
                else:
                    st.warning("Please enter a name")
        
        with col2:
            if st.button("Cancel"):
                st.session_state.show_duplicate_dialog = False
                st.rerun()


def render_new_schema_dialog():
    """Render new schema dialog."""
    with st.expander("➕ Create New Schema", expanded=True):
        new_name = st.text_input("Schema Directory Name", key="new_schema_name")
        template = st.selectbox("Base Template", list_schemas(), key="new_schema_template")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create", type="primary"):
                if new_name:
                    existing = list_schemas()
                    if new_name in existing:
                        st.error("Schema already exists!")
                    else:
                        try:
                            base_schema = get_schema(template)
                            new_schema = copy.deepcopy(base_schema)
                            new_schema.name = new_name.replace("_", " ").title()
                            new_schema.description = f"New schema based on {template}"
                            save_schema(new_schema, new_name)
                            st.success(f"Created schema: {new_name}")
                            st.session_state.active_schema_name = new_name
                            st.session_state.show_new_schema_dialog = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
                else:
                    st.warning("Please enter a name")
        
        with col2:
            if st.button("Cancel", key="cancel_new"):
                st.session_state.show_new_schema_dialog = False
                st.rerun()


def render_risk_config(schema: SchemaConfig):
    """Render risk configuration section."""
    st.subheader("🎯 Risk Configuration")
    
    # Generic Entity Config (Visual Tokens)
    with st.expander("🎨 Visual Tokens & Attributes", expanded=False):
        render_generic_entity_config(schema.risk, "risk", is_kernel=True)
    
    st.markdown("---")
    
    # Risk Levels
    st.markdown("### 📊 Risk Levels")
    render_level_editor(schema)
    
    st.markdown("---")
    
    # Risk Categories
    st.markdown("### 🗂️ Risk Categories")
    render_category_editor(schema)
    
    st.markdown("---")
    
    # Risk Statuses
    st.markdown("### 📋 Risk Statuses")
    render_status_editor(schema.risk.statuses, "risk_status")
    
    st.markdown("---")
    
    # Risk Origins
    st.markdown("### 🏷️ Risk Origins")
    render_origin_editor(schema)
    
    st.markdown("---")
    
    # Risk Subtypes
    st.markdown("### 🏷️ Risk Subtypes")
    render_subtype_editor(schema)


def render_level_editor(schema: SchemaConfig):
    """Edit risk levels with add/edit/remove."""
    levels = schema.risk.levels
    
    for i, level in enumerate(levels):
        with st.expander(f"{level.emoji} {level.label}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_id = st.text_input("ID", level.id, key=f"level_id_{i}")
                new_label = st.text_input("Label", level.label, key=f"level_label_{i}")
                new_desc = st.text_area("Description", level.description, key=f"level_desc_{i}", height=80)
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    new_color = st.color_picker("Color", level.color, key=f"level_color_{i}")
                with col_b:
                    new_emoji = st.text_input("Emoji", level.emoji, key=f"level_emoji_{i}")
                with col_c:
                    new_shape = st.selectbox("Shape", ["diamond", "dot", "box", "hexagon", "star"],
                                             index=["diamond", "dot", "box", "hexagon", "star"].index(level.shape) if level.shape in ["diamond", "dot", "box", "hexagon", "star"] else 1,
                                             key=f"level_shape_{i}")
                
                # Check for changes
                if (new_id != level.id or new_label != level.label or 
                    new_desc != level.description or new_color != level.color or
                    new_emoji != level.emoji or new_shape != level.shape):
                    level.id = new_id
                    level.label = new_label
                    level.description = new_desc
                    level.color = new_color
                    level.emoji = new_emoji
                    level.shape = new_shape
                    st.session_state.schema_modified = True
            
            with col2:
                st.markdown("**Preview:**")
                st.markdown(f"<div style='background:{level.color};color:white;padding:10px;border-radius:5px;text-align:center'>{level.emoji} {level.label}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                if st.button("🗑️ Delete", key=f"del_level_{i}"):
                    if len(levels) > 1:
                        levels.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
                    else:
                        st.warning("Must have at least one level")
    
    # Add new level
    if st.button("➕ Add Risk Level"):
        levels.append(LevelConfig(
            id=f"new_level_{len(levels)}",
            label="New Level",
            description="",
            color="#808080",
            shape="dot",
            emoji="○"
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_category_editor(schema: SchemaConfig):
    """Edit risk categories."""
    categories = schema.risk.categories
    
    # Display as 2-column grid
    cols = st.columns(2)
    
    for i, cat in enumerate(categories):
        with cols[i % 2]:
            with st.expander(f"{cat.label}", expanded=False):
                new_id = st.text_input("ID", cat.id, key=f"cat_id_{i}")
                new_label = st.text_input("Label", cat.label, key=f"cat_label_{i}")
                new_desc = st.text_area("Description", cat.description, key=f"cat_desc_{i}", height=60)
                new_color = st.color_picker("Color", cat.color, key=f"cat_color_{i}")
                
                if (new_id != cat.id or new_label != cat.label or 
                    new_desc != cat.description or new_color != cat.color):
                    cat.id = new_id
                    cat.label = new_label
                    cat.description = new_desc
                    cat.color = new_color
                    st.session_state.schema_modified = True
                
                if st.button("🗑️ Delete", key=f"del_cat_{i}"):
                    if len(categories) > 1:
                        categories.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Category"):
        categories.append(CategoryConfig(
            id=f"new_category_{len(categories)}",
            label="New Category",
            description="",
            color="#808080"
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_status_editor(statuses: List[StatusConfig], prefix: str):
    """Edit status configurations."""
    for i, status in enumerate(statuses):
        with st.expander(f"{'✅' if status.is_active else '❌'} {status.label}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_id = st.text_input("ID", status.id, key=f"{prefix}_id_{i}")
                new_label = st.text_input("Label", status.label, key=f"{prefix}_label_{i}")
                new_desc = st.text_area("Description", status.description, key=f"{prefix}_desc_{i}", height=60)
                new_active = st.checkbox("Is Active", status.is_active, key=f"{prefix}_active_{i}")
                
                if (new_id != status.id or new_label != status.label or 
                    new_desc != status.description or new_active != status.is_active):
                    status.id = new_id
                    status.label = new_label
                    status.description = new_desc
                    status.is_active = new_active
                    st.session_state.schema_modified = True
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_{prefix}_{i}"):
                    if len(statuses) > 1:
                        statuses.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button(f"➕ Add Status", key=f"add_{prefix}"):
        statuses.append(StatusConfig(
            id=f"new_status_{len(statuses)}",
            label="New Status",
            description="",
            is_active=True
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_origin_editor(schema: SchemaConfig):
    """Edit risk origins."""
    origins = schema.risk.origins
    
    cols = st.columns(2)
    for i, origin in enumerate(origins):
        with cols[i % 2]:
            with st.expander(f"{origin.label}", expanded=False):
                new_id = st.text_input("ID", origin.id, key=f"origin_id_{i}")
                new_label = st.text_input("Label", origin.label, key=f"origin_label_{i}")
                new_desc = st.text_area("Description", origin.description, key=f"origin_desc_{i}", height=60)
                
                if (new_id != origin.id or new_label != origin.label or new_desc != origin.description):
                    origin.id = new_id
                    origin.label = new_label
                    origin.description = new_desc
                    st.session_state.schema_modified = True
                
                if st.button("🗑️ Delete", key=f"del_origin_{i}"):
                    if len(origins) > 1:
                        origins.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Origin"):
        from config.schema_loader import OriginConfig
        origins.append(OriginConfig(
            id=f"new_origin_{len(origins)}",
            label="New Origin",
            description=""
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_subtype_editor(schema: SchemaConfig):
    """Edit risk subtypes with nested extension fields."""
    subtypes = schema.risk.subtypes
    # Gather available level IDs for the applies_to checkboxes
    level_ids = [lvl.id for lvl in schema.risk.levels]
    level_labels = {lvl.id: lvl.label for lvl in schema.risk.levels}

    for i, st_cfg in enumerate(subtypes):
        with st.expander(f"🏷️ {st_cfg.label}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                new_id = st.text_input("ID", st_cfg.id, key=f"subtype_id_{i}")
                new_label = st.text_input("Label", st_cfg.label, key=f"subtype_label_{i}")

                # Applies-to level checkboxes
                st.markdown("**Applies to levels:**")
                applies_cols = st.columns(len(level_ids)) if level_ids else [st]
                new_applies = []
                for j, lid in enumerate(level_ids):
                    with applies_cols[j]:
                        checked = st.checkbox(
                            level_labels.get(lid, lid),
                            value=(lid in st_cfg.applies_to),
                            key=f"subtype_applies_{i}_{lid}"
                        )
                        if checked:
                            new_applies.append(lid)

                # Detect changes
                if (new_id != st_cfg.id or new_label != st_cfg.label
                        or sorted(new_applies) != sorted(st_cfg.applies_to)):
                    st_cfg.id = new_id
                    st_cfg.label = new_label
                    st_cfg.applies_to = new_applies
                    st.session_state.schema_modified = True

            with col2:
                if st.button("🗑️ Delete Subtype", key=f"del_subtype_{i}"):
                    if len(subtypes) > 1:
                        subtypes.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
                    else:
                        st.warning("Must have at least one subtype")

            # ── Extension fields ──────────────────────────────────────────
            st.markdown("**Extension Fields:**")
            ext_fields = st_cfg.extension_fields
            if ext_fields:
                for k, ef in enumerate(ext_fields):
                    ef_cols = st.columns([2, 1, 1, 1, 1])
                    with ef_cols[0]:
                        new_name = st.text_input(
                            "Name", ef.name, key=f"ef_name_{i}_{k}"
                        )
                        if new_name != ef.name:
                            ef.name = new_name
                            st.session_state.schema_modified = True
                    with ef_cols[1]:
                        type_opts = ["string", "enum", "boolean", "integer", "float"]
                        cur_idx = type_opts.index(ef.type) if ef.type in type_opts else 0
                        new_type = st.selectbox(
                            "Type", type_opts, index=cur_idx,
                            key=f"ef_type_{i}_{k}"
                        )
                        if new_type != ef.type:
                            ef.type = new_type
                            st.session_state.schema_modified = True
                    with ef_cols[2]:
                        new_req = st.checkbox(
                            "Required", ef.required, key=f"ef_req_{i}_{k}"
                        )
                        if new_req != ef.required:
                            ef.required = new_req
                            st.session_state.schema_modified = True
                    with ef_cols[3]:
                        new_desc = st.text_input(
                            "Desc", ef.description, key=f"ef_desc_{i}_{k}"
                        )
                        if new_desc != ef.description:
                            ef.description = new_desc
                            st.session_state.schema_modified = True
                    with ef_cols[4]:
                        if st.button("🗑️", key=f"del_ef_{i}_{k}"):
                            ext_fields.pop(k)
                            st.session_state.schema_modified = True
                            st.rerun()

                    # Enum values editor (only for enum type)
                    if ef.type == "enum":
                        vals_str = ", ".join(ef.values) if ef.values else ""
                        new_vals = st.text_input(
                            "Enum values (comma-separated)",
                            vals_str, key=f"ef_vals_{i}_{k}"
                        )
                        parsed = [v.strip() for v in new_vals.split(",") if v.strip()]
                        if parsed != ef.values:
                            ef.values = parsed
                            st.session_state.schema_modified = True
            else:
                st.caption("No extension fields defined.")

            # Add extension field button
            if st.button("➕ Add Extension Field", key=f"add_ef_{i}"):
                ext_fields.append(RiskSubtypeFieldConfig(
                    name=f"new_field_{len(ext_fields)}",
                    type="string",
                    required=False,
                    description=""
                ))
                st.session_state.schema_modified = True
                st.rerun()

    # Add new subtype
    if st.button("➕ Add Risk Subtype"):
        subtypes.append(RiskSubtypeConfig(
            id=f"new_subtype_{len(subtypes)}",
            label="New Subtype",
            applies_to=list(level_ids),
            extension_fields=[]
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_tpo_config(schema: SchemaConfig):
    """Render TPO configuration section."""
    st.subheader("🏆 TPO Configuration")
    
    # Generic Entity Config (Visual Tokens)
    with st.expander("🎨 Visual Tokens & Attributes", expanded=False):
        render_generic_entity_config(schema.tpo, "tpo", is_kernel=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 TPO Clusters")
    clusters = schema.tpo.clusters
    
    cols = st.columns(2)
    for i, cluster in enumerate(clusters):
        with cols[i % 2]:
            with st.expander(f"{cluster.label}", expanded=False):
                new_id = st.text_input("ID", cluster.id, key=f"cluster_id_{i}")
                new_label = st.text_input("Label", cluster.label, key=f"cluster_label_{i}")
                new_desc = st.text_area("Description", cluster.description, key=f"cluster_desc_{i}", height=60)
                new_color = st.color_picker("Color", cluster.color, key=f"cluster_color_{i}")
                
                if (new_id != cluster.id or new_label != cluster.label or 
                    new_desc != cluster.description or new_color != cluster.color):
                    cluster.id = new_id
                    cluster.label = new_label
                    cluster.description = new_desc
                    cluster.color = new_color
                    st.session_state.schema_modified = True
                
                if st.button("🗑️ Delete", key=f"del_cluster_{i}"):
                    if len(clusters) > 1:
                        clusters.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Cluster"):
        clusters.append(ClusterConfig(
            id=f"new_cluster_{len(clusters)}",
            label="New Cluster",
            description="",
            color="#f1c40f"
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_mitigation_config(schema: SchemaConfig):
    """Render mitigation configuration section."""
    st.subheader("🛡️ Mitigation Configuration")
    
    # Generic Entity Config (Visual Tokens)
    with st.expander("🎨 Visual Tokens & Attributes", expanded=False):
        render_generic_entity_config(schema.mitigation, "mitigation", is_kernel=True)
    
    st.markdown("---")
    
    st.markdown("### 📦 Mitigation Types")
    types = schema.mitigation.types
    
    for i, mit_type in enumerate(types):
        with st.expander(f"{mit_type.label}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_id = st.text_input("ID", mit_type.id, key=f"mit_type_id_{i}")
                new_label = st.text_input("Label", mit_type.label, key=f"mit_type_label_{i}")
                new_desc = st.text_area("Description", mit_type.description, key=f"mit_type_desc_{i}", height=60)
                new_color = st.color_picker("Color", mit_type.color, key=f"mit_type_color_{i}")
                new_style = st.selectbox("Line Style", ["solid", "dotted", "dashed", "thick"],
                                         index=["solid", "dotted", "dashed", "thick"].index(mit_type.line_style) if mit_type.line_style in ["solid", "dotted", "dashed", "thick"] else 0,
                                         key=f"mit_type_style_{i}")
                
                if (new_id != mit_type.id or new_label != mit_type.label or 
                    new_desc != mit_type.description or new_color != mit_type.color or
                    new_style != mit_type.line_style):
                    mit_type.id = new_id
                    mit_type.label = new_label
                    mit_type.description = new_desc
                    mit_type.color = new_color
                    mit_type.line_style = new_style
                    st.session_state.schema_modified = True
            
            with col2:
                st.markdown("**Preview:**")
                style_css = "solid" if mit_type.line_style == "thick" else mit_type.line_style
                st.markdown(f"<div style='border:3px {style_css} {mit_type.color};padding:5px;text-align:center'>{mit_type.label}</div>", unsafe_allow_html=True)
                
                if st.button("🗑️ Delete", key=f"del_mit_type_{i}"):
                    if len(types) > 1:
                        types.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Mitigation Type"):
        types.append(TypeConfig(
            id=f"new_type_{len(types)}",
            label="New Type",
            description="",
            color="#808080",
            line_style="solid"
        ))
        st.session_state.schema_modified = True
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Mitigation Statuses")
    render_status_editor(schema.mitigation.statuses, "mit_status")


def render_relationship_config(schema: SchemaConfig):
    """Render relationship configuration section."""
    st.subheader("🔗 Relationship Configuration")
    
    # Influence strengths
    st.markdown("### 💪 Influence Strengths")
    strengths = schema.influences.strengths
    
    for i, strength in enumerate(strengths):
        with st.expander(f"{strength.label} (value: {strength.value})", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_id = st.text_input("ID", strength.id, key=f"str_id_{i}")
                new_label = st.text_input("Label", strength.label, key=f"str_label_{i}")
                new_value = st.slider("Value", 0.0, 1.0, strength.value, 0.05, key=f"str_value_{i}")
                new_desc = st.text_area("Description", strength.description, key=f"str_desc_{i}", height=60)
                new_color = st.color_picker("Color", strength.color, key=f"str_color_{i}")
                
                if (new_id != strength.id or new_label != strength.label or
                    new_value != strength.value or new_desc != strength.description or
                    new_color != strength.color):
                    strength.id = new_id
                    strength.label = new_label
                    strength.value = new_value
                    strength.description = new_desc
                    strength.color = new_color
                    st.session_state.schema_modified = True
            
            with col2:
                # Visual gauge
                pct = int(strength.value * 100)
                st.markdown(f"**{pct}%**")
                st.progress(strength.value)
                
                if st.button("🗑️ Delete", key=f"del_str_{i}"):
                    if len(strengths) > 1:
                        strengths.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Strength Level"):
        strengths.append(StrengthConfig(
            id=f"new_strength_{len(strengths)}",
            label="New Strength",
            value=0.5,
            description="",
            color="#808080"
        ))
        st.session_state.schema_modified = True
        st.rerun()
    
    st.markdown("---")
    
    # Effectiveness levels
    st.markdown("### 🎯 Mitigation Effectiveness Levels")
    effectiveness = schema.mitigates.effectiveness_levels
    
    for i, eff in enumerate(effectiveness):
        with st.expander(f"{eff.label} ({int(eff.reduction*100)}% reduction)", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_id = st.text_input("ID", eff.id, key=f"eff_id_{i}")
                new_label = st.text_input("Label", eff.label, key=f"eff_label_{i}")
                new_reduction = st.slider("Reduction %", 0, 100, int(eff.reduction*100), 5, key=f"eff_red_{i}")
                new_desc = st.text_area("Description", eff.description, key=f"eff_desc_{i}", height=60)
                
                if (new_id != eff.id or new_label != eff.label or
                    new_reduction/100 != eff.reduction or new_desc != eff.description):
                    eff.id = new_id
                    eff.label = new_label
                    eff.reduction = new_reduction / 100
                    eff.description = new_desc
                    st.session_state.schema_modified = True
            
            with col2:
                st.markdown(f"**{int(eff.reduction*100)}% reduction**")
                st.progress(eff.reduction)
                
                if st.button("🗑️ Delete", key=f"del_eff_{i}"):
                    if len(effectiveness) > 1:
                        effectiveness.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Effectiveness Level"):
        effectiveness.append(EffectivenessConfig(
            id=f"new_eff_{len(effectiveness)}",
            label="New Level",
            reduction=0.5,
            description=""
        ))
        st.session_state.schema_modified = True
        st.rerun()
    
    st.markdown("---")
    
    # Impact levels
    st.markdown("### 📊 TPO Impact Levels")
    impact_levels = schema.impacts_tpo.impact_levels
    
    for i, il in enumerate(impact_levels):
        with st.expander(f"{il.label} (value: {il.value})", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_id = st.text_input("ID", il.id, key=f"il_id_{i}")
                new_label = st.text_input("Label", il.label, key=f"il_label_{i}")
                new_value = st.number_input("Value", 1, 10, il.value, key=f"il_value_{i}")
                new_desc = st.text_area("Description", il.description, key=f"il_desc_{i}", height=60)
                new_color = st.color_picker("Color", il.color, key=f"il_color_{i}")
                
                if (new_id != il.id or new_label != il.label or
                    new_value != il.value or new_desc != il.description or
                    new_color != il.color):
                    il.id = new_id
                    il.label = new_label
                    il.value = new_value
                    il.description = new_desc
                    il.color = new_color
                    st.session_state.schema_modified = True
            
            with col2:
                st.markdown(f"<div style='background:{il.color};color:white;padding:10px;text-align:center;border-radius:5px'>{il.label}</div>", unsafe_allow_html=True)
                
                if st.button("🗑️ Delete", key=f"del_il_{i}"):
                    if len(impact_levels) > 1:
                        impact_levels.pop(i)
                        st.session_state.schema_modified = True
                        st.rerun()
    
    if st.button("➕ Add Impact Level"):
        impact_levels.append(ImpactLevelConfig(
            id=f"new_impact_{len(impact_levels)}",
            label="New Level",
            value=len(impact_levels) + 1,
            description="",
            color="#808080"
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_context_nodes_config(schema: SchemaConfig):
    """Render context nodes configuration section."""
    st.subheader("🧩 Context Nodes")
    st.info("⚠️ All context nodes use the unified **ContextNode** Neo4j label with `node_type` and `zone` as stored properties. Reserved base properties: `source`, `import_adapter`.")
    
    context_nodes = schema.context_nodes
    
    if not context_nodes:
        st.markdown("*No context nodes defined yet.*")
    
    # Display existing context nodes
    for i, node in enumerate(context_nodes):
        with st.expander(f"{node.emoji} {node.label} (zone: {node.zone})", expanded=i == 0):
            col1, col2 = st.columns(2)
            
            with col1:
                new_id = st.text_input("ID", value=node.id, key=f"cn_id_{i}")
                if new_id != node.id:
                    node.id = new_id
                    st.session_state.schema_modified = True
                
                new_label = st.text_input("Label", value=node.label, key=f"cn_label_{i}")
                if new_label != node.label:
                    node.label = new_label
                    st.session_state.schema_modified = True
                
                # Read-only Neo4j label
                st.text_input("Neo4j Label", value="ContextNode", key=f"cn_neo4j_{i}", disabled=True)
                st.caption(f"node_type = `{node.id}`")
                
                new_desc = st.text_area("Description", value=node.description, key=f"cn_desc_{i}", height=80)
                if new_desc != node.description:
                    node.description = new_desc
                    st.session_state.schema_modified = True
            
            with col2:
                new_emoji = st.text_input("Emoji", value=node.emoji, key=f"cn_emoji_{i}")
                if new_emoji != node.emoji:
                    node.emoji = new_emoji
                    st.session_state.schema_modified = True
                
                new_color = st.color_picker("Color", value=node.color, key=f"cn_color_{i}")
                if new_color != node.color:
                    node.color = new_color
                    st.session_state.schema_modified = True
                
                shape_options = ["box", "dot", "diamond", "hexagon", "star", "triangle"]
                shape_idx = shape_options.index(node.shape) if node.shape in shape_options else 0
                new_shape = st.selectbox("Shape", shape_options, index=shape_idx, key=f"cn_shape_{i}")
                if new_shape != node.shape:
                    node.shape = new_shape
                    st.session_state.schema_modified = True
                
                zone_options = ["upper", "lower"]
                zone_idx = zone_options.index(node.zone) if node.zone in zone_options else 1
                new_zone = st.selectbox("Zone", zone_options, index=zone_idx, key=f"cn_zone_{i}")
                if new_zone != node.zone:
                    node.zone = new_zone
                    st.session_state.schema_modified = True
                
                border_options = ["solid", "double", "dashed"]
                border_idx = border_options.index(node.border) if node.border in border_options else 0
                new_border = st.selectbox("Border", border_options, index=border_idx, key=f"cn_border_{i}")
                if new_border != node.border:
                    node.border = new_border
                    st.session_state.schema_modified = True
            
            # Properties
            st.markdown("##### Node Properties")
            render_attribute_editor(node.properties, f"cn_{i}")
            
            # Delete node button
            st.markdown("---")
            if st.button(f"🗑️ Delete {node.label}", key=f"cn_delete_{i}", type="secondary"):
                schema.context_nodes.pop(i)
                st.session_state.schema_modified = True
                st.rerun()
    
    # Add new context node button
    st.markdown("---")
    if st.button("➕ Add Context Node", type="primary"):
        schema.context_nodes.append(ContextNodeConfig(
            id=f"context_{len(context_nodes) + 1}",
            label="New Context Node",
            neo4j_label="ContextNode",
            description="",
            color="#808080",
            shape="box",
            emoji="📦",
            size=30,
            zone="lower",
            border="solid"
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_context_edges_config(schema: SchemaConfig):
    """Render context edges configuration section."""
    st.subheader("🔗 Context Edges")
    st.info("Define relationships between context nodes and/or core entities (Risk, TPO, Mitigation).")
    
    context_edges = schema.context_edges
    
    # Build list of available entities
    entity_options = ["risk", "tpo", "mitigation"]
    for cn in schema.context_nodes:
        entity_options.append(cn.id)
    
    if not context_edges:
        st.markdown("*No context edges defined yet.*")
    
    # Display existing edges
    for i, edge in enumerate(context_edges):
        with st.expander(f"🔗 {edge.label}: {edge.from_node} → {edge.to_node}", expanded=i == 0):
            col1, col2 = st.columns(2)
            
            with col1:
                new_id = st.text_input("ID", value=edge.id, key=f"ce_id_{i}")
                if new_id != edge.id:
                    edge.id = new_id
                    st.session_state.schema_modified = True
                
                new_label = st.text_input("Label", value=edge.label, key=f"ce_label_{i}")
                if new_label != edge.label:
                    edge.label = new_label
                    st.session_state.schema_modified = True
                
                new_neo4j = st.text_input("Neo4j Type", value=edge.neo4j_type, key=f"ce_neo4j_{i}")
                if new_neo4j != edge.neo4j_type:
                    edge.neo4j_type = new_neo4j
                    st.session_state.schema_modified = True
                
                new_desc = st.text_area("Description", value=edge.description, key=f"ce_desc_{i}", height=80)
                if new_desc != edge.description:
                    edge.description = new_desc
                    st.session_state.schema_modified = True
            
            with col2:
                from_idx = entity_options.index(edge.from_node) if edge.from_node in entity_options else 0
                new_from = st.selectbox("From Node", entity_options, index=from_idx, key=f"ce_from_{i}")
                if new_from != edge.from_node:
                    edge.from_node = new_from
                    st.session_state.schema_modified = True
                
                to_idx = entity_options.index(edge.to_node) if edge.to_node in entity_options else 0
                new_to = st.selectbox("To Node", entity_options, index=to_idx, key=f"ce_to_{i}")
                if new_to != edge.to_node:
                    edge.to_node = new_to
                    st.session_state.schema_modified = True
                
                new_color = st.color_picker("Color", value=edge.color, key=f"ce_color_{i}")
                if new_color != edge.color:
                    edge.color = new_color
                    st.session_state.schema_modified = True
                
                style_options = ["solid", "dashed", "dotted"]
                style_idx = style_options.index(edge.line_style) if edge.line_style in style_options else 0
                new_style = st.selectbox("Line Style", style_options, index=style_idx, key=f"ce_style_{i}")
                if new_style != edge.line_style:
                    edge.line_style = new_style
                    st.session_state.schema_modified = True
                
                new_bidir = st.checkbox("Bidirectional", value=edge.bidirectional, key=f"ce_bidir_{i}")
                if new_bidir != edge.bidirectional:
                    edge.bidirectional = new_bidir
                    st.session_state.schema_modified = True
            
            # Edge properties
            st.markdown("##### Edge Properties")
            render_attribute_editor(edge.properties, f"ce_{i}")
            
            # Delete edge button
            st.markdown("---")
            if st.button(f"🗑️ Delete {edge.label}", key=f"ce_delete_{i}", type="secondary"):
                schema.context_edges.pop(i)
                st.session_state.schema_modified = True
                st.rerun()
    
    # Add new edge button
    st.markdown("---")
    if st.button("➕ Add Context Edge", type="primary"):
        schema.context_edges.append(ContextEdgeConfig(
            id=f"context_edge_{len(context_edges) + 1}",
            label="New Edge",
            neo4j_type="CUSTOM_EDGE",
            description="",
            from_node="risk",
            to_node="tpo",
            color="#808080",
            line_style="solid",
            bidirectional=False
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_yaml_preview(schema: SchemaConfig):
    """Display and edit YAML with syntax highlighting."""
    st.subheader("📄 Schema YAML")
    
    schema_path = get_loader().get_schema_path(st.session_state.active_schema_name)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        edit_mode = st.toggle("Edit Mode", False, key="yaml_edit_mode")
    
    with col2:
        if st.button("🔄 Reload from Disk"):
            load_active_schema()
            st.rerun()
    
    if edit_mode:
        # Load raw YAML
        with open(schema_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        new_content = st.text_area(
            "Schema YAML",
            yaml_content,
            height=600,
            key="yaml_editor"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Validate", use_container_width=True):
                try:
                    data = yaml.safe_load(new_content)
                    loader = get_loader()
                    parsed = loader._parse_schema(data)
                    errors = validate_schema(parsed)
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        st.success("Schema is valid!")
                except yaml.YAMLError as e:
                    st.error(f"YAML syntax error: {e}")
                except Exception as e:
                    st.error(f"Validation error: {e}")
        
        with col2:
            if st.button("💾 Save YAML", type="primary", use_container_width=True):
                try:
                    # Validate first
                    data = yaml.safe_load(new_content)
                    loader = get_loader()
                    parsed = loader._parse_schema(data)
                    errors = validate_schema(parsed)
                    
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        # Backup existing
                        backup_path = schema_path.with_suffix('.yaml.bak')
                        if schema_path.exists():
                            with open(schema_path, 'r') as f:
                                backup_content = f.read()
                            with open(backup_path, 'w') as f:
                                f.write(backup_content)
                        
                        # Save new content
                        with open(schema_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        # Reload schema
                        load_active_schema()
                        st.success("YAML saved successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Save failed: {e}")
        
        with col3:
            if st.button("↩️ Revert", use_container_width=True):
                st.rerun()
    else:
        # Display mode - show current schema as YAML
        loader = get_loader()
        yaml_data = loader._schema_to_dict(schema)
        yaml_str = yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        st.code(yaml_str, language="yaml")


# =============================================================================
# DATABASE TAB
# =============================================================================

def render_database_tab():
    """Render database management tab."""
    if not st.session_state.config_connected:
        st.warning("Please connect to Neo4j database using the sidebar.")
        return
    
    conn = st.session_state.config_connection
    
    # Database statistics
    st.subheader("📊 Database Statistics")
    
    if st.button("🔄 Refresh Statistics", type="primary"):
        st.session_state.db_stats = get_database_stats(conn)
    
    if st.session_state.db_stats:
        stats = st.session_state.db_stats
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🎯 Risks", stats.get("risks", 0))
        with col2:
            st.metric("🏆 TPOs", stats.get("tpos", 0))
        with col3:
            st.metric("🛡️ Mitigations", stats.get("mitigations", 0))
        with col4:
            st.metric("🔗 Influences", stats.get("influences", 0))
        with col5:
            st.metric("📌 Impacts", stats.get("impacts", 0))
        
        # Detailed breakdown
        with st.expander("📋 Detailed Breakdown", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Risk Levels:**")
                for level, count in stats.get("risks_by_level", {}).items():
                    st.markdown(f"- {level}: {count}")
                
                st.markdown("**Risk Categories:**")
                for cat, count in stats.get("risks_by_category", {}).items():
                    st.markdown(f"- {cat}: {count}")
            
            with col2:
                st.markdown("**TPO Clusters:**")
                for cluster, count in stats.get("tpos_by_cluster", {}).items():
                    st.markdown(f"- {cluster}: {count}")
                
                st.markdown("**Mitigation Types:**")
                for mit_type, count in stats.get("mits_by_type", {}).items():
                    st.markdown(f"- {mit_type}: {count}")
    
    st.markdown("---")
    
    # Schema compatibility check
    st.subheader("🔍 Schema Compatibility Check")
    
    if st.button("Check Schema vs Database"):
        check_schema_compatibility(conn, st.session_state.active_schema)
    
    st.markdown("---")
    
    # Migration tools
    st.subheader("🔄 Migration Tools")
    st.info("Migration tools detect schema changes and generate Cypher scripts to update database data.")
    
    with st.expander("Migration Generation", expanded=False):
        st.markdown("**Detected Changes:**")
        st.caption("Compare current database values with schema configuration")
        
        if st.button("🔍 Detect Required Migrations"):
            detect_migrations(conn, st.session_state.active_schema)


def get_database_stats(conn: Neo4jConnection) -> Dict[str, Any]:
    """Get database statistics."""
    stats = {}
    
    try:
        # Node counts
        result = conn.execute_query("MATCH (r:Risk) RETURN count(r) as count")
        stats["risks"] = result[0]["count"] if result else 0
        
        result = conn.execute_query("MATCH (t:TPO) RETURN count(t) as count")
        stats["tpos"] = result[0]["count"] if result else 0
        
        result = conn.execute_query("MATCH (m:Mitigation) RETURN count(m) as count")
        stats["mitigations"] = result[0]["count"] if result else 0
        
        # Relationship counts
        result = conn.execute_query("MATCH ()-[i:INFLUENCES]->() RETURN count(i) as count")
        stats["influences"] = result[0]["count"] if result else 0
        
        result = conn.execute_query("MATCH ()-[i:IMPACTS_TPO]->() RETURN count(i) as count")
        stats["impacts"] = result[0]["count"] if result else 0
        
        result = conn.execute_query("MATCH ()-[m:MITIGATES]->() RETURN count(m) as count")
        stats["mitigates"] = result[0]["count"] if result else 0
        
        # Breakdowns
        result = conn.execute_query("MATCH (r:Risk) RETURN r.level as level, count(r) as count")
        stats["risks_by_level"] = {r["level"]: r["count"] for r in result}
        
        result = conn.execute_query("MATCH (r:Risk) UNWIND r.categories as cat RETURN cat, count(r) as count")
        stats["risks_by_category"] = {r["cat"]: r["count"] for r in result}
        
        result = conn.execute_query("MATCH (t:TPO) RETURN t.cluster as cluster, count(t) as count")
        stats["tpos_by_cluster"] = {r["cluster"]: r["count"] for r in result}
        
        result = conn.execute_query("MATCH (m:Mitigation) RETURN m.type as type, count(m) as count")
        stats["mits_by_type"] = {r["type"]: r["count"] for r in result}
        
    except Exception as e:
        st.error(f"Error getting stats: {e}")
    
    return stats


def check_schema_compatibility(conn: Neo4jConnection, schema: SchemaConfig):
    """Check if database values match schema configuration."""
    issues = []
    
    try:
        # Check risk levels
        result = conn.execute_query("MATCH (r:Risk) RETURN DISTINCT r.level as level")
        db_levels = {r["level"] for r in result if r["level"]}
        schema_levels = set(schema.risk_levels)
        
        orphan_levels = db_levels - schema_levels
        if orphan_levels:
            issues.append(f"⚠️ **Risk levels in DB not in schema:** {orphan_levels}")
        
        # Check categories
        result = conn.execute_query("MATCH (r:Risk) UNWIND r.categories as cat RETURN DISTINCT cat")
        db_cats = {r["cat"] for r in result if r["cat"]}
        schema_cats = set(schema.risk_categories)
        
        orphan_cats = db_cats - schema_cats
        if orphan_cats:
            issues.append(f"⚠️ **Categories in DB not in schema:** {orphan_cats}")
        
        # Check TPO clusters
        result = conn.execute_query("MATCH (t:TPO) RETURN DISTINCT t.cluster as cluster")
        db_clusters = {r["cluster"] for r in result if r["cluster"]}
        schema_clusters = set(schema.tpo_clusters)
        
        orphan_clusters = db_clusters - schema_clusters
        if orphan_clusters:
            issues.append(f"⚠️ **TPO clusters in DB not in schema:** {orphan_clusters}")
        
        # Check mitigation types
        result = conn.execute_query("MATCH (m:Mitigation) RETURN DISTINCT m.type as type")
        db_types = {r["type"] for r in result if r["type"]}
        schema_types = set(schema.mitigation_types)
        
        orphan_types = db_types - schema_types
        if orphan_types:
            issues.append(f"⚠️ **Mitigation types in DB not in schema:** {orphan_types}")
        
        # Check influence strengths
        result = conn.execute_query("MATCH ()-[i:INFLUENCES]->() RETURN DISTINCT i.strength as strength")
        db_strengths = {r["strength"] for r in result if r["strength"]}
        schema_strengths = set(schema.influence_strengths)
        
        orphan_strengths = db_strengths - schema_strengths
        if orphan_strengths:
            issues.append(f"⚠️ **Influence strengths in DB not in schema:** {orphan_strengths}")
        
        if issues:
            for issue in issues:
                st.warning(issue)
        else:
            st.success("✅ Database values are compatible with schema")
            
    except Exception as e:
        st.error(f"Error checking compatibility: {e}")


def detect_migrations(conn: Neo4jConnection, schema: SchemaConfig):
    """Detect required migrations based on schema changes."""
    migrations = []
    
    try:
        # Get current values
        result = conn.execute_query("MATCH (r:Risk) RETURN DISTINCT r.level as level")
        db_levels = {r["level"] for r in result if r["level"]}
        schema_levels = set(schema.risk_levels)
        
        orphan_levels = db_levels - schema_levels
        for level in orphan_levels:
            st.markdown(f"""
**Level: `{level}`** not found in schema

Suggested migration:
```cypher
// Option 1: Rename to existing level
MATCH (r:Risk) WHERE r.level = '{level}' 
SET r.level = '<new_level_name>'

// Option 2: Delete risks with this level
MATCH (r:Risk) WHERE r.level = '{level}' 
DETACH DELETE r
```
""")
        
        if not orphan_levels:
            st.info("No migrations needed for risk levels")
            
    except Exception as e:
        st.error(f"Error detecting migrations: {e}")


# =============================================================================
# DATA MANAGEMENT TAB
# =============================================================================


def render_demo_reset_section(conn):
    """Render the demo data reset section."""
    st.markdown("### 🔄 Reset Demo Data")
    st.info(
        "Wipes the **entire database** and reloads both the ODT New Space demo dataset "
        "and all 7 TC test cases (TC01-TC07) to a clean, reproducible state."
    )

    app_root = Path(__file__).parent.parent
    odt_path = app_root / "demo_data_loader_en.cypher"
    tc_path  = app_root / "demo_tc_dataset.cypher"

    # Show file availability status
    col_a, col_b = st.columns(2)
    with col_a:
        if odt_path.exists():
            st.success(f"✅ ODT file found: `{odt_path.name}`")
        else:
            st.error(f"❌ ODT file missing: `demo_data_loader_en.cypher`")
    with col_b:
        if tc_path.exists():
            st.success(f"✅ TC file found: `{tc_path.name}`")
        else:
            st.error(f"❌ TC file missing: `demo_tc_dataset.cypher`")

    files_ok = odt_path.exists() and tc_path.exists()

    confirmed = st.checkbox(
        "⚠️ I understand this will delete ALL data in the database and reload the demo",
        key="reset_demo_confirm"
    )

    if st.button(
        "🔄 Reset Demo Data",
        type="primary",
        disabled=(not confirmed or not files_ok),
        key="reset_demo_btn"
    ):
        _execute_demo_reset(conn, odt_path, tc_path)


def _execute_demo_reset(conn, odt_path, tc_path):
    """Execute the full demo reset: wipe all data, reload ODT + TC datasets."""

    def _parse_statements(cypher_text, skip_purge=False):
        """
        Split a Cypher script into individual executable statements.

        Rules:
        - Split on semicolon (;) -- each statement ends with ;
        - Strip whitespace from each statement
        - Discard empty statements
        - Discard comment-only statements (lines that are all // comments)
        - If skip_purge=True, discard any statement containing DETACH DELETE
          (to avoid re-running the ODT file's built-in purge line)
        """
        raw_statements = cypher_text.split(";")
        result = []
        for raw in raw_statements:
            stmt = raw.strip()
            if not stmt:
                continue
            # Keep only if at least one line is not a comment/blank
            non_comment_lines = [
                line for line in stmt.splitlines()
                if line.strip() and not line.strip().startswith("//")
            ]
            if not non_comment_lines:
                continue
            if skip_purge and "DETACH DELETE" in stmt.upper():
                continue
            result.append(stmt)
        return result

    try:
        with st.spinner("Resetting demo data — this may take a few seconds..."):

            # Step 1: Count existing nodes for before/after feedback
            before_result = conn.execute_query("MATCH (n) RETURN count(n) AS cnt")
            before_count = before_result[0]["cnt"] if before_result else 0

            # Step 2: Wipe the entire database
            st.write("🗑️ Wiping database...")
            conn.execute_write("MATCH (n) DETACH DELETE n")

            # Step 3: Load ODT dataset
            # skip_purge=True because demo_data_loader_en.cypher has its own
            # MATCH (n) DETACH DELETE n; at line 8 -- skip it since we already wiped.
            odt_text = odt_path.read_text(encoding="utf-8")
            odt_statements = _parse_statements(odt_text, skip_purge=True)

            st.write(f"📥 Loading ODT dataset ({len(odt_statements)} statements)...")
            odt_progress = st.progress(0.0, text="Loading ODT data...")
            for i, stmt in enumerate(odt_statements):
                conn.execute_write(stmt)
                odt_progress.progress(
                    (i + 1) / len(odt_statements),
                    text=f"ODT (New Space): {i + 1}/{len(odt_statements)}"
                )
            odt_progress.empty()

            # Step 4: Load TC datasets
            # skip_purge=False: demo_tc_dataset.cypher uses only MERGE, no purge.
            tc_text = tc_path.read_text(encoding="utf-8")
            tc_statements = _parse_statements(tc_text, skip_purge=False)

            st.write(f"📥 Loading TC datasets ({len(tc_statements)} statements)...")
            tc_progress = st.progress(0.0, text="Loading TC data...")
            for i, stmt in enumerate(tc_statements):
                conn.execute_write(stmt)
                tc_progress.progress(
                    (i + 1) / len(tc_statements),
                    text=f"TC: {i + 1}/{len(tc_statements)}"
                )
            tc_progress.empty()

            # Step 5: Count after
            after_result = conn.execute_query("MATCH (n) RETURN count(n) AS cnt")
            after_count = after_result[0]["cnt"] if after_result else 0

            # Success feedback
            st.success(
                f"✅ Reset complete — "
                f"deleted **{before_count}** nodes, "
                f"loaded **{after_count}** nodes "
                f"({len(odt_statements)} ODT + {len(tc_statements)} TC statements executed)."
            )

            # Invalidate cached stats so the Database tab refreshes
            st.session_state.db_stats = None

    except Exception as e:
        import traceback
        st.error(f"❌ Reset failed: {e}")
        with st.expander("Full traceback"):
            st.code(traceback.format_exc())


def render_data_management():
    """Render data management tab."""
    schema = st.session_state.active_schema

    if not schema:
        st.warning("No schema loaded. Select a schema from the sidebar.")
        return

    st.subheader("📊 Data Management")

    # Guard: require DB connection for ALL operations in this tab
    if not st.session_state.config_connected:
        st.warning("Connect to Neo4j database for data management features.")
        return

    conn = st.session_state.config_connection

    # NEW: Demo Reset section (top of tab)
    render_demo_reset_section(conn)
    st.markdown("---")

    # Test Data Generator
    st.markdown("### 🧪 Generate Test Data")
    st.info("Generate Cypher script with sample data matching your schema configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_risks_per_level = st.number_input("Risks per level", 2, 20, 5, key="test_num_risks")
    with col2:
        num_tpos = st.number_input("TPOs (total)", 2, 15, 5, key="test_num_tpos")
    with col3:
        num_mitigations = st.number_input("Mitigations", 2, 20, 8, key="test_num_mits")
    
    if st.button("🔧 Generate Cypher Script", type="primary"):
        cypher_script = generate_test_data_cypher(
            schema, num_risks_per_level, num_tpos, num_mitigations
        )
        st.session_state.generated_cypher = cypher_script
        st.success(f"Generated {len(cypher_script.split(';'))} Cypher statements!")
    
    if st.session_state.get("generated_cypher"):
        cypher = st.session_state.generated_cypher
        
        # Preview
        with st.expander("📄 Preview Generated Cypher", expanded=False):
            st.code(cypher[:3000] + ("..." if len(cypher) > 3000 else ""), language="cypher")
        
        col1, col2 = st.columns(2)
        
        with col1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "📥 Download Cypher File",
                cypher,
                f"test_data_{st.session_state.active_schema_name}_{timestamp}.cypher",
                "text/plain"
            )
        
        with col2:
            if st.session_state.config_connected:
                if st.button("⚡ Load Directly to Database"):
                    try:
                        conn = st.session_state.config_connection
                        statements = [s.strip() for s in cypher.split(';') if s.strip()]
                        
                        progress = st.progress(0)
                        for i, stmt in enumerate(statements):
                            if stmt:
                                conn.execute_write(stmt)
                            progress.progress((i + 1) / len(statements))
                        
                        st.success("Test data loaded successfully!")
                        st.session_state.db_stats = None
                    except Exception as e:
                        st.error(f"Error loading data: {e}")
            else:
                st.info("Connect to DB to load directly")
    
    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗑️ Clear Database")
        st.warning("This will delete all nodes and relationships!")
        
        confirm_text = st.text_input("Type 'DELETE ALL' to confirm", key="clear_confirm")
        
        if st.button("🗑️ Clear Database", type="primary", disabled=confirm_text != "DELETE ALL"):
            try:
                conn.execute_write("MATCH (n) DETACH DELETE n")
                st.success("Database cleared successfully!")
                st.session_state.db_stats = None
            except Exception as e:
                st.error(f"Error clearing database: {e}")
    
    with col2:
        st.markdown("### 📥 Load Demo Data")
        st.info("Load sample data for testing")
        
        schema_name = st.session_state.active_schema_name
        demo_file = Path(__file__).parent / f"demo_data_loader_en.cypher"
        
        if demo_file.exists():
            if st.button("📥 Load Demo Data"):
                try:
                    with open(demo_file, 'r') as f:
                        cypher_script = f.read()
                    
                    # Execute in chunks
                    statements = [s.strip() for s in cypher_script.split(';') if s.strip()]
                    
                    progress = st.progress(0)
                    for i, stmt in enumerate(statements):
                        if stmt:
                            conn.execute_write(stmt)
                        progress.progress((i + 1) / len(statements))
                    
                    st.success("Demo data loaded!")
                    st.session_state.db_stats = None
                except Exception as e:
                    st.error(f"Error loading demo data: {e}")
        else:
            st.warning("Demo data file not found")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Backup to JSON")
        
        if st.button("📦 Create Backup"):
            try:
                backup_data = create_json_backup(conn)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rim_backup_{timestamp}.json"
                
                st.download_button(
                    "📥 Download Backup",
                    json.dumps(backup_data, indent=2, default=str),
                    filename,
                    "application/json"
                )
            except Exception as e:
                st.error(f"Backup error: {e}")
    
    with col2:
        st.markdown("### 📂 Restore from JSON")
        
        uploaded = st.file_uploader("Upload backup JSON", type="json", key="restore_upload")
        
        if uploaded and st.button("📤 Restore"):
            try:
                backup_data = json.load(uploaded)
                restore_from_json(conn, backup_data)
                st.success("Restore complete!")
                st.session_state.db_stats = None
            except Exception as e:
                st.error(f"Restore error: {e}")


def generate_test_data_cypher(schema: SchemaConfig, risks_per_level: int, 
                               num_tpos: int, num_mitigations: int) -> str:
    """
    Generate Cypher script with test data based on schema configuration.
    
    Creates:
    - Risks for each level with varied categories, statuses, origins
    - TPOs distributed across clusters
    - Mitigations with different types and statuses
    - Influence relationships between risks
    - Mitigation links to risks
    - TPO impact links from strategic risks
    """
    import random
    
    lines = []
    lines.append("// Test data generated from schema: " + schema.name)
    lines.append("// Generated: " + datetime.now().isoformat())
    lines.append("")
    
    # Get schema values
    levels = [l.label for l in schema.risk.levels]
    categories = [c.label for c in schema.risk.categories]
    statuses = [s.label for s in schema.risk.statuses if s.is_active]
    origins = [o.label for o in schema.risk.origins]
    clusters = [c.label for c in schema.tpo.clusters]
    mit_types = [t.label for t in schema.mitigation.types]
    mit_statuses = [s.label for s in schema.mitigation.statuses]
    strengths = [s.label for s in schema.influences.strengths]
    effectiveness_levels = [e.label for e in schema.mitigates.effectiveness_levels]
    impact_levels = [il.label for il in schema.impacts_tpo.impact_levels]
    
    risk_refs = []
    tpo_refs = []
    mit_refs = []
    
    # Generate Risks
    lines.append("// ===== RISKS =====")
    risk_counter = 1
    for level in levels:
        for i in range(risks_per_level):
            ref = f"R{risk_counter:03d}"
            risk_refs.append((ref, level))
            
            cat = random.choice(categories)
            status = random.choice(statuses) if statuses else "Active"
            origin = random.choice(origins) if origins else "New"
            likelihood = random.randint(1, 10)
            impact = random.randint(1, 10)
            
            name = f"Test {level} Risk {i+1}"
            desc = f"Sample {level.lower()} risk in {cat} category for testing"
            
            lines.append(f"""
CREATE (r{risk_counter}:Risk {{
    reference: '{ref}',
    name: '{name}',
    description: '{desc}',
    level: '{level}',
    category: '{cat}',
    status: '{status}',
    origin: '{origin}',
    likelihood: {likelihood},
    impact: {impact},
    is_contingent: false,
    is_legacy: {'true' if origin == 'Legacy' else 'false'}
}})""")
            risk_counter += 1
    
    # Generate TPOs
    lines.append("")
    lines.append("// ===== TPOs =====")
    for i in range(num_tpos):
        ref = f"TPO{i+1:02d}"
        tpo_refs.append(ref)
        
        cluster = clusters[i % len(clusters)]
        name = f"Test {cluster} Objective {i+1}"
        desc = f"Sample TPO in {cluster} cluster"
        
        lines.append(f"""
CREATE (tpo{i+1}:TPO {{
    reference: '{ref}',
    name: '{name}',
    description: '{desc}',
    cluster: '{cluster}'
}})""")
    
    # Generate Mitigations
    lines.append("")
    lines.append("// ===== MITIGATIONS =====")
    for i in range(num_mitigations):
        ref = f"MIT{i+1:03d}"
        mit_refs.append(ref)
        
        mit_type = mit_types[i % len(mit_types)]
        mit_status = mit_statuses[i % len(mit_statuses)]
        name = f"Test {mit_type} Mitigation {i+1}"
        desc = f"Sample {mit_type.lower()} mitigation measure"
        
        lines.append(f"""
CREATE (m{i+1}:Mitigation {{
    reference: '{ref}',
    name: '{name}',
    description: '{desc}',
    type: '{mit_type}',
    status: '{mit_status}'
}})""")
    
    # Generate Influence relationships
    lines.append("")
    lines.append("// ===== INFLUENCES =====")
    influence_count = 0
    
    # Strategic risks influenced by operational
    strategic_risks = [(ref, idx) for idx, (ref, lvl) in enumerate(risk_refs, 1) if lvl == levels[0]]
    operational_risks = [(ref, idx) for idx, (ref, lvl) in enumerate(risk_refs, 1) if lvl != levels[0]]
    
    for strat_ref, strat_idx in strategic_risks[:min(5, len(strategic_risks))]:
        # Each strategic risk influenced by 1-3 operational risks
        num_influences = min(random.randint(1, 3), len(operational_risks))
        for op_ref, op_idx in random.sample(operational_risks, num_influences):
            strength = random.choice(strengths)
            confidence = round(random.uniform(0.6, 1.0), 2)
            
            lines.append(f"""
MATCH (from:Risk {{reference: '{op_ref}'}}), (to:Risk {{reference: '{strat_ref}'}})
CREATE (from)-[:INFLUENCES {{
    influence_type: 'L1',
    strength: '{strength}',
    confidence: {confidence},
    description: 'Test influence relationship'
}}]->(to)""")
            influence_count += 1
    
    # Some L2 influences between strategic risks
    if len(strategic_risks) >= 2:
        for i in range(min(3, len(strategic_risks) - 1)):
            src = strategic_risks[i]
            tgt = strategic_risks[(i + 1) % len(strategic_risks)]
            strength = random.choice(strengths)
            
            lines.append(f"""
MATCH (from:Risk {{reference: '{src[0]}'}}), (to:Risk {{reference: '{tgt[0]}'}})
CREATE (from)-[:INFLUENCES {{
    influence_type: 'L2',
    strength: '{strength}',
    confidence: 0.8,
    description: 'Strategic amplification'
}}]->(to)""")
    
    # Generate Mitigates relationships
    lines.append("")
    lines.append("// ===== MITIGATES =====")
    for i, mit_ref in enumerate(mit_refs):
        # Each mitigation covers 1-3 risks
        num_targets = min(random.randint(1, 3), len(risk_refs))
        target_risks = random.sample(risk_refs, num_targets)
        
        for risk_ref, _ in target_risks:
            effectiveness = random.choice(effectiveness_levels)
            
            lines.append(f"""
MATCH (m:Mitigation {{reference: '{mit_ref}'}}), (r:Risk {{reference: '{risk_ref}'}})
CREATE (m)-[:MITIGATES {{
    effectiveness: '{effectiveness}',
    description: 'Test mitigation link'
}}]->(r)""")
    
    # Generate IMPACTS_TPO relationships
    lines.append("")
    lines.append("// ===== TPO IMPACTS =====")
    for strat_ref, _ in strategic_risks[:min(5, len(strategic_risks))]:
        # Each strategic risk impacts 1-2 TPOs
        num_impacts = min(random.randint(1, 2), len(tpo_refs))
        target_tpos = random.sample(tpo_refs, num_impacts)
        
        for tpo_ref in target_tpos:
            impact_level = random.choice(impact_levels)
            
            lines.append(f"""
MATCH (r:Risk {{reference: '{strat_ref}'}}), (t:TPO {{reference: '{tpo_ref}'}})
CREATE (r)-[:IMPACTS_TPO {{
    impact_level: '{impact_level}',
    description: 'Test TPO impact'
}}]->(t)""")
    
    # ===== CONTEXT NODES =====
    context_node_refs = {}  # node_type_id -> list of references
    
    for context_node in schema.context_nodes:
        node_type_id = context_node.id
        context_node_refs[node_type_id] = []
        
        lines.append("")
        lines.append(f"// ===== CONTEXT NODE: {context_node.label.upper()} =====")
        
        # Generate a few instances of each context node
        num_instances = min(5, num_tpos)  # Use TPO count as rough guide
        for i in range(num_instances):
            ref = f"{node_type_id.upper()[:3]}{i+1:02d}"
            context_node_refs[node_type_id].append(ref)
            
            name = f"Test {context_node.label} {i+1}"
            desc = f"Sample {context_node.label.lower()} for testing"
            
            # Build attributes string — always include node_type, source
            attrs = [
                f"reference: '{ref}'",
                f"node_type: '{node_type_id}'",
                f"source: 'test_generator'",
                f"name: '{name}'",
                f"description: '{desc}'"
            ]
            
            # Add custom properties with random values
            for attr in context_node.properties:
                if attr.name not in ['reference', 'name', 'description', 'node_type', 'source', 'import_adapter']:
                    if attr.type == 'int':
                        attrs.append(f"{attr.name}: {random.randint(1, 10)}")
                    elif attr.type == 'float':
                        attrs.append(f"{attr.name}: {round(random.uniform(0, 10), 2)}")
                    elif attr.type == 'boolean':
                        attrs.append(f"{attr.name}: {'true' if random.random() > 0.5 else 'false'}")
                    else:
                        attrs.append(f"{attr.name}: 'Sample {attr.name}'")
            
            attrs_str = ",\\n    ".join(attrs)
            lines.append(f"""
CREATE (cn{node_type_id}_{i+1}:ContextNode {{
    {attrs_str}
}})""")
    
    # ===== CONTEXT EDGES =====
    for context_edge in schema.context_edges:
        lines.append("")
        lines.append(f"// ===== CONTEXT EDGE: {context_edge.label.upper()} =====")
        
        neo4j_type = context_edge.neo4j_type
        from_node = context_edge.from_node
        to_node = context_edge.to_node
        
        # Get source and target references
        if from_node == "risk":
            from_refs = [(ref, level) for ref, level in risk_refs[:5]]
            from_label = "Risk"
        elif from_node == "tpo":
            from_refs = [(ref, None) for ref in tpo_refs[:5]]
            from_label = "TPO"
        elif from_node == "mitigation":
            from_refs = [(ref, None) for ref in mit_refs[:5]]
            from_label = "Mitigation"
        elif from_node in context_node_refs:
            from_refs = [(ref, None) for ref in context_node_refs.get(from_node, [])[:5]]
            from_label = "ContextNode"
        else:
            continue
        
        if to_node == "risk":
            to_refs = [(ref, level) for ref, level in risk_refs[:5]]
            to_label = "Risk"
        elif to_node == "tpo":
            to_refs = [(ref, None) for ref in tpo_refs[:5]]
            to_label = "TPO"
        elif to_node == "mitigation":
            to_refs = [(ref, None) for ref in mit_refs[:5]]
            to_label = "Mitigation"
        elif to_node in context_node_refs:
            to_refs = [(ref, None) for ref in context_node_refs.get(to_node, [])[:5]]
            to_label = "ContextNode"
        else:
            continue
        
        # Create some relationships
        if from_refs and to_refs:
            for j, (from_ref, _) in enumerate(from_refs[:3]):
                to_ref, _ = random.choice(to_refs)
                
                # Build attributes string
                rel_attrs = [f"description: 'Test {context_edge.label} relationship'"]
                
                for attr in context_edge.properties:
                    if attr.type == 'int':
                        rel_attrs.append(f"{attr.name}: {random.randint(1, 10)}")
                    elif attr.type == 'float':
                        rel_attrs.append(f"{attr.name}: {round(random.uniform(0, 1), 2)}")
                    elif attr.type == 'boolean':
                        rel_attrs.append(f"{attr.name}: {'true' if random.random() > 0.5 else 'false'}")
                    else:
                        rel_attrs.append(f"{attr.name}: 'Sample'")
                
                rel_attrs_str = ",\\n    ".join(rel_attrs)
                
                lines.append(f"""
MATCH (from:{from_label} {{reference: '{from_ref}'}}), (to:{to_label} {{reference: '{to_ref}'}})
CREATE (from)-[:{neo4j_type} {{
    {rel_attrs_str}
}}]->(to)""")
    
    lines.append("")
    lines.append("// ===== END OF TEST DATA =====")
    
    return ";\n".join(lines) + ";"


def create_json_backup(conn: Neo4jConnection) -> Dict[str, Any]:
    """Create JSON backup of database."""
    backup = {
        "timestamp": datetime.now().isoformat(),
        "risks": [],
        "tpos": [],
        "mitigations": [],
        "influences": [],
        "tpo_impacts": [],
        "mitigates": []
    }
    
    # Export nodes
    result = conn.execute_query("MATCH (r:Risk) RETURN properties(r) as props")
    backup["risks"] = [r["props"] for r in result]
    
    result = conn.execute_query("MATCH (t:TPO) RETURN properties(t) as props")
    backup["tpos"] = [r["props"] for r in result]
    
    result = conn.execute_query("MATCH (m:Mitigation) RETURN properties(m) as props")
    backup["mitigations"] = [r["props"] for r in result]
    
    # Export relationships
    result = conn.execute_query("""
        MATCH (s:Risk)-[i:INFLUENCES]->(t:Risk)
        RETURN properties(i) as props, s.id as source_id, t.id as target_id
    """)
    backup["influences"] = [{"props": r["props"], "source_id": r["source_id"], "target_id": r["target_id"]} for r in result]
    
    result = conn.execute_query("""
        MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
        RETURN properties(i) as props, r.id as risk_id, t.id as tpo_id
    """)
    backup["tpo_impacts"] = [{"props": r["props"], "risk_id": r["risk_id"], "tpo_id": r["tpo_id"]} for r in result]
    
    result = conn.execute_query("""
        MATCH (m:Mitigation)-[mi:MITIGATES]->(r:Risk)
        RETURN properties(mi) as props, m.id as mitigation_id, r.id as risk_id
    """)
    backup["mitigates"] = [{"props": r["props"], "mitigation_id": r["mitigation_id"], "risk_id": r["risk_id"]} for r in result]
    
    return backup


def restore_from_json(conn: Neo4jConnection, backup: Dict[str, Any]):
    """Restore database from JSON backup."""
    # Clear existing data
    conn.execute_write("MATCH (n) DETACH DELETE n")
    
    # Restore nodes
    for risk in backup.get("risks", []):
        params = {"props": risk}
        conn.execute_write("CREATE (r:Risk) SET r = $props", params)
    
    for tpo in backup.get("tpos", []):
        params = {"props": tpo}
        conn.execute_write("CREATE (t:TPO) SET t = $props", params)
    
    for mit in backup.get("mitigations", []):
        params = {"props": mit}
        conn.execute_write("CREATE (m:Mitigation) SET m = $props", params)
    
    # Restore relationships
    for inf in backup.get("influences", []):
        params = {"source_id": inf["source_id"], "target_id": inf["target_id"], "props": inf["props"]}
        conn.execute_write("""
            MATCH (s:Risk {id: $source_id}), (t:Risk {id: $target_id})
            CREATE (s)-[i:INFLUENCES]->(t) SET i = $props
        """, params)
    
    for impact in backup.get("tpo_impacts", []):
        params = {"risk_id": impact["risk_id"], "tpo_id": impact["tpo_id"], "props": impact["props"]}
        conn.execute_write("""
            MATCH (r:Risk {id: $risk_id}), (t:TPO {id: $tpo_id})
            CREATE (r)-[i:IMPACTS_TPO]->(t) SET i = $props
        """, params)
    
    for mit in backup.get("mitigates", []):
        params = {"mitigation_id": mit["mitigation_id"], "risk_id": mit["risk_id"], "props": mit["props"]}
        conn.execute_write("""
            MATCH (m:Mitigation {id: $mitigation_id}), (r:Risk {id: $risk_id})
            CREATE (m)-[mi:MITIGATES]->(r) SET mi = $props
        """, params)


# =============================================================================
# HEALTH CHECK TAB
# =============================================================================

def render_health_check():
    """Render health check tab."""
    st.subheader("🔍 System Health Check")
    
    if st.button("▶️ Run Health Check", type="primary"):
        run_health_check()
    
    if st.session_state.health_report:
        render_health_report(st.session_state.health_report)


def run_health_check():
    """Run comprehensive health check."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "schema": {"status": "unknown", "issues": []},
        "database": {"status": "unknown", "issues": []},
        "integrity": {"status": "unknown", "issues": []}
    }
    
    # Schema check
    try:
        schema = st.session_state.active_schema
        if schema:
            errors = validate_schema(schema)
            if errors:
                report["schema"]["status"] = "warning"
                report["schema"]["issues"] = errors
            else:
                report["schema"]["status"] = "ok"
        else:
            report["schema"]["status"] = "error"
            report["schema"]["issues"] = ["No schema loaded"]
    except Exception as e:
        report["schema"]["status"] = "error"
        report["schema"]["issues"] = [str(e)]
    
    # Database check
    if st.session_state.config_connected:
        try:
            conn = st.session_state.config_connection
            conn.execute_query("RETURN 1")
            report["database"]["status"] = "ok"
        except Exception as e:
            report["database"]["status"] = "error"
            report["database"]["issues"] = [str(e)]
    else:
        report["database"]["status"] = "disconnected"
        report["database"]["issues"] = ["Not connected to database"]
    
    # Integrity check
    if st.session_state.config_connected and st.session_state.active_schema:
        try:
            conn = st.session_state.config_connection
            schema = st.session_state.active_schema
            
            issues = []
            
            # Check for orphan risks (no relationships)
            result = conn.execute_query("""
                MATCH (r:Risk)
                WHERE NOT (r)-[:INFLUENCES]-() AND NOT (r)-[:IMPACTS_TPO]->() AND NOT ()-[:MITIGATES]->(r)
                RETURN r.name as name, r.id as id
            """)
            if result:
                issues.append(f"Orphan risks (no relationships): {len(result)}")
            
            # Check for invalid enum values
            result = conn.execute_query("MATCH (r:Risk) WHERE NOT r.level IN $levels RETURN count(r) as count", 
                                       {"levels": schema.risk_levels})
            if result and result[0]["count"] > 0:
                issues.append(f"Risks with invalid level: {result[0]['count']}")
            
            # Check for missing required fields
            result = conn.execute_query("MATCH (r:Risk) WHERE r.name IS NULL RETURN count(r) as count")
            if result and result[0]["count"] > 0:
                issues.append(f"Risks without name: {result[0]['count']}")
            
            if issues:
                report["integrity"]["status"] = "warning"
                report["integrity"]["issues"] = issues
            else:
                report["integrity"]["status"] = "ok"
                
        except Exception as e:
            report["integrity"]["status"] = "error"
            report["integrity"]["issues"] = [str(e)]
    else:
        report["integrity"]["status"] = "skipped"
        report["integrity"]["issues"] = ["Database not connected or schema not loaded"]
    
    st.session_state.health_report = report


def render_health_report(report: Dict[str, Any]):
    """Render health check report."""
    st.markdown(f"**Last check:** {report['timestamp']}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = report["schema"]["status"]
        icon = "✅" if status == "ok" else "⚠️" if status == "warning" else "❌"
        st.markdown(f"### {icon} Schema")
        if report["schema"]["issues"]:
            for issue in report["schema"]["issues"]:
                st.warning(issue)
        elif status == "ok":
            st.success("Schema is valid")
    
    with col2:
        status = report["database"]["status"]
        icon = "✅" if status == "ok" else "⚠️" if status == "disconnected" else "❌"
        st.markdown(f"### {icon} Database")
        if report["database"]["issues"]:
            for issue in report["database"]["issues"]:
                st.warning(issue)
        elif status == "ok":
            st.success("Database connection OK")
    
    with col3:
        status = report["integrity"]["status"]
        icon = "✅" if status == "ok" else "⚠️" if status in ["warning", "skipped"] else "❌"
        st.markdown(f"### {icon} Data Integrity")
        if report["integrity"]["issues"]:
            for issue in report["integrity"]["issues"]:
                st.warning(issue)
        elif status == "ok":
            st.success("Data integrity OK")


# =============================================================================
# SCOPES TAB
# =============================================================================

def render_scopes_tab():
    """Render analysis scopes CRUD tab."""
    schema = st.session_state.active_schema
    
    if not schema:
        st.warning("No schema loaded. Select a schema from the sidebar.")
        return
    
    st.subheader("📐 Analysis Scopes")
    st.info("Define named subsets of graph nodes for focused analysis.")
    
    # Current scopes
    scopes = schema.scopes or []
    
    # ── Create new scope ──────────────────────────────────────────
    with st.expander("➕ Create New Scope", expanded=not scopes):
        with st.form("new_scope_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Scope ID", placeholder="fuel_chain")
                new_name = st.text_input("Display Name", placeholder="⛽ Fuel Supply Chain")
            with col2:
                new_desc = st.text_area("Description", placeholder="Risks related to fuel supply", height=68)
                new_color = st.color_picker("Scope Color", "#808080")
            
            # Node picker — list nodes from DB if connected
            node_options = []
            if st.session_state.get("config_connected"):
                try:
                    conn = st.session_state.config_connection
                    result = conn.execute_query(
                        "MATCH (n) WHERE n.id IS NOT NULL AND n.name IS NOT NULL "
                        "RETURN n.id AS id, n.name AS name, labels(n)[0] AS label ORDER BY label, n.name"
                    )
                    node_options = [
                        {"id": r["id"], "display": f"[{r['label']}] {r['name']}"}
                        for r in result
                    ]
                except Exception:
                    pass
            
            if node_options:
                display_map = {n["display"]: n["id"] for n in node_options}
                selected_displays = st.multiselect("Select Nodes", list(display_map.keys()))
                selected_node_ids = [display_map[d] for d in selected_displays]
            else:
                raw_ids = st.text_area("Node IDs (one per line)", placeholder="Paste UUIDs, one per line")
                selected_node_ids = [x.strip() for x in raw_ids.split("\n") if x.strip()]
            
            include_edges = st.checkbox("Include connected edges", value=True)
            
            submitted = st.form_submit_button("Create Scope", type="primary")
            if submitted and new_id and new_name:
                # Check for duplicate ID
                if any(s.id == new_id for s in scopes):
                    st.error(f"A scope with ID '{new_id}' already exists.")
                else:
                    from config.schema_loader import AnalysisScopeConfig
                    new_scope = AnalysisScopeConfig(
                        id=new_id,
                        name=new_name,
                        description=new_desc,
                        node_ids=selected_node_ids,
                        include_connected_edges=include_edges,
                        color=new_color,
                    )
                    schema.scopes.append(new_scope)
                    _save_active_schema(schema)
                    st.success(f"Scope '{new_name}' created with {len(selected_node_ids)} nodes.")
                    st.rerun()
    
    # ── Existing scopes ───────────────────────────────────────────
    if not scopes:
        st.caption("No scopes defined yet — create one above.")
        return
    
    for i, scope in enumerate(scopes):
        with st.expander(f"{scope.name}  •  {len(scope.node_ids)} nodes", expanded=False):
            col1, col2, col3 = st.columns([4, 4, 1])
            with col1:
                edited_name = st.text_input("Name", scope.name, key=f"scope_name_{scope.id}")
                edited_desc = st.text_area("Description", scope.description, key=f"scope_desc_{scope.id}", height=68)
            with col2:
                edited_color = st.color_picker("Color", scope.color, key=f"scope_color_{scope.id}")
                st.caption(f"**ID:** `{scope.id}`")
                st.caption(f"**Edges included:** {'Yes' if scope.include_connected_edges else 'No'}")
            with col3:
                if st.button("🗑️", key=f"del_scope_{scope.id}", help="Delete this scope"):
                    schema.scopes.pop(i)
                    _save_active_schema(schema)
                    st.rerun()
            
            # Save edits
            if edited_name != scope.name or edited_desc != scope.description or edited_color != scope.color:
                if st.button("💾 Save Changes", key=f"save_scope_{scope.id}"):
                    scope.name = edited_name
                    scope.description = edited_desc
                    scope.color = edited_color
                    _save_active_schema(schema)
                    st.success("Scope updated.")
                    st.rerun()
            
            # Node list
            if scope.node_ids:
                st.markdown(f"**Nodes ({len(scope.node_ids)}):**")
                st.code("\n".join(scope.node_ids[:50]) + ("\n..." if len(scope.node_ids) > 50 else ""))


def _save_active_schema(schema):
    """Save the active schema back to its YAML file."""
    loader = get_loader()
    schema_name = st.session_state.active_schema_name
    loader.save_schema(schema, schema_name)
    st.session_state.active_schema = schema


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    st.set_page_config(
        page_title="RIM Configuration Manager",
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("⚙️ RIM Configuration Manager")
    st.caption("Manage RIM application configuration through YAML schemas")
    
    init_session_state()
    
    # Sidebar: Connection & Active Schema
    with st.sidebar:
        render_connection_panel()
        render_active_schema_selector()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Schema Management",
        "📐 Scopes",
        "🗄️ Database",
        "📊 Data Management",
        "🔍 Health Check"
    ])
    
    with tab1:
        render_schema_management()
    
    with tab2:
        render_scopes_tab()
    
    with tab3:
        render_database_tab()
    
    with tab4:
        render_data_management()
    
    with tab5:
        render_health_check()


if __name__ == "__main__":
    main()
