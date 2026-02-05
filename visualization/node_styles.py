"""
Node Styling for RIM Graph Visualization.

Enhanced node shapes with semantic meaning:
- Diamonds (◆) for Business Risks - pointed = danger, consequence-oriented
- Circles (●) for Operational Risks - foundation, cause-oriented
- Rounded Boxes (🛡️) for Mitigations - shield-like, protective
- Hexagons (⬡) for TPOs - objectives, goals
"""

from typing import Dict, Any, Optional
from visualization.colors import (
    RISK_COLORS,
    EXPOSURE_COLORS,
    MITIGATION_COLORS,
    TPO_COLORS,
    HIGHLIGHT_COLOR,
    get_color_by_level,
    get_color_by_exposure,
    get_mitigation_color,
    get_mitigation_border_color
)


# =============================================================================
# SHAPE CONFIGURATIONS
# =============================================================================

# Risk shapes by level and status
RISK_SHAPES = {
    "business": {
        "default": "diamond",      # Pointed = danger, high-level
        "contingent": "diamond"    # Hollow diamond for potential
    },
    "operational": {
        "default": "dot",          # Circle = foundation
        "contingent": "diamond"    # Diamond outline for contingent
    }
}

# Mitigation shape (shield-like rounded box)
MITIGATION_SHAPE = "box"

# TPO shape
TPO_SHAPE = "hexagon"


# =============================================================================
# SIZE CONFIGURATIONS
# =============================================================================

NODE_SIZES = {
    "business_risk": 35,
    "operational_risk": 28,
    "contingent_risk": 30,
    "mitigation": 40,
    "tpo": 40,
    "highlight_bonus": 10
}

EXPOSURE_SIZE_MULTIPLIER = 1.2  # Size increase per exposure unit


# =============================================================================
# BORDER CONFIGURATIONS
# =============================================================================

BORDER_STYLES = {
    # Risk status borders
    "active": {"dashes": False, "width": 2},
    "contingent": {"dashes": [8, 4], "width": 3},
    "archived": {"dashes": [2, 2], "width": 2},
    "legacy": {"dashes": False, "width": 4, "color": "#7F8C8D"},
    
    # Mitigation type borders
    "dedicated": {"dashes": False, "width": 3},
    "inherited": {"dashes": [4, 4], "width": 2},
    "baseline": {"dashes": False, "width": 5},
    
    # Mitigation status borders
    "implemented": {"dashes": False},
    "in_progress": {"dashes": [8, 2, 2, 2]},
    "proposed": {"dashes": [6, 3]},
    "deferred": {"dashes": [2, 2]},
    
    # Selection
    "highlighted": {"width": 6}
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def wrap_label(text: str, max_width: int = 20) -> str:
    """
    Wrap text into multiple lines for better display.
    
    Args:
        text: Text to wrap
        max_width: Maximum characters per line
    
    Returns:
        Wrapped text with newlines
    """
    if not text or len(text) <= max_width:
        return text or ""
    
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Limit to 3 lines max
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2][:max_width-3] + "..."
    
    return '\n'.join(lines)


