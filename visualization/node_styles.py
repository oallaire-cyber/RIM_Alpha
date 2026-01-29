"""
Node Styling for RIM Graph Visualization.

Provides styling configuration for different node types.
"""

from typing import Dict, Any, Optional, List
from visualization.colors import (
    get_color_by_level,
    get_color_by_exposure,
    get_mitigation_color,
    TPO_COLORS,
    HIGHLIGHT_COLOR
)


def wrap_label(text: str, max_width: int = 20) -> str:
    """
    Wrap text into multiple lines for better display.
    
    Args:
        text: Text to wrap
        max_width: Maximum characters per line
    
    Returns:
        Wrapped text with newlines
    """
    if len(text) <= max_width:
        return text
    
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
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def create_tpo_node_config(
    node: Dict[str, Any],
    is_highlighted: bool = False
) -> Dict[str, Any]:
    """
    Create node configuration for a TPO.
    
    Args:
        node: TPO node dictionary
        is_highlighted: Whether node is selected
    
    Returns:
        PyVis node configuration dictionary
    """
    color = TPO_COLORS["background"]
    shape = "hexagon"
    size = 35
    
    if is_highlighted:
        border_color = HIGHLIGHT_COLOR
        border_width = 6
        shadow_color = HIGHLIGHT_COLOR
    else:
        border_color = TPO_COLORS["border"]
        border_width = 2
        shadow_color = "rgba(0,0,0,0.2)"
    
    # Build tooltip
    title_parts = [
        f"🎯 {node['reference']}: {node['name']}",
        f"Type: Top Program Objective",
        f"Cluster: {node.get('cluster', 'N/A')}",
        f"Description: {node.get('description', 'N/A')}"
    ]
    if is_highlighted:
        title_parts.append("★ SELECTED NODE")
    title = "\n".join(title_parts)
    
    # Label
    label = f"{node['reference']}"
    if is_highlighted:
        label = f"★ {label}"
    
    return {
        "label": label,
        "title": title,
        "color": {
            "background": color,
            "border": border_color,
            "highlight": {"background": TPO_COLORS["highlight"], "border": HIGHLIGHT_COLOR}
        },
        "size": size + (10 if is_highlighted else 0),
        "shape": shape,
        "borderWidth": border_width,
        "borderWidthSelected": 6,
        "font": {"color": "#333333", "size": 16, "face": "Arial", "bold": True},
        "shadow": {"enabled": True, "color": shadow_color, "size": 15 if is_highlighted else 10}
    }


def create_mitigation_node_config(
    node: Dict[str, Any],
    is_highlighted: bool = False
) -> Dict[str, Any]:
    """
    Create node configuration for a Mitigation.
    
    Args:
        node: Mitigation node dictionary
        is_highlighted: Whether node is selected
    
    Returns:
        PyVis node configuration dictionary
    """
    mit_type = node.get("type", "Dedicated")
    mit_status = node.get("status", "Proposed")
    
    color = get_mitigation_color(mit_type, mit_status)
    shape = "box"
    size = 30
    
    if is_highlighted:
        border_color = HIGHLIGHT_COLOR
        border_width = 6
        shadow_color = HIGHLIGHT_COLOR
    else:
        border_color = "#1e8449"
        border_width = 2
        shadow_color = "rgba(0,0,0,0.2)"
    
    # Status and type emojis
    status_emoji = {
        "Proposed": "📋",
        "In Progress": "🔄",
        "Implemented": "✅",
        "Deferred": "⏸️"
    }
    type_emoji = {
        "Dedicated": "🎯",
        "Inherited": "📥",
        "Baseline": "📐"
    }
    
    # Build tooltip
    title_parts = [
        f"🛡️ {node['name']}",
        f"Type: {mit_type} {type_emoji.get(mit_type, '')}",
        f"Status: {mit_status} {status_emoji.get(mit_status, '')}",
        f"Owner: {node.get('owner', 'N/A')}"
    ]
    if node.get('source_entity'):
        title_parts.append(f"Source: {node['source_entity']}")
    if node.get('description'):
        title_parts.append(f"Description: {node['description']}")
    if is_highlighted:
        title_parts.append("★ SELECTED NODE")
    title = "\n".join(title_parts)
    
    # Label
    label = wrap_label(node["name"], max_width=18)
    if is_highlighted:
        label = f"★ {label}"
    label = f"🛡️ {label}"
    
    return {
        "label": label,
        "title": title,
        "color": {
            "background": color,
            "border": border_color,
            "highlight": {"background": "#2ecc71", "border": HIGHLIGHT_COLOR}
        },
        "size": size + (10 if is_highlighted else 0),
        "shape": shape,
        "borderWidth": border_width,
        "borderWidthSelected": 6,
        "font": {"color": "#ffffff", "size": 14, "face": "Arial"},
        "shadow": {"enabled": True, "color": shadow_color, "size": 15 if is_highlighted else 10},
        "shapeProperties": {"borderDashes": [3, 3] if mit_status == "Proposed" else False}
    }


