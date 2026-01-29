"""
Edge Styling for RIM Graph Visualization.

Provides styling configuration for different edge types.
"""

from typing import Dict, Any, Optional, List, Tuple
from visualization.colors import (
    get_influence_color,
    get_effectiveness_color,
    get_impact_color
)


# Width multipliers for influence strengths
STRENGTH_WIDTH_MULTIPLIERS = {
    "Critical": 2.0,
    "Strong": 1.5,
    "Moderate": 1.2,
    "Weak": 1.0
}

# Base widths for influence types
INFLUENCE_BASE_WIDTHS = {
    "Level1": 2.0,    # Op→Strat
    "Level2": 2.5,    # Strat→Strat
    "Level3": 1.5     # Op→Op
}

# Widths for effectiveness levels
EFFECTIVENESS_WIDTHS = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1.5
}

# Widths for impact levels
IMPACT_WIDTHS = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1.5
}


def create_influence_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for an INFLUENCES relationship.
    
    Args:
        edge: Edge dictionary with influence details
    
    Returns:
        PyVis edge configuration dictionary
    """
    strength = edge.get("strength", "Moderate")
    influence_type = edge.get("influence_type", "Unknown")
    
    # Get color based on influence type
    color = get_influence_color(influence_type)
    
    # Get base width based on influence type
    base_width = 1.5
    for key, width in INFLUENCE_BASE_WIDTHS.items():
        if key in influence_type:
            base_width = width
            break
    
    # Apply strength multiplier
    multiplier = STRENGTH_WIDTH_MULTIPLIERS.get(strength, 1.0)
    width = base_width * multiplier
    
    # Build tooltip
    title = f"{influence_type} ({strength})"
    if edge.get("description"):
        title += f"\n{edge['description']}"
    
    return {
        "title": title,
        "width": width,
        "color": color
    }


def create_tpo_impact_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for an IMPACTS_TPO relationship.
    
    Args:
        edge: Edge dictionary with impact details
    
    Returns:
        PyVis edge configuration dictionary
    """
    impact_level = edge.get("impact_level", "Medium")
    
    color = "#3498db"  # Blue for TPO impacts
    width = IMPACT_WIDTHS.get(impact_level, 2)
    
    # Build tooltip
    title = f"Impacts TPO ({impact_level})"
    if edge.get("description"):
        title += f"\n{edge['description']}"
    
    return {
        "title": title,
        "width": width,
        "color": color,
        "dashes": True
    }


def create_mitigates_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for a MITIGATES relationship.
    
    Args:
        edge: Edge dictionary with mitigation details
    
    Returns:
        PyVis edge configuration dictionary
    """
    effectiveness = edge.get("effectiveness", "Medium")
    
    color = get_effectiveness_color(effectiveness)
    width = EFFECTIVENESS_WIDTHS.get(effectiveness, 2)
    
    # Build tooltip
    title = f"🛡️ Mitigates ({effectiveness})"
    if edge.get("description"):
        title += f"\n{edge['description']}"
    
    return {
        "title": title,
        "width": width,
        "color": color,
        "dashes": [5, 5],
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}}
    }


def create_edge_config(edge: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create edge configuration for any edge type.
    
    Args:
        edge: Edge dictionary
    
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


def filter_edges_by_score(
    edges: List[Dict[str, Any]],
    max_edges: int,
    edge_scores: Optional[Dict[Tuple[str, str], float]] = None
) -> List[Dict[str, Any]]:
    """
    Filter edges to show only the most important ones.
    
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
        # Sort edges by score
        scored = [(e, edge_scores.get((e["source"], e["target"]), 0)) for e in edges]
        scored.sort(key=lambda x: -x[1])
        return [e for e, s in scored[:max_edges]]
    else:
        # Fallback: prioritize by strength/impact
        def edge_priority(e: Dict[str, Any]) -> int:
            strength_order = {"Critical": 4, "Strong": 3, "Moderate": 2, "Weak": 1}
            impact_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
            
            if e.get("edge_type") == "IMPACTS_TPO":
                return impact_order.get(e.get("impact_level", "Medium"), 2)
            elif e.get("edge_type") == "MITIGATES":
                return strength_order.get(e.get("effectiveness", "Medium"), 2)
            return strength_order.get(e.get("strength", "Moderate"), 2)
        
        sorted_edges = sorted(edges, key=edge_priority, reverse=True)
        return sorted_edges[:max_edges]
