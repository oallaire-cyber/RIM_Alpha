"""
Layout Management for RIM Application.

Provides graph layout generation and persistence.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import math

from config.settings import TPO_CLUSTERS


class LayoutManager:
    """
    Manager for saving/restoring node positions.
    
    Persists custom layouts to JSON file for later retrieval.
    """
    
    def __init__(self, layout_file: str = "graph_layouts.json"):
        """
        Initialize the layout manager.
        
        Args:
            layout_file: Path to the JSON file for storing layouts
        """
        self.layout_file = layout_file
        self.layouts = self._load_layouts()
    
    def _load_layouts(self) -> Dict[str, Any]:
        """Load layouts from JSON file."""
        if Path(self.layout_file).exists():
            try:
                with open(self.layout_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_layouts(self):
        """Save layouts to JSON file."""
        with open(self.layout_file, 'w', encoding='utf-8') as f:
            json.dump(self.layouts, f, indent=2, ensure_ascii=False)
    
    def save_layout(self, name: str, positions: Dict[str, Dict[str, float]]):
        """
        Save a layout with the given name.
        
        Args:
            name: Name for the layout
            positions: Dictionary mapping node IDs to {x, y} positions
        """
        self.layouts[name] = {
            "positions": positions,
            "saved_at": datetime.now().isoformat(),
            "node_count": len(positions)
        }
        self._save_layouts()
    
    def load_layout(self, name: str) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Load a layout by name.
        
        Args:
            name: Name of the layout to load
        
        Returns:
            Position dictionary or None if not found
        """
        layout = self.layouts.get(name)
        return layout["positions"] if layout else None
    
    def list_layouts(self) -> Dict[str, Dict[str, Any]]:
        """
        List all saved layouts with their metadata.
        
        Returns:
            Dictionary of layout names to metadata
        """
        return {
            name: {
                "saved_at": data["saved_at"],
                "node_count": data["node_count"]
            }
            for name, data in self.layouts.items()
        }
    
    def delete_layout(self, name: str) -> bool:
        """
        Delete a layout by name.
        
        Args:
            name: Name of the layout to delete
        
        Returns:
            True if deleted, False if not found
        """
        if name in self.layouts:
            del self.layouts[name]
            self._save_layouts()
            return True
        return False
    
    def has_layout(self, name: str) -> bool:
        """Check if a layout exists."""
        return name in self.layouts


