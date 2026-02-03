"""
Legend Component for RIM Graph Visualization.

Provides a comprehensive visual legend showing node shapes,
colors, and edge types used in the Risk Influence Map.

Legend content is dynamically generated from the active schema.
"""

import streamlit as st
from config.settings import (
    RISK_LEVEL_CONFIG, MITIGATION_TYPE_CONFIG, RISK_LEVELS,
    MITIGATION_TYPES, get_active_schema
)


def render_graph_legend(expanded: bool = False):
    """
    Render the comprehensive graph legend in the sidebar.
    
    Args:
        expanded: Whether to expand the legend by default
    """
    with st.sidebar.expander("📖 Graph Legend", expanded=expanded):
        render_node_legend_sidebar()
        st.markdown("---")
        render_edge_legend_sidebar()
        st.markdown("---")
        render_status_legend_sidebar()


def render_node_legend_sidebar():
    """Render the node shapes and colors legend for sidebar (single column)."""
    st.markdown("**🔷 Node Types**")
    
    # Build risk levels HTML dynamically from schema - use single line HTML to avoid rendering issues
    levels_html = '<div style="font-size: 12px; line-height: 1.6;">'
    
    for level in RISK_LEVELS:
        config = RISK_LEVEL_CONFIG.get(level, {})
        color = config.get("color", "#808080")
        emoji = config.get("emoji", "●")
        shape = config.get("shape", "dot")
        
        levels_html += f'<div style="margin-bottom: 6px;"><span style="font-size: 16px;">{emoji}</span> <strong style="color: {color};">{level}</strong> <span style="color: #888;">- {shape.capitalize()}</span></div>'
    
    # Add contingent and legacy indicators
    levels_html += '<div style="margin-bottom: 6px;"><span style="font-size: 16px;">◇</span> <strong style="color: #8E44AD;">Contingent</strong> <span style="color: #888;">- Hollow</span></div>'
    levels_html += '<div style="margin-bottom: 6px;"><span style="font-size: 16px; color: #7F8C8D;">[L]</span> <strong style="color: #7F8C8D;">Legacy</strong> <span style="color: #888;">- Gray border</span></div>'
    levels_html += '</div>'
    
    st.markdown(levels_html, unsafe_allow_html=True)
    
    # Exposure gradient
    st.markdown("**Exposure Colors**")
    st.markdown('<div style="font-size: 11px; line-height: 1.8;"><span style="background: #C0392B; color: white; padding: 1px 6px; border-radius: 3px;">Critical</span> <span style="background: #E74C3C; color: white; padding: 1px 6px; border-radius: 3px;">High</span> <span style="background: #F39C12; color: white; padding: 1px 6px; border-radius: 3px;">Medium</span> <span style="background: #F1C40F; color: #333; padding: 1px 6px; border-radius: 3px;">Low</span></div>', unsafe_allow_html=True)
    
    # Mitigations section - dynamic from schema
    st.markdown("**🛡️ Mitigations**")
    
    mit_html = '<div style="font-size: 12px; line-height: 1.8;">'
    for mit_type in MITIGATION_TYPES:
        config = MITIGATION_TYPE_CONFIG.get(mit_type, {})
        color = config.get("color", "#808080")
        mit_html += f'<div><span style="background: {color}; color: white; padding: 2px 6px; border-radius: 6px; font-size: 11px;">🛡️</span> <strong>{mit_type}</strong></div>'
    mit_html += '</div>'
    
    st.markdown(mit_html, unsafe_allow_html=True)
    
    # TPO section
    st.markdown("**🎯 TPO**")
    st.markdown('<div style="font-size: 12px;"><span style="font-size: 16px;">⬡</span> <strong style="color: #D4AC0D;">Hexagon</strong> <span style="color: #888;">- Gold</span></div>', unsafe_allow_html=True)


