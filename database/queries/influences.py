"""
Influence database queries.

Contains all Cypher queries for INFLUENCES relationship operations.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection


# =============================================================================
# INFLUENCE CREATE OPERATIONS
# =============================================================================

def create_influence(
    conn: Neo4jConnection,
    source_id: str,
    target_id: str,
    strength: str,
    description: str = "",
    confidence: float = 0.8
) -> Optional[str]:
    """
    Create an INFLUENCES relationship between two risks.
    
    The influence type is automatically determined based on source/target levels:
    - Operational → Business = Level1_Op_to_Bus
    - Business → Business = Level2_Bus_to_Bus
    - Operational → Operational = Level3_Op_to_Op
    
    Args:
        conn: Database connection
        source_id: Source risk UUID
        target_id: Target risk UUID
        strength: "Weak", "Moderate", "Strong", or "Critical"
        description: Influence description
        confidence: Confidence score (0-1)
    
    Returns:
        Created influence ID or None if failed
    """
    query = """
    MATCH (source:Risk {id: $source_id})
    MATCH (target:Risk {id: $target_id})
    
    // Determine type based on levels
    WITH source, target,
         CASE 
            WHEN source.level = 'Operational' AND target.level = 'Business' THEN 'Level1_Op_to_Bus'
            WHEN source.level = 'Business' AND target.level = 'Business' THEN 'Level2_Bus_to_Bus'
            WHEN source.level = 'Operational' AND target.level = 'Operational' THEN 'Level3_Op_to_Op'
            ELSE 'Unknown'
         END as determined_type
    
    CREATE (source)-[i:INFLUENCES {
        id: randomUUID(),
        influence_type: determined_type,
        strength: $strength,
        description: $description,
        confidence: $confidence,
        created_at: datetime(),
        last_validated: datetime()
    }]->(target)
    RETURN i.id as id
    """
    
    params = {
        "source_id": source_id,
        "target_id": target_id,
        "strength": strength,
        "description": description,
        "confidence": confidence
    }
    
    result = conn.execute_query(query, params)
    return result[0]["id"] if result else None


# =============================================================================
# INFLUENCE READ OPERATIONS
# =============================================================================

def get_all_influences(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Retrieve all influence relationships.
    
    Args:
        conn: Database connection
    
    Returns:
        List of influence dictionaries
    """
    query = """
    MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
    RETURN i.id as id, source.id as source_id, source.name as source_name,
           source.level as source_level, target.id as target_id,
           target.name as target_name, target.level as target_level,
           i.influence_type as influence_type, i.strength as strength,
           i.description as description, i.confidence as confidence
    ORDER BY i.strength DESC
    """
    
    return conn.execute_query(query)


