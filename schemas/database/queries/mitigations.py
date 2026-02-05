"""
Mitigation database queries.

Contains all Cypher queries for Mitigation node CRUD operations
and MITIGATES relationship management.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection


# =============================================================================
# MITIGATION CREATE OPERATIONS
# =============================================================================

def create_mitigation(
    conn: Neo4jConnection,
    name: str,
    mitigation_type: str,
    status: str,
    description: str = "",
    owner: str = "",
    source_entity: str = ""
) -> Optional[str]:
    """
    Create a new Mitigation node.
    
    Args:
        conn: Database connection
        name: Mitigation name
        mitigation_type: "Dedicated", "Inherited", or "Baseline"
        status: "Proposed", "In Progress", "Implemented", or "Deferred"
        description: Mitigation description
        owner: Mitigation owner
        source_entity: Source for inherited/baseline mitigations
    
    Returns:
        Created mitigation ID or None if failed
    """
    query = """
    CREATE (m:Mitigation {
        id: randomUUID(),
        name: $name,
        type: $type,
        status: $status,
        description: $description,
        owner: $owner,
        source_entity: $source_entity,
        created_at: datetime(),
        updated_at: datetime()
    })
    RETURN m.id as id
    """
    
    params = {
        "name": name,
        "type": mitigation_type,
        "status": status,
        "description": description,
        "owner": owner,
        "source_entity": source_entity
    }
    
    result = conn.execute_query(query, params)
    return result[0]["id"] if result else None


# =============================================================================
# MITIGATION READ OPERATIONS
# =============================================================================

def get_all_mitigations(
    conn: Neo4jConnection,
    type_filter: Optional[List[str]] = None,
    status_filter: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all mitigations with optional filters.
    
    Args:
        conn: Database connection
        type_filter: List of types to include
        status_filter: List of statuses to include
    
    Returns:
        List of mitigation dictionaries
    """
    conditions = []
    params = {}
    
    if type_filter and len(type_filter) > 0:
        conditions.append("m.type IN $types")
        params["types"] = type_filter
    
    if status_filter and len(status_filter) > 0:
        conditions.append("m.status IN $statuses")
        params["statuses"] = status_filter
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
    MATCH (m:Mitigation)
    {where_clause}
    RETURN m.id as id, m.name as name, m.type as type,
           m.status as status, m.description as description,
           m.owner as owner, m.source_entity as source_entity
    ORDER BY m.name
    """
    
    return conn.execute_query(query, params)


def get_mitigation_by_id(conn: Neo4jConnection, mitigation_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a mitigation by its ID.
    
    Args:
        conn: Database connection
        mitigation_id: Mitigation UUID
    
    Returns:
        Mitigation dictionary or None if not found
    """
    query = """
    MATCH (m:Mitigation {id: $id})
    RETURN m.id as id, m.name as name, m.type as type,
           m.status as status, m.description as description,
           m.owner as owner, m.source_entity as source_entity
    """
    
    result = conn.execute_query(query, {"id": mitigation_id})
    return result[0] if result else None