def render_edge_legend_sidebar():
    """Render the edge types legend for sidebar."""
    st.markdown("**➡️ Edge Types**")
    
    # Get level names for edge descriptions
    level_names = RISK_LEVELS[:2] if len(RISK_LEVELS) >= 2 else ["Level A", "Level B"]
    l1_name = level_names[1] if len(level_names) > 1 else "Op"
    l2_name = level_names[0] if len(level_names) > 0 else "Strat"
    
    # Build short names for legend
    l1_short = l1_name[:4] if len(l1_name) > 4 else l1_name
    l2_short = l2_name[:5] if len(l2_name) > 5 else l2_name
    
    st.markdown(f"""
    <div style="font-size: 12px; line-height: 1.8;">
        <div>
            <span style="color: #E74C3C;">━━►</span>
            <strong>L1</strong> {l1_short}→{l2_short}
        </div>
        <div>
            <span style="color: #8E44AD;">──►</span>
            <strong>L2</strong> {l2_short}→{l2_short}
        </div>
        <div>
            <span style="color: #2980B9;">┄┄►</span>
            <strong>L3</strong> {l1_short}→{l1_short}
        </div>
        <div style="margin-top: 4px;">
            <span style="color: #1ABC9C;">━━⊣</span>
            <strong>Mitigates</strong> (bar-end)
        </div>
        <div>
            <span style="color: #E67E22;">─∙▷</span>
            <strong>TPO Impact</strong> (vee)
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_legend_sidebar():
    """Render the status indicators legend for sidebar."""
    st.markdown("**📋 Status**")
    
    st.markdown("""
    <div style="font-size: 11px; line-height: 1.6;">
        <div><span style="color: #1ABC9C;">━━━</span> Implemented</div>
        <div><span style="color: #1ABC9C;">─∙─</span> In Progress</div>
        <div><span style="color: #1ABC9C;">─ ─</span> Proposed</div>
        <div><span style="color: #BDC3C7;">∙∙∙</span> Deferred</div>
    </div>
    """, unsafe_allow_html=True)


def render_compact_legend():
    """
    Render a compact one-line legend for quick reference.
    Useful for displaying above the graph.
    """
    # Build level items dynamically
    level_items = ""
    for level in RISK_LEVELS[:2]:  # Show first 2 levels
        config = RISK_LEVEL_CONFIG.get(level, {})
        color = config.get("color", "#808080")
        emoji = config.get("emoji", "●")
        level_items += f'<span><strong style="color: {color};">{emoji}</strong> <span style="color: #000;">{level}</span></span>'
    
    st.markdown(f"""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; padding: 8px; background: #f8f9fa; border-radius: 8px; font-size: 12px; margin-bottom: 12px; color: #000000;">
        {level_items}
        <span><strong style="color: #1ABC9C;">🛡️</strong> <span style="color: #000;">Mitigation</span></span>
        <span><strong style="color: #D4AC0D;">⬡</strong> <span style="color: #000;">TPO</span></span>
        <span style="border-left: 1px solid #ddd; padding-left: 12px;"><span style="color: #E74C3C;">━</span> <span style="color: #000;">L1</span></span>
        <span><span style="color: #8E44AD;">─</span> <span style="color: #000;">L2</span></span>
        <span><span style="color: #2980B9;">┄</span> <span style="color: #000;">L3</span></span>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_legend():
    """
    Render the legend in the sidebar with proper styling.
    Call this from your main app to add the legend to the sidebar.
    """
    render_graph_legend(expanded=False)


# =============================================================================
# Original full-width versions (for main area if needed)
# =============================================================================

def render_node_legend():
    """Render the node shapes and colors legend (full width version)."""
    st.markdown("### 🔷 Node Types")
    
    # Risks section - dynamic from schema
    st.markdown("**Risks (Threats)**")
    
    col1, col2 = st.columns(2)
    
    levels = RISK_LEVELS[:2] if len(RISK_LEVELS) >= 2 else RISK_LEVELS
    
    for i, level in enumerate(levels):
        config = RISK_LEVEL_CONFIG.get(level, {})
        color = config.get("color", "#808080")
        emoji = config.get("emoji", "●")
        description = config.get("description", "")
        shape = config.get("shape", "dot")
        
        with col1 if i == 0 else col2:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 20px; margin-right: 8px;">{emoji}</span>
                <div>
                    <strong style="color: {color};">{level} Risk</strong><br/>
                    <small style="color: #666;">{shape.capitalize()} - {description or 'Risk type'}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 20px; margin-right: 8px;">◇</span>
            <div>
                <strong style="color: #8E44AD;">Contingent Risk</strong><br/>
                <small style="color: #666;">Hollow diamond - Potential</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 20px; margin-right: 8px; color: #7F8C8D;">[L]●</span>
            <div>
                <strong style="color: #7F8C8D;">Legacy Risk</strong><br/>
                <small style="color: #666;">Gray border - Inherited</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Exposure gradient
    st.markdown("**Exposure Heat Map** (when coloring by exposure)")
    st.markdown("""
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
        <span style="background: #C0392B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">Critical ≥7</span>
        <span style="background: #E74C3C; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">High ≥4</span>
        <span style="background: #F39C12; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">Medium ≥2</span>
        <span style="background: #F1C40F; color: #333; padding: 2px 8px; border-radius: 4px; font-size: 12px;">Low &lt;2</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Mitigations section - dynamic
    st.markdown("**Mitigations (Defenses)** 🛡️")
    
    mit_items = []
    for mit_type in MITIGATION_TYPES:
        config = MITIGATION_TYPE_CONFIG.get(mit_type, {})
        color = config.get("color", "#808080")
        line_style = config.get("line_style", "solid")
        
        border = "2px solid " + color
        if line_style == "dotted":
            border = "2px dashed " + color
        elif line_style == "thick":
            border = "4px solid " + color
        
        mit_items.append(f'''
        <div style="display: flex; align-items: center;">
            <span style="background: {color}; color: white; padding: 4px 8px; border-radius: 8px; font-size: 14px; border: {border};">🛡️</span>
            <span style="margin-left: 6px; font-size: 13px;"><strong>{mit_type}</strong></span>
        </div>
        ''')
    
    st.markdown(f"""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 12px;">
        {''.join(mit_items)}
    </div>
    """, unsafe_allow_html=True)
    
    # TPO section
    st.markdown("**Program Objectives**")
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 20px; margin-right: 8px;">⬡</span>
        <div>
            <strong style="color: #D4AC0D;">🎯 TPO</strong><br/>
            <small style="color: #666;">Gold hexagon - Program goal</small>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_edge_legend():
    """Render the edge types legend (full width version)."""
    st.markdown("### ➡️ Relationship Types")
    
    # Get level names for descriptions
    level_names = RISK_LEVELS[:2] if len(RISK_LEVELS) >= 2 else ["Strategic", "Operational"]
    l1_name = level_names[1] if len(level_names) > 1 else "Operational"
    l2_name = level_names[0] if len(level_names) > 0 else "Strategic"
    
    # Influence edges
    st.markdown("**Influence Links** (Risk → Risk)")
    
    st.markdown(f"""
    <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 6px;">
                <span style="color: #E74C3C;">━━━━━►</span>
            </td>
            <td style="padding: 6px;">
                <strong>Level 1</strong>: {l1_name} → {l2_name}<br/>
                <small style="color: #666;">Causes consequence</small>
            </td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 6px;">
                <span style="color: #8E44AD;">───────►</span>
            </td>
            <td style="padding: 6px;">
                <strong>Level 2</strong>: {l2_name} → {l2_name}<br/>
                <small style="color: #666;">Amplifies impact</small>
            </td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 6px;">
                <span style="color: #2980B9;">- - - - -►</span>
            </td>
            <td style="padding: 6px;">
                <strong>Level 3</strong>: {l1_name} → {l1_name}<br/>
                <small style="color: #666;">Contributes to</small>
            </td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    # Mitigation edges
    st.markdown("**Mitigation Links** (Mitigation → Risk)")
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 8px 0;">
        <span style="color: #1ABC9C; font-size: 16px;">━━━━━⊣</span>
        <span style="margin-left: 8px; font-size: 13px;">Bar-end arrow = "Blocks" the risk</span>
    </div>
    <small style="color: #666;">Width indicates effectiveness (Critical > High > Medium > Low)</small>
    """, unsafe_allow_html=True)
    
    # TPO Impact edges
    st.markdown("**TPO Impact Links** (Risk → TPO)")
    st.markdown("""
    <div style="display: flex; align-items: center; margin: 8px 0;">
        <span style="color: #E67E22; font-size: 16px;">─∙─∙─▷</span>
        <span style="margin-left: 8px; font-size: 13px;">Vee arrow = "Threatens" objective</span>
    </div>
    <small style="color: #666;">Dash-dot pattern, width by impact level</small>
    """, unsafe_allow_html=True)


def render_status_legend():
    """Render the status indicators legend (full width version)."""
    st.markdown("### 📋 Status Indicators")
    
    st.markdown("**Mitigation Status** (Border Style)")
    st.markdown("""
    <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 4px;"><span style="color: #1ABC9C;">━━━━━</span></td>
            <td style="padding: 4px;"><strong>Implemented</strong> - Solid border</td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 4px;"><span style="color: #1ABC9C;">─∙─∙─</span></td>
            <td style="padding: 4px;"><strong>In Progress</strong> - Dash-dot border</td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 4px;"><span style="color: #1ABC9C;">─ ─ ─ ─</span></td>
            <td style="padding: 4px;"><strong>Proposed</strong> - Dashed border</td>
        </tr>
        <tr>
            <td style="padding: 4px;"><span style="color: #BDC3C7;">∙∙∙∙∙∙∙</span></td>
            <td style="padding: 4px;"><strong>Deferred</strong> - Dotted + grayed</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown("**Coverage Status**")
    st.markdown("""
    <div style="font-size: 13px;">
        <div style="margin: 4px 0;">⚠️ <strong>No Mitigations</strong> - Risk has no defenses</div>
        <div style="margin: 4px 0;">📋 <strong>Proposed Only</strong> - Only proposed mitigations</div>
        <div style="margin: 4px 0;">🔶 <strong>Partially Covered</strong> - Some implemented</div>
        <div style="margin: 4px 0;">✅ <strong>Well Covered</strong> - Fully mitigated</div>
    </div>
    """, unsafe_allow_html=True)
