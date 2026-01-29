"""
Graph Renderer for RIM Visualization.

Provides the main render_graph function using PyVis.
"""

from typing import Dict, Any, Optional, List, Tuple
import tempfile
import os

from visualization.node_styles import create_node_config
from visualization.edge_styles import create_edge_config, filter_edges_by_score
from visualization.graph_options import (
    get_network_options,
    get_position_capture_js,
    get_fullscreen_js
)
from ui.layouts import generate_auto_spread_layout


def render_graph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    color_by: str = "level",
    physics_enabled: bool = True,
    positions: Optional[Dict[str, Dict[str, float]]] = None,
    capture_positions: bool = False,
    highlighted_node_id: Optional[str] = None,
    max_edges: Optional[int] = None,
    edge_scores: Optional[Dict[Tuple[str, str], float]] = None,
    height: int = 720
) -> Optional[str]:
    """
    Render the RIM graph using PyVis.
    
    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries
        color_by: Coloring scheme ("level" or "exposure")
        physics_enabled: Enable physics simulation
        positions: Dict of node positions {node_id: {x, y}}
        capture_positions: Enable position capture UI
        highlighted_node_id: ID of node to highlight
        max_edges: Maximum number of edges to display
        edge_scores: Dict mapping (source, target) to score
        height: Graph container height in pixels
    
    Returns:
        HTML content string, or None if using Streamlit
    """
    if not nodes:
        return None
    
    # Filter edges if needed
    filtered_edges = filter_edges_by_score(edges, max_edges, edge_scores)
    
    # Generate auto layout if physics disabled and no positions
    if not physics_enabled and not positions:
        positions = generate_auto_spread_layout(nodes)
    
    # Create network
    try:
        from pyvis.network import Network
    except ImportError:
        raise ImportError("PyVis is required. Install with: pip install pyvis")
    
    net = Network(
        height=f"{height-20}px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=True
    )
    
    # Configure network
    net.set_options(get_network_options(physics_enabled))
    
    # Add nodes
    for node in nodes:
        node_config = create_node_config(node, color_by, highlighted_node_id)
        
        # Apply positions if provided
        if positions and node["id"] in positions:
            pos = positions[node["id"]]
            node_config["x"] = pos["x"]
            node_config["y"] = pos["y"]
        
        net.add_node(node["id"], **node_config)
    
    # Add edges
    for edge in filtered_edges:
        edge_config = create_edge_config(edge)
        net.add_edge(
            edge["source"],
            edge["target"],
            **edge_config
        )
    
    # Generate HTML
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
    tmp_path = tmp_file.name
    tmp_file.close()
    
    net.save_graph(tmp_path)
    
    with open(tmp_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    # Inject position capture JS if requested
    if capture_positions:
        html_content = html_content.replace('</body>', get_position_capture_js() + '</body>')
    
    # Always add fullscreen capability
    html_content = html_content.replace('</body>', get_fullscreen_js() + '</body>')
    
    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except PermissionError:
        pass
    
    return html_content


def render_graph_streamlit(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    color_by: str = "level",
    physics_enabled: bool = True,
    positions: Optional[Dict[str, Dict[str, float]]] = None,
    capture_positions: bool = False,
    highlighted_node_id: Optional[str] = None,
    max_edges: Optional[int] = None,
    edge_scores: Optional[Dict[Tuple[str, str], float]] = None,
    height: int = 720
):
    """
    Render the RIM graph directly in Streamlit.
    
    Args:
        Same as render_graph
    """
    import streamlit as st
    
    if not nodes:
        st.info("No risks to display. Create your first risk!")
        return
    
    html_content = render_graph(
        nodes=nodes,
        edges=edges,
        color_by=color_by,
        physics_enabled=physics_enabled,
        positions=positions,
        capture_positions=capture_positions,
        highlighted_node_id=highlighted_node_id,
        max_edges=max_edges,
        edge_scores=edge_scores,
        height=height
    )
    
    if html_content:
        st.components.v1.html(html_content, height=height, scrolling=False)


def render_subgraph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    center_node_id: str,
    direction: str = "both",
    max_depth: Optional[int] = 5,
    include_tpos: bool = True,
    level_filter: Optional[str] = None,
    **kwargs
) -> Optional[str]:
    """
    Render a subgraph centered on a specific node.
    
    Args:
        nodes: All available nodes
        edges: All available edges
        center_node_id: ID of the center node
        direction: "upstream", "downstream", or "both"
        max_depth: Maximum traversal depth
        include_tpos: Whether to include TPO nodes
        level_filter: Filter to specific level ("Strategic", "Operational", or None for all)
        **kwargs: Additional arguments passed to render_graph
    
    Returns:
        HTML content string
    """
    # Build adjacency lists
    downstream_adj = {}  # node -> nodes it influences
    upstream_adj = {}    # node -> nodes that influence it
    
    for edge in edges:
        source, target = edge["source"], edge["target"]
        
        if source not in downstream_adj:
            downstream_adj[source] = []
        downstream_adj[source].append(target)
        
        if target not in upstream_adj:
            upstream_adj[target] = []
        upstream_adj[target].append(source)
    
    # BFS to find connected nodes
    visited = {center_node_id}
    to_visit = [(center_node_id, 0)]
    
    while to_visit:
        current_id, depth = to_visit.pop(0)
        
        if max_depth is not None and depth >= max_depth:
            continue
        
        # Downstream traversal
        if direction in ("downstream", "both"):
            for neighbor in downstream_adj.get(current_id, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    to_visit.append((neighbor, depth + 1))
        
        # Upstream traversal
        if direction in ("upstream", "both"):
            for neighbor in upstream_adj.get(current_id, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    to_visit.append((neighbor, depth + 1))
    
    # Filter nodes
    node_map = {n["id"]: n for n in nodes}
    filtered_nodes = []
    
    for node_id in visited:
        if node_id not in node_map:
            continue
        
        node = node_map[node_id]
        node_type = node.get("node_type", "Risk")
        
        # TPO filter
        if node_type == "TPO" and not include_tpos:
            continue
        
        # Level filter (only applies to risks)
        if level_filter and level_filter != "all":
            if node_type == "Risk" and node.get("level") != level_filter:
                continue
        
        filtered_nodes.append(node)
    
    # Filter edges to only those between visible nodes
    visible_ids = {n["id"] for n in filtered_nodes}
    filtered_edges = [
        e for e in edges
        if e["source"] in visible_ids and e["target"] in visible_ids
    ]
    
    # Highlight the center node
    kwargs["highlighted_node_id"] = center_node_id
    
    return render_graph(
        nodes=filtered_nodes,
        edges=filtered_edges,
        **kwargs
    )