def get_influence_by_id(conn: Neo4jConnection, influence_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an influence by its ID.
    
    Args:
        conn: Database connection
        influence_id: Influence relationship UUID
    
    Returns:
        Influence dictionary or None if not found
    """
    query = """
    MATCH (source:Risk)-[i:INFLUENCES {id: $id}]->(target:Risk)
    RETURN i.id as id, source.id as source_id, source.name as source_name,
           source.level as source_level, target.id as target_id,
           target.name as target_name, target.level as target_level,
           i.influence_type as influence_type, i.strength as strength,
           i.description as description, i.confidence as confidence
    """
    
    result = conn.execute_query(query, {"id": influence_id})
    return result[0] if result else None


def get_influences_from_risk(conn: Neo4jConnection, risk_id: str) -> List[Dict[str, Any]]:
    """
    Get all influences originating from a specific risk.
    
    Args:
        conn: Database connection
        risk_id: Source risk UUID
    
    Returns:
        List of influence dictionaries
    """
    query = """
    MATCH (source:Risk {id: $risk_id})-[i:INFLUENCES]->(target:Risk)
    RETURN i.id as id, target.id as target_id, target.name as target_name,
           target.level as target_level, i.influence_type as influence_type,
           i.strength as strength, i.confidence as confidence,
           i.description as description
    ORDER BY i.strength DESC
    """
    
    return conn.execute_query(query, {"risk_id": risk_id})


def get_influences_to_risk(conn: Neo4jConnection, risk_id: str) -> List[Dict[str, Any]]:
    """
    Get all influences pointing to a specific risk.
    
    Args:
        conn: Database connection
        risk_id: Target risk UUID
    
    Returns:
        List of influence dictionaries
    """
    query = """
    MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk {id: $risk_id})
    RETURN i.id as id, source.id as source_id, source.name as source_name,
           source.level as source_level, i.influence_type as influence_type,
           i.strength as strength, i.confidence as confidence,
           i.description as description
    ORDER BY i.strength DESC
    """
    
    return conn.execute_query(query, {"risk_id": risk_id})


def get_influence_edges(
    conn: Neo4jConnection,
    node_ids: List[str]
) -> List[Dict[str, Any]]:
    """
    Get influence edges for graph visualization.
    
    Args:
        conn: Database connection
        node_ids: List of node IDs to include
    
    Returns:
        List of edge dictionaries
    """
    if not node_ids:
        return []
    
    query = """
    MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
    WHERE source.id IN $node_ids AND target.id IN $node_ids
    RETURN source.id as source, target.id as target,
           i.influence_type as influence_type, i.strength as strength,
           'INFLUENCES' as edge_type
    """
    
    return conn.execute_query(query, {"node_ids": node_ids})


def get_influences_by_type(conn: Neo4jConnection, influence_type: str) -> List[Dict[str, Any]]:
    """
    Get all influences of a specific type.
    
    Args:
        conn: Database connection
        influence_type: Influence type to filter by
    
    Returns:
        List of influence dictionaries
    """
    query = """
    MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
    WHERE i.influence_type = $influence_type
    RETURN i.id as id, source.id as source_id, source.name as source_name,
           target.id as target_id, target.name as target_name,
           i.strength as strength, i.confidence as confidence
    ORDER BY i.strength DESC
    """
    
    return conn.execute_query(query, {"influence_type": influence_type})


# =============================================================================
# INFLUENCE UPDATE OPERATIONS
# =============================================================================

def update_influence(
    conn: Neo4jConnection,
    influence_id: str,
    strength: str,
    description: str,
    confidence: float
) -> bool:
    """
    Update an influence relationship.
    
    Args:
        conn: Database connection
        influence_id: Influence relationship UUID
        strength: Updated strength
        description: Updated description
        confidence: Updated confidence
    
    Returns:
        True if successful, False otherwise
    """
    query = """
    MATCH ()-[i:INFLUENCES {id: $id}]->()
    SET i.strength = $strength,
        i.description = $description,
        i.confidence = $confidence,
        i.last_validated = datetime()
    RETURN i.id
    """
    
    params = {
        "id": influence_id,
        "strength": strength,
        "description": description,
        "confidence": confidence
    }
    
    result = conn.execute_query(query, params)
    return len(result) > 0


# =============================================================================
# INFLUENCE DELETE OPERATIONS
# =============================================================================

def delete_influence(conn: Neo4jConnection, influence_id: str) -> bool:
    """
    Delete an influence relationship.
    
    Args:
        conn: Database connection
        influence_id: Influence relationship UUID
    
    Returns:
        True if successful
    """
    query = """
    MATCH ()-[i:INFLUENCES {id: $id}]->()
    DELETE i
    """
    
    conn.execute_query(query, {"id": influence_id})
    return True


# =============================================================================
# INFLUENCE NETWORK TRAVERSAL
# =============================================================================

def get_downstream_risks(
    conn: Neo4jConnection,
    risk_id: str,
    max_depth: int = 10
) -> List[Dict[str, Any]]:
    """
    Get all risks downstream (influenced by) a specific risk.
    
    Args:
        conn: Database connection
        risk_id: Starting risk UUID
        max_depth: Maximum traversal depth
    
    Returns:
        List of risk dictionaries with depth
    """
    query = """
    MATCH path = (start:Risk {id: $risk_id})-[:INFLUENCES*1..%d]->(downstream:Risk)
    WITH downstream, min(length(path)) as depth
    RETURN downstream.id as id, downstream.name as name,
           downstream.level as level, downstream.exposure as exposure,
           depth
    ORDER BY depth, downstream.exposure DESC
    """ % max_depth
    
    return conn.execute_query(query, {"risk_id": risk_id})


def get_upstream_risks(
    conn: Neo4jConnection,
    risk_id: str,
    max_depth: int = 10
) -> List[Dict[str, Any]]:
    """
    Get all risks upstream (influencing) a specific risk.
    
    Args:
        conn: Database connection
        risk_id: Starting risk UUID
        max_depth: Maximum traversal depth
    
    Returns:
        List of risk dictionaries with depth
    """
    query = """
    MATCH path = (upstream:Risk)-[:INFLUENCES*1..%d]->(target:Risk {id: $risk_id})
    WITH upstream, min(length(path)) as depth
    RETURN upstream.id as id, upstream.name as name,
           upstream.level as level, upstream.exposure as exposure,
           depth
    ORDER BY depth, upstream.exposure DESC
    """ % max_depth
    
    return conn.execute_query(query, {"risk_id": risk_id})


def get_influence_path(
    conn: Neo4jConnection,
    source_id: str,
    target_id: str,
    max_depth: int = 5
) -> List[List[Dict[str, Any]]]:
    """
    Find all paths between two risks.
    
    Args:
        conn: Database connection
        source_id: Source risk UUID
        target_id: Target risk UUID
        max_depth: Maximum path length
    
    Returns:
        List of paths, each path is a list of node dictionaries
    """
    query = """
    MATCH path = (source:Risk {id: $source_id})-[:INFLUENCES*1..%d]->(target:Risk {id: $target_id})
    WITH path, length(path) as path_length
    ORDER BY path_length
    LIMIT 5
    UNWIND nodes(path) as node
    WITH path, collect({
        id: node.id,
        name: node.name,
        level: node.level
    }) as path_nodes
    RETURN path_nodes
    """ % max_depth
    
    result = conn.execute_query(query, {"source_id": source_id, "target_id": target_id})
    return [r["path_nodes"] for r in result]


# =============================================================================
# INFLUENCE STATISTICS
# =============================================================================

def get_influence_count(conn: Neo4jConnection) -> int:
    """Get total number of influences."""
    query = "MATCH ()-[i:INFLUENCES]->() RETURN count(i) as count"
    result = conn.execute_query(query)
    return result[0]["count"] if result else 0


def get_influence_count_by_type(conn: Neo4jConnection) -> Dict[str, int]:
    """Get influence count by type."""
    query = """
    MATCH ()-[i:INFLUENCES]->()
    RETURN i.influence_type as type, count(i) as count
    ORDER BY count DESC
    """
    result = conn.execute_query(query)
    return {r["type"]: r["count"] for r in result if r["type"]}


def get_influence_count_by_strength(conn: Neo4jConnection) -> Dict[str, int]:
    """Get influence count by strength."""
    query = """
    MATCH ()-[i:INFLUENCES]->()
    RETURN i.strength as strength, count(i) as count
    ORDER BY count DESC
    """
    result = conn.execute_query(query)
    return {r["strength"]: r["count"] for r in result if r["strength"]}


def get_most_influential_risks(conn: Neo4jConnection, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get risks with the most outgoing influences.
    
    Args:
        conn: Database connection
        limit: Maximum number of results
    
    Returns:
        List of risk dictionaries with influence count
    """
    query = """
    MATCH (r:Risk)-[i:INFLUENCES]->()
    WITH r, count(i) as influence_count
    ORDER BY influence_count DESC
    LIMIT $limit
    RETURN r.id as id, r.name as name, r.level as level,
           r.exposure as exposure, influence_count
    """
    
    return conn.execute_query(query, {"limit": limit})


def get_most_influenced_risks(conn: Neo4jConnection, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get risks with the most incoming influences.
    
    Args:
        conn: Database connection
        limit: Maximum number of results
    
    Returns:
        List of risk dictionaries with influence count
    """
    query = """
    MATCH (r:Risk)<-[i:INFLUENCES]-()
    WITH r, count(i) as influenced_by_count
    ORDER BY influenced_by_count DESC
    LIMIT $limit
    RETURN r.id as id, r.name as name, r.level as level,
           r.exposure as exposure, influenced_by_count
    """
    
    return conn.execute_query(query, {"limit": limit})
