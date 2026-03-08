"""
Generic Relationship CRUD operations with constraint enforcement.

Works with any relationship type defined in the schema registry,
providing type-agnostic CRUD while enforcing from_entity/to_entity constraints.
"""

from typing import Any, Dict, List, Optional
from neo4j import Driver
from core import RelationshipTypeDefinition, EntityTypeDefinition, get_registry


class ConstraintViolationError(Exception):
    """Raised when relationship violates from/to entity constraints."""
    pass


class RelationshipValidationError(Exception):
    """Raised when relationship data fails validation."""
    pass


def create_relationship(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    source_id: str,
    target_id: str,
    source_entity_type: EntityTypeDefinition,
    target_entity_type: EntityTypeDefinition,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a relationship between two nodes.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition from registry
        source_id: ID of source entity
        target_id: ID of target entity
        source_entity_type: Entity type of source
        target_entity_type: Entity type of target
        data: Relationship properties
        
    Returns:
        Created relationship with ID
        
    Raises:
        ConstraintViolationError: If entity types not allowed
        RelationshipValidationError: If data fails validation
    """
    data = data or {}
    
    # Enforce constraints
    if not rel_type.can_connect(source_entity_type.id, target_entity_type.id):
        raise ConstraintViolationError(
            f"Relationship '{rel_type.id}' cannot connect "
            f"'{source_entity_type.id}' to '{target_entity_type.id}'. "
            f"Expected from: {rel_type.from_entity_types}, to: {rel_type.to_entity_types}"
        )
    
    # Validate data
    is_valid, errors = rel_type.validate(data)
    if not is_valid:
        raise RelationshipValidationError(f"Validation failed: {'; '.join(errors)}")
    
    # Generate relationship ID
    import uuid
    rel_id = data.get("id", str(uuid.uuid4()))
    data["id"] = rel_id
    
    # Build query
    source_label = source_entity_type.neo4j_label
    target_label = target_entity_type.neo4j_label
    neo4j_type = rel_type.neo4j_type
    
    # Build property clause
    if data:
        props = ", ".join([f"{k}: ${k}" for k in data.keys()])
        props_clause = f"{{{props}}}"
    else:
        props_clause = ""
    
    query = f"""
    MATCH (a:{source_label} {{id: $source_id}})
    MATCH (b:{target_label} {{id: $target_id}})
    CREATE (a)-[r:{neo4j_type} {props_clause}]->(b)
    RETURN r, elementId(r) as relId
    """
    
    params = {"source_id": source_id, "target_id": target_id, **data}
    
    with driver.session() as session:
        result = session.run(query, params)
        record = result.single()
        if record:
            rel = dict(record["r"])
            rel["_element_id"] = record["relId"]
            rel["source_id"] = source_id
            rel["target_id"] = target_id
            return rel
    
    return data


def get_all_relationships(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Get all relationships of a type.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        filters: Optional filters on relationship properties
        
    Returns:
        List of relationship dictionaries with source/target info
    """
    neo4j_type = rel_type.neo4j_type
    
    # Fast existence guard — avoid Neo4j 01N51 warning for schema-defined types
    # that have not yet been persisted to the database.
    with driver.session() as session:
        result = session.run(
            "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types"
        )
        record = result.single()
        existing_types = record["types"] if record else []
    
    if neo4j_type not in existing_types:
        return []

    where_clauses = []
    params = {}
    
    if filters:
        for key, value in filters.items():
            if value is None:
                continue
            param_name = f"filter_{key}"
            if isinstance(value, list):
                if value:
                    where_clauses.append(f"r.{key} IN ${param_name}")
                    params[param_name] = value
            else:
                where_clauses.append(f"r.{key} = ${param_name}")
                params[param_name] = value
    
    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)
    
    query = f"""
    MATCH (a)-[r:{neo4j_type}]->(b)
    {where_str}
    RETURN r, a, b, elementId(r) as relId, a.id as source_id, b.id as target_id
    """
    
    relationships = []
    with driver.session() as session:
        result = session.run(query, params)
        for record in result:
            rel = dict(record["r"])
            rel["_element_id"] = record["relId"]
            rel["source_id"] = record["source_id"]
            rel["target_id"] = record["target_id"]
            rel["_source"] = dict(record["a"])
            rel["_target"] = dict(record["b"])
            relationships.append(rel)
    
    return relationships



