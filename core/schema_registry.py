"""
Schema Registry - Runtime access to schema definitions.

Kernel-aware: ensures Risk, Mitigation entities and Influence, Mitigates 
relationships are always present.

Provides:
- SchemaRegistry: Central registry for all schema definitions
- SchemaValidationError: Raised when schema fails validation
- get_registry(): Get the global registry instance
- load_schema(): Load schema by name
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from core.entity import EntityTypeDefinition
from core.relationship import RelationshipTypeDefinition


class SchemaValidationError(Exception):
    """Raised when schema fails validation."""
    pass


class SchemaRegistry:
    """
    Central registry for schema definitions.
    
    Mandatory kernel:
      - Exactly one risk entity type (is_risk_type=True)
      - Exactly one mitigation entity type (is_mitigation_type=True)
      - Exactly one influence relationship type (is_influence_type=True)
      - Exactly one mitigates relationship type (is_mitigates_type=True)
    
    Everything else is extensible via additional_entities and additional_relationships.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._entity_types: Dict[str, EntityTypeDefinition] = {}
        self._relationship_types: Dict[str, RelationshipTypeDefinition] = {}
        self._schema_name: Optional[str] = None
        self._schema_version: Optional[str] = None
        self._ui_config: Dict[str, Any] = {}
        self._analysis_config: Dict[str, Any] = {}
        self._raw_schema: Dict[str, Any] = {}
    
    def load_from_yaml(self, schema_path: Path) -> None:
        """
        Load schema from YAML file.
        
        Args:
            schema_path: Path to schema.yaml file
            
        Raises:
            SchemaValidationError: If schema is invalid or missing required elements
        """
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self._raw_schema = data
        self._schema_name = data.get("name", "Unknown")
        self._schema_version = data.get("version", "1.0")
        
        # Load kernel first (mandatory)
        self._load_kernel(data)
        
        # Load context nodes (U6)
        self._load_context_nodes(data)
        
        # Load extensible parts
        self._load_additional_entities(data)
        self._load_additional_relationships(data)
        self._load_context_edges(data)
        
        # Load configuration
        self._ui_config = data.get("ui", {})
        self._analysis_config = data.get("analysis", {})
        
        # Validate schema integrity
        self._validate_schema()
    
    def _load_kernel(self, data: Dict[str, Any]) -> None:
        """
        Load mandatory kernel: risk + mitigation entities, influence + mitigates relationships.
        
        Args:
            data: Full schema data
            
        Raises:
            SchemaValidationError: If kernel elements are missing
        """
        self._entity_types.clear()
        self._relationship_types.clear()
        
        # === MANDATORY: Risk entity ===
        risk_data = data.get("risk")
        if not risk_data:
            # Backward compatibility: check under entities.risk
            risk_data = data.get("entities", {}).get("risk")
        
        if not risk_data:
            raise SchemaValidationError(
                "Schema must define a 'risk' section (mandatory kernel entity)"
            )
        
        self._entity_types["risk"] = EntityTypeDefinition.from_risk_schema(risk_data)
        
        # === MANDATORY: Mitigation entity ===
        mitigation_data = data.get("mitigation")
        if not mitigation_data:
            # Backward compatibility: check under entities.mitigation
            mitigation_data = data.get("entities", {}).get("mitigation")
        
        if not mitigation_data:
            raise SchemaValidationError(
                "Schema must define a 'mitigation' section (mandatory kernel entity)"
            )
        
        self._entity_types["mitigation"] = EntityTypeDefinition.from_mitigation_schema(mitigation_data)
        
        # === MANDATORY: Influence relationship ===
        influence_data = data.get("influences")
        if not influence_data:
            # Backward compatibility: check under relationships.influences
            influence_data = data.get("relationships", {}).get("influences")
        
        if not influence_data:
            raise SchemaValidationError(
                "Schema must define an 'influences' section (mandatory kernel relationship)"
            )
        
        self._relationship_types["influences"] = RelationshipTypeDefinition.from_influence_schema(
            influence_data
        )
        
        # === MANDATORY: Mitigates relationship ===
        mitigates_data = data.get("mitigates")
        if not mitigates_data:
            # Backward compatibility: check under relationships.mitigates
            mitigates_data = data.get("relationships", {}).get("mitigates")
        
        if not mitigates_data:
            raise SchemaValidationError(
                "Schema must define a 'mitigates' section (mandatory kernel relationship)"
            )
        
        self._relationship_types["mitigates"] = RelationshipTypeDefinition.from_mitigates_schema(
            mitigates_data
        )
    
    def _load_context_nodes(self, data: Dict[str, Any]) -> None:
        """
        Load context node types from the context_nodes section.
        
        Also handles backward compat for legacy entities.custom_entities list.
        
        Args:
            data: Full schema data
        """
        # New format: top-level context_nodes map
        context_nodes = data.get("context_nodes", {})
        for node_id, node_data in context_nodes.items():
            if node_id not in self._entity_types:
                self._entity_types[node_id] = EntityTypeDefinition.from_context_node_schema(
                    node_id, node_data
                )
        
        # Backward compat: legacy entities.custom_entities list
        if not context_nodes:
            entities_section = data.get("entities", {})
            for custom in entities_section.get("custom_entities", []):
                cid = custom.get("id")
                if cid and cid not in self._entity_types:
                    self._entity_types[cid] = EntityTypeDefinition.from_context_node_schema(
                        cid, custom
                    )
    
    def _load_context_edges(self, data: Dict[str, Any]) -> None:
        """
        Load context edge types from the context_edges section.
        
        Args:
            data: Full schema data
        """
        kernel_ids = {"influences", "mitigates"}
        
        # New format: context_edges map
        context_edges = data.get("context_edges", {})
        if isinstance(context_edges, list):
            # Fallback if list
            for rel_data in context_edges:
                rel_id = rel_data.get("id")
                if rel_id and rel_id not in kernel_ids and rel_id not in self._relationship_types:
                    self._relationship_types[rel_id] = RelationshipTypeDefinition.from_context_edge_schema(
                        rel_data
                    )
        else:
            for rel_id, rel_data in context_edges.items():
                if rel_id and rel_id not in kernel_ids and rel_id not in self._relationship_types:
                    # Inject ID if missing
                    if "id" not in rel_data:
                        rel_data["id"] = rel_id
                    self._relationship_types[rel_id] = RelationshipTypeDefinition.from_context_edge_schema(
                        rel_data
                    )
    
    def _load_additional_entities(self, data: Dict[str, Any]) -> None:
        """
        Load extensible entity types (non-kernel, non-context-node).
        
        Args:
            data: Full schema data
        """
        kernel_ids = {"risk", "mitigation"}
        
        # New format: additional_entities list
        for entity_data in data.get("additional_entities", []):
            entity_id = entity_data.get("id")
            if entity_id and entity_id not in kernel_ids and entity_id not in self._entity_types:
                self._entity_types[entity_id] = EntityTypeDefinition.from_additional_schema(
                    entity_data
                )
        
        # Backward compatibility: entities section (tpo, etc.)
        entities_section = data.get("entities", {})
        for entity_id, entity_data in entities_section.items():
            if entity_id in kernel_ids or entity_id in self._entity_types:
                continue  # Already loaded as kernel or context node
            
            if entity_id == "custom_entities":
                continue  # Handled by _load_context_nodes
            
            if isinstance(entity_data, dict):
                entity_data_with_id = {**entity_data, "id": entity_id}
                self._entity_types[entity_id] = EntityTypeDefinition.from_additional_schema(
                    entity_data_with_id
                )
    
    def _load_additional_relationships(self, data: Dict[str, Any]) -> None:
        """
        Load extensible relationship types.
        
        Args:
            data: Full schema data
        """
        kernel_ids = {"influences", "mitigates"}
        
        # New format: additional_relationships list
        for rel_data in data.get("additional_relationships", []):
            rel_id = rel_data.get("id")
            if rel_id and rel_id not in kernel_ids:
                self._relationship_types[rel_id] = RelationshipTypeDefinition.from_additional_schema(
                    rel_data
                )
        
        # Backward compatibility: relationships section
        rels_section = data.get("relationships", {})
        for rel_id, rel_data in rels_section.items():
            if rel_id in kernel_ids:
                continue  # Already loaded as kernel
            
            if rel_id == "custom_relationships":
                # Legacy custom_relationships list
                for custom in rel_data:
                    cid = custom.get("id")
                    if cid and cid not in self._relationship_types:
                        self._relationship_types[cid] = RelationshipTypeDefinition.from_additional_schema(
                            custom
                        )
            elif rel_id not in self._relationship_types:
                if isinstance(rel_data, dict):
                    rel_data_with_id = {**rel_data, "id": rel_id}
                    self._relationship_types[rel_id] = RelationshipTypeDefinition.from_additional_schema(
                        rel_data_with_id
                    )
    
    def _validate_schema(self) -> None:
        """
        Validate schema integrity at load time.
        
        Raises:
            SchemaValidationError: If validation fails
        """
        errors = []
        
        # 1. Risk entity must exist and be marked as kernel
        risk_type = self._entity_types.get("risk")
        if not risk_type or not risk_type.is_risk_type:
            errors.append("Missing mandatory risk entity type")
        
        # 2. At least one risk level must be defined
        if risk_type and not risk_type.categorical_groups.get("levels"):
            errors.append("Risk entity must define at least one level")
        
        # 3. Mitigation entity must exist and be marked as kernel
        mit_entity = self._entity_types.get("mitigation")
        if not mit_entity or not mit_entity.is_mitigation_type:
            errors.append("Missing mandatory mitigation entity type")
        
        # 4. Influence relationship must exist and be marked as kernel
        influence_type = self._relationship_types.get("influences")
        if not influence_type or not influence_type.is_influence_type:
            errors.append("Missing mandatory influence relationship type")
        
        # 5. At least one influence type must be defined
        if influence_type and not influence_type.categorical_groups.get("types"):
            errors.append("Influence relationship must define at least one type")
        
        # 6. Mitigates relationship must exist and be marked as kernel
        mitigates_type = self._relationship_types.get("mitigates")
        if not mitigates_type or not mitigates_type.is_mitigates_type:
            errors.append("Missing mandatory mitigates relationship type")
        
        # 7. Edge constraints reference valid entity types
        for rel_id, rel_type in self._relationship_types.items():
            for from_type in rel_type.from_entity_types:
                if from_type not in self._entity_types:
                    errors.append(
                        f"Relationship '{rel_id}' references unknown from_entity '{from_type}'"
                    )
            for to_type in rel_type.to_entity_types:
                if to_type not in self._entity_types:
                    errors.append(
                        f"Relationship '{rel_id}' references unknown to_entity '{to_type}'"
                    )
        
        # 8. Influence type level constraints reference valid risk levels
        if influence_type and risk_type:
            valid_levels = {
                level.get("id") for level in risk_type.categorical_groups.get("levels", [])
            }
            for constraint in influence_type.influence_type_constraints:
                if constraint.from_level and constraint.from_level not in valid_levels:
                    errors.append(
                        f"Influence type '{constraint.influence_type_id}' references "
                        f"unknown from_level '{constraint.from_level}'"
                    )
                if constraint.to_level and constraint.to_level not in valid_levels:
                    errors.append(
                        f"Influence type '{constraint.influence_type_id}' references "
                        f"unknown to_level '{constraint.to_level}'"
                    )
        
        if errors:
            raise SchemaValidationError(
                f"Schema validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )
    
    # ─── Entity Accessors ─────────────────────────────────────────
    
    def get_entity_type(self, entity_type_id: str) -> Optional[EntityTypeDefinition]:
        """Get entity type by ID."""
        return self._entity_types.get(entity_type_id)
    
    def get_risk_type(self) -> EntityTypeDefinition:
        """Get the mandatory risk entity type."""
        return self._entity_types["risk"]
    
    def get_mitigation_type(self) -> EntityTypeDefinition:
        """Get the mandatory mitigation entity type."""
        return self._entity_types["mitigation"]
    
    def get_entity_type_by_neo4j_label(self, label: str) -> Optional[EntityTypeDefinition]:
        """Get entity type by Neo4j label."""
        for et in self._entity_types.values():
            if et.neo4j_label == label:
                return et
        return None
    
    def has_entity(self, entity_type_id: str) -> bool:
        """Check if an entity type exists in the schema."""
        return entity_type_id in self._entity_types
    
    def get_additional_entity_types(self) -> Dict[str, EntityTypeDefinition]:
        """Get all non-kernel entity types (excludes risk and mitigation)."""
        kernel_ids = {"risk", "mitigation"}
        return {k: v for k, v in self._entity_types.items() if k not in kernel_ids}
    
    def get_context_node_types(self) -> Dict[str, EntityTypeDefinition]:
        """Get all context node types."""
        return {k: v for k, v in self._entity_types.items() if v.is_context_node}
    
    def get_context_nodes_by_zone(self, zone: str) -> Dict[str, EntityTypeDefinition]:
        """Get context node types filtered by zone ('upper' or 'lower')."""
        return {
            k: v for k, v in self._entity_types.items()
            if v.is_context_node and v.zone == zone
        }
    
    # ─── Relationship Accessors ───────────────────────────────────
    
    def get_relationship_type(self, rel_type_id: str) -> Optional[RelationshipTypeDefinition]:
        """Get relationship type by ID."""
        return self._relationship_types.get(rel_type_id)
    
    def get_influence_type(self) -> RelationshipTypeDefinition:
        """Get the mandatory influence relationship type."""
        return self._relationship_types["influences"]
    
    def get_mitigates_type(self) -> RelationshipTypeDefinition:
        """Get the mandatory mitigates relationship type."""
        return self._relationship_types["mitigates"]
    
    def has_relationship(self, rel_type_id: str) -> bool:
        """Check if a relationship type exists in the schema."""
        return rel_type_id in self._relationship_types
    
    def get_additional_relationship_types(self) -> Dict[str, RelationshipTypeDefinition]:
        """Get all non-kernel relationship types (excludes influences and mitigates)."""
        kernel_ids = {"influences", "mitigates"}
        return {k: v for k, v in self._relationship_types.items() if k not in kernel_ids}
    
    # ─── Convenience Methods ──────────────────────────────────────
    
    def get_risk_levels(self) -> List[Dict[str, Any]]:
        """Convenience: get all risk levels from the risk entity."""
        return self._entity_types["risk"].categorical_groups.get("levels", [])
    
    def get_risk_level_ids(self) -> List[str]:
        """Get list of risk level IDs."""
        return [l.get("id") for l in self.get_risk_levels()]
    
    def get_risk_level_labels(self) -> List[str]:
        """Get list of risk level labels."""
        return [l.get("label", l.get("id")) for l in self.get_risk_levels()]
    
    def get_influence_types(self) -> List[Dict[str, Any]]:
        """Convenience: get all influence types."""
        return self._relationship_types["influences"].categorical_groups.get("types", [])
    
    def get_influence_strengths(self) -> List[Dict[str, Any]]:
        """Convenience: get all influence strengths."""
        return self._relationship_types["influences"].categorical_groups.get("strengths", [])
    
    def get_mitigation_effectiveness_levels(self) -> List[Dict[str, Any]]:
        """Convenience: get all mitigation effectiveness levels."""
        return self._relationship_types["mitigates"].categorical_groups.get("effectiveness_levels", [])
    
    # ─── Properties ───────────────────────────────────────────────
    
    @property
    def entity_types(self) -> Dict[str, EntityTypeDefinition]:
        """All entity types (kernel + additional)."""
        return self._entity_types
    
    @property
    def relationship_types(self) -> Dict[str, RelationshipTypeDefinition]:
        """All relationship types (kernel + additional)."""
        return self._relationship_types
    
    @property
    def schema_name(self) -> str:
        """Schema name from YAML."""
        return self._schema_name or "Unknown"
    
    @property
    def schema_version(self) -> str:
        """Schema version from YAML."""
        return self._schema_version or "1.0"
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration section."""
        return self._ui_config
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration section."""
        return self._analysis_config
    
    def get_raw_schema(self) -> Dict[str, Any]:
        """Get the raw schema dictionary."""
        return self._raw_schema


# ─── Global instance ──────────────────────────────────────────────

_registry: Optional[SchemaRegistry] = None


def get_registry() -> SchemaRegistry:
    """
    Get the global schema registry instance.
    
    Returns:
        The global SchemaRegistry (creates if needed)
    """
    global _registry
    if _registry is None:
        _registry = SchemaRegistry()
    return _registry


def load_schema(schema_name: str = "default") -> SchemaRegistry:
    """
    Load schema by name.
    
    Args:
        schema_name: Name of schema directory under schemas/
        
    Returns:
        The loaded SchemaRegistry
    """
    registry = get_registry()
    schema_path = Path(__file__).parent.parent / "schemas" / schema_name / "schema.yaml"
    registry.load_from_yaml(schema_path)
    return registry


def reset_registry() -> None:
    """Reset the global registry (for testing)."""
    global _registry
    _registry = None
