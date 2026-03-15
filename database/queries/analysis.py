"""
Analysis database queries.

Contains queries for statistics, graph data retrieval, and analysis support.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection
from database.queries import risks, mitigations, influences

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
    
    # When a scope is active it is the authoritative boundary — visual filters
    # (level, status, origin…) must not silently cull nodes that are explicitly
    # in scope.  Fetch all risks without pre-filtering; the scope intersection
    # step below will produce the correct restricted set.
    _scope_active = (
        filters.get("scope_node_ids") is not None
        or bool(filters.get("active_scopes"))
    )
    if _scope_active:
        risk_nodes = risks.get_risks_with_filters(conn)
    else:
        risk_nodes = risks.get_risks_with_filters(
            conn,
            levels=filters.get("level"),
            categories=filters.get("categories"),
            statuses=filters.get("status"),
            origins=filters.get("origins"),
        )
    
    nodes = list(risk_nodes) if risk_nodes else []
    risk_ids = [n["id"] for n in nodes]
    

    
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

    # Get generic context nodes
    from database.queries import generic_entity, generic_relationship
    from core import get_registry
    registry = get_registry()
    
    context_node_ids = set()
    for entity_id, entity_type in registry.get_additional_entity_types().items():
        if entity_id == "tpo":
            continue
        if filters.get(f"show_{entity_id}", True):
            entity_filters = {"node_type": entity_id}
            for group_name in entity_type.categorical_groups:
                if f"{entity_id}_{group_name}" in filters:
                    entity_filters[group_name] = filters[f"{entity_id}_{group_name}"]
            
            entities = generic_entity.get_all_entities(conn._driver, entity_type, entity_filters)
            
            for node in entities:
                node["node_type"] = entity_id
                node["is_context_node"] = entity_type.is_context_node
                node["zone"] = getattr(entity_type, "zone", "lower")
                nodes.append(node)
                context_node_ids.add(node["id"])
            print(f"DEBUG: Fetched {len(entities)} context nodes of type {entity_id}. Total context IDs: {context_node_ids}")
    
    # Get edges (respecting relationship filters)
    edges = []
    
    # Influence edges between risks (only if show_influences is True)
    show_influences = filters.get("show_influences", True)
    if show_influences and risk_ids:
        influence_edges = influences.get_influence_edges(conn, risk_ids)
        # Filter by strength if specified
        strength_filter = filters.get("influence_strengths")
        if strength_filter:
            influence_edges = [
                e for e in influence_edges
                if e.get("strength", "") in strength_filter
                or not e.get("strength")  # keep edges without strength set
            ]
        edges.extend(influence_edges)
    

    
    # Mitigates edges (only if show_mitigates is True)
    show_mitigates = filters.get("show_mitigates", True)
    if show_mitigations and show_mitigates and risk_ids and mitigation_ids:
        mitigates_edges = mitigations.get_mitigates_edges(conn, mitigation_ids, risk_ids)
        # Filter by effectiveness if specified
        effectiveness_filter = filters.get("mitigation_effectiveness")
        if effectiveness_filter:
            mitigates_edges = [
                e for e in mitigates_edges
                if e.get("effectiveness", "") in effectiveness_filter
                or not e.get("effectiveness")  # keep edges without effectiveness set
            ]
        edges.extend(mitigates_edges)

    # Generic context edges
    for rel_id, rel_type in registry.get_additional_relationship_types().items():
        if rel_id == "impacts_tpo":
            continue
        if filters.get(f"show_{rel_id}", True):
            rel_filters = {}
            for group_name in rel_type.categorical_groups:
                if f"{rel_id}_{group_name}" in filters:
                    rel_filters[group_name] = filters[f"{rel_id}_{group_name}"]
            
            rels = generic_relationship.get_all_relationships(conn._driver, rel_type, rel_filters)
            for r in rels:
                edge = dict(r)
                edge["source"] = r["source_id"]
                edge["target"] = r["target_id"]
                edge["edge_type"] = rel_type.neo4j_type
                edges.append(edge)
    
    # Apply scope filtering — smart expansion from explicit active scopes
    active_scopes = filters.get("active_scopes")
    
    # Backward compatibility for old scope_node_ids filter
    scope_node_ids = filters.get("scope_node_ids")
    scope_include_neighbors = filters.get("scope_include_neighbors", False)
    
    if active_scopes:
        scope_node_ids = []
        for scope in active_scopes:
            scope_node_ids.extend(scope.node_ids)
            if getattr(scope, "include_connected_edges", False):
                scope_include_neighbors = True
                
    if scope_node_ids is not None:
        scope_set = set(scope_node_ids)
        
        # Step 1: Collect in-scope risk IDs
        scoped_risk_ids = scope_set & set(risk_ids)
        scoped_context_ids = scope_set & context_node_ids
        
        # Step 2: Optionally expand to 1-hop neighbors
        if scope_include_neighbors:
            neighbor_risk_ids = set()
            neighbor_context_ids = set()
            for e in edges:
                src, tgt = e.get("source"), e.get("target")
                if src in (scoped_risk_ids | scoped_context_ids) and tgt in set(risk_ids):
                    neighbor_risk_ids.add(tgt)
                if tgt in (scoped_risk_ids | scoped_context_ids) and src in set(risk_ids):
                    neighbor_risk_ids.add(src)
                if src in (scoped_risk_ids | scoped_context_ids) and tgt in context_node_ids:
                    neighbor_context_ids.add(tgt)
                if tgt in (scoped_risk_ids | scoped_context_ids) and src in context_node_ids:
                    neighbor_context_ids.add(src)
            scoped_risk_ids |= neighbor_risk_ids
            scoped_context_ids |= neighbor_context_ids
        
        # Step 3: Keep mitigations/ContextNodes connected to scoped risks
        connected_mit_ids = set()
        connected_context_ids = set()
        for e in edges:
            src, tgt = e.get("source"), e.get("target")
            # Mitigations connect via MITIGATES edges (mitigation → risk)
            if tgt in scoped_risk_ids and src in set(mitigation_ids):
                connected_mit_ids.add(src)
            if src in scoped_risk_ids and tgt in set(mitigation_ids):
                connected_mit_ids.add(tgt)
            # Context nodes connect via custom edges
            if tgt in scoped_risk_ids and src in context_node_ids:
                connected_context_ids.add(src)
            if src in scoped_risk_ids and tgt in context_node_ids:
                connected_context_ids.add(tgt)
        
        # Step 4: Build expanded node set
        expanded_set = scoped_risk_ids | connected_mit_ids | scoped_context_ids | connected_context_ids
        
        nodes = [n for n in nodes if n.get("id") in expanded_set]
        edges = [
            e for e in edges
            if e.get("source") in expanded_set and e.get("target") in expanded_set
        ]
    
    print(f"DEBUG: Returning {len(nodes)} nodes. Context IDs in final list: {[n['id'] for n in nodes if n.get('node_type') not in ('Risk', 'Mitigation', 'TPO')]}")
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
    from database.queries import generic_relationship
    from core import get_registry
    impacts_tpo_type = get_registry().get_relationship_type("impacts_tpo")
    all_tpo_impacts = generic_relationship.get_all_relationships(conn._driver, impacts_tpo_type) if impacts_tpo_type else []
    # Map generic generic relation ids to specific ones expected here
    for impact in all_tpo_impacts:
        impact["risk_id"] = impact.get("source_id")
        impact["tpo_id"] = impact.get("target_id")
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

def get_statistics(conn: Neo4jConnection, active_scopes: list = None) -> Dict[str, Any]:
    """
    Get comprehensive graph statistics, optionally filtered by active scopes.
    
    Args:
        conn: Database connection
        active_scopes: Optional list of AnalysisScopeConfig objects
    
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
    all_risks = risks.get_all_risks(conn)
    all_mitigations = mitigations.get_all_mitigations(conn)
    
    # Influence counts
    all_influences = influences.get_all_influences(conn)
    
    # Generic context data (TPOs)
    from database.queries import generic_entity, generic_relationship
    from core import get_registry
    registry = get_registry()
    tpo_type = registry.get_entity_type("tpo")
    if tpo_type:
        all_tpos = generic_entity.get_all_entities(conn._driver, tpo_type)
        impacts_tpo_type = registry.get_relationship_type("impacts_tpo")
        all_tpo_impacts = generic_relationship.get_all_relationships(conn._driver, impacts_tpo_type) if impacts_tpo_type else []
        # Rename field maps to match old `tpo_id` usage for internal arrays
        for imp in all_tpo_impacts:
            imp["risk_id"] = imp.get("source_id")
            imp["tpo_id"] = imp.get("target_id")
    else:
        all_tpos = []
        all_tpo_impacts = []
    
    # Mitigation counts
    all_mitigates = mitigations.get_all_mitigates_relationships(conn)
    
    # Process scope filtering if active scopes are provided
    if active_scopes:
        scope_node_ids = set()
        scope_include_neighbors = False
        
        for scope in active_scopes:
            scope_node_ids.update(scope.node_ids)
            if getattr(scope, "include_connected_edges", False):
                scope_include_neighbors = True
        
        filtered_risks = [r for r in all_risks if r["id"] in scope_node_ids]
        filtered_risk_ids = {r["id"] for r in filtered_risks}
        
        if scope_include_neighbors:
            neighbor_risk_ids = set()
            for inf in all_influences:
                src, tgt = inf["source_id"], inf["target_id"]
                if src in filtered_risk_ids:
                    neighbor_risk_ids.add(tgt)
                if tgt in filtered_risk_ids:
                    neighbor_risk_ids.add(src)
            filtered_risk_ids.update(neighbor_risk_ids)
            # Re-fetch the filtered risks with neighbors included
            filtered_risks = [r for r in all_risks if r["id"] in filtered_risk_ids]
            
        all_risks = filtered_risks
        
        # Filter influences to those connecting scoped risks
        all_influences = [
            inf for inf in all_influences
            if inf["source_id"] in filtered_risk_ids and inf["target_id"] in filtered_risk_ids
        ]
        
        # Keep TPOs connected to scoped risks
        all_tpo_impacts = [
            imp for imp in all_tpo_impacts
            if imp["risk_id"] in filtered_risk_ids
        ]
        connected_tpo_ids = {imp["tpo_id"] for imp in all_tpo_impacts}
        all_tpos = [t for t in all_tpos if t["id"] in connected_tpo_ids]
        
        # Keep mitigations connected to scoped risks
        all_mitigates = [
            mit for mit in all_mitigates
            if mit["risk_id"] in filtered_risk_ids
        ]
        connected_mit_ids = {mit["mitigation_id"] for mit in all_mitigates}
        all_mitigations = [m for m in all_mitigations if m["id"] in connected_mit_ids]
    
    # Compute statistics from filtered lists
    stats["total_risks"] = len(all_risks)
    
    # Level and Status counts
    # Use schema-driven level names
    if len(RISK_LEVELS) >= 1:
        stats["level1_risks"] = sum(1 for r in all_risks if r["level"] == RISK_LEVELS[0])
        stats["level1_name"] = RISK_LEVELS[0]
    if len(RISK_LEVELS) >= 2:
        stats["level2_risks"] = sum(1 for r in all_risks if r["level"] == RISK_LEVELS[1])
        stats["level2_name"] = RISK_LEVELS[1]
    
    # Keep backward compatibility keys
    stats["strategic_risks"] = stats.get("level1_risks", 0)
    stats["operational_risks"] = stats.get("level2_risks", 0)
    stats["contingent_risks"] = sum(1 for r in all_risks if r["status"] == "Contingent")
    stats["new_risks"] = sum(1 for r in all_risks if r["origin"] == "New")
    stats["legacy_risks"] = sum(1 for r in all_risks if r["origin"] == "Legacy")
    
    if stats["total_risks"] > 0:
        exposures = [r.get("exposure", 0) for r in all_risks if r.get("exposure") is not None]
        stats["avg_exposure"] = round(sum(exposures) / len(exposures), 1) if exposures else 0
    else:
        stats["avg_exposure"] = 0
        
    for r in all_risks:
        for cat in r.get("categories", []):
            stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
    
    stats["total_influences"] = len(all_influences)
    stats["total_tpos"] = len(all_tpos)
    stats["total_tpo_impacts"] = len(all_tpo_impacts)
    
    for t in all_tpos:
        cluster = t.get("cluster", "Unknown")
        stats["tpo_clusters"][cluster] = stats["tpo_clusters"].get(cluster, 0) + 1
        
    stats["total_mitigations"] = len(all_mitigations)
    stats["total_mitigates"] = len(all_mitigates)
    
    for m in all_mitigations:
        m_type = m.get("mitigation_type", "Unknown")
        m_status = m.get("status", "Unknown")
        stats["mitigations_by_type"][m_type] = stats["mitigations_by_type"].get(m_type, 0) + 1
        stats["mitigations_by_status"][m_status] = stats["mitigations_by_status"].get(m_status, 0) + 1
        
    return stats


