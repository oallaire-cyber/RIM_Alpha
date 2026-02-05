"""
TPO (Top Program Objectives) database queries.

Contains all Cypher queries for TPO node CRUD operations
and TPO Impact relationship management.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection


# =============================================================================
# TPO CREATE OPERATIONS
# =============================================================================

def create_tpo(
    conn: Neo4jConnection,
    reference: str,
    name: str,
    cluster: str,
    description: str = ""
) -> Optional[str]:
    """
    Create a new TPO node.
    
    Args:
        conn: Database connection
        reference: Short reference code (e.g., "TPO-01")
        name: TPO name
        cluster: Cluster category
        description: TPO description
    
    Returns:
        Created TPO ID or None if failed
    """
    query = """
    CREATE (t:TPO {
        id: randomUUID(),
        reference: $reference,
        name: $name,
        cluster: $cluster,
        description: $description,
        created_at: datetime(),
        updated_at: datetime()
    })
    RETURN t.id as id
    """
    
    params = {
        "reference": reference,
        "name": name,
        "cluster": cluster,
        "description": description
    }
    
    result = conn.execute_query(query, params)
    return result[0]["id"] if result else None


# =============================================================================
# TPO READ OPERATIONS
# =============================================================================

def get_all_tpos(
    conn: Neo4jConnection,
    cluster_filter: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all TPOs with optional cluster filter.
    
    Args:
        conn: Database connection
        cluster_filter: List of clusters to include
    
    Returns:
        List of TPO dictionaries
    """
    conditions = []
    params = {}
    
    if cluster_filter and len(cluster_filter) > 0:
        conditions.append("t.cluster IN $clusters")
        params["clusters"] = cluster_filter
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
    MATCH (t:TPO)
    {where_clause}
    RETURN t.id as id, t.reference as reference, t.name as name,
           t.cluster as cluster, t.description as description
    ORDER BY t.reference
    """
    
    return conn.execute_query(query, params)


def get_tpo_by_id(conn: Neo4jConnection, tpo_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a TPO by its ID.
    
    Args:
        conn: Database connection
        tpo_id: TPO UUID
    
    Returns:
        TPO dictionary or None if not found
    """
    query = """
    MATCH (t:TPO {id: $id})
    RETURN t.id as id, t.reference as reference, t.name as name,
           t.cluster as cluster, t.description as description
    """
    
    result = conn.execute_query(query, {"id": tpo_id})
    return result[0] if result else None