def get_relationship_by_id(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    rel_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get a single relationship by ID.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        rel_id: Relationship ID
        
    Returns:
        Relationship dictionary or None
    """
    neo4j_type = rel_type.neo4j_type
    
    query = f"""
    MATCH (a)-[r:{neo4j_type} {{id: $id}}]->(b)
    RETURN r, a, b, elementId(r) as relId, a.id as source_id, b.id as target_id
    """
    
    with driver.session() as session:
        result = session.run(query, {"id": rel_id})
        record = result.single()
        if record:
            rel = dict(record["r"])
            rel["_element_id"] = record["relId"]
            rel["source_id"] = record["source_id"]
            rel["target_id"] = record["target_id"]
            rel["_source"] = dict(record["a"])
            rel["_target"] = dict(record["b"])
            return rel
    
    return None


def get_relationships_from_entity(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    entity_id: str
) -> List[Dict[str, Any]]:
    """
    Get relationships originating from an entity.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        entity_id: Source entity ID
        
    Returns:
        List of outgoing relationships
    """
    neo4j_type = rel_type.neo4j_type
    
    query = f"""
    MATCH (a {{id: $entity_id}})-[r:{neo4j_type}]->(b)
    RETURN r, a, b, elementId(r) as relId, a.id as source_id, b.id as target_id
    """
    
    relationships = []
    with driver.session() as session:
        result = session.run(query, {"entity_id": entity_id})
        for record in result:
            rel = dict(record["r"])
            rel["_element_id"] = record["relId"]
            rel["source_id"] = record["source_id"]
            rel["target_id"] = record["target_id"]
            rel["_source"] = dict(record["a"])
            rel["_target"] = dict(record["b"])
            relationships.append(rel)
    
    return relationships


def get_relationships_to_entity(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    entity_id: str
) -> List[Dict[str, Any]]:
    """
    Get relationships pointing to an entity.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        entity_id: Target entity ID
        
    Returns:
        List of incoming relationships
    """
    neo4j_type = rel_type.neo4j_type
    
    query = f"""
    MATCH (a)-[r:{neo4j_type}]->(b {{id: $entity_id}})
    RETURN r, a, b, elementId(r) as relId, a.id as source_id, b.id as target_id
    """
    
    relationships = []
    with driver.session() as session:
        result = session.run(query, {"entity_id": entity_id})
        for record in result:
            rel = dict(record["r"])
            rel["_element_id"] = record["relId"]
            rel["source_id"] = record["source_id"]
            rel["target_id"] = record["target_id"]
            rel["_source"] = dict(record["a"])
            rel["_target"] = dict(record["b"])
            relationships.append(rel)
    
    return relationships


def update_relationship(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    rel_id: str,
    data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update a relationship's properties.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        rel_id: Relationship ID
        data: Updated properties
        
    Returns:
        Updated relationship or None if not found
    """
    # Validate
    is_valid, errors = rel_type.validate(data)
    if not is_valid:
        raise RelationshipValidationError(f"Validation failed: {'; '.join(errors)}")
    
    neo4j_type = rel_type.neo4j_type
    
    # Build SET clause (exclude 'id' from updates)
    set_parts = [f"r.{k} = ${k}" for k in data.keys() if k != "id"]
    if not set_parts:
        return get_relationship_by_id(driver, rel_type, rel_id)
    
    set_clause = ", ".join(set_parts)
    params = {"id": rel_id, **data}
    
    query = f"""
    MATCH (a)-[r:{neo4j_type} {{id: $id}}]->(b)
    SET {set_clause}
    RETURN r, a, b, elementId(r) as relId, a.id as source_id, b.id as target_id
    """
    
    with driver.session() as session:
        result = session.run(query, params)
        record = result.single()
        if record:
            rel = dict(record["r"])
            rel["_element_id"] = record["relId"]
            rel["source_id"] = record["source_id"]
            rel["target_id"] = record["target_id"]
            return rel
    
    return None


def delete_relationship(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    rel_id: str
) -> bool:
    """
    Delete a relationship by ID.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        rel_id: Relationship ID
        
    Returns:
        True if deleted, False if not found
    """
    neo4j_type = rel_type.neo4j_type
    
    query = f"""
    MATCH ()-[r:{neo4j_type} {{id: $id}}]->()
    DELETE r
    RETURN count(r) as deleted
    """
    
    with driver.session() as session:
        result = session.run(query, {"id": rel_id})
        record = result.single()
        return record and record["deleted"] > 0


def count_relationships(
    driver: Driver,
    rel_type: RelationshipTypeDefinition,
    filters: Optional[Dict[str, Any]] = None
) -> int:
    """
    Count relationships of a type.
    
    Args:
        driver: Neo4j driver
        rel_type: Relationship type definition
        filters: Optional filters
        
    Returns:
        Count of matching relationships
    """
    neo4j_type = rel_type.neo4j_type
    
    where_clauses = []
    params = {}
    
    if filters:
        for key, value in filters.items():
            if value is None:
                continue
            param_name = f"filter_{key}"
            if isinstance(value, list):
                if value:
                    where_clauses.append(f"r.{key} IN ${param_name}")
                    params[param_name] = value
            else:
                where_clauses.append(f"r.{key} = ${param_name}")
                params[param_name] = value
    
    where_str = ""
    if where_clauses:
        where_str = "WHERE " + " AND ".join(where_clauses)
    
    query = f"""
    MATCH ()-[r:{neo4j_type}]->()
    {where_str}
    RETURN count(r) as cnt
    """
    
    with driver.session() as session:
        result = session.run(query, params)
        record = result.single()
        return record["cnt"] if record else 0


# =============================================================================
# INFLUENCE-SPECIFIC HELPERS
# =============================================================================

def get_influence_type_for_risk_levels(
    source_level: str,
    target_level: str
) -> Optional[str]:
    """
    Determine the influence type based on source and target risk levels.
    Uses the schema registry's influence type constraints.
    
    Args:
        source_level: Level of source risk (e.g., "Operational")
        target_level: Level of target risk (e.g., "Strategic")
        
    Returns:
        Influence type ID, or None if ambiguous/no match
    """
    registry = get_registry()
    influence_type = registry.get_influence_type()
    return influence_type.get_influence_type_for_levels(source_level, target_level)


def get_valid_influence_types(
    source_level: str,
    target_level: str
) -> List[str]:
    """
    Get all valid influence types for a level combination.
    
    Args:
        source_level: Level of source risk
        target_level: Level of target risk
        
    Returns:
        List of valid influence type IDs
    """
    registry = get_registry()
    influence_type = registry.get_influence_type()
    return influence_type.get_valid_influence_types_for_levels(source_level, target_level)
