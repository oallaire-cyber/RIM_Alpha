"""
Risk database queries.

Contains all Cypher queries for Risk node CRUD operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database.connection import Neo4jConnection


# =============================================================================
# CREATE OPERATIONS
# =============================================================================

def create_risk(
    conn: Neo4jConnection,
    name: str,
    level: str,
    categories: List[str],
    description: str = "",
    status: str = "Active",
    origin: str = "New",
    owner: str = "",
    probability: Optional[float] = None,
    impact: Optional[float] = None,
    activation_condition: Optional[str] = None,
    activation_decision_date: Optional[str] = None,
    subtype: Optional[str] = None,
    ext_fields: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Create a new Risk node.
    
    Args:
        conn: Database connection
        name: Risk name
        level: "Business" or "Operational"
        categories: List of category strings
        description: Risk description
        status: "Active", "Contingent", or "Archived"
        origin: "New" or "Legacy"
        owner: Risk owner
        probability: Probability score (0-10)
        impact: Impact score (0-10)
        activation_condition: Condition for contingent risks
        activation_decision_date: Decision date for contingent risks
        subtype: Risk subtype ID (e.g., "generic", "cyber_entry_point")
        ext_fields: Extension field dict with ext_ prefixed keys
    
    Returns:
        Created risk ID or None if failed
    """
    # Calculate exposure
    exposure = None
    current_score_type = "None"
    if probability is not None and impact is not None:
        exposure = probability * impact
        current_score_type = "Qualitative_4x4"
    
    # Review dates
    last_review_date = datetime.now().isoformat()
    next_review_date = (datetime.now() + timedelta(days=90)).isoformat()
    
    # Build extension fields SET clause
    ext_set_clause = ""
    ext_items = {}
    if ext_fields:
        ext_items = {k: v for k, v in ext_fields.items() if k.startswith("ext_") and v is not None}
        if ext_items:
            ext_set_clause = "SET " + ", ".join(f"r.{k} = ${k}" for k in ext_items.keys())
    
    query = f"""
    CREATE (r:Risk {{
        id: randomUUID(),
        name: $name,
        description: $description,
        level: $level,
        status: $status,
        origin: $origin,
        activation_condition: $activation_condition,
        activation_decision_date: $activation_decision_date,
        categories: $categories,
        owner: $owner,
        current_score_type: $current_score_type,
        probability: $probability,
        impact: $impact,
        exposure: $exposure,
        subtype: $subtype,
        created_at: datetime(),
        updated_at: datetime(),
        last_review_date: $last_review_date,
        next_review_date: $next_review_date
    }})
    {ext_set_clause}
    RETURN r.id as id
    """
    
    params = {
        "name": name,
        "level": level,
        "categories": categories,
        "description": description,
        "status": status,
        "origin": origin,
        "activation_condition": activation_condition,
        "activation_decision_date": activation_decision_date,
        "owner": owner,
        "current_score_type": current_score_type,
        "probability": probability,
        "impact": impact,
        "exposure": exposure,
        "subtype": subtype or "generic",
        "last_review_date": last_review_date,
        "next_review_date": next_review_date
    }
    # Merge extension field values into params
    params.update(ext_items)
    
    result = conn.execute_query(query, params)
    return result[0]["id"] if result else None


# =============================================================================
# READ OPERATIONS
# =============================================================================

