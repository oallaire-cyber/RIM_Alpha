"""
Risk database queries.

Contains all Cypher queries for Risk node CRUD operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database.connection import Neo4jConnection

# Statuses excluded from active exposure analysis.
# Mirrors models.enums.LIFECYCLE_INACTIVE_STATUSES (as strings to avoid cross-layer import).
_INACTIVE_STATUSES = ["Accepted", "Watching", "Suppressed", "Closed", "Archived"]


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
    severity: Optional[float] = None,
    trigger_condition: Optional[str] = None,
    acceptance_date: Optional[str] = None,
    acceptance_owner: Optional[str] = None,
    archive_date: Optional[str] = None,
    subtype: Optional[str] = None,
    ext_fields: Optional[Dict[str, Any]] = None,
    is_template: bool = False,
    # Legacy parameter aliases (backward compat for callers not yet updated)
    activation_condition: Optional[str] = None,
    activation_decision_date: Optional[str] = None,
) -> Optional[str]:
    """
    Create a new Risk node.

    Args:
        conn: Database connection
        name: Risk name
        level: "Business" or "Operational"
        categories: List of category strings
        description: Risk description
        status: Active, Contingent, Archived, Accepted, Watching, Suppressed, or Closed
        origin: "New" or "Legacy"
        owner: Risk owner
        probability: Probability score (0-10)
        severity: Severity score (0-10)
        trigger_condition: Condition string for re-activating Watching/Suppressed risks
        acceptance_date: ISO date when risk was formally accepted
        acceptance_owner: Person who formally accepted the risk
        archive_date: ISO date when risk was archived
        subtype: Risk subtype ID (e.g., "generic", "cyber_entry_point")
        ext_fields: Extension field dict with ext_ prefixed keys
        is_template: If True, marks this as a GenericRisk template (excluded from exposure engine)
    
    Returns:
        Created risk ID or None if failed
    """
    # Legacy alias resolution (callers passing old keyword names)
    trigger_condition = trigger_condition or activation_condition
    acceptance_date = acceptance_date or activation_decision_date

    # Calculate exposure
    exposure = None
    current_score_type = "None"
    if probability is not None and severity is not None:
        exposure = probability * severity
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
        trigger_condition: $trigger_condition,
        acceptance_date: $acceptance_date,
        acceptance_owner: $acceptance_owner,
        archive_date: $archive_date,
        categories: $categories,
        owner: $owner,
        current_score_type: $current_score_type,
        probability: $probability,
        severity: $severity,
        exposure: $exposure,
        subtype: $subtype,
        is_template: $is_template,
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
        "trigger_condition": trigger_condition,
        "acceptance_date": acceptance_date,
        "acceptance_owner": acceptance_owner,
        "archive_date": archive_date,
        "owner": owner,
        "current_score_type": current_score_type,
        "probability": probability,
        "severity": severity,
        "exposure": exposure,
        "subtype": subtype or "generic",
        "is_template": is_template,
        "last_review_date": last_review_date,
        "next_review_date": next_review_date,
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
    origin_filter: Optional[str] = None,
    exclude_inactive: bool = True,
    exclude_templates: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieve all risks with optional filters.

    Args:
        conn: Database connection
        level_filter: Filter by level
        category_filter: Filter by category
        status_filter: Filter by status
        origin_filter: Filter by origin
        exclude_inactive: When True (default), excludes Accepted/Watching/Suppressed/Closed/Archived
                          risks from results. Pass False for CRUD forms or lifecycle review.
        exclude_templates: When True (default), excludes GenericRisk templates from results.
                           Pass False for CRUD template management or template library UI.

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

    if exclude_inactive:
        conditions.append("NOT r.status IN $inactive_statuses")
        params["inactive_statuses"] = _INACTIVE_STATUSES

    if exclude_templates:
        conditions.append("(r.is_template IS NULL OR r.is_template = false)")

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
           COALESCE(r.trigger_condition, r.activation_condition) as trigger_condition,
           COALESCE(r.acceptance_date, r.activation_decision_date) as acceptance_date,
           r.acceptance_owner as acceptance_owner,
           r.archive_date as archive_date,
           r.owner as owner, r.probability as probability,
           r.severity as severity, r.exposure as exposure,
           r.current_score_type as current_score_type,
           COALESCE(r.is_template, false) as is_template,
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
           COALESCE(r.trigger_condition, r.activation_condition) as trigger_condition,
           COALESCE(r.acceptance_date, r.activation_decision_date) as acceptance_date,
           r.acceptance_owner as acceptance_owner,
           r.archive_date as archive_date,
           r.owner as owner, r.probability as probability,
           r.severity as severity, r.exposure as exposure,
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
           r.severity as severity, r.exposure as exposure,
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
    origins: Optional[List[str]] = None,
    exclude_inactive: bool = True,
    exclude_templates: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieve risks with multiple filter lists (for visualization).

    Args:
        conn: Database connection
        levels: List of levels to include (None = all, [] = none)
        categories: List of categories to include
        statuses: List of statuses to include
        origins: List of origins to include
        exclude_inactive: When True (default), excludes Accepted/Watching/Suppressed/Closed/Archived
                          risks from results. Pass False for canvas display or lifecycle review.
        exclude_templates: When True (default), excludes GenericRisk templates from canvas display.

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

    if exclude_inactive:
        conditions.append("NOT r.status IN $inactive_statuses")
        params["inactive_statuses"] = _INACTIVE_STATUSES

    if exclude_templates:
        conditions.append("(r.is_template IS NULL OR r.is_template = false)")

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
    severity: Optional[float] = None,
    trigger_condition: Optional[str] = None,
    acceptance_date: Optional[str] = None,
    acceptance_owner: Optional[str] = None,
    archive_date: Optional[str] = None,
    subtype: Optional[str] = None,
    ext_fields: Optional[Dict[str, Any]] = None,
    is_template: Optional[bool] = None,
    # Legacy parameter aliases (backward compat for callers not yet updated)
    activation_condition: Optional[str] = None,
    activation_decision_date: Optional[str] = None,
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
        severity: Updated severity
        trigger_condition: Updated trigger condition
        acceptance_date: Updated acceptance date
        acceptance_owner: Updated acceptance owner
        archive_date: Updated archive date
        subtype: Risk subtype ID
        ext_fields: Extension field dict with ext_ prefixed keys (None values = clear)
        is_template: If provided, updates the template flag

    Returns:
        True if successful, False otherwise
    """
    # Legacy alias resolution
    trigger_condition = trigger_condition or activation_condition
    acceptance_date = acceptance_date or activation_decision_date

    exposure = (probability * severity) if (probability and severity) else None

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
        r.trigger_condition = $trigger_condition,
        r.acceptance_date = $acceptance_date,
        r.acceptance_owner = $acceptance_owner,
        r.archive_date = $archive_date,
        r.owner = $owner,
        r.probability = $probability,
        r.severity = $severity,
        r.exposure = $exposure,
        r.subtype = $subtype,
        r.is_template = COALESCE($is_template_val, r.is_template, false),
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
        "trigger_condition": trigger_condition,
        "acceptance_date": acceptance_date,
        "acceptance_owner": acceptance_owner,
        "archive_date": archive_date,
        "owner": owner,
        "probability": probability,
        "severity": severity,
        "exposure": exposure,
        "subtype": subtype or "generic",
        # COALESCE: if caller passes None, preserve existing value (or default false)
        "is_template_val": is_template,
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