def get_tpo_by_reference(conn: Neo4jConnection, reference: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a TPO by its reference code.
    
    Args:
        conn: Database connection
        reference: TPO reference code
    
    Returns:
        TPO dictionary or None if not found
    """
    query = """
    MATCH (t:TPO {reference: $reference})
    RETURN t.id as id, t.reference as reference, t.name as name,
           t.cluster as cluster, t.description as description
    """
    
    result = conn.execute_query(query, {"reference": reference})
    return result[0] if result else None


def get_tpos_for_graph(
    conn: Neo4jConnection,
    cluster_filter: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve TPOs formatted for graph visualization.
    
    Args:
        conn: Database connection
        cluster_filter: List of clusters to include
    
    Returns:
        List of TPO dictionaries with node_type
    """
    conditions = []
    params = {}
    
    if cluster_filter and len(cluster_filter) > 0:
        conditions.append("t.cluster IN $clusters")
        params["clusters"] = cluster_filter
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
    MATCH (t:TPO)
    {where_clause}
    RETURN t.id as id, t.reference as reference, t.name as name,
           t.cluster as cluster, t.description as description,
           'TPO' as node_type
    ORDER BY t.reference
    """
    
    return conn.execute_query(query, params)


# =============================================================================
# TPO UPDATE OPERATIONS
# =============================================================================

def update_tpo(
    conn: Neo4jConnection,
    tpo_id: str,
    reference: str,
    name: str,
    cluster: str,
    description: str
) -> bool:
    """
    Update an existing TPO.
    
    Args:
        conn: Database connection
        tpo_id: TPO UUID to update
        reference: Updated reference
        name: Updated name
        cluster: Updated cluster
        description: Updated description
    
    Returns:
        True if successful, False otherwise
    """
    query = """
    MATCH (t:TPO {id: $id})
    SET t.reference = $reference,
        t.name = $name,
        t.cluster = $cluster,
        t.description = $description,
        t.updated_at = datetime()
    RETURN t.id
    """
    
    params = {
        "id": tpo_id,
        "reference": reference,
        "name": name,
        "cluster": cluster,
        "description": description
    }
    
    result = conn.execute_query(query, params)
    return len(result) > 0


# =============================================================================
# TPO DELETE OPERATIONS
# =============================================================================

def delete_tpo(conn: Neo4jConnection, tpo_id: str) -> bool:
    """
    Delete a TPO and all its relationships.
    
    Args:
        conn: Database connection
        tpo_id: TPO UUID to delete
    
    Returns:
        True if successful
    """
    query = """
    MATCH (t:TPO {id: $id})
    DETACH DELETE t
    """
    
    conn.execute_query(query, {"id": tpo_id})
    return True


# =============================================================================
# TPO IMPACT RELATIONSHIP OPERATIONS
# =============================================================================

def create_tpo_impact(
    conn: Neo4jConnection,
    risk_id: str,
    tpo_id: str,
    impact_level: str,
    description: str = ""
) -> Optional[str]:
    """
    Create an IMPACTS_TPO relationship from a Strategic Risk to a TPO.
    
    Args:
        conn: Database connection
        risk_id: Risk UUID (must be Strategic)
        tpo_id: TPO UUID
        impact_level: "Low", "Medium", "High", or "Critical"
        description: Impact description
    
    Returns:
        Created impact ID or None if failed
    
    Raises:
        ValueError: If risk is not Strategic
    """
    # Verify the risk is Strategic
    check_query = """
    MATCH (r:Risk {id: $risk_id})
    RETURN r.level as level
    """
    check_result = conn.execute_query(check_query, {"risk_id": risk_id})
    
    if not check_result or check_result[0]["level"] != "Strategic":
        raise ValueError("Only Strategic risks can impact TPOs")
    
    query = """
    MATCH (r:Risk {id: $risk_id})
    MATCH (t:TPO {id: $tpo_id})
    CREATE (r)-[i:IMPACTS_TPO {
        id: randomUUID(),
        impact_level: $impact_level,
        description: $description,
        created_at: datetime()
    }]->(t)
    RETURN i.id as id
    """
    
    params = {
        "risk_id": risk_id,
        "tpo_id": tpo_id,
        "impact_level": impact_level,
        "description": description
    }
    
    result = conn.execute_query(query, params)
    return result[0]["id"] if result else None


def get_all_tpo_impacts(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Retrieve all TPO impact relationships.
    
    Args:
        conn: Database connection
    
    Returns:
        List of TPO impact dictionaries
    """
    query = """
    MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
    RETURN i.id as id, r.id as risk_id, r.name as risk_name,
           t.id as tpo_id, t.reference as tpo_reference, t.name as tpo_name,
           i.impact_level as impact_level, i.description as description
    ORDER BY t.reference
    """
    
    return conn.execute_query(query)


def get_tpo_impacts_for_risk(conn: Neo4jConnection, risk_id: str) -> List[Dict[str, Any]]:
    """
    Get all TPO impacts for a specific risk.
    
    Args:
        conn: Database connection
        risk_id: Risk UUID
    
    Returns:
        List of TPO impact dictionaries
    """
    query = """
    MATCH (r:Risk {id: $risk_id})-[i:IMPACTS_TPO]->(t:TPO)
    RETURN i.id as id, t.id as tpo_id, t.reference as tpo_reference,
           t.name as tpo_name, t.cluster as tpo_cluster,
           i.impact_level as impact_level, i.description as description
    ORDER BY t.reference
    """
    
    return conn.execute_query(query, {"risk_id": risk_id})


def get_risks_impacting_tpo(conn: Neo4jConnection, tpo_id: str) -> List[Dict[str, Any]]:
    """
    Get all risks that impact a specific TPO.
    
    Args:
        conn: Database connection
        tpo_id: TPO UUID
    
    Returns:
        List of risk dictionaries with impact info
    """
    query = """
    MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO {id: $tpo_id})
    RETURN r.id as id, r.name as name, r.level as level,
           r.exposure as exposure, i.impact_level as impact_level,
           i.description as description
    ORDER BY r.exposure DESC
    """
    
    return conn.execute_query(query, {"tpo_id": tpo_id})


def get_tpo_impact_edges(
    conn: Neo4jConnection,
    risk_ids: List[str],
    tpo_ids: List[str]
) -> List[Dict[str, Any]]:
    """
    Get TPO impact edges for graph visualization.
    
    Args:
        conn: Database connection
        risk_ids: List of risk IDs to include
        tpo_ids: List of TPO IDs to include
    
    Returns:
        List of edge dictionaries
    """
    if not risk_ids or not tpo_ids:
        return []
    
    query = """
    MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
    WHERE r.id IN $risk_ids AND t.id IN $tpo_ids
    RETURN r.id as source, t.id as target,
           i.impact_level as impact_level, i.description as description,
           'IMPACTS_TPO' as edge_type
    """
    
    return conn.execute_query(query, {"risk_ids": risk_ids, "tpo_ids": tpo_ids})


def update_tpo_impact(
    conn: Neo4jConnection,
    impact_id: str,
    impact_level: str,
    description: str
) -> bool:
    """
    Update a TPO impact relationship.
    
    Args:
        conn: Database connection
        impact_id: Impact relationship UUID
        impact_level: Updated impact level
        description: Updated description
    
    Returns:
        True if successful, False otherwise
    """
    query = """
    MATCH ()-[i:IMPACTS_TPO {id: $id}]->()
    SET i.impact_level = $impact_level,
        i.description = $description
    RETURN i.id
    """
    
    params = {
        "id": impact_id,
        "impact_level": impact_level,
        "description": description
    }
    
    result = conn.execute_query(query, params)
    return len(result) > 0


def delete_tpo_impact(conn: Neo4jConnection, impact_id: str) -> bool:
    """
    Delete a TPO impact relationship.
    
    Args:
        conn: Database connection
        impact_id: Impact relationship UUID
    
    Returns:
        True if successful
    """
    query = """
    MATCH ()-[i:IMPACTS_TPO {id: $id}]->()
    DELETE i
    """
    
    conn.execute_query(query, {"id": impact_id})
    return True


# =============================================================================
# TPO STATISTICS
# =============================================================================

def get_tpo_count(conn: Neo4jConnection) -> int:
    """Get total number of TPOs."""
    query = "MATCH (t:TPO) RETURN count(t) as count"
    result = conn.execute_query(query)
    return result[0]["count"] if result else 0


def get_tpo_impact_count(conn: Neo4jConnection) -> int:
    """Get total number of TPO impact relationships."""
    query = "MATCH ()-[i:IMPACTS_TPO]->() RETURN count(i) as count"
    result = conn.execute_query(query)
    return result[0]["count"] if result else 0


def get_tpo_count_by_cluster(conn: Neo4jConnection) -> Dict[str, int]:
    """Get TPO count by cluster."""
    query = """
    MATCH (t:TPO)
    RETURN t.cluster as cluster, count(t) as count
    ORDER BY count DESC
    """
    result = conn.execute_query(query)
    return {r["cluster"]: r["count"] for r in result}
