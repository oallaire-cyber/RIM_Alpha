"""
Edge Styling for RIM Graph Visualization.

Enhanced edge styles with semantic differentiation:
- Influence edges: Standard arrows with color by type (Level 1/2/3)
- Mitigation edges: Bar-end arrows (⊣) representing "blocking" effect
- TPO Impact edges: Vee arrows (▷) with dash-dot pattern
"""

from typing import Dict, Any, Optional, List, Tuple
from visualization.colors import (
    INFLUENCE_TYPE_COLORS,
    EFFECTIVENESS_COLORS,
    IMPACT_COLORS,
    get_influence_color,
    get_effectiveness_color,
    get_impact_color
)


# =============================================================================
# ARROW CONFIGURATIONS
# =============================================================================

ARROW_STYLES = {
    "influence": {
        "to": {
            "enabled": True,
            "scaleFactor": 1.0,
            "type": "arrow"  # Standard arrow for influence
        }
    },
    "mitigation": {
        "to": {
            "enabled": True,
            "scaleFactor": 0.8,
            "type": "bar"  # Bar end = "blocking" metaphor
        }
    },
    "impact": {
        "to": {
            "enabled": True,
            "scaleFactor": 1.2,
            "type": "vee"  # Vee arrow = "targeting" metaphor
        }
    }
}


# =============================================================================
# WIDTH CONFIGURATIONS
# =============================================================================

# Base widths for influence types
INFLUENCE_BASE_WIDTHS = {
    "Level1": 4.0,    # Op→Bus (thickest - major impact)
    "Level2": 3.0,    # Bus→Bus
    "Level3": 2.0     # Op→Op (thinnest)
}

# Width multipliers for influence strengths
STRENGTH_WIDTH_MULTIPLIERS = {
    "Critical": 1.5,
    "Strong": 1.25,
    "Moderate": 1.0,
    "Weak": 0.75
}

# Widths for effectiveness levels (mitigation edges)
EFFECTIVENESS_WIDTHS = {
    "Critical": 5,
    "High": 4,
    "Medium": 3,
    "Low": 2
}

# Widths for impact levels (TPO edges)
IMPACT_WIDTHS = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1.5
}


# =============================================================================
# DASH PATTERNS
# =============================================================================

DASH_PATTERNS = {
    # Influence types
    "level1": False,           # Solid for Op→Bus
    "level2": False,           # Solid for Bus→Bus
    "level3": [8, 4],          # Dashed for Op→Op
    
    # Mitigation effectiveness
    "mitigation_critical": False,
    "mitigation_high": False,
    "mitigation_medium": [6, 3],
    "mitigation_low": [3, 3],
    
    # TPO Impact (all use dash-dot pattern)
    "impact_critical": [10, 5, 2, 5],
    "impact_high": [8, 4, 2, 4],
    "impact_medium": [6, 3, 2, 3],
    "impact_low": [4, 4]
}


# =============================================================================
# SMOOTH CURVE SETTINGS
# =============================================================================

SMOOTH_SETTINGS = {
    "influence": {
        "type": "curvedCW",
        "roundness": 0.15
    },
    "mitigation": {
        "type": "curvedCCW",
        "roundness": 0.2
    },
    "impact": {
        "type": "curvedCW",
        "roundness": 0.1
    }
}


# =============================================================================
# EDGE CONFIGURATION FUNCTIONS
# =============================================================================

