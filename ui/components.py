"""
Reusable UI Components for RIM Application.

Provides Streamlit-based UI components for statistics,
metrics display, and common UI patterns.
"""

from typing import Dict, List, Any, Optional, Callable
from ui.styles import (
    get_level_badge, get_status_badge, get_origin_badge,
    get_mitigation_type_badge, get_effectiveness_badge
)


def render_statistics_cards(stats: Dict[str, Any], use_streamlit: bool = True):
    """
    Render statistics as metric cards.
    
    Args:
        stats: Statistics dictionary from get_statistics()
        use_streamlit: If True, use Streamlit components
    """
    if use_streamlit:
        import streamlit as st
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Risks", stats.get("total_risks", 0))
        with col2:
            st.metric("Strategic", stats.get("strategic_risks", 0))
        with col3:
            st.metric("Operational", stats.get("operational_risks", 0))
        with col4:
            st.metric("Avg Exposure", f"{stats.get('avg_exposure', 0):.1f}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("TPOs", stats.get("total_tpos", 0))
        with col2:
            st.metric("Influences", stats.get("total_influences", 0))
        with col3:
            st.metric("Mitigations", stats.get("total_mitigations", 0))
        with col4:
            st.metric("TPO Impacts", stats.get("total_tpo_impacts", 0))


def render_risk_badge(risk: Dict[str, Any]) -> str:
    """
    Generate HTML badge for a risk.
    
    Args:
        risk: Risk dictionary
    
    Returns:
        HTML string for the badge
    """
    level = risk.get("level", "Unknown")
    status = risk.get("status", "Active")
    origin = risk.get("origin", "New")
    
    level_badge = get_level_badge(level)
    status_badge = get_status_badge(status)
    origin_badge = get_origin_badge(origin)
    
    return f"{level_badge} {status_badge} {origin_badge}"


def render_mitigation_badge(mitigation: Dict[str, Any]) -> str:
    """
    Generate HTML badge for a mitigation.
    
    Args:
        mitigation: Mitigation dictionary
    
    Returns:
        HTML string for the badge
    """
    mit_type = mitigation.get("type", "Dedicated")
    status = mitigation.get("status", "Proposed")
    
    type_badge = get_mitigation_type_badge(mit_type)
    status_badge = get_status_badge(status)
    
    return f"{type_badge} {status_badge}"


def render_coverage_indicator(coverage_status: str) -> str:
    """
    Generate HTML for coverage status indicator.
    
    Args:
        coverage_status: One of: unmitigated, proposed_only, partially_covered, well_covered
    
    Returns:
        HTML string with icon and label
    """
    indicators = {
        "unmitigated": ("⛔", "Unmitigated", "color: #dc3545"),
        "proposed_only": ("⚠️", "Proposed Only", "color: #ffc107"),
        "partially_covered": ("🔶", "Partially Covered", "color: #fd7e14"),
        "well_covered": ("✅", "Well Covered", "color: #28a745")
    }
    
    icon, label, style = indicators.get(coverage_status, ("❓", "Unknown", "color: #6c757d"))
    return f'<span style="{style}">{icon} {label}</span>'


def render_influence_flags(flags: List[str]) -> str:
    """
    Generate HTML for influence analysis flags.
    
    Args:
        flags: List of flag strings (e.g., ["Top Propagator", "Bottleneck"])
    
    Returns:
        HTML string with flag badges
    """
    flag_styles = {
        "Top Propagator": ("🔺", "background-color: #9c27b0; color: white"),
        "Convergence Point": ("🔻", "background-color: #2196f3; color: white"),
        "Bottleneck": ("⚡", "background-color: #ff9800; color: white")
    }
    
    badges = []
    for flag in flags:
        icon, style = flag_styles.get(flag, ("•", "background-color: #6c757d; color: white"))
        badges.append(f'<span class="badge" style="{style}; padding: 2px 6px; border-radius: 4px; margin-right: 4px;">{icon} {flag}</span>')
    
    return " ".join(badges)


def render_exposure_bar(exposure: float, max_exposure: float = 16.0) -> str:
    """
    Generate HTML for exposure progress bar.
    
    Args:
        exposure: Risk exposure value
        max_exposure: Maximum exposure for scaling
    
    Returns:
        HTML string with progress bar
    """
    percentage = min(100, (exposure / max_exposure) * 100)
    
    if percentage >= 75:
        color = "#dc3545"  # Red
    elif percentage >= 50:
        color = "#fd7e14"  # Orange
    elif percentage >= 25:
        color = "#ffc107"  # Yellow
    else:
        color = "#28a745"  # Green
    
    return f'''
    <div style="background-color: #e9ecef; border-radius: 4px; height: 8px; width: 100%;">
        <div style="background-color: {color}; width: {percentage}%; height: 100%; border-radius: 4px;"></div>
    </div>
    <small style="color: #6c757d;">{exposure:.1f} / {max_exposure:.1f}</small>
    '''


def render_category_chips(categories: List[str]) -> str:
    """
    Generate HTML for category chips.
    
    Args:
        categories: List of category names
    
    Returns:
        HTML string with chips
    """
    category_colors = {
        "Programme": "#007bff",
        "Produit": "#28a745",
        "Industriel": "#fd7e14",
        "Supply Chain": "#6f42c1"
    }
    
    chips = []
    for cat in categories:
        color = category_colors.get(cat, "#6c757d")
        chips.append(f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; margin-right: 4px;">{cat}</span>')
    
    return " ".join(chips)


def render_risk_card(risk: Dict[str, Any], show_mitigations: bool = False) -> str:
    """
    Generate HTML for a risk card.
    
    Args:
        risk: Risk dictionary with optional mitigations list
        show_mitigations: Whether to show mitigation info
    
    Returns:
        HTML string for the card
    """
    name = risk.get("name", "Unknown")
    level = risk.get("level", "Unknown")
    exposure = risk.get("exposure") or 0
    categories = risk.get("categories", [])
    
    badges = render_risk_badge(risk)
    category_html = render_category_chips(categories)
    exposure_html = render_exposure_bar(exposure)
    
    html = f'''
    <div style="border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; margin-bottom: 8px; background-color: white;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <strong>{name}</strong>
            <span>{badges}</span>
        </div>
        <div style="margin-top: 8px;">{category_html}</div>
        <div style="margin-top: 8px;">
            <small><strong>Exposure:</strong></small>
            {exposure_html}
        </div>
    '''
    
    if show_mitigations and "mitigations" in risk:
        mits = risk["mitigations"]
        if mits:
            html += f'<div style="margin-top: 8px;"><small><strong>Mitigations:</strong> {len(mits)}</small></div>'
        else:
            html += '<div style="margin-top: 8px;"><small style="color: #dc3545;">⚠️ No mitigations</small></div>'
    
    html += '</div>'
    return html


def render_mitigation_card(mitigation: Dict[str, Any], show_risks: bool = False) -> str:
    """
    Generate HTML for a mitigation card.
    
    Args:
        mitigation: Mitigation dictionary with optional risks list
        show_risks: Whether to show addressed risks
    
    Returns:
        HTML string for the card
    """
    name = mitigation.get("name", "Unknown")
    mit_type = mitigation.get("type", "Dedicated")
    status = mitigation.get("status", "Proposed")
    owner = mitigation.get("owner", "")
    
    badges = render_mitigation_badge(mitigation)
    
    html = f'''
    <div style="border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; margin-bottom: 8px; background-color: white;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <strong>{name}</strong>
            <span>{badges}</span>
        </div>
    '''
    
    if owner:
        html += f'<div style="margin-top: 8px;"><small><strong>Owner:</strong> {owner}</small></div>'
    
    if show_risks and "risks" in mitigation:
        risks = mitigation["risks"]
        html += f'<div style="margin-top: 8px;"><small><strong>Addresses:</strong> {len(risks)} risks</small></div>'
    
    html += '</div>'
    return html


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a value as percentage string."""
    return f"{value:.{decimals}f}%"


def format_count(count: int, singular: str, plural: str = None) -> str:
    """Format count with proper singular/plural form."""
    if plural is None:
        plural = singular + "s"
    return f"{count} {singular if count == 1 else plural}"


def create_download_link(data: bytes, filename: str, link_text: str) -> str:
    """
    Create HTML download link for binary data.
    
    Args:
        data: Binary data to download
        filename: Suggested filename
        link_text: Text to display for the link
    
    Returns:
        HTML anchor tag string
    """
    import base64
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'