def get_mitigation_by_name(conn: Neo4jConnection, name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a mitigation by its name.
    
    Args:
        conn: Database connection
        name: Mitigation name
    
    Returns:
        Mitigation dictionary or None if not found
    """
    query = """
    MATCH (m:Mitigation {name: $name})
    RETURN m.id as id, m.name as name, m.type as type,
           m.status as status, m.description as description,
           m.owner as owner, m.source_entity as source_entity
    """
    
    result = conn.execute_query(query, {"name": name})
    return result[0] if result else None


def get_mitigations_for_graph(
    conn: Neo4jConnection,
    type_filter: Optional[List[str]] = None,
    status_filter: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve mitigations formatted for graph visualization.
    
    Args:
        conn: Database connection
        type_filter: List of types to include
        status_filter: List of statuses to include
    
    Returns:
        List of mitigation dictionaries with node_type
    """
    conditions = []
    params = {}
    
    if type_filter and len(type_filter) > 0:
        conditions.append("m.type IN $types")
        params["types"] = type_filter
    
    if status_filter and len(status_filter) > 0:
        conditions.append("m.status IN $statuses")
        params["statuses"] = status_filter
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
    MATCH (m:Mitigation)
    {where_clause}
    RETURN m.id as id, m.name as name, m.type as type,
           m.status as status, m.owner as owner,
           m.source_entity as source_entity,
           m.description as description,
           'Mitigation' as node_type
    ORDER BY m.name
    """
    
    return conn.execute_query(query, params)


# =============================================================================
# MITIGATION UPDATE OPERATIONS
# =============================================================================

def update_mitigation(
    conn: Neo4jConnection,
    mitigation_id: str,
    name: str,
    mitigation_type: str,
    status: str,
    description: str,
    owner: str,
    source_entity: str
) -> bool:
    """
    Update an existing mitigation.
    
    Args:
        conn: Database connection
        mitigation_id: Mitigation UUID to update
        name: Updated name
        mitigation_type: Updated type
        status: Updated status
        description: Updated description
        owner: Updated owner
        source_entity: Updated source entity
    
    Returns:
        True if successful, False otherwise
    """
    query = """
    MATCH (m:Mitigation {id: $id})
    SET m.name = $name,
        m.type = $type,
        m.status = $status,
        m.description = $description,
        m.owner = $owner,
        m.source_entity = $source_entity,
        m.updated_at = datetime()
    RETURN m.id
    """
    
    params = {
        "id": mitigation_id,
        "name": name,
        "type": mitigation_type,
        "status": status,
        "description": description,
        "owner": owner,
        "source_entity": source_entity
    }
    
    result = conn.execute_query(query, params)
    return len(result) > 0


# =============================================================================
# MITIGATION DELETE OPERATIONS
# =============================================================================

def delete_mitigation(conn: Neo4jConnection, mitigation_id: str) -> bool:
    """
    Delete a mitigation and all its relationships.
    
    Args:
        conn: Database connection
        mitigation_id: Mitigation UUID to delete
    
    Returns:
        True if successful
    """
    query = """
    MATCH (m:Mitigation {id: $id})
    DETACH DELETE m
    """
    
    conn.execute_query(query, {"id": mitigation_id})
    return True


# =============================================================================
# MITIGATES RELATIONSHIP OPERATIONS
# =============================================================================

def create_mitigates_relationship(
    conn: Neo4jConnection,
    mitigation_id: str,
    risk_id: str,
    effectiveness: str,
    description: str = ""
) -> Optional[str]:
    """
    Create a MITIGATES relationship from a Mitigation to a Risk.
    
    Args:
        conn: Database connection
        mitigation_id: Mitigation UUID
        risk_id: Risk UUID
        effectiveness: "Low", "Medium", "High", or "Critical"
        description: Relationship description
    
    Returns:
        Created relationship ID or None if failed
    """
    query = """
    MATCH (m:Mitigation {id: $mitigation_id})
    MATCH (r:Risk {id: $risk_id})
    CREATE (m)-[rel:MITIGATES {
        id: randomUUID(),
        effectiveness: $effectiveness,
        description: $description,
        created_at: datetime()
    }]->(r)
    RETURN rel.id as id
    """
    
    params = {
        "mitigation_id": mitigation_id,
        "risk_id": risk_id,
        "effectiveness": effectiveness,
        "description": description
    }
    
    result = conn.execute_query(query, params)
    return result[0]["id"] if result else None


def get_all_mitigates_relationships(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Retrieve all MITIGATES relationships.
    
    Args:
        conn: Database connection
    
    Returns:
        List of relationship dictionaries
    """
    query = """
    MATCH (m:Mitigation)-[rel:MITIGATES]->(r:Risk)
    RETURN rel.id as id, m.id as mitigation_id, m.name as mitigation_name,
           m.type as mitigation_type, r.id as risk_id, r.name as risk_name,
           r.level as risk_level, rel.effectiveness as effectiveness,
           rel.description as description
    ORDER BY m.name, r.name
    """
    
    return conn.execute_query(query)


def get_mitigations_for_risk(conn: Neo4jConnection, risk_id: str) -> List[Dict[str, Any]]:
    """
    Get all mitigations that mitigate a specific risk.
    
    Args:
        conn: Database connection
        risk_id: Risk UUID
    
    Returns:
        List of mitigation dictionaries with effectiveness
    """
    query = """
    MATCH (m:Mitigation)-[rel:MITIGATES]->(r:Risk {id: $risk_id})
    RETURN m.id as id, m.name as name, m.type as type,
           m.status as status, m.owner as owner,
           rel.effectiveness as effectiveness, rel.description as rel_description
    ORDER BY rel.effectiveness DESC
    """
    
    return conn.execute_query(query, {"risk_id": risk_id})


def get_risks_for_mitigation(conn: Neo4jConnection, mitigation_id: str) -> List[Dict[str, Any]]:
    """
    Get all risks mitigated by a specific mitigation.
    
    Args:
        conn: Database connection
        mitigation_id: Mitigation UUID
    
    Returns:
        List of risk dictionaries with effectiveness
    """
    query = """
    MATCH (m:Mitigation {id: $mitigation_id})-[rel:MITIGATES]->(r:Risk)
    RETURN r.id as id, r.name as name, r.level as level,
           r.status as status, r.exposure as exposure,
           rel.effectiveness as effectiveness, rel.description as rel_description
    ORDER BY r.exposure DESC
    """
    
    return conn.execute_query(query, {"mitigation_id": mitigation_id})


def get_mitigates_edges(
    conn: Neo4jConnection,
    mitigation_ids: List[str],
    risk_ids: List[str]
) -> List[Dict[str, Any]]:
    """
    Get MITIGATES edges for graph visualization.
    
    Args:
        conn: Database connection
        mitigation_ids: List of mitigation IDs to include
        risk_ids: List of risk IDs to include
    
    Returns:
        List of edge dictionaries
    """
    if not mitigation_ids or not risk_ids:
        return []
    
    query = """
    MATCH (m:Mitigation)-[rel:MITIGATES]->(r:Risk)
    WHERE m.id IN $mit_ids AND r.id IN $risk_ids
    RETURN m.id as source, r.id as target,
           rel.effectiveness as effectiveness, rel.description as description,
           'MITIGATES' as edge_type
    """
    
    return conn.execute_query(query, {"mit_ids": mitigation_ids, "risk_ids": risk_ids})


def update_mitigates_relationship(
    conn: Neo4jConnection,
    relationship_id: str,
    effectiveness: str,
    description: str
) -> bool:
    """
    Update a MITIGATES relationship.
    
    Args:
        conn: Database connection
        relationship_id: Relationship UUID
        effectiveness: Updated effectiveness
        description: Updated description
    
    Returns:
        True if successful, False otherwise
    """
    query = """
    MATCH ()-[rel:MITIGATES {id: $id}]->()
    SET rel.effectiveness = $effectiveness,
        rel.description = $description
    RETURN rel.id
    """
    
    params = {
        "id": relationship_id,
        "effectiveness": effectiveness,
        "description": description
    }
    
    result = conn.execute_query(query, params)
    return len(result) > 0


def delete_mitigates_relationship(conn: Neo4jConnection, relationship_id: str) -> bool:
    """
    Delete a MITIGATES relationship.
    
    Args:
        conn: Database connection
        relationship_id: Relationship UUID
    
    Returns:
        True if successful
    """
    query = """
    MATCH ()-[rel:MITIGATES {id: $id}]->()
    DELETE rel
    """
    
    conn.execute_query(query, {"id": relationship_id})
    return True


# =============================================================================
# MITIGATION STATISTICS
# =============================================================================

def get_mitigation_count(conn: Neo4jConnection) -> int:
    """Get total number of mitigations."""
    query = "MATCH (m:Mitigation) RETURN count(m) as count"
    result = conn.execute_query(query)
    return result[0]["count"] if result else 0


def get_mitigates_count(conn: Neo4jConnection) -> int:
    """Get total number of MITIGATES relationships."""
    query = "MATCH ()-[rel:MITIGATES]->() RETURN count(rel) as count"
    result = conn.execute_query(query)
    return result[0]["count"] if result else 0


def get_mitigation_count_by_type(conn: Neo4jConnection) -> Dict[str, int]:
    """Get mitigation count by type."""
    query = """
    MATCH (m:Mitigation)
    RETURN m.type as type, count(m) as count
    ORDER BY count DESC
    """
    result = conn.execute_query(query)
    return {r["type"]: r["count"] for r in result if r["type"]}


def get_mitigation_count_by_status(conn: Neo4jConnection) -> Dict[str, int]:
    """Get mitigation count by status."""
    query = """
    MATCH (m:Mitigation)
    RETURN m.status as status, count(m) as count
    ORDER BY count DESC
    """
    result = conn.execute_query(query)
    return {r["status"]: r["count"] for r in result if r["status"]}


def get_unmitigated_risks(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Get all risks that have no mitigations.
    
    Args:
        conn: Database connection
    
    Returns:
        List of risk dictionaries
    """
    query = """
    MATCH (r:Risk)
    WHERE NOT (r)<-[:MITIGATES]-(:Mitigation)
    RETURN r.id as id, r.name as name, r.level as level,
           r.status as status, r.exposure as exposure,
           r.categories as categories
    ORDER BY r.exposure DESC
    """
    
    return conn.execute_query(query)


def get_risk_mitigation_summary(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Get mitigation summary for all risks.
    
    Args:
        conn: Database connection
    
    Returns:
        List of risks with mitigation counts
    """
    query = """
    MATCH (r:Risk)
    OPTIONAL MATCH (m:Mitigation)-[rel:MITIGATES]->(r)
    WITH r, 
         count(m) as mitigation_count,
         collect({
             id: m.id, 
             name: m.name, 
             status: m.status, 
             effectiveness: rel.effectiveness
         }) as mitigations
    RETURN r.id as id, r.name as name, r.level as level,
           r.status as status, r.exposure as exposure,
           r.origin as origin, r.categories as categories,
           mitigation_count, mitigations
    ORDER BY mitigation_count ASC, r.exposure DESC
    """
    
    return conn.execute_query(query)
