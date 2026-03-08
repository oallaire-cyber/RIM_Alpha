"""
Generic Entity CRUD operations - Schema-driven database queries.

Works with any entity type defined in the schema registry,
providing type-agnostic CRUD operations while respecting schema constraints.
"""

from typing import Any, Dict, List, Optional
from neo4j import Driver
from core import EntityTypeDefinition, get_registry


class EntityValidationError(Exception):
    """Raised when entity data fails validation."""
    pass


def create_entity(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create an entity in Neo4j.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition from registry
        data: Entity data (name, attributes, etc.)
        
    Returns:
        Created entity with ID
        
    Raises:
        EntityValidationError: If data fails validation
    """
    # Validate data
    is_valid, errors = entity_type.validate(data)
    if not is_valid:
        raise EntityValidationError(f"Validation failed: {'; '.join(errors)}")
    
    # Prepare data (convert types, apply defaults)
    prepared = entity_type.prepare_data(data)
    
    # Build query with node label
    label = entity_type.neo4j_label
    
    # Ensure 'id' is set
    if "id" not in prepared:
        import uuid
        prepared["id"] = str(uuid.uuid4())
    
    # Build property string dynamically
    props = ", ".join([f"{k}: ${k}" for k in prepared.keys()])
    
    query = f"""
    CREATE (n:{label} {{{props}}})
    RETURN n, elementId(n) as nodeId
    """
    
    with driver.session() as session:
        result = session.run(query, prepared)
        record = result.single()
        if record:
            node = dict(record["n"])
            node["_element_id"] = record["nodeId"]
            return node
    
    return prepared


def get_all_entities(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all entities of a type.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition
        filters: Optional filters (attribute_name -> value or list of values)
        
    Returns:
        List of entity dictionaries
    """
    label = entity_type.neo4j_label
    
    # Fast existence guard — avoids Neo4j warnings when querying a label
    # that exists in the schema but has no data in the database yet.
    with driver.session() as session:
        result = session.run(
            "CALL db.labels() YIELD label RETURN collect(label) AS labels"
        )
        record = result.single()
        existing_labels = record["labels"] if record else []
    
    if label not in existing_labels:
        return []

    where_clauses = []
    params = {}
    
    if filters:
        for key, value in filters.items():
            if value is None:
                continue
            if isinstance(value, list):
                # Filter by any of the values
                if value:  # Only add if list is non-empty
                    param_name = f"filter_{key}"
                    where_clauses.append(f"n.{key} IN ${param_name}")
                    params[param_name] = value
            else:
                param_name = f"filter_{key}"
                where_clauses.append(f"n.{key} = ${param_name}")
                params[param_name] = value
    
    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)
    
    query = f"""
    MATCH (n:{label})
    {where_str}
    RETURN n, elementId(n) as nodeId
    ORDER BY n.name
    """
    
    entities = []
    with driver.session() as session:
        result = session.run(query, params)
        for record in result:
            entity = dict(record["n"])
            entity["_element_id"] = record["nodeId"]
            entities.append(entity)
    
    return entities



def get_entity_by_id(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    entity_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get a single entity by its ID.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition
        entity_id: Entity ID
        
    Returns:
        Entity dictionary or None
    """
    label = entity_type.neo4j_label
    
    query = f"""
    MATCH (n:{label} {{id: $id}})
    RETURN n, elementId(n) as nodeId
    """
    
    with driver.session() as session:
        result = session.run(query, {"id": entity_id})
        record = result.single()
        if record:
            entity = dict(record["n"])
            entity["_element_id"] = record["nodeId"]
            return entity
    
    return None


def update_entity(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    entity_id: str,
    data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update an entity.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition
        entity_id: Entity ID
        data: Updated data
        
    Returns:
        Updated entity or None if not found
    """
    # Validate
    is_valid, errors = entity_type.validate(data)
    if not is_valid:
        raise EntityValidationError(f"Validation failed: {'; '.join(errors)}")
    
    # Prepare data
    prepared = entity_type.prepare_data(data)
    prepared["id"] = entity_id  # Keep same ID
    
    label = entity_type.neo4j_label
    
    # Build SET clause
    set_parts = [f"n.{k} = ${k}" for k in prepared.keys() if k != "id"]
    set_clause = ", ".join(set_parts)
    
    query = f"""
    MATCH (n:{label} {{id: $id}})
    SET {set_clause}
    RETURN n, elementId(n) as nodeId
    """
    
    with driver.session() as session:
        result = session.run(query, prepared)
        record = result.single()
        if record:
            entity = dict(record["n"])
            entity["_element_id"] = record["nodeId"]
            return entity
    
    return None


def delete_entity(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    entity_id: str,
    cascade: bool = True
) -> bool:
    """
    Delete an entity.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition
        entity_id: Entity ID
        cascade: If True, delete relationships too
        
    Returns:
        True if deleted, False if not found
    """
    label = entity_type.neo4j_label
    
    if cascade:
        query = f"""
        MATCH (n:{label} {{id: $id}})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
    else:
        query = f"""
        MATCH (n:{label} {{id: $id}})
        DELETE n
        RETURN count(n) as deleted
        """
    
    with driver.session() as session:
        result = session.run(query, {"id": entity_id})
        record = result.single()
        return record and record["deleted"] > 0


def count_entities(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    filters: Optional[Dict[str, Any]] = None
) -> int:
    """
    Count entities of a type.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition
        filters: Optional filters
        
    Returns:
        Count of matching entities
    """
    label = entity_type.neo4j_label
    
    where_clauses = []
    params = {}
    
    if filters:
        for key, value in filters.items():
            if value is None:
                continue
            param_name = f"filter_{key}"
            if isinstance(value, list):
                if value:
                    where_clauses.append(f"n.{key} IN ${param_name}")
                    params[param_name] = value
            else:
                where_clauses.append(f"n.{key} = ${param_name}")
                params[param_name] = value
    
    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)
    
    query = f"""
    MATCH (n:{label})
    {where_str}
    RETURN count(n) as cnt
    """
    
    with driver.session() as session:
        result = session.run(query, params)
        record = result.single()
        return record["cnt"] if record else 0


def search_entities(
    driver: Driver,
    entity_type: EntityTypeDefinition,
    search_term: str,
    search_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Search entities by text match.
    
    Args:
        driver: Neo4j driver
        entity_type: Entity type definition
        search_term: Search text
        search_fields: Fields to search (defaults to 'name' and 'description')
        
    Returns:
        List of matching entities
    """
    if not search_fields:
        search_fields = ["name", "description"]
    
    label = entity_type.neo4j_label
    
    # Build OR conditions for search
    search_conditions = [
        f"toLower(n.{field}) CONTAINS toLower($search_term)"
        for field in search_fields
    ]
    where_clause = " OR ".join(search_conditions)
    
    query = f"""
    MATCH (n:{label})
    WHERE {where_clause}
    RETURN n, elementId(n) as nodeId
    ORDER BY n.name
    """
    
    entities = []
    with driver.session() as session:
        result = session.run(query, {"search_term": search_term})
        for record in result:
            entity = dict(record["n"])
            entity["_element_id"] = record["nodeId"]
            entities.append(entity)
    
    return entities