def truncate_label(text: str, max_length: int = 25) -> str:
    """
    Truncate text and add ellipsis if too long.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length-3] + "..."


def build_risk_tooltip(node: Dict[str, Any], is_highlighted: bool = False) -> str:
    """Build tooltip content for a risk node."""
    level = node.get("level", "Operational")
    origin = node.get("origin", "New")
    status = node.get("status", "Active")
    exposure = node.get("exposure")
    categories = node.get("categories", [])
    
    # Level indicator
    level_icon = "◆" if level == "Business" else "●"
    
    parts = [
        f"{level_icon} {node.get('name', 'Unknown Risk')}",
        f"Level: {level}",
        f"Origin: {origin}",
        f"Status: {status}",
        f"Categories: {', '.join(categories) if categories else 'N/A'}",
        f"Exposure: {exposure:.2f}" if exposure else "Exposure: N/A",
        f"Owner: {node.get('owner', 'N/A')}"
    ]
    
    if is_highlighted:
        parts.append("★ SELECTED NODE")
    
    return "\n".join(parts)


def build_mitigation_tooltip(node: Dict[str, Any], is_highlighted: bool = False) -> str:
    """Build tooltip content for a mitigation node."""
    mit_type = node.get("type", "Dedicated")
    mit_status = node.get("status", "Proposed")
    
    # Status emoji
    status_emoji = {
        "Proposed": "📋",
        "In Progress": "🔄",
        "Implemented": "✅",
        "Deferred": "⏸️"
    }
    
    parts = [
        f"🛡️ {node.get('name', 'Unknown Mitigation')}",
        f"Type: {mit_type}",
        f"Status: {mit_status} {status_emoji.get(mit_status, '')}",
        f"Owner: {node.get('owner', 'N/A')}"
    ]
    
    if node.get('source_entity'):
        parts.append(f"Source: {node['source_entity']}")
    if node.get('description'):
        parts.append(f"Description: {node['description']}")
    if is_highlighted:
        parts.append("★ SELECTED NODE")
    
    return "\n".join(parts)


def build_tpo_tooltip(node: Dict[str, Any], is_highlighted: bool = False) -> str:
    """Build tooltip content for a TPO node."""
    parts = [
        f"🎯 {node.get('reference', 'TPO')}: {node.get('name', 'Unknown')}",
        f"Type: Top Program Objective",
        f"Cluster: {node.get('cluster', 'N/A')}",
        f"Description: {node.get('description', 'N/A')}"
    ]
    
    if is_highlighted:
        parts.append("★ SELECTED NODE")
    
    return "\n".join(parts)


# =============================================================================
# NODE CONFIGURATION FUNCTIONS
# =============================================================================

def create_risk_node_config(
    node: Dict[str, Any],
    color_by: str = "level",
    is_highlighted: bool = False
) -> Dict[str, Any]:
    """
    Create enhanced risk node configuration.
    
    Uses diamond shape for business risks (consequence-oriented)
    and circle for operational risks (cause-oriented).
    Contingent risks use hollow diamond with dashed border.
    
    Args:
        node: Risk node dictionary
        color_by: Coloring scheme ("level" or "exposure")
        is_highlighted: Whether node is selected
    
    Returns:
        PyVis node configuration dictionary
    """
    level = node.get("level", "Operational")
    status = node.get("status", "Active")
    origin = node.get("origin", "New")
    exposure = node.get("exposure") or 0
    
    level_key = level.lower()
    
    # =========================
    # SHAPE SELECTION
    # =========================
    if status == "Contingent":
        shape = "diamond"
        is_contingent = True
    elif level == "Business":
        shape = "diamond"
        is_contingent = False
    else:  # Operational
        shape = "dot"
        is_contingent = False
    
    # =========================
    # COLOR SELECTION
    # =========================
    if color_by == "exposure":
        base_color = get_color_by_exposure(exposure)
    else:
        base_color = get_color_by_level(level)
    
    # Contingent risks are semi-transparent
    if is_contingent:
        # Add transparency to color
        background_color = base_color + "4D"  # 30% opacity
    else:
        background_color = base_color
    
    # =========================
    # SIZE CALCULATION
    # =========================
    if level == "Business":
        base_size = NODE_SIZES["business_risk"]
    else:
        base_size = NODE_SIZES["operational_risk"]
    
    # Scale size with exposure
    size = base_size + (exposure * EXPOSURE_SIZE_MULTIPLIER) if exposure else base_size
    
    if is_highlighted:
        size += NODE_SIZES["highlight_bonus"]
    
    # =========================
    # BORDER STYLING
    # =========================
    if is_highlighted:
        border_color = HIGHLIGHT_COLOR
        border_width = BORDER_STYLES["highlighted"]["width"]
    elif origin == "Legacy":
        border_color = BORDER_STYLES["legacy"]["color"]
        border_width = BORDER_STYLES["legacy"]["width"]
    else:
        border_color = base_color
        border_width = BORDER_STYLES["active"]["width"]
    
    # Border dashes based on status
    if status == "Contingent":
        border_dashes = BORDER_STYLES["contingent"]["dashes"]
        border_width = BORDER_STYLES["contingent"]["width"]
    elif status == "Archived":
        border_dashes = BORDER_STYLES["archived"]["dashes"]
    else:
        border_dashes = False
    
    # =========================
    # LABEL CONSTRUCTION
    # =========================
    # Shape indicator prefix
    if level == "Business":
        label_prefix = "◆ "
    else:
        label_prefix = "● "
    
    if origin == "Legacy":
        label_prefix = f"[L] {label_prefix}"
    
    if is_highlighted:
        label_prefix = f"★ {label_prefix}"
    
    label = label_prefix + wrap_label(node.get("name", ""), 18)
    
    # =========================
    # BUILD CONFIGURATION
    # =========================
    config = {
        "label": label,
        "title": build_risk_tooltip(node, is_highlighted),
        "shape": shape,
        "size": size,
        "color": {
            "background": background_color,
            "border": border_color,
            "highlight": {
                "background": base_color,
                "border": HIGHLIGHT_COLOR
            }
        },
        "borderWidth": border_width,
        "borderWidthSelected": BORDER_STYLES["highlighted"]["width"],
        "shapeProperties": {
            "borderDashes": border_dashes
        },
        "font": {
            "color": "#2C3E50",
            "size": 20,
            "face": "Arial",
            "bold": level == "Business"
        },
        "shadow": {
            "enabled": True,
            "color": HIGHLIGHT_COLOR if is_highlighted else "rgba(0,0,0,0.2)",
            "size": 15 if is_highlighted else 8,
            "x": 3,
            "y": 3
        }
    }
    
    return config


def create_mitigation_node_config(
    node: Dict[str, Any],
    is_highlighted: bool = False
) -> Dict[str, Any]:
    """
    Create enhanced mitigation node configuration.
    
    Uses rounded box shape (shield-like) to clearly distinguish
    from risk nodes. Border style indicates type and status.
    
    Args:
        node: Mitigation node dictionary
        is_highlighted: Whether node is selected
    
    Returns:
        PyVis node configuration dictionary
    """
    mit_type = node.get("type", "Dedicated")
    mit_status = node.get("status", "Proposed")
    
    type_key = mit_type.lower()
    status_key = mit_status.lower().replace(" ", "_")
    
    # =========================
    # COLOR SELECTION
    # =========================
    base_color = get_mitigation_color(mit_type, mit_status)
    
    # =========================
    # SIZE
    # =========================
    size = NODE_SIZES["mitigation"]
    if is_highlighted:
        size += NODE_SIZES["highlight_bonus"]
    
    # =========================
    # BORDER STYLING
    # =========================
    # Border color
    if is_highlighted:
        border_color = HIGHLIGHT_COLOR
    else:
        border_color = get_mitigation_border_color(mit_type)
    
    # Border width based on type
    type_border = BORDER_STYLES.get(type_key, BORDER_STYLES["dedicated"])
    border_width = type_border.get("width", 3)
    
    # Border dashes based on status (overrides type if status is not implemented)
    status_border = BORDER_STYLES.get(status_key, {})
    if status_key != "implemented" and "dashes" in status_border:
        border_dashes = status_border["dashes"]
    else:
        border_dashes = type_border.get("dashes", False)
    
    # =========================
    # LABEL CONSTRUCTION
    # =========================
    # Status icon
    status_icons = {
        "proposed": "📋",
        "in_progress": "🔄",
        "implemented": "✅",
        "deferred": "⏸️"
    }
    
    label = f"🛡️ {wrap_label(node.get('name', ''), 16)}"
    if is_highlighted:
        label = f"★ {label}"
    
    # =========================
    # BUILD CONFIGURATION
    # =========================
    config = {
        "label": label,
        "title": build_mitigation_tooltip(node, is_highlighted),
        "shape": MITIGATION_SHAPE,
        "size": size,
        "color": {
            "background": base_color,
            "border": border_color,
            "highlight": {
                "background": MITIGATION_COLORS["dedicated"]["implemented"],
                "border": HIGHLIGHT_COLOR
            }
        },
        "borderWidth": border_width,
        "borderWidthSelected": BORDER_STYLES["highlighted"]["width"],
        "shapeProperties": {
            "borderRadius": 12,  # Rounded corners for shield-like appearance
            "borderDashes": border_dashes
        },
        "font": {
            "color": "#FFFFFF",
            "size": 20,
            "face": "Arial"
        },
        "shadow": {
            "enabled": True,
            "color": HIGHLIGHT_COLOR if is_highlighted else "rgba(0,0,0,0.15)",
            "size": 12 if is_highlighted else 6,
            "x": 2,
            "y": 2
        }
    }
    
    return config


def create_tpo_node_config(
    node: Dict[str, Any],
    is_highlighted: bool = False
) -> Dict[str, Any]:
    """
    Create node configuration for a TPO.
    
    Uses hexagon shape to represent program objectives/goals.
    Gold color for high visibility.
    
    Args:
        node: TPO node dictionary
        is_highlighted: Whether node is selected
    
    Returns:
        PyVis node configuration dictionary
    """
    # =========================
    # SIZE
    # =========================
    size = NODE_SIZES["tpo"]
    if is_highlighted:
        size += NODE_SIZES["highlight_bonus"]
    
    # =========================
    # BORDER STYLING
    # =========================
    if is_highlighted:
        border_color = HIGHLIGHT_COLOR
        border_width = BORDER_STYLES["highlighted"]["width"]
    else:
        border_color = TPO_COLORS["border"]
        border_width = 3
    
    # =========================
    # LABEL CONSTRUCTION
    # =========================
    label = f"🎯 {node.get('reference', 'TPO')}"
    if is_highlighted:
        label = f"★ {label}"
    
    # =========================
    # BUILD CONFIGURATION
    # =========================
    config = {
        "label": label,
        "title": build_tpo_tooltip(node, is_highlighted),
        "shape": TPO_SHAPE,
        "size": size,
        "color": {
            "background": TPO_COLORS["background"],
            "border": border_color,
            "highlight": {
                "background": TPO_COLORS["highlight"],
                "border": HIGHLIGHT_COLOR
            }
        },
        "borderWidth": border_width,
        "borderWidthSelected": BORDER_STYLES["highlighted"]["width"],
        "font": {
            "color": TPO_COLORS["text"],
            "size": 20,
            "face": "Arial",
            "bold": True
        },
        "shadow": {
            "enabled": True,
            "color": HIGHLIGHT_COLOR if is_highlighted else "rgba(0,0,0,0.2)",
            "size": 15 if is_highlighted else 10,
            "x": 3,
            "y": 3
        }
    }
    
    return config


def create_node_config(
    node: Dict[str, Any],
    color_by: str = "level",
    highlighted_node_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create node configuration for any node type.
    
    Dispatcher function that routes to the appropriate
    type-specific configuration function.
    
    Args:
        node: Node dictionary with 'node_type' field
        color_by: Coloring scheme for risks ("level" or "exposure")
        highlighted_node_id: ID of highlighted node
    
    Returns:
        PyVis node configuration dictionary
    """
    node_type = node.get("node_type", "Risk")
    is_highlighted = highlighted_node_id and node.get("id") == highlighted_node_id
    
    if node_type == "TPO":
        return create_tpo_node_config(node, is_highlighted)
    elif node_type == "Mitigation":
        return create_mitigation_node_config(node, is_highlighted)
    else:
        return create_risk_node_config(node, color_by, is_highlighted)


