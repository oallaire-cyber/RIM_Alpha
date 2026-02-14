"""
Legend Component for RIM Graph Visualization.

Provides a comprehensive visual legend showing node shapes,
colors, and edge types used in the Risk Influence Map.

Legend content is dynamically generated from the active schema registry.
"""

import streamlit as st
from core import get_registry


def render_graph_legend(expanded: bool = False):
    """
    Render the comprehensive graph legend in the sidebar.
    
    Args:
        expanded: Whether to expand the legend by default
    """
    registry = get_registry()
    with st.sidebar.expander("📖 Graph Legend", expanded=expanded):
        render_node_legend_sidebar(registry)
        st.markdown("---")
        render_edge_legend_sidebar(registry)
        st.markdown("---")
        render_status_legend_sidebar(registry)


def render_node_legend_sidebar(registry=None):
    """Render the node shapes and colors legend for sidebar."""
    registry = registry or get_registry()
    st.markdown("**🔷 Node Types**")
    
    nodes_html = '<div style="font-size: 12px; line-height: 1.6;">'
    
    # Render entity types from schema
    for entity_id, entity in registry.entity_types.items():
        # For risks, show each level separately
        if entity_id == "risk" and "levels" in entity.categorical_groups:
            for level in entity.categorical_groups["levels"]:
                color = level.get("color", entity.color)
                emoji = level.get("emoji", entity.emoji)
                shape = level.get("shape", entity.shape)
                label = level.get("label", level.get("id", "Risk"))
                nodes_html += f'<div style="margin-bottom: 6px;"><span style="font-size: 16px;">{emoji}</span> <strong style="color: {color};">{label} Risk</strong> <span style="color: #888;">- {shape.capitalize()}</span></div>'
        else:
            # Regular entity types (mitigation, TPO, etc.)
            color = entity.color
            emoji = entity.emoji
            shape = entity.shape
            label = entity.label
            nodes_html += f'<div style="margin-bottom: 6px;"><span style="font-size: 16px;">{emoji}</span> <strong style="color: {color};">{label}</strong> <span style="color: #888;">- {shape.capitalize()}</span></div>'
    
    nodes_html += '</div>'
    st.markdown(nodes_html, unsafe_allow_html=True)
    
    # Exposure gradient (handled by engines, but commonly these 4)
    st.markdown("**Exposure Colors**")
    st.markdown('<div style="font-size: 11px; line-height: 1.8;"><span style="background: #C0392B; color: white; padding: 1px 6px; border-radius: 3px;">Critical</span> <span style="background: #E74C3C; color: white; padding: 1px 6px; border-radius: 3px;">High</span> <span style="background: #F39C12; color: white; padding: 1px 6px; border-radius: 3px;">Medium</span> <span style="background: #F1C40F; color: #333; padding: 1px 6px; border-radius: 3px;">Low</span></div>', unsafe_allow_html=True)


def render_edge_legend_sidebar(registry=None):
    """Render the edge types legend for sidebar."""
    registry = registry or get_registry()
    st.markdown("**➡️ Edge Types**")
    
    edges_html = '<div style="font-size: 12px; line-height: 1.8;">'
    
    # Render all relationship types from schema
    for rel_id, rel in registry.relationship_types.items():
        color = rel.color
        label = rel.label
        style = rel.line_style
        
        # Simple line drawing based on style
        line = "━━" if style == "solid" else "──" if style == "dashed" else "┄┄"
        arrow = "►"
        if rel.is_mitigates_type:
            arrow = "⊣"
        
        edges_html += f'<div><span style="color: {color};">{line}{arrow}</span> <strong>{label}</strong></div>'
    
    edges_html += '</div>'
    st.markdown(edges_html, unsafe_allow_html=True)


def render_status_legend_sidebar(registry=None):
    """Render status indicators from schema."""
    registry = registry or get_registry()
    st.markdown("**📋 Key Categories**")
    
    # Show mitigation statuses as an example of categorical groups
    mit_type = registry.get_mitigation_type()
    if mit_type and "statuses" in mit_type.categorical_groups:
        st.markdown("*Mitigation Status*")
        status_html = '<div style="font-size: 11px; line-height: 1.6;">'
        for status in mit_type.categorical_groups["statuses"]:
            label = status.get("label", status.get("id"))
            icon = status.get("icon", "•")
            status_html += f'<div>{icon} {label}</div>'
        status_html += '</div>'
        st.markdown(status_html, unsafe_allow_html=True)


def render_compact_legend():
    """Render a compact one-line legend for quick reference."""
    registry = get_registry()
    items = []
    
    # Show entity types, with risk levels expanded
    for entity_id, entity in registry.entity_types.items():
        if entity_id == "risk" and "levels" in entity.categorical_groups:
            # Show each risk level separately
            for level in entity.categorical_groups["levels"]:
                color = level.get("color", entity.color)
                emoji = level.get("emoji", entity.emoji)
                label = level.get("label", "Risk")
                items.append(f'<span><strong style="color: {color};">{emoji}</strong> <span style="color: #000;">{label}</span></span>')
        else:
            items.append(f'<span><strong style="color: {entity.color};">{entity.emoji}</strong> <span style="color: #000;">{entity.label}</span></span>')
    
    # Major edges
    for rel in registry.relationship_types.values():
        line = "━" if rel.line_style == "solid" else "─"
        items.append(f'<span><span style="color: {rel.color};">{line}</span> <span style="color: #000;">{rel.label}</span></span>')
    
    st.markdown(f"""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; padding: 8px; background: #f8f9fa; border-radius: 8px; font-size: 12px; margin-bottom: 12px; color: #000000;">
        {' '.join(items)}
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_legend():
    """Render the legend in the sidebar."""
    render_graph_legend(expanded=False)


# Backward-compatible aliases
render_node_legend = render_node_legend_sidebar
render_edge_legend = render_edge_legend_sidebar
render_status_legend = render_status_legend_sidebar