def get_all_risks(
    conn: Neo4jConnection,
    level_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    origin_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all risks with optional filters.
    
    Args:
        conn: Database connection
        level_filter: Filter by level
        category_filter: Filter by category
        status_filter: Filter by status
        origin_filter: Filter by origin
    
    Returns:
        List of risk dictionaries
    """
    conditions = []
    params = {}
    
    if level_filter:
        conditions.append("r.level = $level")
        params["level"] = level_filter
    
    if category_filter:
        conditions.append("$category IN r.categories")
        params["category"] = category_filter
    
    if status_filter:
        conditions.append("r.status = $status")
        params["status"] = status_filter
    
    if origin_filter:
        conditions.append("r.origin = $origin")
        params["origin"] = origin_filter
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
    MATCH (r:Risk)
    {where_clause}
    OPTIONAL MATCH path = shortestPath((r)-[:INFLUENCES*0..10]->(b:Risk))
    WHERE EXISTS {{ (b)-[:IMPACTS_TPO]->(:TPO) }}
    WITH r, min(length(path)) as inf_dist
    WITH r, CASE WHEN inf_dist IS NULL THEN -1 ELSE inf_dist + 1 END as computed_distance
    RETURN r.id as id, r.name as name, r.level as level,
           r.categories as categories, r.description as description,
           r.status as status, r.origin as origin,
           r.activation_condition as activation_condition,
           r.activation_decision_date as activation_decision_date,
           r.owner as owner, r.probability as probability,
           r.impact as impact, r.exposure as exposure,
           r.current_score_type as current_score_type,
           properties(r) as all_props,
           computed_distance,
           CASE WHEN computed_distance = -1 THEN true ELSE false END as is_orphan
    ORDER BY r.exposure DESC
    """
    
    results = conn.execute_query(query, params)
    # Post-process: extract subtype and ext_* keys from all_props into each result
    processed = []
    for row in results:
        row_dict = dict(row)
        all_props = row_dict.pop("all_props", {})
        if all_props:
            # Extract subtype from all_props (avoids Neo4j warning for missing property)
            if "subtype" in all_props:
                row_dict["subtype"] = all_props["subtype"]
            for k, v in all_props.items():
                if k.startswith("ext_") and k not in row_dict:
                    row_dict[k] = v
        # Ensure subtype key always exists
        row_dict.setdefault("subtype", None)
        processed.append(row_dict)
    return processed


def get_risk_by_id(conn: Neo4jConnection, risk_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a risk by its ID.
    
    Args:
        conn: Database connection
        risk_id: Risk UUID
    
    Returns:
        Risk dictionary or None if not found
    """
    query = """
    MATCH (r:Risk {id: $id})
    OPTIONAL MATCH path = shortestPath((r)-[:INFLUENCES*0..10]->(b:Risk))
    WHERE EXISTS { (b)-[:IMPACTS_TPO]->(:TPO) }
    WITH r, min(length(path)) as inf_dist
    WITH r, CASE WHEN inf_dist IS NULL THEN -1 ELSE inf_dist + 1 END as computed_distance
    RETURN r.id as id, r.name as name, r.level as level,
           r.categories as categories, r.description as description,
           r.status as status, r.origin as origin,
           r.activation_condition as activation_condition,
           r.activation_decision_date as activation_decision_date,
           r.owner as owner, r.probability as probability,
           r.impact as impact, r.exposure as exposure,
           properties(r) as all_props,
           computed_distance,
           CASE WHEN computed_distance = -1 THEN true ELSE false END as is_orphan
    """
    
    result = conn.execute_query(query, {"id": risk_id})
    if not result:
        return None
    # Post-process: extract subtype and ext_* keys from all_props
    row_dict = dict(result[0])
    all_props = row_dict.pop("all_props", {})
    if all_props:
        if "subtype" in all_props:
            row_dict["subtype"] = all_props["subtype"]
        for k, v in all_props.items():
            if k.startswith("ext_") and k not in row_dict:
                row_dict[k] = v
    row_dict.setdefault("subtype", None)
    return row_dict


def get_risk_by_name(conn: Neo4jConnection, name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a risk by its name.
    
    Args:
        conn: Database connection
        name: Risk name
    
    Returns:
        Risk dictionary or None if not found
    """
    query = """
    MATCH (r:Risk {name: $name})
    OPTIONAL MATCH path = shortestPath((r)-[:INFLUENCES*0..10]->(b:Risk))
    WHERE EXISTS { (b)-[:IMPACTS_TPO]->(:TPO) }
    WITH r, min(length(path)) as inf_dist
    WITH r, CASE WHEN inf_dist IS NULL THEN -1 ELSE inf_dist + 1 END as computed_distance
    RETURN r.id as id, r.name as name, r.level as level,
           r.categories as categories, r.description as description,
           r.status as status, r.origin as origin,
           r.owner as owner, r.probability as probability,
           r.impact as impact, r.exposure as exposure,
           computed_distance,
           CASE WHEN computed_distance = -1 THEN true ELSE false END as is_orphan
    """
    
    result = conn.execute_query(query, {"name": name})
    return result[0] if result else None


def get_risks_by_level(conn: Neo4jConnection, level: str) -> List[Dict[str, Any]]:
    """
    Retrieve all risks of a specific level.
    
    Args:
        conn: Database connection
        level: "Business" or "Operational"
    
    Returns:
        List of risk dictionaries
    """
    return get_all_risks(conn, level_filter=level)


def get_risks_with_filters(
    conn: Neo4jConnection,
    levels: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    origins: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve risks with multiple filter lists (for visualization).
    
    Args:
        conn: Database connection
        levels: List of levels to include (None = all, [] = none)
        categories: List of categories to include
        statuses: List of statuses to include
        origins: List of origins to include
    
    Returns:
        List of risk dictionaries
    """
    # Empty list means "show nothing" - return early
    if levels is not None and len(levels) == 0:
        return []
    
    conditions = []
    params = {}
    
    if levels and len(levels) > 0:
        conditions.append("r.level IN $levels")
        params["levels"] = levels
    
    if categories and len(categories) > 0:
        conditions.append("ANY(cat IN r.categories WHERE cat IN $categories)")
        params["categories"] = categories
    
    if statuses and len(statuses) > 0:
        conditions.append("r.status IN $statuses")
        params["statuses"] = statuses
    
    if origins and len(origins) > 0:
        conditions.append("(r.origin IN $origins OR r.origin IS NULL)")
        params["origins"] = origins
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
    MATCH (r:Risk)
    {where_clause}
    OPTIONAL MATCH path = shortestPath((r)-[:INFLUENCES*0..10]->(b:Risk))
    WHERE EXISTS {{ (b)-[:IMPACTS_TPO]->(:TPO) }}
    WITH r, min(length(path)) as inf_dist
    WITH r, CASE WHEN inf_dist IS NULL THEN -1 ELSE inf_dist + 1 END as computed_distance
    RETURN r.id as id, r.name as name, r.level as level,
           r.categories as categories, r.status as status,
           r.origin as origin, r.exposure as exposure, r.owner as owner,
           'Risk' as node_type,
           properties(r) as all_props,
           computed_distance,
           CASE WHEN computed_distance = -1 THEN true ELSE false END as is_orphan
    ORDER BY r.exposure DESC
    """
    
    results = conn.execute_query(query, params)
    # Post-process: extract subtype from all_props (avoids Neo4j warning)
    processed = []
    for row in results:
        row_dict = dict(row)
        all_props = row_dict.pop("all_props", {})
        if all_props and "subtype" in all_props:
            row_dict["subtype"] = all_props["subtype"]
        row_dict.setdefault("subtype", None)
        processed.append(row_dict)
    return processed


# =============================================================================
# UPDATE OPERATIONS
# =============================================================================

def update_risk(
    conn: Neo4jConnection,
    risk_id: str,
    name: str,
    level: str,
    categories: List[str],
    description: str,
    status: str,
    origin: str = "New",
    owner: str = "",
    probability: Optional[float] = None,
    impact: Optional[float] = None,
    activation_condition: Optional[str] = None,
    activation_decision_date: Optional[str] = None,
    subtype: Optional[str] = None,
    ext_fields: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Update an existing risk.
    
    Args:
        conn: Database connection
        risk_id: Risk UUID to update
        name: Updated name
        level: Updated level
        categories: Updated categories
        description: Updated description
        status: Updated status
        origin: Updated origin
        owner: Updated owner
        probability: Updated probability
        impact: Updated impact
        activation_condition: Updated activation condition
        activation_decision_date: Updated decision date
        subtype: Risk subtype ID
        ext_fields: Extension field dict with ext_ prefixed keys (None values = clear)
    
    Returns:
        True if successful, False otherwise
    """
    exposure = (probability * impact) if (probability and impact) else None
    
    # Build extension field SET and REMOVE clauses
    ext_set_parts = []
    ext_remove_parts = []
    ext_params = {}
    if ext_fields is not None:
        for k, v in ext_fields.items():
            if not k.startswith("ext_"):
                continue
            if v is not None:
                ext_params[k] = v
                ext_set_parts.append(f"r.{k} = ${k}")
            else:
                ext_remove_parts.append(f"r.{k}")
    
    ext_set_clause = (", " + ", ".join(ext_set_parts)) if ext_set_parts else ""
    ext_remove_clause = ("REMOVE " + ", ".join(ext_remove_parts)) if ext_remove_parts else ""
    
    query = f"""
    MATCH (r:Risk {{id: $id}})
    SET r.name = $name,
        r.level = $level,
        r.categories = $categories,
        r.description = $description,
        r.status = $status,
        r.origin = $origin,
        r.activation_condition = $activation_condition,
        r.activation_decision_date = $activation_decision_date,
        r.owner = $owner,
        r.probability = $probability,
        r.impact = $impact,
        r.exposure = $exposure,
        r.subtype = $subtype,
        r.updated_at = datetime(){ext_set_clause}
    {ext_remove_clause}
    RETURN r.id
    """
    
    params = {
        "id": risk_id,
        "name": name,
        "level": level,
        "categories": categories,
        "description": description,
        "status": status,
        "origin": origin,
        "activation_condition": activation_condition,
        "activation_decision_date": activation_decision_date,
        "owner": owner,
        "probability": probability,
        "impact": impact,
        "exposure": exposure,
        "subtype": subtype or "generic",
    }
    params.update(ext_params)
    
    result = conn.execute_query(query, params)
    return len(result) > 0


# =============================================================================
# DELETE OPERATIONS
# =============================================================================

def delete_risk(conn: Neo4jConnection, risk_id: str) -> bool:
    """
    Delete a risk and all its relationships.
    
    Args:
        conn: Database connection
        risk_id: Risk UUID to delete
    
    Returns:
        True if successful
    """
    query = """
    MATCH (r:Risk {id: $id})
    DETACH DELETE r
    """
    
    conn.execute_query(query, {"id": risk_id})
    return True


# =============================================================================
# STATISTICS
# =============================================================================

def get_risk_count(conn: Neo4jConnection) -> int:
    """Get total number of risks."""
    query = "MATCH (r:Risk) RETURN count(r) as count"
    result = conn.execute_query(query)
    return result[0]["count"] if result else 0


def get_risk_count_by_level(conn: Neo4jConnection, level: str) -> int:
    """Get number of risks by level."""
    query = "MATCH (r:Risk {level: $level}) RETURN count(r) as count"
    result = conn.execute_query(query, {"level": level})
    return result[0]["count"] if result else 0


def get_risk_count_by_status(conn: Neo4jConnection, status: str) -> int:
    """Get number of risks by status."""
    query = "MATCH (r:Risk {status: $status}) RETURN count(r) as count"
    result = conn.execute_query(query, {"status": status})
    return result[0]["count"] if result else 0


def get_risk_count_by_origin(conn: Neo4jConnection, origin: str) -> int:
    """Get number of risks by origin."""
    query = "MATCH (r:Risk {origin: $origin}) RETURN count(r) as count"
    result = conn.execute_query(query, {"origin": origin})
    return result[0]["count"] if result else 0


def get_average_exposure(conn: Neo4jConnection) -> float:
    """Get average risk exposure."""
    query = """
    MATCH (r:Risk) 
    WHERE r.exposure IS NOT NULL 
    RETURN avg(r.exposure) as avg
    """
    result = conn.execute_query(query)
    return round(result[0]["avg"] or 0, 2) if result else 0


def get_risk_count_by_category(conn: Neo4jConnection) -> Dict[str, int]:
    """Get risk count by category."""
    query = """
    MATCH (r:Risk)
    UNWIND r.categories as category
    RETURN category, count(r) as count
    ORDER BY count DESC
    """
    result = conn.execute_query(query)
    return {r["category"]: r["count"] for r in result}