def create_influence_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for an INFLUENCES relationship.
    
    Uses standard arrow with color coding by influence type:
    - Level 1 (Op→Bus): Red, thick, solid - causes consequence
    - Level 2 (Bus→Bus): Purple, medium, solid - amplifies
    - Level 3 (Op→Op): Blue, thin, dashed - contributes
    
    Args:
        edge: Edge dictionary with influence details
    
    Returns:
        PyVis edge configuration dictionary
    """
    strength = edge.get("strength", "Moderate")
    influence_type = edge.get("influence_type", "Unknown")
    
    # =========================
    # COLOR
    # =========================
    color = get_influence_color(influence_type)
    
    # =========================
    # WIDTH
    # =========================
    # Get base width for influence type
    base_width = 2.0
    for key, width in INFLUENCE_BASE_WIDTHS.items():
        if key in influence_type:
            base_width = width
            break
    
    # Apply strength multiplier
    multiplier = STRENGTH_WIDTH_MULTIPLIERS.get(strength, 1.0)
    width = base_width * multiplier
    
    # =========================
    # DASH PATTERN
    # =========================
    dashes = False
    if "Level3" in influence_type:
        dashes = DASH_PATTERNS["level3"]
    
    # =========================
    # TOOLTIP
    # =========================
    # Format type for display
    type_display = influence_type.replace("_", " → ").replace("Level1", "Level 1").replace("Level2", "Level 2").replace("Level3", "Level 3")
    
    title_parts = [f"⚡ {type_display}", f"Strength: {strength}"]
    if edge.get("description"):
        title_parts.append(f"Description: {edge['description']}")
    title = "\n".join(title_parts)
    
    # =========================
    # BUILD CONFIGURATION
    # =========================
    config = {
        "title": title,
        "width": width,
        "color": {
            "color": color,
            "highlight": color,
            "hover": color
        },
        "arrows": ARROW_STYLES["influence"],
        "dashes": dashes,
        "smooth": SMOOTH_SETTINGS["influence"]
    }
    
    return config


def create_mitigates_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for a MITIGATES relationship.
    
    Uses bar-end arrow (⊣) to represent "blocking" effect.
    Green color family indicates protective action.
    Width and dash pattern indicate effectiveness.
    
    Args:
        edge: Edge dictionary with mitigation details
    
    Returns:
        PyVis edge configuration dictionary
    """
    effectiveness = edge.get("effectiveness", "Medium")
    
    # =========================
    # COLOR
    # =========================
    color = get_effectiveness_color(effectiveness)
    
    # =========================
    # WIDTH
    # =========================
    width = EFFECTIVENESS_WIDTHS.get(effectiveness, 3)
    
    # =========================
    # DASH PATTERN
    # =========================
    dash_key = f"mitigation_{effectiveness.lower()}"
    dashes = DASH_PATTERNS.get(dash_key, False)
    
    # =========================
    # TOOLTIP
    # =========================
    # Effectiveness icon
    eff_icons = {
        "Critical": "🛡️🛡️🛡️",
        "High": "🛡️🛡️",
        "Medium": "🛡️",
        "Low": "🔰"
    }
    
    title_parts = [
        f"{eff_icons.get(effectiveness, '🛡️')} Mitigates",
        f"Effectiveness: {effectiveness}"
    ]
    if edge.get("description"):
        title_parts.append(f"Description: {edge['description']}")
    title = "\n".join(title_parts)
    
    # =========================
    # BUILD CONFIGURATION
    # =========================
    config = {
        "title": title,
        "width": width,
        "color": {
            "color": color,
            "highlight": color,
            "hover": color
        },
        "arrows": ARROW_STYLES["mitigation"],  # Bar-end arrow
        "dashes": dashes,
        "smooth": SMOOTH_SETTINGS["mitigation"]
    }
    
    return config


def create_tpo_impact_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for an IMPACTS_TPO relationship.
    
    Uses vee arrow (▷) to represent "targeting" effect on objectives.
    Orange color family indicates threat to goals.
    Dash-dot pattern distinguishes from other edge types.
    
    Args:
        edge: Edge dictionary with impact details
    
    Returns:
        PyVis edge configuration dictionary
    """
    impact_level = edge.get("impact_level", "Medium")
    
    # =========================
    # COLOR
    # =========================
    color = get_impact_color(impact_level)
    
    # =========================
    # WIDTH
    # =========================
    width = IMPACT_WIDTHS.get(impact_level, 2)
    
    # =========================
    # DASH PATTERN
    # =========================
    dash_key = f"impact_{impact_level.lower()}"
    dashes = DASH_PATTERNS.get(dash_key, [6, 3, 2, 3])
    
    # =========================
    # TOOLTIP
    # =========================
    # Impact icon
    impact_icons = {
        "Critical": "💥",
        "High": "⚠️",
        "Medium": "📊",
        "Low": "📉"
    }
    
    title_parts = [
        f"{impact_icons.get(impact_level, '📊')} Impacts TPO",
        f"Impact Level: {impact_level}"
    ]
    if edge.get("description"):
        title_parts.append(f"Description: {edge['description']}")
    title = "\n".join(title_parts)
    
    # =========================
    # BUILD CONFIGURATION
    # =========================
    config = {
        "title": title,
        "width": width,
        "color": {
            "color": color,
            "highlight": color,
            "hover": color
        },
        "arrows": ARROW_STYLES["impact"],  # Vee arrow
        "dashes": dashes,
        "smooth": SMOOTH_SETTINGS["impact"]
    }
    
    return config


def create_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for any edge type.
    
    Dispatcher function that routes to the appropriate
    type-specific configuration function.
    
    Args:
        edge: Edge dictionary with 'edge_type' field
    
    Returns:
        PyVis edge configuration dictionary
    """
    edge_type = edge.get("edge_type", "INFLUENCES")
    
    if edge_type == "IMPACTS_TPO":
        return create_tpo_impact_edge_config(edge)
    elif edge_type == "MITIGATES":
        return create_mitigates_edge_config(edge)
    else:
        return create_influence_edge_config(edge)


# =============================================================================
# EDGE FILTERING
# =============================================================================