def generate_layered_layout(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Generate a layered layout with TPOs at top, Strategic in middle, Operational at bottom.
    
    Args:
        nodes: List of node dictionaries
    
    Returns:
        Position dictionary mapping node IDs to {x, y}
    """
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    strategic = [n for n in nodes if n.get("level") == "Strategic" and n.get("node_type") != "TPO"]
    operational = [n for n in nodes if n.get("level") == "Operational" and n.get("node_type") != "TPO"]
    mitigations = [n for n in nodes if n.get("node_type") == "Mitigation"]
    
    positions = {}
    
    # TPOs at very top
    y_tpo = 50
    x_spacing = 800 / max(len(tpos), 1)
    for i, node in enumerate(tpos):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": y_tpo
        }
    
    # Strategic in middle
    y_strategic = 250
    x_spacing = 800 / max(len(strategic), 1)
    for i, node in enumerate(strategic):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": y_strategic
        }
    
    # Operational at bottom
    y_operational = 550
    x_spacing = 800 / max(len(operational), 1)
    for i, node in enumerate(operational):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": y_operational
        }
    
    # Mitigations on the right side
    if mitigations:
        y_mit = 300
        for i, node in enumerate(mitigations):
            positions[node["id"]] = {
                "x": 950,
                "y": y_mit + (i * 50)
            }
    
    return positions


def generate_category_layout(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Generate a layout grouped by categories in 2x2 grid, TPOs on top.
    
    Args:
        nodes: List of node dictionaries
    
    Returns:
        Position dictionary mapping node IDs to {x, y}
    """
    categories = ["Programme", "Produit", "Industriel", "Supply Chain"]
    positions = {}
    
    # Place TPOs at the top
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    x_spacing = 800 / max(len(tpos), 1)
    for i, node in enumerate(tpos):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": 50
        }
    
    # 2x2 grid for risks
    grid_positions = [
        (200, 250),   # Programme (top left)
        (600, 250),   # Produit (top right)
        (200, 500),   # Industriel (bottom left)
        (600, 500)    # Supply Chain (bottom right)
    ]
    
    risk_nodes = [n for n in nodes if n.get("node_type") not in ("TPO", "Mitigation")]
    
    for cat_idx, category in enumerate(categories):
        cat_nodes = [n for n in risk_nodes if category in n.get("categories", [])]
        base_x, base_y = grid_positions[cat_idx]
        
        for i, node in enumerate(cat_nodes):
            offset_x = (i % 3) * 100 - 100
            offset_y = (i // 3) * 80
            positions[node["id"]] = {
                "x": base_x + offset_x,
                "y": base_y + offset_y
            }
    
    # Mitigations on the right
    mitigations = [n for n in nodes if n.get("node_type") == "Mitigation"]
    for i, node in enumerate(mitigations):
        positions[node["id"]] = {
            "x": 900,
            "y": 200 + (i * 50)
        }
    
    return positions


def generate_tpo_cluster_layout(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Generate a layout grouped by TPO clusters with risks below.
    
    Args:
        nodes: List of node dictionaries
    
    Returns:
        Position dictionary mapping node IDs to {x, y}
    """
    positions = {}
    
    # Cluster positions
    cluster_positions = {
        "Product Efficiency": (100, 50),
        "Business Efficiency": (300, 50),
        "Industrial Efficiency": (500, 50),
        "Sustainability": (700, 50),
        "Safety": (900, 50)
    }
    
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    cluster_counts = {c: 0 for c in TPO_CLUSTERS}
    
    for node in tpos:
        cluster = node.get("cluster", "Product Efficiency")
        base_x, base_y = cluster_positions.get(cluster, (500, 50))
        offset = cluster_counts.get(cluster, 0) * 60
        positions[node["id"]] = {
            "x": base_x,
            "y": base_y + offset
        }
        if cluster in cluster_counts:
            cluster_counts[cluster] += 1
    
    # Place strategic risks in middle
    strategic = [n for n in nodes if n.get("level") == "Strategic" and n.get("node_type") != "TPO"]
    x_spacing = 800 / max(len(strategic), 1)
    for i, node in enumerate(strategic):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": 350
        }
    
    # Place operational risks at bottom
    operational = [n for n in nodes if n.get("level") == "Operational" and n.get("node_type") != "TPO"]
    x_spacing = 800 / max(len(operational), 1)
    for i, node in enumerate(operational):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": 550
        }
    
    # Mitigations on the side
    mitigations = [n for n in nodes if n.get("node_type") == "Mitigation"]
    for i, node in enumerate(mitigations):
        positions[node["id"]] = {
            "x": 1000,
            "y": 300 + (i * 50)
        }
    
    return positions


def generate_auto_spread_layout(nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Generate an automatic spread layout with size-aware spacing.
    
    Uses a hierarchical layout: TPOs at top, Strategic in middle, Operational at bottom.
    Nodes are spread horizontally with spacing based on node sizes.
    
    Args:
        nodes: List of node dictionaries
    
    Returns:
        Position dictionary mapping node IDs to {x, y}
    """
    positions = {}
    
    def get_node_size(node: Dict[str, Any]) -> float:
        """Calculate the visual size of a node."""
        node_type = node.get("node_type", "Risk")
        if node_type == "TPO":
            return 35
        elif node_type == "Mitigation":
            return 30
        else:
            exposure = node.get("exposure") or 0
            return 25 + (exposure * 1.5) if exposure else 25
    
    def get_node_width(node: Dict[str, Any]) -> float:
        """Estimate the total width a node needs."""
        size = get_node_size(node)
        label_width = 180  # max label width
        return max(size * 2, label_width) + 20
    
    # Separate nodes by type/level
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    strategic = [n for n in nodes if n.get("level") == "Strategic" and n.get("node_type") not in ("TPO", "Mitigation")]
    operational = [n for n in nodes if n.get("level") == "Operational" and n.get("node_type") not in ("TPO", "Mitigation")]
    mitigations = [n for n in nodes if n.get("node_type") == "Mitigation"]
    
    # Layout parameters
    canvas_width = 1400
    margin_x = 100
    min_spacing = 50
    
    def layout_row(node_list: List[Dict], y_position: float) -> float:
        """Layout a row of nodes, returns row height."""
        n = len(node_list)
        if n == 0:
            return 0
        
        if n == 1:
            positions[node_list[0]["id"]] = {
                "x": int(canvas_width / 2),
                "y": int(y_position)
            }
            return get_node_size(node_list[0]) * 2
        
        # Calculate spacings
        spacings = []
        for i in range(n - 1):
            current_width = get_node_width(node_list[i])
            next_width = get_node_width(node_list[i + 1])
            spacing = (current_width / 2) + min_spacing + (next_width / 2)
            spacings.append(spacing)
        
        total_width = sum(spacings)
        
        # Scale if too wide
        available_width = canvas_width - 2 * margin_x
        if total_width > available_width:
            scale = available_width / total_width
            spacings = [s * scale for s in spacings]
            total_width = available_width
        
        # Center the row
        start_x = (canvas_width - total_width) / 2
        start_x = max(start_x, margin_x)
        
        # Place nodes
        current_x = start_x
        max_size = 0
        for i, node in enumerate(node_list):
            positions[node["id"]] = {
                "x": int(current_x),
                "y": int(y_position)
            }
            max_size = max(max_size, get_node_size(node))
            if i < len(spacings):
                current_x += spacings[i]
        
        return max_size * 2
    
    def layout_grid(node_list: List[Dict], y_start: float, max_per_row: int = 5) -> float:
        """Layout nodes in a grid pattern."""
        n = len(node_list)
        if n == 0:
            return 0
        
        rows = math.ceil(n / max_per_row)
        current_y = y_start
        total_height = 0
        
        for row_idx in range(rows):
            start_idx = row_idx * max_per_row
            end_idx = min(start_idx + max_per_row, n)
            row_nodes = node_list[start_idx:end_idx]
            
            row_height = layout_row(row_nodes, current_y)
            
            max_node_size = max(get_node_size(node) for node in row_nodes)
            row_spacing = max_node_size * 2 + min_spacing + 40
            
            current_y += row_spacing
            total_height += row_spacing
        
        return total_height
    
    # Layout each layer
    y_tpo = 80
    tpo_height = layout_row(tpos, y_tpo) if tpos else 0
    
    max_tpo_size = max([get_node_size(n) for n in tpos], default=35)
    y_strategic = y_tpo + max(tpo_height, max_tpo_size * 2) + 80
    
    if len(strategic) <= 5:
        strategic_height = layout_row(strategic, y_strategic) if strategic else 0
    else:
        strategic_height = layout_grid(strategic, y_strategic, 5)
    
    max_strategic_size = max([get_node_size(n) for n in strategic], default=25)
    y_operational = y_strategic + max(strategic_height, max_strategic_size * 2) + 100
    
    if len(operational) <= 6:
        layout_row(operational, y_operational)
    else:
        layout_grid(operational, y_operational, 6)
    
    # Mitigations on the right side
    if mitigations:
        y_mit = y_strategic
        for i, node in enumerate(mitigations):
            positions[node["id"]] = {
                "x": int(canvas_width - 100),
                "y": int(y_mit + (i * 60))
            }
    
    return positions


# Layout generators registry
LAYOUT_GENERATORS = {
    "layered": ("Layered (Risk Levels)", generate_layered_layout),
    "category": ("By Category", generate_category_layout),
    "tpo_cluster": ("By TPO Cluster", generate_tpo_cluster_layout),
    "auto_spread": ("Auto Spread", generate_auto_spread_layout),
}


def get_layout_options() -> List[str]:
    """Get list of available layout names."""
    return [name for name, _ in LAYOUT_GENERATORS.values()]


def generate_layout(layout_type: str, nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Generate layout using the specified generator.
    
    Args:
        layout_type: Key of the layout generator
        nodes: List of node dictionaries
    
    Returns:
        Position dictionary
    """
    if layout_type in LAYOUT_GENERATORS:
        _, generator = LAYOUT_GENERATORS[layout_type]
        return generator(nodes)
    
    # Default to layered
    return generate_layered_layout(nodes)
