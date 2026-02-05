"""
Color Utilities for RIM Graph Visualization.

Enhanced color schemes with semantic meaning:
- Warm colors (red/orange/purple) for risks/threats
- Cool colors (teal/green) for mitigations/protection
- Gold for TPOs/objectives
"""

from typing import Optional


# =============================================================================
# RISK COLORS - Warm spectrum (threats)
# =============================================================================

RISK_COLORS = {
    "business": {
        "base": "#8E44AD",      # Purple - consequence-oriented
        "light": "#BB8FCE",
        "dark": "#6C3483"
    },
    "operational": {
        "base": "#2980B9",      # Blue - cause-oriented
        "light": "#5DADE2",
        "dark": "#1F618D"
    }
}

# Legacy compatibility aliases
LEVEL_COLORS = {
    "Business": RISK_COLORS["business"]["base"],
    "Operational": RISK_COLORS["operational"]["base"]
}

# Exposure gradient - Heat map concept (critical = hot, low = cool)
EXPOSURE_COLORS = {
    "critical": "#C0392B",     # Dark red - immediate danger
    "high": "#E74C3C",         # Red - significant concern
    "medium": "#F39C12",       # Orange - attention needed
    "low": "#F1C40F",          # Yellow - manageable
    "none": "#BDC3C7"          # Gray - not assessed
}


# =============================================================================
# MITIGATION COLORS - Cool/Green spectrum (protection)
# =============================================================================

MITIGATION_COLORS = {
    "dedicated": {
        "implemented": "#1ABC9C",    # Teal - active protection
        "in_progress": "#48C9B0",
        "proposed": "#A3E4D7",
        "deferred": "#D5DBDB"
    },
    "inherited": {
        "implemented": "#3498DB",    # Blue - external source
        "in_progress": "#5DADE2",
        "proposed": "#AED6F1",
        "deferred": "#D6DBDF"
    },
    "baseline": {
        "implemented": "#9B59B6",    # Purple - standard practice
        "in_progress": "#AF7AC5",
        "proposed": "#D7BDE2",
        "deferred": "#D7DBDD"
    }
}

# Legacy compatibility alias
MITIGATION_TYPE_COLORS = {
    "Dedicated": MITIGATION_COLORS["dedicated"]["implemented"],
    "Inherited": MITIGATION_COLORS["inherited"]["implemented"],
    "Baseline": MITIGATION_COLORS["baseline"]["implemented"]
}

# Mitigation border colors by type
MITIGATION_BORDER_COLORS = {
    "Dedicated": "#0E6655",    # Dark teal
    "Inherited": "#1A5276",    # Dark blue
    "Baseline": "#5B2C6F"      # Dark purple
}


# =============================================================================
# TPO COLORS - Gold (objectives/goals)
# =============================================================================

TPO_COLORS = {
    "background": "#F1C40F",   # Gold
    "border": "#D4AC0D",       # Dark gold
    "highlight": "#F7DC6F",    # Light gold
    "text": "#7D6608"          # Dark gold for text
}


# =============================================================================
# INFLUENCE TYPE COLORS (Edge colors for risk relationships)
# =============================================================================

INFLUENCE_TYPE_COLORS = {
    "Level1": "#E74C3C",       # Red (Op→Bus) - causes consequence
    "Level2": "#8E44AD",       # Purple (Bus→Bus) - amplifies
    "Level3": "#2980B9"        # Blue (Op→Op) - contributes
}


# =============================================================================
# EFFECTIVENESS COLORS (Mitigation edge colors)
# =============================================================================

EFFECTIVENESS_COLORS = {
    "Critical": "#0E6655",     # Dark teal - strong block
    "High": "#1ABC9C",         # Teal
    "Medium": "#48C9B0",       # Light teal
    "Low": "#A3E4D7"           # Very light teal
}


# =============================================================================
# IMPACT COLORS (TPO impact edge colors)
# =============================================================================

IMPACT_COLORS = {
    "Critical": "#D35400",     # Dark orange
    "High": "#E67E22",         # Orange
    "Medium": "#F39C12",       # Light orange
    "Low": "#F5B041"           # Yellow-orange
}


# =============================================================================
# HIGHLIGHT AND SELECTION
# =============================================================================

