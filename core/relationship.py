"""
Generic Relationship abstraction for schema-driven edge types.

Provides:
- RelationshipTypeDefinition: Blueprint for relationship types
- InfluenceTypeConstraint: Level constraints for influence types

Influence edges are identified by is_influence_type=True (mandatory kernel).
Mitigates edges are identified by is_mitigates_type=True (mandatory kernel).
All other relationship types are extensible via schema.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.attribute import AttributeDefinition, AttributeValidator


@dataclass
class InfluenceTypeConstraint:
    """
    Optional level constraint for an influence type.
    
    When defined, the influence type is only valid for the specified
    source_level → target_level combination.
    
    Attributes:
        influence_type_id: ID of the influence type
        from_level: Required source risk level (None = any)
        to_level: Required target risk level (None = any)
    """
    influence_type_id: str
    from_level: Optional[str] = None
    to_level: Optional[str] = None
    
    def matches(self, source_level: str, target_level: str) -> bool:
        """
        Check if this constraint matches the given levels.
        
        Args:
            source_level: Level of source risk
            target_level: Level of target risk
            
        Returns:
            True if constraint matches (or has no restrictions)
        """
        from_ok = self.from_level is None or self.from_level.lower() == source_level.lower()
        to_ok = self.to_level is None or self.to_level.lower() == target_level.lower()
        return from_ok and to_ok


@dataclass
class RelationshipTypeDefinition:
    """
    Blueprint for a relationship type.
    
    Influence and Mitigates edges are identified by kernel flags.
    All other relationship types are extensible via schema.
    
    Attributes:
        id: Unique identifier
        label: Display name
        neo4j_type: Neo4j relationship type
        description: Human-readable description
        from_entity_types: Valid source entity type IDs (empty = any)
        to_entity_types: Valid target entity type IDs (empty = any)
        color: Edge color
        line_style: solid, dashed, dotted
        attributes: Attribute definitions for edge properties
        categorical_groups: Groups like types, strengths, effectiveness_levels
        is_influence_type: True ONLY for mandatory influence relationship
        is_mitigates_type: True ONLY for mandatory mitigates relationship
        influence_type_constraints: Level constraints for influence types
        engine_hint: Which engine plugin uses this relationship
        bidirectional: Whether the relationship is bidirectional
    """
    id: str
    label: str
    neo4j_type: str
    description: str = ""
    
    # Connection constraints — enforced on creation
    from_entity_types: List[str] = field(default_factory=list)
    to_entity_types: List[str] = field(default_factory=list)
    
    # Visual properties
    color: str = "#808080"
    line_style: str = "solid"
    
    # Attributes
    attributes: List[AttributeDefinition] = field(default_factory=list)
    categorical_groups: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    # Kernel flags
    is_influence_type: bool = False
    is_mitigates_type: bool = False
    
    # Influence-specific: level constraints per influence type
    influence_type_constraints: List[InfluenceTypeConstraint] = field(default_factory=list)
    
    # Engine plugin hint (which engine plugin uses this relationship)
    engine_hint: Optional[str] = None
    
    bidirectional: bool = False
    
    # Internal validator
    _validator: Optional[AttributeValidator] = field(default=None, repr=False)
    
    def __post_init__(self):
        """Initialize the attribute validator."""
        self._validator = AttributeValidator(self.attributes)
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate relationship data."""
        if self._validator is None:
            self._validator = AttributeValidator(self.attributes)
        return self._validator.validate_all(data)
    
    def can_connect(self, from_type: str, to_type: str) -> bool:
        """
        Check if relationship can connect these entity types.
        
        Args:
            from_type: Source entity type ID
            to_type: Target entity type ID
            
        Returns:
            True if connection is valid
        """
        from_ok = not self.from_entity_types or from_type in self.from_entity_types
        to_ok = not self.to_entity_types or to_type in self.to_entity_types
        return from_ok and to_ok
    
    def get_influence_type_for_levels(
        self, source_level: str, target_level: str
    ) -> Optional[str]:
        """
        For influence relationships: find the matching influence type
        given source and target risk levels.
        
        Args:
            source_level: Level of source risk
            target_level: Level of target risk
            
        Returns:
            Influence type ID, or None if no single match
        """
        if not self.is_influence_type:
            return None
        
        matches = []
        for constraint in self.influence_type_constraints:
            if constraint.matches(source_level, target_level):
                matches.append(constraint.influence_type_id)
        
        # Return single match, None otherwise (user must select)
        return matches[0] if len(matches) == 1 else None
    
    def get_valid_influence_types_for_levels(
        self, source_level: str, target_level: str
    ) -> List[str]:
        """
        Get all valid influence type IDs for a given level combination.
        Types with no level constraints are always valid.
        
        Args:
            source_level: Level of source risk
            target_level: Level of target risk
            
        Returns:
            List of valid influence type IDs
        """
        if not self.is_influence_type:
            return []
        
        valid = []
        for constraint in self.influence_type_constraints:
            if constraint.matches(source_level, target_level):
                valid.append(constraint.influence_type_id)
        return valid
    
    def get_categorical_values(self, group_name: str) -> List[str]:
        """Get valid values for a categorical group."""
        group = self.categorical_groups.get(group_name, [])
        return [item.get("label", item.get("id")) for item in group]
    
    def get_categorical_item(self, group_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific categorical item by ID."""
        group = self.categorical_groups.get(group_name, [])
        for item in group:
            if item.get("id") == item_id or item.get("label") == item_id:
                return item
        return None
    
    @classmethod
    def from_influence_schema(cls, data: Dict[str, Any]) -> "RelationshipTypeDefinition":
        """
        Create from the mandatory 'influences' section of schema YAML.
        
        Args:
            data: Influences section from schema YAML
            
        Returns:
            RelationshipTypeDefinition for influence relationship
        """
        attributes = [
            AttributeDefinition.from_dict(a)
            for a in data.get("attributes", [])
        ]
        
        # Parse categorical groups
        categorical_groups = {}
        for key in ["types", "strengths"]:
            if key in data:
                categorical_groups[key] = data[key]
        
        # Parse influence type constraints from the 'types' list
        influence_type_constraints = []
        for type_def in data.get("types", []):
            constraint = InfluenceTypeConstraint(
                influence_type_id=type_def.get("id"),
                from_level=type_def.get("from_level"),
                to_level=type_def.get("to_level"),
            )
            influence_type_constraints.append(constraint)
        
        return cls(
            id="influences",
            label="Influences",
            neo4j_type=data.get("neo4j_type", "INFLUENCES"),
            description="Risk-to-risk influence (mandatory kernel relationship)",
            from_entity_types=["risk"],
            to_entity_types=["risk"],
            color=data.get("color", "#e74c3c"),
            line_style=data.get("line_style", "solid"),
            attributes=attributes,
            categorical_groups=categorical_groups,
            is_influence_type=True,
            is_mitigates_type=False,
            influence_type_constraints=influence_type_constraints,
            bidirectional=False,
        )
    
    @classmethod
    def from_mitigates_schema(cls, data: Dict[str, Any]) -> "RelationshipTypeDefinition":
        """
        Create from the mandatory 'mitigates' section of schema YAML.
        
        Args:
            data: Mitigates section from schema YAML
            
        Returns:
            RelationshipTypeDefinition for mitigates relationship
        """
        attributes = [
            AttributeDefinition.from_dict(a)
            for a in data.get("attributes", [])
        ]
        
        # Parse categorical groups
        categorical_groups = {}
        for key in ["effectiveness_levels"]:
            if key in data:
                categorical_groups[key] = data[key]
        
        return cls(
            id="mitigates",
            label="Mitigates",
            neo4j_type=data.get("neo4j_type", "MITIGATES"),
            description="Mitigation-to-risk (mandatory kernel relationship)",
            from_entity_types=["mitigation"],
            to_entity_types=["risk"],
            color=data.get("color", "#27ae60"),
            line_style=data.get("line_style", "solid"),
            attributes=attributes,
            categorical_groups=categorical_groups,
            is_influence_type=False,
            is_mitigates_type=True,
            influence_type_constraints=[],
            bidirectional=False,
        )
    
    @classmethod
    def from_additional_schema(cls, data: Dict[str, Any]) -> "RelationshipTypeDefinition":
        """
        Create from an additional_relationships entry in schema YAML.
        
        Args:
            data: Relationship data from additional_relationships section
            
        Returns:
            RelationshipTypeDefinition for the additional relationship
        """
        rel_id = data.get("id", "unknown")
        
        attributes = [
            AttributeDefinition.from_dict(a)
            for a in data.get("attributes", [])
        ]
        
        # Gather all potential categorical groups
        categorical_groups = {}
        for key in ["types", "strengths", "impact_levels", "effectiveness_levels"]:
            if key in data:
                categorical_groups[key] = data[key]
        
        # Handle from_entity/to_entity as lists for flexibility
        from_entities = []
        if data.get("from_entity"):
            from_val = data["from_entity"]
            from_entities = [from_val] if isinstance(from_val, str) else from_val
        
        to_entities = []
        if data.get("to_entity"):
            to_val = data["to_entity"]
            to_entities = [to_val] if isinstance(to_val, str) else to_val
        
        return cls(
            id=rel_id,
            label=data.get("label", rel_id.replace("_", " ").title()),
            neo4j_type=data.get("neo4j_type", rel_id.upper()),
            description=data.get("description", ""),
            from_entity_types=from_entities,
            to_entity_types=to_entities,
            color=data.get("color", "#808080"),
            line_style=data.get("line_style", "solid"),
            attributes=attributes,
            categorical_groups=categorical_groups,
            is_influence_type=False,
            is_mitigates_type=False,
            engine_hint=data.get("engine_hint"),
            bidirectional=data.get("bidirectional", False),
        )
