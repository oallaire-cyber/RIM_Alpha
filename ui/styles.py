"""
CSS styles for RIM application.

Contains all custom CSS styles used throughout the Streamlit interface.
"""

import streamlit as st


# =============================================================================
# CSS STYLE DEFINITIONS
# =============================================================================

CSS_STYLES = """
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 0.5rem;
    }
    
    /* Sub-header styling */
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Badge base styles */
    .badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Contingent risk badge */
    .contingent-badge {
        background-color: #f39c12;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Strategic risk badge */
    .strategic-badge {
        background-color: #9b59b6;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Operational risk badge */
    .operational-badge {
        background-color: #3498db;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* TPO badge */
    .tpo-badge {
        background-color: #f1c40f;
        color: #333;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Legacy risk badge */
    .legacy-badge {
        background-color: #95a5a6;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* New risk badge */
    .new-badge {
        background-color: #27ae60;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Mitigation badge (generic) */
    .mitigation-badge {
        background-color: #2ecc71;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Mitigation type: Dedicated */
    .mitigation-dedicated {
        background-color: #27ae60;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Mitigation type: Inherited */
    .mitigation-inherited {
        background-color: #3498db;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Mitigation type: Baseline */
    .mitigation-baseline {
        background-color: #9b59b6;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Status badges */
    .status-active {
        background-color: #27ae60;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .status-proposed {
        background-color: #3498db;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .status-in-progress {
        background-color: #f39c12;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .status-implemented {
        background-color: #27ae60;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .status-deferred {
        background-color: #95a5a6;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Effectiveness badges */
    .effectiveness-low {
        background-color: #7dcea0;
        color: #333;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .effectiveness-medium {
        background-color: #f4d03f;
        color: #333;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .effectiveness-high {
        background-color: #e67e22;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    .effectiveness-critical {
        background-color: #e74c3c;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    
    /* Card styling */
    .risk-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        background-color: #fafafa;
    }
    
    .risk-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Metric highlight */
    .metric-highlight {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
    }
    
    /* Analysis panel styling */
    .analysis-panel {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Warning/Alert styling */
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 4px;
        padding: 0.75rem;
        color: #856404;
    }
    
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #28a745;
        border-radius: 4px;
        padding: 0.75rem;
        color: #155724;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #dc3545;
        border-radius: 4px;
        padding: 0.75rem;
        color: #721c24;
    }
    
    /* Progress bar customization */
    .coverage-progress {
        height: 20px;
        border-radius: 10px;
        background-color: #e9ecef;
    }
    
    .coverage-progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Influence type colors */
    .influence-level1 {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .influence-level2 {
        color: #9b59b6;
        font-weight: bold;
    }
    
    .influence-level3 {
        color: #3498db;
        font-weight: bold;
    }
</style>
"""


# =============================================================================
# BADGE CLASSES MAPPING
# =============================================================================

BADGE_CLASSES = {
    # Risk levels
    "Strategic": "strategic-badge",
    "Operational": "operational-badge",
    
    # Risk origins
    "New": "new-badge",
    "Legacy": "legacy-badge",
    
    # Risk statuses
    "Active": "status-active",
    "Contingent": "contingent-badge",
    "Archived": "legacy-badge",
    
    # Mitigation types
    "Dedicated": "mitigation-dedicated",
    "Inherited": "mitigation-inherited",
    "Baseline": "mitigation-baseline",
    
    # Mitigation statuses
    "Proposed": "status-proposed",
    "In Progress": "status-in-progress",
    "Implemented": "status-implemented",
    "Deferred": "status-deferred",
    
    # Effectiveness
    "Low": "effectiveness-low",
    "Medium": "effectiveness-medium",
    "High": "effectiveness-high",
    "Critical": "effectiveness-critical",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def inject_styles():
    """Inject CSS styles into the Streamlit app."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


def get_badge_html(text: str, badge_type: str = None) -> str:
    """
    Generate HTML for a styled badge.
    
    Args:
        text: Text to display in the badge
        badge_type: Type of badge (determines styling). If None, uses text to lookup.
    
    Returns:
        HTML string for the badge
    """
    badge_class = BADGE_CLASSES.get(badge_type or text, "badge")
    return f'<span class="{badge_class}">{text}</span>'


def get_level_badge(level: str) -> str:
    """Get badge HTML for a risk level."""
    return get_badge_html(level, level)


def get_status_badge(status: str) -> str:
    """Get badge HTML for a status."""
    return get_badge_html(status, status)


def get_origin_badge(origin: str) -> str:
    """Get badge HTML for a risk origin."""
    return get_badge_html(origin, origin)


def get_mitigation_type_badge(mit_type: str) -> str:
    """Get badge HTML for a mitigation type."""
    return get_badge_html(mit_type, mit_type)


def get_effectiveness_badge(effectiveness: str) -> str:
    """Get badge HTML for effectiveness level."""
    return get_badge_html(effectiveness, effectiveness)