HIGHLIGHT_COLOR = "#E74C3C"    # Red for selection highlight
SELECTION_GLOW = "#FFD700"     # Gold glow for emphasis


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_color_by_level(level: str) -> str:
    """
    Get node color based on risk level.
    
    Args:
        level: Risk level ("Strategic" or "Operational")
    
    Returns:
        Hex color string
    """
    level_key = level.lower() if level else "operational"
    if level_key in RISK_COLORS:
        return RISK_COLORS[level_key]["base"]
    return RISK_COLORS["operational"]["base"]


def get_color_by_exposure(exposure: Optional[float]) -> str:
    """
    Get node color based on exposure value using heat map gradient.
    
    Args:
        exposure: Risk exposure value (0-16 typically)
    
    Returns:
        Hex color string
    """
    if exposure is None:
        return EXPOSURE_COLORS["none"]
    if exposure >= 7:
        return EXPOSURE_COLORS["critical"]
    elif exposure >= 4:
        return EXPOSURE_COLORS["high"]
    elif exposure >= 2:
        return EXPOSURE_COLORS["medium"]
    else:
        return EXPOSURE_COLORS["low"]


def get_mitigation_color(mitigation_type: str, status: str = "Implemented") -> str:
    """
    Get mitigation node color based on type and status.
    
    Args:
        mitigation_type: Type of mitigation (Dedicated, Inherited, Baseline)
        status: Mitigation status (Implemented, In Progress, Proposed, Deferred)
    
    Returns:
        Hex color string
    """
    type_key = mitigation_type.lower() if mitigation_type else "dedicated"
    status_key = status.lower().replace(" ", "_") if status else "implemented"
    
    if type_key in MITIGATION_COLORS:
        type_colors = MITIGATION_COLORS[type_key]
        if status_key in type_colors:
            return type_colors[status_key]
        return type_colors["implemented"]
    
    return MITIGATION_COLORS["dedicated"]["implemented"]


def get_mitigation_border_color(mitigation_type: str) -> str:
    """
    Get mitigation border color based on type.
    
    Args:
        mitigation_type: Type of mitigation
    
    Returns:
        Hex color string
    """
    return MITIGATION_BORDER_COLORS.get(mitigation_type, MITIGATION_BORDER_COLORS["Dedicated"])


def get_influence_color(influence_type: str) -> str:
    """
    Get edge color based on influence type.
    
    Args:
        influence_type: Type of influence (Level1, Level2, Level3)
    
    Returns:
        Hex color string
    """
    for key in INFLUENCE_TYPE_COLORS:
        if key in influence_type:
            return INFLUENCE_TYPE_COLORS[key]
    return INFLUENCE_TYPE_COLORS["Level3"]


def get_effectiveness_color(effectiveness: str) -> str:
    """
    Get mitigation edge color based on effectiveness.
    
    Args:
        effectiveness: Effectiveness level (Critical, High, Medium, Low)
    
    Returns:
        Hex color string
    """
    return EFFECTIVENESS_COLORS.get(effectiveness, EFFECTIVENESS_COLORS["Medium"])


def get_impact_color(impact_level: str) -> str:
    """
    Get TPO impact edge color based on impact level.
    
    Args:
        impact_level: Impact level (Critical, High, Medium, Low)
    
    Returns:
        Hex color string
    """
    return IMPACT_COLORS.get(impact_level, IMPACT_COLORS["Medium"])


def interpolate_color(start_color: str, end_color: str, factor: float) -> str:
    """
    Interpolate between two colors.
    
    Args:
        start_color: Starting hex color
        end_color: Ending hex color
        factor: Interpolation factor (0-1)
    
    Returns:
        Interpolated hex color
    """
    # Remove # prefix and handle alpha channel
    start = start_color.lstrip('#')[:6]
    end = end_color.lstrip('#')[:6]
    
    # Parse RGB components
    r1, g1, b1 = int(start[0:2], 16), int(start[2:4], 16), int(start[4:6], 16)
    r2, g2, b2 = int(end[0:2], 16), int(end[2:4], 16), int(end[4:6], 16)
    
    # Interpolate
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def get_exposure_gradient_position(exposure: Optional[float], max_exposure: float = 16.0) -> float:
    """
    Get the gradient position (0-1) for an exposure value.
    
    Args:
        exposure: Exposure value
        max_exposure: Maximum expected exposure value
    
    Returns:
        Position in gradient (0 = low, 1 = critical)
    """
    if exposure is None:
        return 0.0
    return min(1.0, max(0.0, exposure / max_exposure))