def create_risk_node_config(
    node: Dict[str, Any],
    color_by: str = "level",
    is_highlighted: bool = False
) -> Dict[str, Any]:
    """
    Create node configuration for a Risk.
    
    Args:
        node: Risk node dictionary
        color_by: Coloring scheme ("level" or "exposure")
        is_highlighted: Whether node is selected
    
    Returns:
        PyVis node configuration dictionary
    """
    exposure = node.get("exposure") or 0
    level = node.get("level", "Operational")
    status = node.get("status", "Active")
    origin = node.get("origin", "New")
    
    # Determine color
    if color_by == "level":
        base_color = get_color_by_level(level)
    else:
        base_color = get_color_by_exposure(exposure)
    
    # Size based on exposure
    size = 25 + (exposure * 1.5) if exposure else 25
    
    # Shape: box for contingent, dot for others
    shape = "box" if status == "Contingent" else "dot"
    
    # Highlight styling
    if is_highlighted:
        border_color = HIGHLIGHT_COLOR
        border_width = 6
        shadow_color = HIGHLIGHT_COLOR
        size += 10
    else:
        if origin == "Legacy":
            border_color = "#7f8c8d"
            border_width = 4
        else:
            border_color = base_color
            border_width = 2
        shadow_color = "rgba(0,0,0,0.2)"
    
    # Build tooltip
    categories_str = ", ".join(node.get("categories", [])) if node.get("categories") else "N/A"
    exposure_str = f"{exposure:.2f}" if exposure else "N/A"
    
    title_parts = [
        f"{node['name']}",
        f"Level: {level}",
        f"Origin: {origin}",
        f"Status: {status}",
        f"Categories: {categories_str}",
        f"Exposure: {exposure_str}",
        f"Owner: {node.get('owner', 'N/A')}"
    ]
    if is_highlighted:
        title_parts.append("★ SELECTED NODE")
    title = "\n".join(title_parts)
    
    # Label
    label = wrap_label(node["name"], max_width=20)
    if is_highlighted:
        label = f"★ {label}"
    if origin == "Legacy":
        label = f"[L] {label}"
    
    return {
        "label": label,
        "title": title,
        "color": {
            "background": base_color,
            "border": border_color,
            "highlight": {"background": base_color, "border": HIGHLIGHT_COLOR}
        },
        "size": size,
        "shape": shape,
        "borderWidth": border_width,
        "borderWidthSelected": 6,
        "font": {"color": "#333333", "size": 16, "face": "Arial"},
        "shadow": {"enabled": True, "color": shadow_color, "size": 15 if is_highlighted else 10},
        "shapeProperties": {"borderDashes": [5, 5] if origin == "Legacy" else False}
    }


def create_node_config(
    node: Dict[str, Any],
    color_by: str = "level",
    highlighted_node_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create node configuration for any node type.
    
    Args:
        node: Node dictionary
        color_by: Coloring scheme for risks
        highlighted_node_id: ID of highlighted node
    
    Returns:
        PyVis node configuration dictionary
    """
    node_type = node.get("node_type", "Risk")
    is_highlighted = highlighted_node_id and node["id"] == highlighted_node_id
    
    if node_type == "TPO":
        return create_tpo_node_config(node, is_highlighted)
    elif node_type == "Mitigation":
        return create_mitigation_node_config(node, is_highlighted)
    else:
        return create_risk_node_config(node, color_by, is_highlighted)
