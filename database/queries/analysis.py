"""
Analysis database queries.

Contains queries for statistics, graph data retrieval, and analysis support.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection
from database.queries import risks, tpos, mitigations, influences

# Schema-driven configuration
from config import RISK_LEVELS


# =============================================================================
# GRAPH DATA RETRIEVAL
# =============================================================================

def get_graph_data(
    conn: Neo4jConnection,
    filters: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Retrieve all data needed for graph visualization.
    
    Args:
        conn: Database connection
        filters: Optional filter dictionary with keys:
            - level: List of risk levels
            - categories: List of categories
            - status: List of statuses
            - origins: List of origins
            - show_tpos: Boolean
            - tpo_clusters: List of TPO clusters
            - show_mitigations: Boolean
            - mitigation_types: List of mitigation types
            - mitigation_statuses: List of mitigation statuses
    
    Returns:
        Tuple of (nodes, edges) where:
            - nodes: List of node dictionaries
            - edges: List of edge dictionaries
    """
    filters = filters or {}
    
    # Get risk nodes
    risk_nodes = risks.get_risks_with_filters(
        conn,
        levels=filters.get("level"),
        categories=filters.get("categories"),
        statuses=filters.get("status"),
        origins=filters.get("origins")
    )
    
    nodes = list(risk_nodes) if risk_nodes else []
    risk_ids = [n["id"] for n in nodes]
    
    # Get TPO nodes if enabled
    show_tpos = filters.get("show_tpos", True)
    tpo_nodes = []
    tpo_ids = []
    
    if show_tpos:
        tpo_nodes = tpos.get_tpos_for_graph(
            conn,
            cluster_filter=filters.get("tpo_clusters")
        )
        nodes.extend(tpo_nodes)
        tpo_ids = [n["id"] for n in tpo_nodes]
    
    # Get mitigation nodes if enabled
    show_mitigations = filters.get("show_mitigations", False)
    mitigation_nodes = []
    mitigation_ids = []
    
    if show_mitigations:
        mitigation_nodes = mitigations.get_mitigations_for_graph(
            conn,
            type_filter=filters.get("mitigation_types"),
            status_filter=filters.get("mitigation_statuses")
        )
        nodes.extend(mitigation_nodes)
        mitigation_ids = [n["id"] for n in mitigation_nodes]
    
    # Get edges
    edges = []
    
    # Influence edges between risks
    if risk_ids:
        influence_edges = influences.get_influence_edges(conn, risk_ids)
        edges.extend(influence_edges)
    
    # TPO impact edges
    if show_tpos and risk_ids and tpo_ids:
        tpo_edges = tpos.get_tpo_impact_edges(conn, risk_ids, tpo_ids)
        edges.extend(tpo_edges)
    
    # Mitigates edges
    if show_mitigations and risk_ids and mitigation_ids:
        mitigates_edges = mitigations.get_mitigates_edges(conn, mitigation_ids, risk_ids)
        edges.extend(mitigates_edges)
    
    return nodes, edges


