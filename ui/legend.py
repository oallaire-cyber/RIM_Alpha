"""
Legend Component for RIM Graph Visualization.

Provides a comprehensive visual legend showing node shapes,
colors, and edge types used in the Risk Influence Map.
"""

import streamlit as st


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
    
    # Risks section - vertical layout for sidebar
    st.markdown("""
    <div style="font-size: 12px; line-height: 1.6;">
        <div style="margin-bottom: 6px;">
            <span style="font-size: 16px;">◆</span>
            <strong style="color: #8E44AD;">Strategic</strong>
            <span style="color: #888;">- Diamond</span>
        </div>
        <div style="margin-bottom: 6px;">
            <span style="font-size: 16px;">●</span>
            <strong style="color: #2980B9;">Operational</strong>
            <span style="color: #888;">- Circle</span>
        </div>
        <div style="margin-bottom: 6px;">
            <span style="font-size: 16px;">◇</span>
            <strong style="color: #8E44AD;">Contingent</strong>
            <span style="color: #888;">- Hollow</span>
        </div>
        <div style="margin-bottom: 6px;">
            <span style="font-size: 16px; color: #7F8C8D;">[L]</span>
            <strong style="color: #7F8C8D;">Legacy</strong>
            <span style="color: #888;">- Gray border</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exposure gradient
    st.markdown("**Exposure Colors**")
    st.markdown("""
    <div style="font-size: 11px; line-height: 1.8;">
        <span style="background: #C0392B; color: white; padding: 1px 6px; border-radius: 3px;">Critical</span>
        <span style="background: #E74C3C; color: white; padding: 1px 6px; border-radius: 3px;">High</span>
        <span style="background: #F39C12; color: white; padding: 1px 6px; border-radius: 3px;">Medium</span>
        <span style="background: #F1C40F; color: #333; padding: 1px 6px; border-radius: 3px;">Low</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Mitigations section
    st.markdown("**🛡️ Mitigations**")
    st.markdown("""
    <div style="font-size: 12px; line-height: 1.8;">
        <div>
            <span style="background: #1ABC9C; color: white; padding: 2px 6px; border-radius: 6px; font-size: 11px;">🛡️</span>
            <strong>Dedicated</strong> <span style="color: #888;">(Teal)</span>
        </div>
        <div>
            <span style="background: #3498DB; color: white; padding: 2px 6px; border-radius: 6px; font-size: 11px; border: 1px dashed #fff;">🛡️</span>
            <strong>Inherited</strong> <span style="color: #888;">(Blue)</span>
        </div>
        <div>
            <span style="background: #9B59B6; color: white; padding: 2px 6px; border-radius: 6px; font-size: 11px;">🛡️</span>
            <strong>Baseline</strong> <span style="color: #888;">(Purple)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TPO section
    st.markdown("**🎯 TPO**")
    st.markdown("""
    <div style="font-size: 12px;">
        <span style="font-size: 16px;">⬡</span>
        <strong style="color: #D4AC0D;">Hexagon</strong>
        <span style="color: #888;">- Gold</span>
    </div>
    """, unsafe_allow_html=True)


def render_edge_legend_sidebar():
    """Render the edge types legend for sidebar."""
    st.markdown("**➡️ Edge Types**")
    
    st.markdown("""
    <div style="font-size: 12px; line-height: 1.8;">
        <div>
            <span style="color: #E74C3C;">━━►</span>
            <strong>L1</strong> Op→Strat
        </div>
        <div>
            <span style="color: #8E44AD;">──►</span>
            <strong>L2</strong> Strat→Strat
        </div>
        <div>
            <span style="color: #2980B9;">┄┄►</span>
            <strong>L3</strong> Op→Op
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
    st.markdown("""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; padding: 8px; background: #f8f9fa; border-radius: 8px; font-size: 12px; margin-bottom: 12px; color: #000000;">
        <span><strong style="color: #8E44AD;">◆</strong> <span style="color: #000;">Strategic</span></span>
        <span><strong style="color: #2980B9;">●</strong> <span style="color: #000;">Operational</span></span>
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
    
    # Risks section
    st.markdown("**Risks (Threats)**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 20px; margin-right: 8px;">◆</span>
            <div>
                <strong style="color: #8E44AD;">Strategic Risk</strong><br/>
                <small style="color: #666;">Diamond - Consequence-oriented</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
            <span style="font-size: 20px; margin-right: 8px;">●</span>
            <div>
                <strong style="color: #2980B9;">Operational Risk</strong><br/>
                <small style="color: #666;">Circle - Cause-oriented</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    # Mitigations section
    st.markdown("**Mitigations (Defenses)** 🛡️")
    
    st.markdown("""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 12px;">
        <div style="display: flex; align-items: center;">
            <span style="background: #1ABC9C; color: white; padding: 4px 8px; border-radius: 8px; font-size: 14px; border: 2px solid #0E6655;">🛡️</span>
            <span style="margin-left: 6px; font-size: 13px;"><strong>Dedicated</strong> (Teal)</span>
        </div>
        <div style="display: flex; align-items: center;">
            <span style="background: #3498DB; color: white; padding: 4px 8px; border-radius: 8px; font-size: 14px; border: 2px dashed #1A5276;">🛡️</span>
            <span style="margin-left: 6px; font-size: 13px;"><strong>Inherited</strong> (Blue)</span>
        </div>
        <div style="display: flex; align-items: center;">
            <span style="background: #9B59B6; color: white; padding: 4px 8px; border-radius: 8px; font-size: 14px; border: 4px solid #5B2C6F;">🛡️</span>
            <span style="margin-left: 6px; font-size: 13px;"><strong>Baseline</strong> (Purple)</span>
        </div>
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
    
    # Influence edges
    st.markdown("**Influence Links** (Risk → Risk)")
    
    st.markdown("""
    <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 6px;">
                <span style="color: #E74C3C;">━━━━━►</span>
            </td>
            <td style="padding: 6px;">
                <strong>Level 1</strong>: Op → Strat<br/>
                <small style="color: #666;">Causes consequence</small>
            </td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 6px;">
                <span style="color: #8E44AD;">───────►</span>
            </td>
            <td style="padding: 6px;">
                <strong>Level 2</strong>: Strat → Strat<br/>
                <small style="color: #666;">Amplifies impact</small>
            </td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 6px;">
                <span style="color: #2980B9;">- - - - -►</span>
            </td>
            <td style="padding: 6px;">
                <strong>Level 3</strong>: Op → Op<br/>
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