# =============================================================================
# NODE SELECTION
# =============================================================================

def get_all_nodes_for_selection(conn: Neo4jConnection, active_scopes: list = None) -> List[Dict[str, Any]]:
    """
    Get all risks and TPOs formatted for dropdown selection.
    
    Args:
        conn: Database connection
        active_scopes: Optional list of AnalysisScopeConfig objects
    
    Returns:
        List of node dictionaries with label and type
    """
    result = []
    
    # Get risks
    all_risks = risks.get_all_risks(conn)
    # Get generic context data (TPOs)
    from database.queries import generic_entity, generic_relationship
    from core import get_registry
    registry = get_registry()
    tpo_type = registry.get_entity_type("tpo")
    if tpo_type:
        all_tpos = generic_entity.get_all_entities(conn._driver, tpo_type)
        impacts_tpo_type = registry.get_relationship_type("impacts_tpo")
        all_tpo_impacts = generic_relationship.get_all_relationships(conn._driver, impacts_tpo_type) if impacts_tpo_type else []
    else:
        all_tpos = []
        all_tpo_impacts = []
    
    if active_scopes:
        scope_node_ids = set()
        scope_include_neighbors = False
        
        for scope in active_scopes:
            scope_node_ids.update(scope.node_ids)
            if getattr(scope, "include_connected_edges", False):
                scope_include_neighbors = True
        
        filtered_risks = [r for r in all_risks if r["id"] in scope_node_ids]
        filtered_risk_ids = {r["id"] for r in filtered_risks}
        
        if scope_include_neighbors:
            # We need influences to expand
            all_influences = influences.get_all_influences(conn)
            neighbor_risk_ids = set()
            for inf in all_influences:
                src, tgt = inf["source_id"], inf["target_id"]
                if src in filtered_risk_ids:
                    neighbor_risk_ids.add(tgt)
                if tgt in filtered_risk_ids:
                    neighbor_risk_ids.add(src)
            filtered_risk_ids.update(neighbor_risk_ids)
            filtered_risks = [r for r in all_risks if r["id"] in filtered_risk_ids]
            
        all_risks = filtered_risks
        
        # Keep TPOs connected to scoped risks
        all_tpo_impacts = [
            imp for imp in all_tpo_impacts
            if imp.get("source_id") in filtered_risk_ids
        ]
        connected_tpo_ids = {imp.get("target_id") for imp in all_tpo_impacts}
        all_tpos = [t for t in all_tpos if t["id"] in connected_tpo_ids]
    
    for r in all_risks:
        result.append({
            "id": r["id"],
            "label": f"[{r['level'][:4]}] {r['name']}",
            "name": r["name"],
            "type": "Risk",
            "level": r["level"]
        })
    
    for t in all_tpos:
        result.append({
            "id": t["id"],
            "label": f"[TPO] {t.get('reference', t.get('name'))}: {t['name']}",
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
    tpo_data = None
    if not risk_data:
        from database.queries import generic_entity
        from core import get_registry
        tpo_type = get_registry().get_entity_type("tpo")
        if tpo_type:
            tpo_data = generic_entity.get_entity_by_id(conn._driver, tpo_type, node_id)
    
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
            from database.queries import generic_entity, generic_relationship
            from core import get_registry
            registry = get_registry()
            tpo_type = registry.get_entity_type("tpo")
            all_tpo_list = []
            if tpo_type:
                all_tpo_list = generic_entity.get_all_entities(conn._driver, tpo_type)
            tpo_ids = [t["id"] for t in all_tpo_list]
            
            if tpo_ids:
                impacts_tpo_type = registry.get_relationship_type("impacts_tpo")
                if impacts_tpo_type:
                    all_rels = generic_relationship.get_all_relationships(conn._driver, impacts_tpo_type)
                    for rel in all_rels:
                        if rel["source_id"] in risk_node_ids and rel["target_id"] in tpo_ids:
                            tpo_edges.append({
                                "source": rel["source_id"],
                                "target": rel["target_id"],
                                "edge_type": impacts_tpo_type.neo4j_type,
                                "impact_level": rel.get("impact_level", "Medium")
                            })
                
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
