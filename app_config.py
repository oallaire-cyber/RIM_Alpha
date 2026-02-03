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

# Internal imports
from config.schema_loader import (
    SchemaLoader, SchemaConfig, get_schema, reload_schema, list_schemas,
    LevelConfig, CategoryConfig, ClusterConfig, TypeConfig, StatusConfig,
    StrengthConfig, EffectivenessConfig, ImpactLevelConfig, CustomAttributeConfig,
    AttributeConfig, CustomEntityConfig, CustomRelationshipConfig,
    validate_schema, save_schema, get_loader
)
from database.connection import Neo4jConnection


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "config_connection" not in st.session_state:
        st.session_state.config_connection = None
    if "config_connected" not in st.session_state:
        st.session_state.config_connected = False
    if "active_schema_name" not in st.session_state:
        st.session_state.active_schema_name = "default"
    if "active_schema" not in st.session_state:
        st.session_state.active_schema = None
    if "schema_modified" not in st.session_state:
        st.session_state.schema_modified = False
    if "db_stats" not in st.session_state:
        st.session_state.db_stats = None
    if "health_report" not in st.session_state:
        st.session_state.health_report = None


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
    
    with st.sidebar.expander("Connection Settings", expanded=not st.session_state.config_connected):
        uri = st.text_input("URI", value="bolt://localhost:7687", key="cfg_neo4j_uri")
        user = st.text_input("User", value="neo4j", key="cfg_neo4j_user")
        password = st.text_input("Password", type="password", key="cfg_neo4j_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", type="primary", use_container_width=True):
                try:
                    conn = Neo4jConnection(uri, user, password)
                    conn.connect()
                    st.session_state.config_connection = conn
                    st.session_state.config_connected = True
                    st.success("Connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        
        with col2:
            if st.button("Disconnect", use_container_width=True, 
                        disabled=not st.session_state.config_connected):
                if st.session_state.config_connection:
                    st.session_state.config_connection.close()
                st.session_state.config_connection = None
                st.session_state.config_connected = False
                st.session_state.db_stats = None
                st.rerun()
    
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
# SCHEMA MANAGEMENT TAB
# =============================================================================

def render_schema_management():
    """Render schema management tab content."""
    schema = st.session_state.active_schema
    
    if not schema:
        st.warning("No schema loaded. Select a schema from the sidebar.")
        return
    
    # Sub-tabs for different schema sections
    subtab1, subtab2, subtab3, subtab4, subtab5, subtab6, subtab7, subtab8 = st.tabs([
        "⚙️ General",
        "🎯 Risk Config",
        "🏆 TPO Config", 
        "🛡️ Mitigation Config",
        "🔗 Relationships",
        "📦 Custom Entities",
        "🔀 Custom Relationships",
        "📄 YAML Preview"
    ])
    
    with subtab1:
        render_general_settings(schema)
    
    with subtab2:
        render_risk_config(schema)
    
    with subtab3:
        render_tpo_config(schema)
    
    with subtab4:
        render_mitigation_config(schema)
    
    with subtab5:
        render_relationship_config(schema)
    
    with subtab6:
        render_custom_entities_config(schema)
    
    with subtab7:
        render_custom_relationships_config(schema)
    
    with subtab8:
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
        origins.append({
            "id": f"new_origin_{len(origins)}",
            "label": "New Origin",
            "description": ""
        })
        st.session_state.schema_modified = True
        st.rerun()


def render_tpo_config(schema: SchemaConfig):
    """Render TPO configuration section."""
    st.subheader("🏆 TPO Configuration")
    
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


def render_custom_entities_config(schema: SchemaConfig):
    """Render custom entities configuration section."""
    st.subheader("📦 Custom Entities")
    st.info("Define custom node types beyond Risk, TPO, and Mitigation. These can be connected to core entities via custom relationships.")
    
    custom_entities = schema.custom_entities
    
    if not custom_entities:
        st.markdown("*No custom entities defined yet.*")
    
    # Display existing custom entities
    for i, entity in enumerate(custom_entities):
        with st.expander(f"{entity.emoji} {entity.label} ({entity.neo4j_label})", expanded=i == 0):
            col1, col2 = st.columns(2)
            
            with col1:
                new_id = st.text_input("ID", value=entity.id, key=f"ce_id_{i}")
                if new_id != entity.id:
                    entity.id = new_id
                    st.session_state.schema_modified = True
                
                new_label = st.text_input("Label", value=entity.label, key=f"ce_label_{i}")
                if new_label != entity.label:
                    entity.label = new_label
                    st.session_state.schema_modified = True
                
                new_neo4j = st.text_input("Neo4j Label", value=entity.neo4j_label, key=f"ce_neo4j_{i}")
                if new_neo4j != entity.neo4j_label:
                    entity.neo4j_label = new_neo4j
                    st.session_state.schema_modified = True
                
                new_desc = st.text_area("Description", value=entity.description, key=f"ce_desc_{i}", height=80)
                if new_desc != entity.description:
                    entity.description = new_desc
                    st.session_state.schema_modified = True
            
            with col2:
                new_color = st.color_picker("Color", value=entity.color, key=f"ce_color_{i}")
                if new_color != entity.color:
                    entity.color = new_color
                    st.session_state.schema_modified = True
                
                shape_options = ["dot", "box", "diamond", "hexagon", "star", "triangle", "triangleDown", "square"]
                current_shape_idx = shape_options.index(entity.shape) if entity.shape in shape_options else 0
                new_shape = st.selectbox("Shape", shape_options, index=current_shape_idx, key=f"ce_shape_{i}")
                if new_shape != entity.shape:
                    entity.shape = new_shape
                    st.session_state.schema_modified = True
                
                new_emoji = st.text_input("Emoji", value=entity.emoji, key=f"ce_emoji_{i}")
                if new_emoji != entity.emoji:
                    entity.emoji = new_emoji
                    st.session_state.schema_modified = True
                
                new_size = st.number_input("Size", value=entity.size, min_value=10, max_value=100, key=f"ce_size_{i}")
                if new_size != entity.size:
                    entity.size = new_size
                    st.session_state.schema_modified = True
            
            # Attributes editor
            st.markdown("##### Attributes")
            if entity.attributes:
                for j, attr in enumerate(entity.attributes):
                    cols = st.columns([2, 1, 1, 1])
                    with cols[0]:
                        st.text(attr.name)
                    with cols[1]:
                        st.text(attr.type)
                    with cols[2]:
                        st.text("Required" if attr.required else "Optional")
                    with cols[3]:
                        if st.button("🗑️", key=f"ce_attr_del_{i}_{j}"):
                            entity.attributes.pop(j)
                            st.session_state.schema_modified = True
                            st.rerun()
            
            # Add attribute
            with st.popover("➕ Add Attribute"):
                attr_name = st.text_input("Attribute Name", key=f"ce_new_attr_name_{i}")
                attr_type = st.selectbox("Type", ["string", "int", "float", "boolean", "date"], key=f"ce_new_attr_type_{i}")
                attr_required = st.checkbox("Required", key=f"ce_new_attr_req_{i}")
                attr_desc = st.text_input("Description", key=f"ce_new_attr_desc_{i}")
                
                if st.button("Add Attribute", key=f"ce_add_attr_{i}") and attr_name:
                    from config.schema_loader import AttributeConfig
                    entity.attributes.append(AttributeConfig(
                        name=attr_name,
                        type=attr_type,
                        required=attr_required,
                        description=attr_desc
                    ))
                    st.session_state.schema_modified = True
                    st.rerun()
            
            # Delete entity button
            if st.button(f"🗑️ Delete {entity.label}", key=f"ce_delete_{i}", type="secondary"):
                schema.custom_entities.pop(i)
                st.session_state.schema_modified = True
                st.rerun()
    
    # Add new entity button
    st.markdown("---")
    if st.button("➕ Add Custom Entity", type="primary"):
        schema.custom_entities.append(CustomEntityConfig(
            id=f"custom_{len(custom_entities) + 1}",
            label="New Entity",
            neo4j_label="CustomEntity",
            description="",
            color="#808080",
            shape="box",
            emoji="📦",
            size=30
        ))
        st.session_state.schema_modified = True
        st.rerun()


def render_custom_relationships_config(schema: SchemaConfig):
    """Render custom relationships configuration section."""
    st.subheader("🔀 Custom Relationships")
    st.info("Define custom relationships between entities. These can connect core entities (Risk, TPO, Mitigation) with custom entities or with each other.")
    
    custom_rels = schema.custom_relationships
    
    # Build list of available entities
    entity_options = ["risk", "tpo", "mitigation"]
    for ce in schema.custom_entities:
        entity_options.append(ce.id)
    
    if not custom_rels:
        st.markdown("*No custom relationships defined yet.*")
    
    # Display existing relationships
    for i, rel in enumerate(custom_rels):
        with st.expander(f"🔗 {rel.label}: {rel.from_entity} → {rel.to_entity}", expanded=i == 0):
            col1, col2 = st.columns(2)
            
            with col1:
                new_id = st.text_input("ID", value=rel.id, key=f"cr_id_{i}")
                if new_id != rel.id:
                    rel.id = new_id
                    st.session_state.schema_modified = True
                
                new_label = st.text_input("Label", value=rel.label, key=f"cr_label_{i}")
                if new_label != rel.label:
                    rel.label = new_label
                    st.session_state.schema_modified = True
                
                new_neo4j = st.text_input("Neo4j Type", value=rel.neo4j_type, key=f"cr_neo4j_{i}")
                if new_neo4j != rel.neo4j_type:
                    rel.neo4j_type = new_neo4j
                    st.session_state.schema_modified = True
                
                new_desc = st.text_area("Description", value=rel.description, key=f"cr_desc_{i}", height=80)
                if new_desc != rel.description:
                    rel.description = new_desc
                    st.session_state.schema_modified = True
            
            with col2:
                from_idx = entity_options.index(rel.from_entity) if rel.from_entity in entity_options else 0
                new_from = st.selectbox("From Entity", entity_options, index=from_idx, key=f"cr_from_{i}")
                if new_from != rel.from_entity:
                    rel.from_entity = new_from
                    st.session_state.schema_modified = True
                
                to_idx = entity_options.index(rel.to_entity) if rel.to_entity in entity_options else 0
                new_to = st.selectbox("To Entity", entity_options, index=to_idx, key=f"cr_to_{i}")
                if new_to != rel.to_entity:
                    rel.to_entity = new_to
                    st.session_state.schema_modified = True
                
                new_color = st.color_picker("Color", value=rel.color, key=f"cr_color_{i}")
                if new_color != rel.color:
                    rel.color = new_color
                    st.session_state.schema_modified = True
                
                style_options = ["solid", "dashed", "dotted"]
                style_idx = style_options.index(rel.line_style) if rel.line_style in style_options else 0
                new_style = st.selectbox("Line Style", style_options, index=style_idx, key=f"cr_style_{i}")
                if new_style != rel.line_style:
                    rel.line_style = new_style
                    st.session_state.schema_modified = True
                
                new_bidir = st.checkbox("Bidirectional", value=rel.bidirectional, key=f"cr_bidir_{i}")
                if new_bidir != rel.bidirectional:
                    rel.bidirectional = new_bidir
                    st.session_state.schema_modified = True
            
            # Relationship attributes
            st.markdown("##### Relationship Attributes")
            if rel.attributes:
                for j, attr in enumerate(rel.attributes):
                    cols = st.columns([2, 1, 1, 1])
                    with cols[0]:
                        st.text(attr.name)
                    with cols[1]:
                        st.text(attr.type)
                    with cols[2]:
                        st.text("Required" if attr.required else "Optional")
                    with cols[3]:
                        if st.button("🗑️", key=f"cr_attr_del_{i}_{j}"):
                            rel.attributes.pop(j)
                            st.session_state.schema_modified = True
                            st.rerun()
            
            # Add attribute
            with st.popover("➕ Add Attribute"):
                attr_name = st.text_input("Attribute Name", key=f"cr_new_attr_name_{i}")
                attr_type = st.selectbox("Type", ["string", "int", "float", "boolean", "date"], key=f"cr_new_attr_type_{i}")
                attr_required = st.checkbox("Required", key=f"cr_new_attr_req_{i}")
                attr_desc = st.text_input("Description", key=f"cr_new_attr_desc_{i}")
                
                if st.button("Add Attribute", key=f"cr_add_attr_{i}") and attr_name:
                    from config.schema_loader import AttributeConfig
                    rel.attributes.append(AttributeConfig(
                        name=attr_name,
                        type=attr_type,
                        required=attr_required,
                        description=attr_desc
                    ))
                    st.session_state.schema_modified = True
                    st.rerun()
            
            # Delete relationship button
            if st.button(f"🗑️ Delete {rel.label}", key=f"cr_delete_{i}", type="secondary"):
                schema.custom_relationships.pop(i)
                st.session_state.schema_modified = True
                st.rerun()
    
    # Add new relationship button
    st.markdown("---")
    if st.button("➕ Add Custom Relationship", type="primary"):
        schema.custom_relationships.append(CustomRelationshipConfig(
            id=f"custom_rel_{len(custom_rels) + 1}",
            label="New Relationship",
            neo4j_type="CUSTOM_REL",
            description="",
            from_entity="risk",
            to_entity="tpo",
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

def render_data_management():
    """Render data management tab."""
    schema = st.session_state.active_schema
    
    if not schema:
        st.warning("No schema loaded. Select a schema from the sidebar.")
        return
    
    st.subheader("📊 Data Management")
    
    # Test Data Generator - doesn't require DB connection
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
    
    # Database operations require connection
    if not st.session_state.config_connected:
        st.warning("Connect to Neo4j database for additional data management features.")
        return
    
    conn = st.session_state.config_connection
    
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
    
    # ===== CUSTOM ENTITIES =====
    custom_entity_refs = {}  # entity_id -> list of references
    
    for custom_entity in schema.custom_entities:
        entity_id = custom_entity.id
        neo4j_label = custom_entity.neo4j_label
        custom_entity_refs[entity_id] = []
        
        lines.append("")
        lines.append(f"// ===== CUSTOM: {custom_entity.label.upper()} =====")
        
        # Generate a few instances of each custom entity
        num_instances = min(5, num_tpos)  # Use TPO count as rough guide
        for i in range(num_instances):
            ref = f"{entity_id.upper()[:3]}{i+1:02d}"
            custom_entity_refs[entity_id].append(ref)
            
            name = f"Test {custom_entity.label} {i+1}"
            desc = f"Sample {custom_entity.label.lower()} for testing"
            
            # Build attributes string
            attrs = [
                f"reference: '{ref}'",
                f"name: '{name}'",
                f"description: '{desc}'"
            ]
            
            # Add custom attributes with random values
            for attr in custom_entity.attributes:
                if attr.name not in ['reference', 'name', 'description']:
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
CREATE (ce{entity_id}_{i+1}:{neo4j_label} {{
    {attrs_str}
}})""")
    
    # ===== CUSTOM RELATIONSHIPS =====
    for custom_rel in schema.custom_relationships:
        lines.append("")
        lines.append(f"// ===== CUSTOM REL: {custom_rel.label.upper()} =====")
        
        neo4j_type = custom_rel.neo4j_type
        from_entity = custom_rel.from_entity
        to_entity = custom_rel.to_entity
        
        # Get source and target references
        if from_entity == "risk":
            from_refs = [(ref, level) for ref, level in risk_refs[:5]]
            from_label = "Risk"
        elif from_entity == "tpo":
            from_refs = [(ref, None) for ref in tpo_refs[:5]]
            from_label = "TPO"
        elif from_entity == "mitigation":
            from_refs = [(ref, None) for ref in mit_refs[:5]]
            from_label = "Mitigation"
        elif from_entity in custom_entity_refs:
            from_refs = [(ref, None) for ref in custom_entity_refs.get(from_entity, [])[:5]]
            # Find custom entity neo4j label
            from_label = next((ce.neo4j_label for ce in schema.custom_entities if ce.id == from_entity), "Custom")
        else:
            continue
        
        if to_entity == "risk":
            to_refs = [(ref, level) for ref, level in risk_refs[:5]]
            to_label = "Risk"
        elif to_entity == "tpo":
            to_refs = [(ref, None) for ref in tpo_refs[:5]]
            to_label = "TPO"
        elif to_entity == "mitigation":
            to_refs = [(ref, None) for ref in mit_refs[:5]]
            to_label = "Mitigation"
        elif to_entity in custom_entity_refs:
            to_refs = [(ref, None) for ref in custom_entity_refs.get(to_entity, [])[:5]]
            to_label = next((ce.neo4j_label for ce in schema.custom_entities if ce.id == to_entity), "Custom")
        else:
            continue
        
        # Create some relationships
        if from_refs and to_refs:
            for j, (from_ref, _) in enumerate(from_refs[:3]):
                to_ref, _ = random.choice(to_refs)
                
                # Build attributes string
                rel_attrs = [f"description: 'Test {custom_rel.label} relationship'"]
                
                for attr in custom_rel.attributes:
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Schema Management",
        "🗄️ Database",
        "📊 Data Management",
        "🔍 Health Check"
    ])
    
    with tab1:
        render_schema_management()
    
    with tab2:
        render_database_tab()
    
    with tab3:
        render_data_management()
    
    with tab4:
        render_health_check()


if __name__ == "__main__":
    main()