# =============================================================================
# LIFECYCLE QUERIES
# =============================================================================

def get_archive_candidates(
    conn: Neo4jConnection,
    retention_days: int = 180,
    scope_node_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Find risks eligible for archiving.

    Candidates are risks in 'Accepted' or 'Closed' status whose acceptance_date
    is older than retention_days and have no linked mitigations in
    'Proposed' or 'In Progress' status.

    Args:
        conn: Database connection
        retention_days: Days after acceptance before a risk becomes a candidate
        scope_node_ids: If provided, restrict to risks in this scope

    Returns:
        List of risk dicts for risks that should be reviewed for archiving
    """
    conditions = [
        "r.status IN ['Accepted', 'Closed']",
        "r.acceptance_date IS NOT NULL",
        f"duration.inDays(date(r.acceptance_date), date()).days >= {retention_days}",
    ]
    params: Dict[str, Any] = {}

    if scope_node_ids is not None:
        conditions.append("r.id IN $scope_node_ids")
        params["scope_node_ids"] = scope_node_ids

    where_clause = "WHERE " + " AND ".join(conditions)

    # Use OPTIONAL MATCH + aggregation instead of EXISTS {} subquery
    # for compatibility with Neo4j 4.x and 5.x alike.
    query = f"""
    MATCH (r:Risk)
    {where_clause}
    OPTIONAL MATCH (m:Mitigation)-[:MITIGATES]->(r)
    WHERE m.status IN ['Proposed', 'In Progress']
    WITH r, COUNT(m) AS active_mitigations
    WHERE active_mitigations = 0
    RETURN r.id AS id, r.name AS name, r.status AS status,
           r.acceptance_date AS acceptance_date,
           r.acceptance_owner AS acceptance_owner,
           r.level AS level, r.exposure AS exposure,
           r.severity AS severity, r.probability AS probability
    ORDER BY r.acceptance_date ASC
    """

    result = conn.execute_query(query, params)
    return [dict(row) for row in result]


# =============================================================================
# TEMPLATE QUERIES (U14)
# =============================================================================

def get_all_templates(conn: Neo4jConnection) -> List[Dict[str, Any]]:
    """
    Retrieve all GenericRisk templates (is_template = true).

    Returns the same field shape as get_all_risks for consistency.
    """
    query = """
    MATCH (r:Risk)
    WHERE r.is_template = true
    RETURN r.id as id, r.name as name, r.level as level,
           r.categories as categories, r.description as description,
           r.status as status, r.origin as origin,
           r.owner as owner, r.probability as probability,
           r.severity as severity, r.exposure as exposure,
           r.current_score_type as current_score_type,
           COALESCE(r.is_template, false) as is_template,
           properties(r) as all_props
    ORDER BY r.name ASC
    """
    results = conn.execute_query(query)
    processed = []
    for row in results:
        row_dict = dict(row)
        all_props = row_dict.pop("all_props", {})
        if all_props:
            if "subtype" in all_props:
                row_dict["subtype"] = all_props["subtype"]
            for k, v in all_props.items():
                if k.startswith("ext_") and k not in row_dict:
                    row_dict[k] = v
        row_dict.setdefault("subtype", None)
        processed.append(row_dict)
    return processed


def create_instantiates_rel(
    conn: Neo4jConnection,
    template_id: str,
    instance_id: str,
) -> bool:
    """
    Create an INSTANTIATES relationship from a template risk to an instance risk.

    Args:
        conn: Database connection
        template_id: UUID of the GenericRisk template
        instance_id: UUID of the specific risk instance

    Returns:
        True if the relationship was created, False otherwise
    """
    query = """
    MATCH (t:Risk {id: $template_id}), (i:Risk {id: $instance_id})
    MERGE (t)-[:INSTANTIATES]->(i)
    RETURN t.id AS template_id
    """
    result = conn.execute_query(query, {"template_id": template_id, "instance_id": instance_id})
    return len(result) > 0


def get_instances_of_template(
    conn: Neo4jConnection,
    template_id: str,
) -> List[Dict[str, Any]]:
    """
    Return all specific risk instances linked from a template via INSTANTIATES.

    Args:
        conn: Database connection
        template_id: UUID of the GenericRisk template

    Returns:
        List of risk dicts for each instance
    """
    query = """
    MATCH (t:Risk {id: $template_id})-[:INSTANTIATES]->(i:Risk)
    RETURN i.id as id, i.name as name, i.level as level,
           i.status as status, i.probability as probability,
           i.severity as severity, i.exposure as exposure
    ORDER BY i.name ASC
    """
    result = conn.execute_query(query, {"template_id": template_id})
    return [dict(row) for row in result]


def get_template_of_instance(
    conn: Neo4jConnection,
    instance_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Return the GenericRisk template that this instance was instantiated from, if any.

    Args:
        conn: Database connection
        instance_id: UUID of the specific risk instance

    Returns:
        Template risk dict or None if the risk has no template parent
    """
    query = """
    MATCH (t:Risk)-[:INSTANTIATES]->(i:Risk {id: $instance_id})
    RETURN t.id as id, t.name as name, t.level as level,
           t.description as description, t.probability as probability,
           t.severity as severity, t.is_template as is_template
    LIMIT 1
    """
    result = conn.execute_query(query, {"instance_id": instance_id})
    return dict(result[0]) if result else None