def filter_edges_by_score(
    edges: List[Dict[str, Any]],
    max_edges: int,
    edge_scores: Optional[Dict[Tuple[str, str], float]] = None
) -> List[Dict[str, Any]]:
    """
    Filter edges to show only the most important ones.
    
    Useful for reducing visual complexity in dense graphs.
    
    Args:
        edges: List of edge dictionaries
        max_edges: Maximum number of edges to return
        edge_scores: Optional dict mapping (source, target) to score
    
    Returns:
        Filtered list of edges
    """
    if max_edges is None or max_edges >= len(edges):
        return edges
    
    if edge_scores:
        # Sort edges by provided score
        scored = [(e, edge_scores.get((e["source"], e["target"]), 0)) for e in edges]
        scored.sort(key=lambda x: -x[1])
        return [e for e, s in scored[:max_edges]]
    else:
        # Fallback: prioritize by strength/impact/effectiveness
        def edge_priority(e: Dict[str, Any]) -> int:
            strength_order = {"Critical": 4, "Strong": 3, "Moderate": 2, "Weak": 1}
            impact_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
            
            edge_type = e.get("edge_type", "INFLUENCES")
            
            if edge_type == "IMPACTS_TPO":
                return impact_order.get(e.get("impact_level", "Medium"), 2)
            elif edge_type == "MITIGATES":
                return impact_order.get(e.get("effectiveness", "Medium"), 2)
            else:
                # For influences, also prioritize by type
                influence_type = e.get("influence_type", "")
                type_bonus = 0
                if "Level1" in influence_type:
                    type_bonus = 3
                elif "Level2" in influence_type:
                    type_bonus = 2
                elif "Level3" in influence_type:
                    type_bonus = 1
                
                return strength_order.get(e.get("strength", "Moderate"), 2) + type_bonus
        
        sorted_edges = sorted(edges, key=edge_priority, reverse=True)
        return sorted_edges[:max_edges]


def filter_edges_by_type(
    edges: List[Dict[str, Any]],
    include_influences: bool = True,
    include_mitigations: bool = True,
    include_impacts: bool = True
) -> List[Dict[str, Any]]:
    """
    Filter edges by relationship type.
    
    Args:
        edges: List of edge dictionaries
        include_influences: Include INFLUENCES edges
        include_mitigations: Include MITIGATES edges
        include_impacts: Include IMPACTS_TPO edges
    
    Returns:
        Filtered list of edges
    """
    filtered = []
    
    for edge in edges:
        edge_type = edge.get("edge_type", "INFLUENCES")
        
        if edge_type == "INFLUENCES" and include_influences:
            filtered.append(edge)
        elif edge_type == "MITIGATES" and include_mitigations:
            filtered.append(edge)
        elif edge_type == "IMPACTS_TPO" and include_impacts:
            filtered.append(edge)
    
    return filtered


# =============================================================================
# LEGEND CONFIGURATION
# =============================================================================

def get_edge_legend_items() -> Dict[str, Any]:
    """
    Get legend configuration for edge types.
    
    Returns:
        Dictionary with legend items for edge relationships
    """
    return {
        "influences": [
            {
                "label": "Level 1: Op → Bus",
                "description": "Causes consequence",
                "color": INFLUENCE_TYPE_COLORS["Level1"],
                "width": 4,
                "dashes": False,
                "arrow": "arrow"
            },
            {
                "label": "Level 2: Bus → Bus",
                "description": "Amplifies",
                "color": INFLUENCE_TYPE_COLORS["Level2"],
                "width": 3,
                "dashes": False,
                "arrow": "arrow"
            },
            {
                "label": "Level 3: Op → Op",
                "description": "Contributes to",
                "color": INFLUENCE_TYPE_COLORS["Level3"],
                "width": 2,
                "dashes": [8, 4],
                "arrow": "arrow"
            }
        ],
        "mitigations": [
            {
                "label": "Critical Effectiveness",
                "color": EFFECTIVENESS_COLORS["Critical"],
                "width": 5,
                "dashes": False,
                "arrow": "bar"
            },
            {
                "label": "High Effectiveness",
                "color": EFFECTIVENESS_COLORS["High"],
                "width": 4,
                "dashes": False,
                "arrow": "bar"
            },
            {
                "label": "Medium Effectiveness",
                "color": EFFECTIVENESS_COLORS["Medium"],
                "width": 3,
                "dashes": [6, 3],
                "arrow": "bar"
            },
            {
                "label": "Low Effectiveness",
                "color": EFFECTIVENESS_COLORS["Low"],
                "width": 2,
                "dashes": [3, 3],
                "arrow": "bar"
            }
        ],
        "impacts": [
            {
                "label": "Critical Impact",
                "color": IMPACT_COLORS["Critical"],
                "width": 4,
                "dashes": [10, 5, 2, 5],
                "arrow": "vee"
            },
            {
                "label": "High Impact",
                "color": IMPACT_COLORS["High"],
                "width": 3,
                "dashes": [8, 4, 2, 4],
                "arrow": "vee"
            },
            {
                "label": "Medium Impact",
                "color": IMPACT_COLORS["Medium"],
                "width": 2,
                "dashes": [6, 3, 2, 3],
                "arrow": "vee"
            }
        ]
    }