# =============================================================================
# LEGEND CONFIGURATION
# =============================================================================

def get_legend_items() -> Dict[str, Any]:
    """
    Get legend configuration for the graph visualization.
    
    Returns:
        Dictionary with legend items for nodes and relationships
    """
    return {
        "nodes": {
            "risks": [
                {"label": "Business Risk", "shape": "diamond", "color": RISK_COLORS["business"]["base"], "icon": "◆"},
                {"label": "Operational Risk", "shape": "dot", "color": RISK_COLORS["operational"]["base"], "icon": "●"},
                {"label": "Contingent Risk", "shape": "diamond", "color": RISK_COLORS["business"]["base"], "dashed": True, "icon": "◇"},
                {"label": "Legacy Risk", "shape": "dot", "color": RISK_COLORS["operational"]["base"], "border": "#7F8C8D", "icon": "●[L]"}
            ],
            "exposure": [
                {"label": "Critical (≥7)", "color": EXPOSURE_COLORS["critical"]},
                {"label": "High (≥4)", "color": EXPOSURE_COLORS["high"]},
                {"label": "Medium (≥2)", "color": EXPOSURE_COLORS["medium"]},
                {"label": "Low (<2)", "color": EXPOSURE_COLORS["low"]}
            ],
            "mitigations": [
                {"label": "Dedicated", "shape": "box", "color": MITIGATION_COLORS["dedicated"]["implemented"], "icon": "🛡️"},
                {"label": "Inherited", "shape": "box", "color": MITIGATION_COLORS["inherited"]["implemented"], "dashed": True, "icon": "🛡️"},
                {"label": "Baseline", "shape": "box", "color": MITIGATION_COLORS["baseline"]["implemented"], "thick": True, "icon": "🛡️"}
            ],
            "tpo": [
                {"label": "Program Objective", "shape": "hexagon", "color": TPO_COLORS["background"], "icon": "🎯"}
            ]
        },
        "status_indicators": {
            "implemented": {"label": "Implemented", "border": "solid"},
            "in_progress": {"label": "In Progress", "border": "dash-dot"},
            "proposed": {"label": "Proposed", "border": "dashed"},
            "deferred": {"label": "Deferred", "border": "dotted"}
        }
    }
