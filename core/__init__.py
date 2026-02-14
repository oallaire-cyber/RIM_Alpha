"""
Core kernel abstractions for RIM schema-driven architecture.

This module provides the foundational classes for the kernel + extensible
schema-driven architecture:

- attribute: Attribute definition and validation
- entity: Generic entity type definitions (Risk is kernel, others extensible)
- relationship: Generic relationship type definitions (Influences/Mitigates kernel)
- schema_registry: Central registry for schema definitions
- migration: Schema migration utilities
"""

from core.attribute import AttributeType, AttributeDefinition, AttributeValidator
from core.entity import EntityTypeDefinition, Entity
from core.relationship import (
    RelationshipTypeDefinition,
    InfluenceTypeConstraint,
)
from core.schema_registry import (
    SchemaRegistry,
    SchemaValidationError,
    get_registry,
    load_schema,
)

__all__ = [
    # Attributes
    "AttributeType",
    "AttributeDefinition", 
    "AttributeValidator",
    # Entities
    "EntityTypeDefinition",
    "Entity",
    # Relationships
    "RelationshipTypeDefinition",
    "InfluenceTypeConstraint",
    # Registry
    "SchemaRegistry",
    "SchemaValidationError",
    "get_registry",
    "load_schema",
]
