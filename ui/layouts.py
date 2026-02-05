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
    Generate a layered layout with TPOs at top, Business in middle, Operational at bottom.
    
    Args:
        nodes: List of node dictionaries
    
    Returns:
        Position dictionary mapping node IDs to {x, y}
    """
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    strategic = [n for n in nodes if n.get("level") == "Business" and n.get("node_type") != "TPO"]
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
    
    # Business in middle
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
    strategic = [n for n in nodes if n.get("level") == "Business" and n.get("node_type") != "TPO"]
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


def generate_auto_spread_layout(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]] = None) -> Dict[str, Dict[str, float]]:
    """
    Generate a hierarchical layout using the Sugiyama algorithm.
    
    The Sugiyama algorithm produces clean layered layouts by:
    1. Assigning nodes to layers based on graph topology
    2. Ordering nodes within layers to minimize edge crossings
    3. Positioning nodes with optimal spacing
    
    For RIM, the semantic hierarchy is respected:
    - TPOs at top (layer 0)
    - Strategic risks in middle layers
    - Operational risks in lower layers
    - Mitigations positioned alongside their targets
    
    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries (optional, for crossing minimization)
    
    Returns:
        Position dictionary mapping node IDs to {x, y}
    """
    if not nodes:
        return {}
    
    # Build node lookup and edge lists
    node_map = {n["id"]: n for n in nodes}
    node_ids = set(node_map.keys())
    
    # Parse edges if provided
    adjacency = {nid: [] for nid in node_ids}  # node -> nodes it points to
    reverse_adj = {nid: [] for nid in node_ids}  # node -> nodes that point to it
    
    if edges:
        for edge in edges:
            src, tgt = edge.get("source"), edge.get("target")
            if src in node_ids and tgt in node_ids:
                adjacency[src].append(tgt)
                reverse_adj[tgt].append(src)
    
    # ==========================================================================
    # PHASE 1: Layer Assignment (strict semantic constraints for RIM)
    # ==========================================================================
    
    def get_semantic_layer(node: Dict[str, Any]) -> int:
        """
        Get the semantic layer for a node based on RIM hierarchy.
        
        RIM hierarchy (top to bottom):
        - Layer 0: TPOs (goals/objectives at the top)
        - Layer 1: Strategic risks (consequences)
        - Layer 2: Operational risks (causes)
        - Layer 3: Mitigations (positioned alongside their targets)
        """
        node_type = node.get("node_type", "Risk")
        level = node.get("level", "Operational")
        
        if node_type == "TPO":
            return 0  # TPOs always at top
        elif node_type == "Mitigation":
            return 3  # Mitigations in a separate layer
        elif level == "Business":
            return 1  # Strategic risks below TPOs
        else:  # Operational
            return 2  # Operational risks below Strategic
    
    # Assign layers based strictly on semantics
    # Unlike traditional Sugiyama, we don't adjust layers based on edges
    # because RIM has a defined semantic hierarchy that must be preserved
    node_layers = {}
    for nid, node in node_map.items():
        node_layers[nid] = get_semantic_layer(node)
    
    # Group nodes by layer
    layers = {}
    for nid, layer in node_layers.items():
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(nid)
    
    # ==========================================================================
    # PHASE 2: Crossing Minimization (Barycenter heuristic)
    # ==========================================================================
    
    def get_barycenter(node_id: str, adjacent_layer_order: Dict[str, int]) -> float:
        """Calculate barycenter (average position) of connected nodes in adjacent layer."""
        connected = adjacency[node_id] + reverse_adj[node_id]
        positions_in_adj = [adjacent_layer_order[n] for n in connected if n in adjacent_layer_order]
        
        if not positions_in_adj:
            return float('inf')  # No connections, keep original position
        
        return sum(positions_in_adj) / len(positions_in_adj)
    
    # Sort layers by layer number
    sorted_layer_nums = sorted(layers.keys())
    
    # Initial ordering: sort by semantic type, then by name for stability
    for layer_num in sorted_layer_nums:
        layer_nodes = layers[layer_num]
        # Sort by node type priority, then name
        def sort_key(nid):
            node = node_map[nid]
            type_priority = {
                "TPO": 0,
                "Risk": 1,
                "Mitigation": 2
            }
            return (
                type_priority.get(node.get("node_type", "Risk"), 1),
                node.get("name", nid)
            )
        layers[layer_num] = sorted(layer_nodes, key=sort_key)
    
    # Barycenter ordering passes (top-down then bottom-up)
    for iteration in range(4):
        # Top-down pass
        for i in range(1, len(sorted_layer_nums)):
            layer_num = sorted_layer_nums[i]
            prev_layer_num = sorted_layer_nums[i - 1]
            
            # Build position map for previous layer
            prev_order = {nid: idx for idx, nid in enumerate(layers[prev_layer_num])}
            
            # Calculate barycenters and sort
            current_nodes = layers[layer_num]
            barycenters = [(nid, get_barycenter(nid, prev_order)) for nid in current_nodes]
            
            # Sort by barycenter, keeping nodes with no connections in their relative positions
            connected = [(nid, bc) for nid, bc in barycenters if bc != float('inf')]
            unconnected = [nid for nid, bc in barycenters if bc == float('inf')]
            
            connected.sort(key=lambda x: x[1])
            layers[layer_num] = [nid for nid, _ in connected] + unconnected
        
        # Bottom-up pass
        for i in range(len(sorted_layer_nums) - 2, -1, -1):
            layer_num = sorted_layer_nums[i]
            next_layer_num = sorted_layer_nums[i + 1]
            
            # Build position map for next layer
            next_order = {nid: idx for idx, nid in enumerate(layers[next_layer_num])}
            
            # Calculate barycenters and sort
            current_nodes = layers[layer_num]
            barycenters = [(nid, get_barycenter(nid, next_order)) for nid in current_nodes]
            
            connected = [(nid, bc) for nid, bc in barycenters if bc != float('inf')]
            unconnected = [nid for nid, bc in barycenters if bc == float('inf')]
            
            connected.sort(key=lambda x: x[1])
            layers[layer_num] = [nid for nid, _ in connected] + unconnected
    
    # ==========================================================================
    # PHASE 3: Coordinate Assignment
    # ==========================================================================
    
    positions = {}
    
    # Layout parameters
    canvas_width = 1400
    margin_x = 100
    layer_spacing = 150  # Vertical spacing between layers
    min_node_spacing = 180  # Minimum horizontal spacing between nodes
    
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
    
    # Calculate Y positions for each layer
    layer_y_positions = {}
    current_y = 80
    
    for layer_num in sorted_layer_nums:
        layer_y_positions[layer_num] = current_y
        
        # Calculate max node size in this layer
        layer_nodes = layers[layer_num]
        if layer_nodes:
            max_size = max(get_node_size(node_map[nid]) for nid in layer_nodes)
            current_y += layer_spacing + max_size
        else:
            current_y += layer_spacing
    
    # Calculate X positions using median method with rubber-banding
    for layer_num in sorted_layer_nums:
        layer_nodes = layers[layer_num]
        n = len(layer_nodes)
        
        if n == 0:
            continue
        
        y_pos = layer_y_positions[layer_num]
        
        if n == 1:
            # Center single node
            positions[layer_nodes[0]] = {
                "x": int(canvas_width / 2),
                "y": int(y_pos)
            }
        else:
            # Calculate ideal positions based on connected nodes in previous layers
            ideal_x = {}
            
            for nid in layer_nodes:
                connected = adjacency[nid] + reverse_adj[nid]
                connected_positions = [positions[c]["x"] for c in connected if c in positions]
                
                if connected_positions:
                    # Use median of connected positions
                    connected_positions.sort()
                    mid = len(connected_positions) // 2
                    if len(connected_positions) % 2 == 0:
                        ideal_x[nid] = (connected_positions[mid-1] + connected_positions[mid]) / 2
                    else:
                        ideal_x[nid] = connected_positions[mid]
                else:
                    ideal_x[nid] = None
            
            # Assign positions ensuring minimum spacing
            available_width = canvas_width - 2 * margin_x
            total_spacing = (n - 1) * min_node_spacing
            
            if total_spacing > available_width:
                # Scale down spacing to fit
                actual_spacing = available_width / (n - 1)
            else:
                actual_spacing = min_node_spacing
            
            # Start position to center the nodes
            total_width = actual_spacing * (n - 1)
            start_x = (canvas_width - total_width) / 2
            
            # Position nodes
            for i, nid in enumerate(layer_nodes):
                x_pos = start_x + i * actual_spacing
                
                # Adjust towards ideal position while maintaining spacing
                if ideal_x[nid] is not None:
                    # Blend between grid position and ideal position
                    blend_factor = 0.3  # How much to move towards ideal
                    min_x = margin_x + i * min_node_spacing * 0.5
                    max_x = canvas_width - margin_x - (n - 1 - i) * min_node_spacing * 0.5
                    ideal = ideal_x[nid]
                    
                    # Ensure we don't violate boundaries
                    target_x = x_pos + (ideal - x_pos) * blend_factor
                    target_x = max(min_x, min(max_x, target_x))
                    x_pos = target_x
                
                positions[nid] = {
                    "x": int(x_pos),
                    "y": int(y_pos)
                }
    
    # ==========================================================================
    # PHASE 4: Post-processing for mitigations
    # ==========================================================================
    
    # Reposition mitigations closer to their target risks
    for nid in node_ids:
        node = node_map[nid]
        if node.get("node_type") == "Mitigation":
            # Find connected risk nodes
            connected = adjacency[nid] + reverse_adj[nid]
            connected_risks = [c for c in connected if c in positions and 
                             node_map[c].get("node_type") != "Mitigation"]
            
            if connected_risks:
                # Position mitigation to the right of its primary target
                primary_target = connected_risks[0]
                target_pos = positions[primary_target]
                
                positions[nid] = {
                    "x": int(min(target_pos["x"] + 250, canvas_width - margin_x)),
                    "y": int(target_pos["y"])
                }
    
    return positions


# Layout generators registry
# Note: auto_spread now uses Sugiyama algorithm for hierarchical layout
LAYOUT_GENERATORS = {
    "layered": ("Layered (Risk Levels)", generate_layered_layout),
    "category": ("By Category", generate_category_layout),
    "tpo_cluster": ("By TPO Cluster", generate_tpo_cluster_layout),
    "auto_spread": ("Hierarchical (Sugiyama)", generate_auto_spread_layout),
}


def get_layout_options() -> List[str]:
    """Get list of available layout names."""
    return [name for name, _ in LAYOUT_GENERATORS.values()]


def generate_layout(
    layout_type: str, 
    nodes: List[Dict[str, Any]], 
    edges: List[Dict[str, Any]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Generate layout using the specified generator.
    
    Args:
        layout_type: Key of the layout generator
        nodes: List of node dictionaries
        edges: List of edge dictionaries (used by Sugiyama algorithm for crossing minimization)
    
    Returns:
        Position dictionary
    """
    if layout_type in LAYOUT_GENERATORS:
        _, generator = LAYOUT_GENERATORS[layout_type]
        
        # Pass edges to auto_spread (Sugiyama) layout if available
        if layout_type == "auto_spread" and edges is not None:
            return generator(nodes, edges)
        
        # Check if the generator accepts edges parameter
        import inspect
        sig = inspect.signature(generator)
        if 'edges' in sig.parameters and edges is not None:
            return generator(nodes, edges)
        
        return generator(nodes)
    
    # Default to layered
    return generate_layered_layout(nodes)
