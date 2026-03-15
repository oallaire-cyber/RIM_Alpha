"""
Graph Renderer for RIM Visualization.

Provides the main render_graph function using PyVis.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from visualization.node_styles import create_node_config
from visualization.edge_styles import create_edge_config, filter_edges_by_score
from visualization.graph_options import (
    get_network_options,
    get_position_capture_js,
    get_fullscreen_js,
    get_export_js,
    get_focus_mode_js,
    get_node_click_postmessage_js,
)

# ── Streamlit click-bridge declare_component (module-level, registered once) ─
# The component embeds the PyVis HTML in an inner srcdoc iframe and relays
# node-click postMessages back to Python via Streamlit.setComponentValue().
import streamlit.components.v1 as _stv1
_BRIDGE_DIR = Path(__file__).parent / "graph_click_bridge"
_graph_click_bridge = _stv1.declare_component("graph_click_bridge", path=str(_BRIDGE_DIR))



def hex_to_rgba(hex_str: str, alpha: float) -> str:
    """Convert hex color to rgba string with given alpha."""
    if not isinstance(hex_str, str):
        return hex_str
        
    # Handle existing rgba strings by replacing their alpha
    if hex_str.startswith('rgba('):
        parts = hex_str.split(',')
        if len(parts) >= 4:
            return f"{parts[0]},{parts[1]},{parts[2]},{alpha})"
            
    if not hex_str.startswith('#'):
        return hex_str
    hex_str = hex_str.lstrip('#')
    if len(hex_str) not in (3, 6):
        return hex_str
    if len(hex_str) == 3:
        r = int(hex_str[0]*2, 16)
        g = int(hex_str[1]*2, 16)
        b = int(hex_str[2]*2, 16)
    else:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


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
    height: int = 720,
    complexity_mode: str = "Advanced",
    exposure_opacity: bool = False,
    high_exposure_threshold: float = 60.0,
    lifecycle_ghosting: bool = False,
    focus_node_ids: Optional[List[str]] = None
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
        complexity_mode: "Simple" or "Advanced" for rendering complexity
        exposure_opacity: Enable exposure-driven opacity (F20)
        high_exposure_threshold: Threshold percentage for fully opaque nodes
        lifecycle_ghosting: Enable status/lifecycle ghosting (F21)
    
    Returns:
        HTML content string, or None if using Streamlit
    """
    if not nodes:
        return None
    
    # Filter edges if needed
    filtered_edges = filter_edges_by_score(edges, max_edges, edge_scores)
    
    # Generate auto layout if physics disabled and no positions
    # Pass edges to enable Sugiyama crossing minimization
    if not physics_enabled and not positions:
        from ui.layouts import generate_auto_spread_layout
        positions = generate_auto_spread_layout(nodes, filtered_edges)
        
    # Set up simple mode node transparency
    transparent_node_ids = set()
    opacity = 0.1
    if complexity_mode == "Simple":
        try:
            from config.settings import SIMPLE_MODE_CONFIG
            top_k = SIMPLE_MODE_CONFIG.get("top_risks_count", 10)
            opacity = SIMPLE_MODE_CONFIG.get("transparent_opacity", 0.1)
        except ImportError:
            top_k = 10
            
        # Get all risk nodes sorted by exposure
        risks = [n for n in nodes if n.get("node_type", "Risk").lower() in ("risk", "undefined", "")]
        risks.sort(key=lambda x: max(x.get("exposure") or 0, x.get("base_exposure") or 0), reverse=True)
        top_risk_ids = {n["id"] for n in risks[:top_k]}
        
        for n in nodes:
            node_type = n.get("node_type", "Risk").lower()
            # Context nodes and TPOs always stay opaque
            if node_type == "tpo" or n.get("is_context_node") or node_type not in ("risk", "mitigation", "tpo", "undefined", "") or n.get("id") == highlighted_node_id:
                continue # Objectives, context nodes, and highlighted node always opaque
            if node_type in ("risk", "undefined", "") and n["id"] in top_risk_ids:
                continue # Top risks always opaque
            # All other nodes (including mitigations) are transparent
            transparent_node_ids.add(n["id"])
            
    # Apply focus_node_ids if provided (from Streamlit interaction)
    if focus_node_ids is not None:
        focus_set = set(focus_node_ids)
        for n in nodes:
            if n["id"] not in focus_set:
                transparent_node_ids.add(n["id"])
    
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
        directed=True,
        cdn_resources="in_line",  # embed all JS inline — required for srcdoc iframe
    )
    
    # Configure network
    net.set_options(get_network_options(physics_enabled))
    
    # Add nodes
    for node in nodes:
        node_config = create_node_config(
            node, 
            color_by=color_by, 
            highlighted_node_id=highlighted_node_id,
            exposure_opacity=exposure_opacity,
            high_exposure_threshold=high_exposure_threshold,
            lifecycle_ghosting=lifecycle_ghosting
        )
        
        # Apply positions if provided
        if positions and node["id"] in positions:
            pos = positions[node["id"]]
            node_config["x"] = pos["x"]
            node_config["y"] = pos["y"]
            
        # Apply transparency if needed
        if node["id"] in transparent_node_ids:
            if isinstance(node_config.get("color"), dict):
                bg = node_config["color"].get("background", "")
                bd = node_config["color"].get("border", "")
                node_config["color"]["background"] = hex_to_rgba(bg, opacity)
                node_config["color"]["border"] = hex_to_rgba(bd, opacity)
            elif isinstance(node_config.get("color"), str):
                node_config["color"] = hex_to_rgba(node_config["color"], opacity)
            if "font" in node_config:
                node_config["font"]["color"] = f"rgba(0,0,0,{opacity})"
        
        net.add_node(node["id"], **node_config)
    
    # Add edges
    for edge in filtered_edges:
        edge_config = create_edge_config(edge)
        
        # Apply transparency if connected to a transparent node
        if edge["source"] in transparent_node_ids or edge["target"] in transparent_node_ids:
            if isinstance(edge_config.get("color"), dict):
                ec = edge_config["color"].get("color", "")
                edge_config["color"]["color"] = hex_to_rgba(ec, opacity)
                edge_config["color"]["highlight"] = hex_to_rgba(ec, opacity)
                edge_config["color"]["hover"] = hex_to_rgba(ec, opacity)
            elif isinstance(edge_config.get("color"), str):
                edge_config["color"] = hex_to_rgba(edge_config["color"], opacity)
        
        net.add_edge(
            edge["source"],
            edge["target"],
            **edge_config
        )
    
    # Generate HTML — generate_html() renders the Jinja2 template in memory and
    # returns a Python str with no file I/O.  This avoids the Windows cp1252
    # UnicodeEncodeError that occurs when save_graph() writes vis.js to disk
    # using the system default codec.  cdn_resources="in_line" (set on the
    # Network above) also ensures there are no relative-path lib/ references in
    # the HTML, preventing 404s from Streamlit's ComponentRequestHandler when
    # the HTML is loaded as a srcdoc iframe inside the declare_component.
    html_content = net.generate_html()

    # Inject position capture JS if requested
    if capture_positions:
        html_content = html_content.replace('</body>', get_position_capture_js() + '</body>')

    # Always add fullscreen capability
    html_content = html_content.replace('</body>', get_fullscreen_js() + '</body>')

    # Always add export capability
    html_content = html_content.replace('</body>', get_export_js() + '</body>')

    # Always add focus mode JS
    html_content = html_content.replace('</body>', get_focus_mode_js() + '</body>')

    # Always add postMessage click bridge (fires after focus mode)
    html_content = html_content.replace('</body>', get_node_click_postmessage_js() + '</body>')

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
    height: int = 720,
    complexity_mode: str = "Advanced",
    focus_node_ids: Optional[List[str]] = None
) -> Optional[str]:
    """
    Render the RIM graph directly in Streamlit via the click-bridge component.

    Returns the UUID of the node that was most recently clicked on the canvas,
    or None if no node was clicked / the background was clicked.
    The caller (ui/home.py) is responsible for persisting this value to
    st.session_state.selected_node_id.
    """
    import streamlit as st

    if not nodes:
        st.info("No risks to display. Create your first risk!")
        return None

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
        height=height,
        complexity_mode=complexity_mode,
        exposure_opacity=st.session_state.get("exposure_opacity_enabled", False),
        high_exposure_threshold=st.session_state.get("high_exposure_threshold", 60),
        lifecycle_ghosting=st.session_state.get("lifecycle_ghosting_enabled", False),
        focus_node_ids=focus_node_ids
    )

    if html_content:
        return _graph_click_bridge(
            html_content=html_content,
            height=height,
            key="rim_graph",
            default=None,
        )
    return None


def render_subgraph(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    center_node_id: str,
    direction: str = "both",
    max_depth: Optional[int] = 5,
    include_tpos: bool = True,
    level_filter: Optional[str] = None,
    exposure_opacity: bool = False,
    high_exposure_threshold: float = 60.0,
    lifecycle_ghosting: bool = False,
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
        level_filter: Filter to specific level ("Business", "Operational", or None for all)
        exposure_opacity: Enable exposure-driven opacity (F20)
        high_exposure_threshold: Threshold percentage for fully opaque nodes
        lifecycle_ghosting: Enable status/lifecycle ghosting (F21)
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
        exposure_opacity=exposure_opacity,
        high_exposure_threshold=high_exposure_threshold,
        lifecycle_ghosting=lifecycle_ghosting,
        **kwargs
    )
