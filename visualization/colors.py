"""
Color Utilities for RIM Graph Visualization.

Provides color schemes for nodes and edges based on various attributes.
"""

from typing import Optional


# Node colors by level
LEVEL_COLORS = {
    "Strategic": "#9b59b6",   # Purple
    "Operational": "#3498db"  # Blue
}

# Node colors by exposure ranges
EXPOSURE_COLORS = {
    "critical": "#e74c3c",    # Red (>= 7)
    "high": "#f39c12",        # Orange (>= 4)
    "medium": "#3498db",      # Blue (>= 2)
    "low": "#27ae60",         # Green (< 2)
    "none": "#95a5a6"         # Gray (None)
}

# TPO colors
TPO_COLORS = {
    "background": "#f1c40f",  # Yellow
    "border": "#f39c12",      # Darker yellow
    "highlight": "#f5d76e"    # Light yellow
}

# Mitigation type colors
MITIGATION_TYPE_COLORS = {
    "Dedicated": "#27ae60",   # Green
    "Inherited": "#3498db",   # Blue
    "Baseline": "#9b59b6"     # Purple
}

# Influence type colors
INFLUENCE_TYPE_COLORS = {
    "Level1": "#e74c3c",      # Red (Op→Strat)
    "Level2": "#9b59b6",      # Purple (Strat→Strat)
    "Level3": "#3498db"       # Blue (Op→Op)
}

# Effectiveness colors (for mitigation edges)
EFFECTIVENESS_COLORS = {
    "Critical": "#145a32",    # Dark green
    "High": "#1e8449",        # Medium green
    "Medium": "#27ae60",      # Light green
    "Low": "#7dcea0"          # Very light green
}

# Impact level colors (for TPO impact edges)
IMPACT_COLORS = {
    "Critical": "#c0392b",
    "High": "#e74c3c",
    "Medium": "#3498db",
    "Low": "#85c1e9"
}

# Selection highlight color
HIGHLIGHT_COLOR = "#e74c3c"  # Red


def get_color_by_level(level: str) -> str:
    """
    Get node color based on risk level.
    
    Args:
        level: Risk level ("Strategic" or "Operational")
    
    Returns:
        Hex color string
    """
    return LEVEL_COLORS.get(level, LEVEL_COLORS["Operational"])


def get_color_by_exposure(exposure: Optional[float]) -> str:
    """
    Get node color based on exposure value.
    
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
        mitigation_type: Type of mitigation
        status: Mitigation status
    
    Returns:
        Hex color string (with transparency for non-implemented)
    """
    color = MITIGATION_TYPE_COLORS.get(mitigation_type, "#27ae60")
    
    # Add transparency for proposed/deferred mitigations
    if status in ["Proposed", "Deferred"]:
        color = color + "99"  # Add alpha channel
    
    return color


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
        effectiveness: Effectiveness level
    
    Returns:
        Hex color string
    """
    return EFFECTIVENESS_COLORS.get(effectiveness, EFFECTIVENESS_COLORS["Medium"])


def get_impact_color(impact_level: str) -> str:
    """
    Get TPO impact edge color based on impact level.
    
    Args:
        impact_level: Impact level
    
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
    # Remove # prefix
    start = start_color.lstrip('#')
    end = end_color.lstrip('#')
    
    # Parse RGB components
    r1, g1, b1 = int(start[0:2], 16), int(start[2:4], 16), int(start[4:6], 16)
    r2, g2, b2 = int(end[0:2], 16), int(end[2:4], 16), int(end[4:6], 16)
    
    # Interpolate
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return f"#{r:02x}{g:02x}{b:02x}"
