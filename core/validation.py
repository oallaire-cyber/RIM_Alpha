"""
Dynamic Pydantic model generation and validation for schema entities.

Generates Pydantic models at runtime based on EntityTypeDefinition from the schema.
"""

from typing import Any, Dict, List, Optional, Type
from datetime import date, datetime
from pydantic import BaseModel, create_model, Field, ValidationError

from core.attribute import AttributeType, AttributeDefinition
import core.entity as entity_module


def get_pydantic_type(attr_type: AttributeType) -> Type:
    """Map AttributeType to Python/Pydantic types."""
    if attr_type == AttributeType.STRING:
        return str
    elif attr_type == AttributeType.INT:
        return int
    elif attr_type == AttributeType.FLOAT:
        return float
    elif attr_type == AttributeType.BOOL:
        return bool
    elif attr_type == AttributeType.DATE:
        return date
    elif attr_type == AttributeType.DATETIME:
        return datetime
    elif attr_type == AttributeType.ENUM:
        return str  # Represented as string, can be validated against choices conceptually
    elif attr_type == AttributeType.LIST_STRING:
        return List[str]
    return Any


def create_entity_model(entity_type: "entity_module.EntityTypeDefinition") -> Type[BaseModel]:
    """
    Dynamically creates a Pydantic model for an EntityTypeDefinition.
    
    Args:
        entity_type: The schema-driven entity definition.
        
    Returns:
        A Pydantic BaseModel class for validation.
    """
    fields = {}
    for attr in entity_type.attributes:
        py_type = get_pydantic_type(attr.type)
        
        # Determine if it's optional
        if not attr.required:
            py_type = Optional[py_type]
            
        field_kwargs = {}
        
        # Set default
        if attr.default is not None:
            field_kwargs["default"] = attr.default
        elif not attr.required:
            field_kwargs["default"] = None
        
        # Add description
        if attr.description:
            field_kwargs["description"] = attr.description
            
        # Add numeric bounds
        if attr.type in (AttributeType.INT, AttributeType.FLOAT):
            if attr.min_value is not None:
                field_kwargs["ge"] = attr.min_value
            if attr.max_value is not None:
                field_kwargs["le"] = attr.max_value
                
        # Validate choices for ENUM
        # Note: In Pydantic v2, we can't easily add dynamic enums inline without 
        # creating actual Enum classes, so we rely on the custom AttributeValidator 
        # for strict enum checking or we could add a root validator. For now, 
        # we let Pydantic handle type/bound validation.
        
        fields[attr.name] = (py_type, Field(**field_kwargs))
        
    model_name = f"{entity_type.id.capitalize()}Model"
    return create_model(model_name, **fields)


def validate_entity_data_pydantic(entity_type: "entity_module.EntityTypeDefinition", data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validates data using the dynamically generated Pydantic model.
    Checks types, bounds, and required fields according to schema.yaml properties.
    
    Args:
        entity_type: The schema-driven entity definition.
        data: The dictionary of properties to validate.
        
    Returns:
        Tuple of (is_valid, list of error messages).
    """
    ModelClass = create_entity_model(entity_type)
    try:
        ModelClass(**data)
        return True, []
    except ValidationError as e:
        errors = []
        for err in e.errors():
            loc = ".".join([str(x) for x in err["loc"]])
            msg = err["msg"]
            errors.append(f"'{loc}': {msg}")
        return False, errors
    except Exception as e:
        return False, [str(e)]