def get_all_edges_scored(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Get all edges with importance scores for progressive disclosure.
    
    Args:
        conn: Database connection
    
    Returns:
        List of edge dictionaries with scores, sorted by score descending
    """
    strength_values = {"Critical": 4, "Strong": 3, "Moderate": 2, "Weak": 1}
    impact_values = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    
    scored_edges = []
    
    # Get influence edges
    all_influences = influences.get_all_influences(conn)
    for inf in all_influences:
        strength = strength_values.get(inf["strength"], 2)
        confidence = inf.get("confidence", 0.8) or 0.8
        score = strength * confidence
        
        scored_edges.append({
            "source": inf["source_id"],
            "target": inf["target_id"],
            "edge_type": "INFLUENCES",
            "influence_type": inf.get("influence_type", ""),
            "strength": inf["strength"],
            "confidence": confidence,
            "score": score,
            "description": inf.get("description", "")
        })
    
    # Get TPO impact edges
    all_tpo_impacts = tpos.get_all_tpo_impacts(conn)
    for impact in all_tpo_impacts:
        impact_score = impact_values.get(impact["impact_level"], 2)
        # TPO impacts get a boost since they're the final targets
        score = impact_score * 1.2
        
        scored_edges.append({
            "source": impact["risk_id"],
            "target": impact["tpo_id"],
            "edge_type": "IMPACTS_TPO",
            "impact_level": impact["impact_level"],
            "score": score,
            "description": impact.get("description", "")
        })
    
    # Sort by score descending
    scored_edges.sort(key=lambda x: -x["score"])
    
    return scored_edges


# =============================================================================
# STATISTICS
# =============================================================================

def get_statistics(conn: Neo4jConnection) -> Dict[str, Any]:
    """
    Get comprehensive graph statistics.
    
    Args:
        conn: Database connection
    
    Returns:
        Dictionary of statistics
    """
    stats = {
        "total_risks": 0,
        "strategic_risks": 0,
        "operational_risks": 0,
        "contingent_risks": 0,
        "new_risks": 0,
        "legacy_risks": 0,
        "total_influences": 0,
        "total_tpos": 0,
        "total_tpo_impacts": 0,
        "total_mitigations": 0,
        "total_mitigates": 0,
        "avg_exposure": 0,
        "categories": {},
        "tpo_clusters": {},
        "mitigations_by_type": {},
        "mitigations_by_status": {}
    }
    
    # Risk counts
    stats["total_risks"] = risks.get_risk_count(conn)
    # Use schema-driven level names
    if len(RISK_LEVELS) >= 1:
        stats["level1_risks"] = risks.get_risk_count_by_level(conn, RISK_LEVELS[0])
        stats["level1_name"] = RISK_LEVELS[0]
    if len(RISK_LEVELS) >= 2:
        stats["level2_risks"] = risks.get_risk_count_by_level(conn, RISK_LEVELS[1])
        stats["level2_name"] = RISK_LEVELS[1]
    # Keep backward compatibility keys
    stats["strategic_risks"] = stats.get("level1_risks", 0)
    stats["operational_risks"] = stats.get("level2_risks", 0)
    stats["contingent_risks"] = risks.get_risk_count_by_status(conn, "Contingent")
    stats["new_risks"] = risks.get_risk_count_by_origin(conn, "New")
    stats["legacy_risks"] = risks.get_risk_count_by_origin(conn, "Legacy")
    stats["avg_exposure"] = risks.get_average_exposure(conn)
    stats["categories"] = risks.get_risk_count_by_category(conn)
    
    # Influence counts
    stats["total_influences"] = influences.get_influence_count(conn)
    
    # TPO counts
    stats["total_tpos"] = tpos.get_tpo_count(conn)
    stats["total_tpo_impacts"] = tpos.get_tpo_impact_count(conn)
    stats["tpo_clusters"] = tpos.get_tpo_count_by_cluster(conn)
    
    # Mitigation counts
    stats["total_mitigations"] = mitigations.get_mitigation_count(conn)
    stats["total_mitigates"] = mitigations.get_mitigates_count(conn)
    stats["mitigations_by_type"] = mitigations.get_mitigation_count_by_type(conn)
    stats["mitigations_by_status"] = mitigations.get_mitigation_count_by_status(conn)
    
    return stats


# =============================================================================
# NODE SELECTION
# =============================================================================

def get_all_nodes_for_selection(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Get all risks and TPOs formatted for dropdown selection.
    
    Args:
        conn: Database connection
    
    Returns:
        List of node dictionaries with label and type
    """
    result = []
    
    # Get risks
    all_risks = risks.get_all_risks(conn)
    for r in all_risks:
        result.append({
            "id": r["id"],
            "label": f"[{r['level'][:4]}] {r['name']}",
            "name": r["name"],
            "type": "Risk",
            "level": r["level"]
        })
    
    # Get TPOs
    all_tpos = tpos.get_all_tpos(conn)
    for t in all_tpos:
        result.append({
            "id": t["id"],
            "label": f"[TPO] {t['reference']}: {t['name']}",
            "name": t["name"],
            "type": "TPO"
        })
    
    return result


# =============================================================================
# INFLUENCE NETWORK ANALYSIS
# =============================================================================

def get_influence_network(
    conn: Neo4jConnection,
    node_id: str,
    direction: str = "both",
    max_depth: Optional[int] = None,
    level_filter: str = "all",
    include_tpos: bool = True
) -> tuple:
    """
    Get the influence network around a specific node.
    
    Args:
        conn: Database connection
        node_id: Starting node UUID
        direction: "upstream", "downstream", or "both"
        max_depth: Maximum traversal depth (None for unlimited)
        level_filter: "all", "Business", or "Operational"
        include_tpos: Whether to include TPOs
    
    Returns:
        Tuple of (nodes, edges, selected_node_info)
    """
    if max_depth is None:
        max_depth = 10
    
    # Check if node is a risk or TPO
    risk_data = risks.get_risk_by_id(conn, node_id)
    tpo_data = tpos.get_tpo_by_id(conn, node_id) if not risk_data else None
    
    if risk_data:
        selected_node_info = {
            "id": node_id,
            "name": risk_data["name"],
            "level": risk_data["level"],
            "node_type": "Risk"
        }
    elif tpo_data:
        selected_node_info = {
            "id": node_id,
            "name": tpo_data["name"],
            "reference": tpo_data["reference"],
            "node_type": "TPO"
        }
    else:
        return [], [], None
    
    nodes_set = {node_id: selected_node_info}
    edges_list = []
    
    # Get downstream nodes
    if direction in ["downstream", "both"] and risk_data:
        downstream = influences.get_downstream_risks(conn, node_id, max_depth)
        for r in downstream:
            if level_filter == "all" or r["level"] == level_filter:
                if r["id"] not in nodes_set:
                    nodes_set[r["id"]] = {
                        "id": r["id"],
                        "name": r["name"],
                        "level": r["level"],
                        "exposure": r.get("exposure"),
                        "node_type": "Risk"
                    }
    
    # Get upstream nodes
    if direction in ["upstream", "both"]:
        if risk_data:
            upstream = influences.get_upstream_risks(conn, node_id, max_depth)
            for r in upstream:
                if level_filter == "all" or r["level"] == level_filter:
                    if r["id"] not in nodes_set:
                        nodes_set[r["id"]] = {
                            "id": r["id"],
                            "name": r["name"],
                            "level": r["level"],
                            "exposure": r.get("exposure"),
                            "node_type": "Risk"
                        }
    
    # Get edges between collected nodes
    node_ids = list(nodes_set.keys())
    if node_ids:
        influence_edges = influences.get_influence_edges(conn, node_ids)
        edges_list.extend(influence_edges)
    
    # Add TPOs if requested
    tpo_nodes = []
    tpo_edges = []
    if include_tpos:
        risk_node_ids = [nid for nid, n in nodes_set.items() if n.get("node_type") == "Risk"]
        if risk_node_ids:
            # Get all TPOs impacted by these risks
            all_tpo_list = tpos.get_all_tpos(conn)
            tpo_ids = [t["id"] for t in all_tpo_list]
            
            if tpo_ids:
                tpo_edges = tpos.get_tpo_impact_edges(conn, risk_node_ids, tpo_ids)
                
                # Only include TPOs that have connections
                connected_tpo_ids = set(e["target"] for e in tpo_edges)
                for t in all_tpo_list:
                    if t["id"] in connected_tpo_ids:
                        tpo_nodes.append({
                            "id": t["id"],
                            "reference": t["reference"],
                            "name": t["name"],
                            "cluster": t["cluster"],
                            "node_type": "TPO"
                        })
    
    nodes_list = list(nodes_set.values())
    nodes_list.extend(tpo_nodes)
    edges_list.extend(tpo_edges)
    
    return nodes_list, edges_list, selected_node_info
