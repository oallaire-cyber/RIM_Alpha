"""
Node Styling for RIM Graph Visualization.

Dynamically styles nodes based on active schema registry.
Supports flexible shapes, colors, and indicators.
"""

from typing import Dict, Any, Optional
from core import get_registry


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def wrap_label(text: str, max_width: int = 20) -> str:
    """Wrap text into multiple lines for better display."""
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
    
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2][:max_width-3] + "..."
    
    return '\n'.join(lines)


def build_generic_tooltip(node: Dict[str, Any], entity_type, is_highlighted: bool = False) -> str:
    """Build tooltip content for a generic node."""
    name = node.get('name', 'Unknown')
    parts = [f"{entity_type.emoji} {name}"]
    
    # Show specific useful fields for tooltips
    tooltip_fields = [
        ("Level", "level"),
        ("Origin", "origin"),
        ("Category", "category"),
        ("Exposure", "exposure"),
    ]
    for label, key in tooltip_fields:
        val = node.get(key)
        if val is not None:
            if isinstance(val, float):
                parts.append(f"{label}: {val:.1f}")
            else:
                parts.append(f"{label}: {val}")
    
    if is_highlighted:
        parts.append("★ SELECTED NODE")
    
    return "\n".join(parts)


# =============================================================================
# NODE CONFIGURATION FUNCTIONS
# =============================================================================

def create_node_config(
    node: Dict[str, Any],
    color_by: str = "level",
    highlighted_node_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create node configuration for any node type from schema.
    """
    registry = get_registry()
    node_type_id = node.get("node_type", "risk").lower()
    entity_type = registry.get_entity_type(node_type_id)
    
    if not entity_type:
        # Fallback for untyped nodes
        return {"label": node.get("name", "Unknown"), "shape": "dot"}

    is_highlighted = highlighted_node_id and node.get("id") == highlighted_node_id
    
    # 🎨 Color and Shape Selection
    # Start with entity defaults
    base_color = entity_type.color
    shape = entity_type.shape
    emoji = entity_type.emoji
    
    # For risks, get shape/color from level configuration in categorical_groups
    if node_type_id == "risk":
        level = node.get("level", "")
        levels = entity_type.categorical_groups.get("levels", [])
        for level_config in levels:
            if level_config.get("label") == level or level_config.get("id") == level.lower():
                base_color = level_config.get("color", base_color)
                shape = level_config.get("shape", shape)
                emoji = level_config.get("emoji", emoji)
                break
    
    # Special: Color risks by exposure if requested
    exposure = node.get("exposure", 0)
    if node_type_id == "risk" and color_by == "exposure":
        from visualization.colors import get_color_by_exposure
        base_color = get_color_by_exposure(exposure)
    
    # 📐 Size Calculation
    # Scale size with exposure if it's a risk
    base_size = 30
    size = base_size + (exposure * 1.2) if exposure else base_size
    
    if is_highlighted:
        size += 10
    
    # 🔲 Border Styling
    border_color = base_color
    border_width = 2
    border_dashes = False
    
    if is_highlighted:
        border_color = "#FFFF00" # Yellow highlight
        border_width = 6
        
    # Check for contingent/proposed status to apply dashes
    status = node.get("status", "").lower()
    if status in ("contingent", "proposed"):
        border_dashes = [8, 4]
        border_width = 3
    
    # 📝 Label Construction
    label = f"{emoji} " + wrap_label(node.get("name", ""), 18)
    if is_highlighted:
        label = f"★ {label}"
    
    # 🏛️ Build Final Config
    config = {
        "label": label,
        "title": build_generic_tooltip(node, entity_type, is_highlighted),
        "shape": shape,
        "size": size,
        "color": {
            "background": base_color,
            "border": border_color,
            "highlight": {
                "background": base_color,
                "border": "#FFFF00"
            }
        },
        "borderWidth": border_width,
        "borderWidthSelected": 6,
        "shapeProperties": {
            "borderDashes": border_dashes,
            "borderRadius": 6 if entity_type.shape == "box" else 0
        },
        "font": {
            "color": "#FFFFFF" if entity_type.shape == "box" else "#2C3E50",
            "size": 20,
            "face": "Arial",
            "bold": node_type_id == "risk"
        },
        "shadow": {
            "enabled": True,
            "color": "rgba(0,0,0,0.2)",
            "size": 10,
            "x": 3,
            "y": 3
        }
    }
    
    return config


def get_legend_items() -> Dict[str, Any]:
    """Get legend configuration from schema registry."""
    registry = get_registry()
    items = {"nodes": {}, "status_indicators": {}}
    
    for entity_id, entity in registry.entity_types.items():
        if entity_id not in items["nodes"]:
            items["nodes"][entity_id] = []
        
        items["nodes"][entity_id].append({
            "label": entity.label,
            "shape": entity.shape,
            "color": entity.color,
            "icon": entity.emoji
        })
        
    return items


# =============================================================================
# BACKWARD-COMPATIBLE CONSTANTS (DEPRECATED - use schema registry)
# =============================================================================

# Legacy shape configurations
RISK_SHAPES = {
    "business": "diamond",
    "operational": "dot",
    "strategic": "diamond",
    "tactical": "dot"
}

MITIGATION_SHAPE = "box"
TPO_SHAPE = "hexagon"

NODE_SIZES = {
    "default": 30,
    "risk": 35,
    "mitigation": 28,
    "tpo": 32
}

BORDER_STYLES = {
    "default": {"width": 2, "dashes": False},
    "contingent": {"width": 3, "dashes": [8, 4]},
    "proposed": {"width": 3, "dashes": [8, 4]},
    "highlighted": {"width": 6, "dashes": False}
}


def truncate_label(text: str, max_length: int = 25) -> str:
    """Truncate text to max length with ellipsis."""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length - 3] + "..."


# Legacy function aliases (all delegate to create_node_config)
def create_risk_node_config(node, color_by="level", highlighted=None):
    """Create risk node config (legacy wrapper)."""
    node["node_type"] = "risk"
    return create_node_config(node, color_by, highlighted)


def create_mitigation_node_config(node, highlighted=None):
    """Create mitigation node config (legacy wrapper)."""
    node["node_type"] = "mitigation"
    return create_node_config(node, "level", highlighted)


def create_tpo_node_config(node, highlighted=None):
    """Create TPO node config (legacy wrapper)."""
    node["node_type"] = "tpo"
    return create_node_config(node, "level", highlighted)
