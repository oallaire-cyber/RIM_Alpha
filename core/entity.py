"""
Generic Entity abstraction for schema-driven node types.

Provides:
- EntityTypeDefinition: Blueprint for entity types (Risk is kernel, others extensible)
- Entity: Instance of an entity type

Risk nodes are identified by is_risk_type=True (mandatory kernel).
Mitigation nodes are identified by is_mitigation_type=True (mandatory kernel).
All other entity types are fully extensible via schema.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.attribute import AttributeDefinition, AttributeValidator


@dataclass
class EntityTypeDefinition:
    """
    Blueprint for an entity type.
    
    Risk and Mitigation nodes are identified by kernel flags.
    All other entity types are extensible via schema.
    
    Attributes:
        id: Unique identifier (e.g., "risk", "mitigation", "asset")
        label: Display name
        neo4j_label: Neo4j node label
        description: Human-readable description
        color: Default color for visualization
        shape: Node shape (dot, diamond, star, triangle, square, hexagon)
        emoji: Emoji icon for UI
        size: Node size in visualization
        attributes: List of attribute definitions
        categorical_groups: Groups like levels, categories, statuses, types, clusters
        is_risk_type: True ONLY for mandatory risk entity
        is_mitigation_type: True ONLY for mandatory mitigation entity
    """
    id: str
    label: str
    neo4j_label: str
    description: str = ""
    
    # Visual properties
    color: str = "#808080"
    shape: str = "dot"
    emoji: str = "📦"
    size: int = 30
    
    # Attributes (standard + engine-required combined)
    attributes: List[AttributeDefinition] = field(default_factory=list)
    
    # Categorical groups (levels, categories, statuses, types, clusters, origins, etc.)
    categorical_groups: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    # Kernel flags
    is_risk_type: bool = False
    is_mitigation_type: bool = False
    
    # Internal validator (set in __post_init__)
    _validator: Optional[AttributeValidator] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Initialize the attribute validator."""
        self._validator = AttributeValidator(self.attributes)
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate entity data.
        
        Args:
            data: Entity data dictionary
            
        Returns:
            Tuple of (is_valid, error messages)
        """
        if self._validator is None:
            self._validator = AttributeValidator(self.attributes)
        return self._validator.validate_all(data)
    
    def prepare_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for database (convert types, apply defaults).
        
        Args:
            data: Raw entity data
            
        Returns:
            Prepared data with conversions and defaults applied
        """
        if self._validator is None:
            self._validator = AttributeValidator(self.attributes)
        return self._validator.convert_all(data)
    
    def get_categorical_values(self, group_name: str) -> List[str]:
        """
        Get valid values for a categorical group.
        
        Args:
            group_name: Name of the group (levels, categories, statuses, etc.)
            
        Returns:
            List of valid label values
        """
        group = self.categorical_groups.get(group_name, [])
        return [item.get("label", item.get("id")) for item in group]
    
    def get_categorical_item(self, group_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific categorical item by ID.
        
        Args:
            group_name: Name of the group
            item_id: ID of the item
            
        Returns:
            Item dictionary or None
        """
        group = self.categorical_groups.get(group_name, [])
        for item in group:
            if item.get("id") == item_id or item.get("label") == item_id:
                return item
        return None
    
    def get_engine_required_attributes(self) -> List[AttributeDefinition]:
        """Get attributes required by the analysis engine."""
        return [a for a in self.attributes if a.engine_required]
    
    @classmethod
    def from_risk_schema(cls, data: Dict[str, Any]) -> "EntityTypeDefinition":
        """
        Create from the mandatory 'risk' section of schema YAML.
        Handles engine_required_attributes specially.
        
        Args:
            data: Risk section from schema YAML
            
        Returns:
            EntityTypeDefinition for risk entity
        """
        # Parse engine-required attributes (marked as engine_required=True)
        engine_attrs = [
            AttributeDefinition.from_dict(a, engine_required=True)
            for a in data.get("engine_required_attributes", [])
        ]
        
        # Parse standard attributes
        standard_attrs = [
            AttributeDefinition.from_dict(a)
            for a in data.get("attributes", [])
        ]
        standard_attrs += [
            AttributeDefinition.from_dict(a)
            for a in data.get("custom_attributes", [])
        ]
        
        # Combine: engine-required first, then standard
        all_attrs = engine_attrs + standard_attrs
        
        # Gather categorical groups
        categorical_groups = {}
        for key in ["levels", "categories", "statuses", "origins"]:
            if key in data:
                categorical_groups[key] = data[key]
        
        # Get visual properties from first level if available
        levels = data.get("levels", [])
        first_level = levels[0] if levels else {}
        
        return cls(
            id="risk",
            label="Risk",
            neo4j_label=data.get("neo4j_label", "Risk"),
            description="Risk nodes (mandatory kernel entity)",
            color=first_level.get("color", "#808080"),
            shape=first_level.get("shape", "dot"),
            emoji=first_level.get("emoji", "🎯"),
            size=first_level.get("size", 30),
            attributes=all_attrs,
            categorical_groups=categorical_groups,
            is_risk_type=True,
            is_mitigation_type=False,
        )
    
    @classmethod
    def from_mitigation_schema(cls, data: Dict[str, Any]) -> "EntityTypeDefinition":
        """
        Create from the mandatory 'mitigation' section of schema YAML.
        
        Args:
            data: Mitigation section from schema YAML
            
        Returns:
            EntityTypeDefinition for mitigation entity
        """
        attributes = [
            AttributeDefinition.from_dict(a)
            for a in data.get("attributes", [])
        ]
        attributes += [
            AttributeDefinition.from_dict(a)
            for a in data.get("custom_attributes", [])
        ]
        
        # Gather categorical groups
        categorical_groups = {}
        for key in ["types", "statuses"]:
            if key in data:
                categorical_groups[key] = data[key]
        
        return cls(
            id="mitigation",
            label="Mitigation",
            neo4j_label=data.get("neo4j_label", "Mitigation"),
            description="Mitigation nodes (mandatory kernel entity)",
            color=data.get("color", "#27ae60"),
            shape=data.get("shape", "square"),
            emoji=data.get("emoji", "🛡️"),
            size=data.get("size", 25),
            attributes=attributes,
            categorical_groups=categorical_groups,
            is_risk_type=False,
            is_mitigation_type=True,
        )
    
    @classmethod
    def from_additional_schema(cls, data: Dict[str, Any]) -> "EntityTypeDefinition":
        """
        Create from an additional_entities entry in schema YAML.
        
        Args:
            data: Entity data from additional_entities or entities section
            
        Returns:
            EntityTypeDefinition for the additional entity
        """
        entity_id = data.get("id", "unknown")
        
        attributes = [
            AttributeDefinition.from_dict(a)
            for a in data.get("attributes", [])
        ]
        attributes += [
            AttributeDefinition.from_dict(a)
            for a in data.get("custom_attributes", [])
        ]
        
        # Gather categorical groups (any key that is a list of dicts with 'id')
        categorical_groups = {}
        for key in ["levels", "categories", "statuses", "origins", "clusters", "types"]:
            if key in data:
                categorical_groups[key] = data[key]
        
        return cls(
            id=entity_id,
            label=data.get("label", entity_id.title()),
            neo4j_label=data.get("neo4j_label", entity_id.title()),
            description=data.get("description", ""),
            color=data.get("color", "#808080"),
            shape=data.get("shape", "dot"),
            emoji=data.get("emoji", "📦"),
            size=data.get("size", 30),
            attributes=attributes,
            categorical_groups=categorical_groups,
            is_risk_type=False,
            is_mitigation_type=False,
        )


@dataclass
class Entity:
    """
    A generic entity instance.
    
    Attributes:
        id: Unique identifier (from Neo4j)
        entity_type: Reference to EntityTypeDefinition
        data: Attribute values
    """
    id: str
    entity_type: EntityTypeDefinition
    data: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get an attribute value."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set an attribute value."""
        self.data[key] = value
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate this entity's data."""
        return self.entity_type.validate(self.data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"id": self.id, "entity_type": self.entity_type.id, **self.data}
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j property format."""
        props = self.entity_type.prepare_data(self.data)
        props["id"] = self.id
        return props
