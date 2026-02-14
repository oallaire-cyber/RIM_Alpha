"""
Attribute definition and validation for schema-driven entities.

Provides type-safe attribute handling with:
- Multiple data types (string, int, float, bool, date, datetime, enum, list)
- Validation with range constraints and choices
- Conversion between formats
- Engine-required attribute flagging
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from enum import Enum


class AttributeType(str, Enum):
    """Supported attribute types."""
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    LIST_STRING = "list_string"


@dataclass
class AttributeDefinition:
    """
    Defines an attribute for an entity or relationship.
    Loaded from schema YAML.
    
    Attributes:
        name: Attribute identifier
        type: Data type for validation and conversion
        required: Whether the attribute must have a value
        default: Default value if none provided
        description: Human-readable description
        choices: Valid values for enum type
        min_value: Minimum for numeric types
        max_value: Maximum for numeric types
        engine_required: True if referenced by analysis formula
    """
    name: str
    type: AttributeType
    required: bool = False
    default: Any = None
    description: str = ""
    choices: List[str] = field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    engine_required: bool = False
    
    def __post_init__(self):
        """Convert string type to AttributeType enum if needed."""
        if isinstance(self.type, str):
            try:
                self.type = AttributeType(self.type.lower())
            except ValueError:
                self.type = AttributeType.STRING
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate value against definition.
        
        Args:
            value: The value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required
        if self.required and value is None:
            return False, f"'{self.name}' is required"
        
        if value is None:
            return True, None
        
        # Type-specific validation
        if self.type in (AttributeType.FLOAT, AttributeType.INT):
            try:
                num_val = float(value)
                if self.min_value is not None and num_val < self.min_value:
                    return False, f"'{self.name}' must be >= {self.min_value}"
                if self.max_value is not None and num_val > self.max_value:
                    return False, f"'{self.name}' must be <= {self.max_value}"
            except (TypeError, ValueError):
                return False, f"'{self.name}' must be a number"
        
        if self.type == AttributeType.ENUM and self.choices:
            if value not in self.choices:
                return False, f"'{self.name}' must be one of: {self.choices}"
        
        if self.type == AttributeType.BOOL:
            if not isinstance(value, bool) and value not in ('true', 'false', 'True', 'False', '1', '0', 1, 0):
                return False, f"'{self.name}' must be a boolean value"
        
        return True, None
    
    def convert(self, value: Any) -> Any:
        """
        Convert value to correct type.
        
        Args:
            value: The value to convert
            
        Returns:
            Converted value, or default if value is None
        """
        if value is None:
            return self.default
        
        converters = {
            AttributeType.STRING: str,
            AttributeType.INT: lambda v: int(float(v)) if v else 0,
            AttributeType.FLOAT: lambda v: float(v) if v else 0.0,
            AttributeType.BOOL: lambda v: v if isinstance(v, bool) else str(v).lower() in ('true', 'yes', '1'),
            AttributeType.DATE: lambda v: v if isinstance(v, date) else datetime.fromisoformat(str(v)).date(),
            AttributeType.DATETIME: lambda v: v if isinstance(v, datetime) else datetime.fromisoformat(str(v)),
            AttributeType.LIST_STRING: lambda v: v if isinstance(v, list) else [str(v)],
            AttributeType.ENUM: str,
        }
        
        try:
            converter = converters.get(self.type, lambda x: x)
            return converter(value)
        except (ValueError, TypeError):
            return value
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], engine_required: bool = False) -> "AttributeDefinition":
        """
        Create from YAML schema dict.
        
        Args:
            data: Dictionary from YAML
            engine_required: Whether this attribute is used by analysis engine
            
        Returns:
            AttributeDefinition instance
        """
        return cls(
            name=data.get("name", data.get("id", "")),
            type=data.get("type", "string"),
            required=data.get("required", False),
            default=data.get("default"),
            description=data.get("description", ""),
            choices=data.get("choices", []),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            engine_required=engine_required,
        )


class AttributeValidator:
    """Validates a set of attributes against definitions."""
    
    def __init__(self, definitions: List[AttributeDefinition]):
        """
        Initialize with attribute definitions.
        
        Args:
            definitions: List of AttributeDefinition objects
        """
        self.definitions = {d.name: d for d in definitions}
    
    def validate_all(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate all attributes.
        
        Args:
            data: Dictionary of attribute name -> value
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        for name, defn in self.definitions.items():
            is_valid, error = defn.validate(data.get(name))
            if not is_valid:
                errors.append(error)
        return len(errors) == 0, errors
    
    def convert_all(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert all values with defaults.
        
        Args:
            data: Dictionary of attribute name -> value
            
        Returns:
            Dictionary with converted values and defaults applied
        """
        result = {}
        
        # Apply definitions
        for name, defn in self.definitions.items():
            if name in data:
                result[name] = defn.convert(data[name])
            elif defn.default is not None:
                result[name] = defn.default
        
        # Pass through extra attributes not in definitions
        for k, v in data.items():
            if k not in result:
                result[k] = v
        
        return result
    
    def get_required_attributes(self) -> List[str]:
        """Get names of required attributes."""
        return [name for name, defn in self.definitions.items() if defn.required]
    
    def get_engine_required_attributes(self) -> List[str]:
        """Get names of engine-required attributes."""
        return [name for name, defn in self.definitions.items() if defn.engine_required]
