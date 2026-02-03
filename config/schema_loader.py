"""
Schema loader for RIM configuration management.

Loads and validates YAML schema files that define the RIM application configuration.
Provides typed dataclasses for all configuration elements.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


# =============================================================================
# DATACLASSES FOR SCHEMA CONFIGURATION
# =============================================================================

@dataclass
class LevelConfig:
    """Risk level configuration."""
    id: str
    label: str
    description: str = ""
    color: str = "#808080"
    shape: str = "dot"
    emoji: str = "●"
    size: int = 30


@dataclass
class CategoryConfig:
    """Risk category configuration."""
    id: str
    label: str
    description: str = ""
    color: str = "#808080"


@dataclass
class StatusConfig:
    """Status configuration for risks, mitigations, etc."""
    id: str
    label: str
    description: str = ""
    is_active: bool = True


@dataclass
class OriginConfig:
    """Risk origin configuration."""
    id: str
    label: str
    description: str = ""


@dataclass
class AttributeConfig:
    """Standard attribute configuration."""
    name: str
    type: str  # string, float, int, date, boolean
    required: bool = False
    default: Any = None
    description: str = ""


@dataclass
class CustomAttributeConfig:
    """Custom attribute configuration."""
    id: str
    label: str
    type: str = "string"
    required: bool = False
    default: Any = None
    description: str = ""


@dataclass
class ClusterConfig:
    """TPO cluster configuration."""
    id: str
    label: str
    description: str = ""
    color: str = "#f1c40f"


@dataclass
class TypeConfig:
    """Type configuration for mitigations, influences, etc."""
    id: str
    label: str
    description: str = ""
    color: str = "#808080"
    line_style: str = "solid"


@dataclass
class StrengthConfig:
    """Influence strength configuration."""
    id: str
    label: str
    value: float
    description: str = ""
    color: str = "#808080"


@dataclass
class EffectivenessConfig:
    """Mitigation effectiveness configuration."""
    id: str
    label: str
    reduction: float  # 0.0 to 1.0
    description: str = ""


@dataclass
class ImpactLevelConfig:
    """TPO impact level configuration."""
    id: str
    label: str
    value: int
    description: str = ""
    color: str = "#808080"


# =============================================================================
# ENTITY CONFIGURATIONS
# =============================================================================

@dataclass
class RiskEntityConfig:
    """Risk entity configuration."""
    neo4j_label: str = "Risk"
    levels: List[LevelConfig] = field(default_factory=list)
    categories: List[CategoryConfig] = field(default_factory=list)
    statuses: List[StatusConfig] = field(default_factory=list)
    origins: List[OriginConfig] = field(default_factory=list)
    attributes: List[AttributeConfig] = field(default_factory=list)
    custom_attributes: List[CustomAttributeConfig] = field(default_factory=list)


@dataclass
class TPOEntityConfig:
    """TPO entity configuration."""
    neo4j_label: str = "TPO"
    clusters: List[ClusterConfig] = field(default_factory=list)
    attributes: List[AttributeConfig] = field(default_factory=list)
    custom_attributes: List[CustomAttributeConfig] = field(default_factory=list)


@dataclass
class MitigationEntityConfig:
    """Mitigation entity configuration."""
    neo4j_label: str = "Mitigation"
    types: List[TypeConfig] = field(default_factory=list)
    statuses: List[StatusConfig] = field(default_factory=list)
    attributes: List[AttributeConfig] = field(default_factory=list)
    custom_attributes: List[CustomAttributeConfig] = field(default_factory=list)


@dataclass
class CustomEntityConfig:
    """
    User-defined entity type.
    
    Allows users to add custom node types beyond Risk, TPO, Mitigation.
    Examples: Asset, Threat Actor, Control Framework, Stakeholder.
    """
    id: str
    label: str
    neo4j_label: str
    description: str = ""
    color: str = "#808080"
    shape: str = "box"  # box, dot, diamond, hexagon, star, triangle
    emoji: str = "📦"
    size: int = 30
    attributes: List[AttributeConfig] = field(default_factory=list)
    custom_attributes: List[CustomAttributeConfig] = field(default_factory=list)


@dataclass
class CustomRelationshipConfig:
    """
    User-defined relationship type.
    
    Allows users to add custom relationships beyond INFLUENCES, IMPACTS_TPO, MITIGATES.
    Examples: OWNS, MANAGES, DEPENDS_ON, PROTECTS.
    """
    id: str
    label: str
    neo4j_type: str
    description: str = ""
    from_entity: str = ""  # Entity ID: "risk", "tpo", "mitigation", or custom entity id
    to_entity: str = ""    # Entity ID
    color: str = "#808080"
    line_style: str = "solid"  # solid, dashed, dotted
    bidirectional: bool = False
    attributes: List[AttributeConfig] = field(default_factory=list)



# =============================================================================
# RELATIONSHIP CONFIGURATIONS
# =============================================================================

@dataclass
class InfluenceRelConfig:
    """Influence relationship configuration."""
    neo4j_type: str = "INFLUENCES"
    types: List[TypeConfig] = field(default_factory=list)
    strengths: List[StrengthConfig] = field(default_factory=list)
    default_confidence: float = 0.8


@dataclass
class TPOImpactRelConfig:
    """TPO impact relationship configuration."""
    neo4j_type: str = "IMPACTS_TPO"
    impact_levels: List[ImpactLevelConfig] = field(default_factory=list)


@dataclass
class MitigatesRelConfig:
    """Mitigates relationship configuration."""
    neo4j_type: str = "MITIGATES"
    effectiveness_levels: List[EffectivenessConfig] = field(default_factory=list)


# =============================================================================
# ANALYSIS CONFIGURATION
# =============================================================================

@dataclass
class ExposureConfig:
    """Exposure calculation configuration."""
    base_formula: str = "likelihood * impact"
    max_base_value: float = 100.0
    propagation_decay: float = 0.85
    convergence_multiplier: float = 0.2


@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    exposure: ExposureConfig = field(default_factory=ExposureConfig)
    cache_timeout_seconds: int = 30
    max_influence_depth: int = 10
    high_exposure_threshold_multiplier: float = 1.2


# =============================================================================
# UI CONFIGURATION
# =============================================================================

@dataclass
class TabConfig:
    """Tab configuration."""
    id: str
    label: str
    icon: str = ""
    enabled: bool = True


@dataclass
class PresetConfig:
    """Filter preset configuration."""
    id: str
    name: str
    description: str = ""
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UIConfig:
    """UI configuration."""
    app_title: str = "Risk Influence Map (RIM)"
    app_icon: str = "🎯"
    layout: str = "wide"
    tabs: List[TabConfig] = field(default_factory=list)
    presets: List[PresetConfig] = field(default_factory=list)
    graph_height: str = "700px"
    graph_bgcolor: str = "#ffffff"


# =============================================================================
# MAIN SCHEMA CONFIGURATION
# =============================================================================

@dataclass
class SchemaConfig:
    """Complete schema configuration."""
    version: str = "1.0"
    name: str = "Default"
    description: str = ""
    
    # Core Entities
    risk: RiskEntityConfig = field(default_factory=RiskEntityConfig)
    tpo: TPOEntityConfig = field(default_factory=TPOEntityConfig)
    mitigation: MitigationEntityConfig = field(default_factory=MitigationEntityConfig)
    
    # Custom Entities (user-defined node types)
    custom_entities: List[CustomEntityConfig] = field(default_factory=list)
    
    # Core Relationships
    influences: InfluenceRelConfig = field(default_factory=InfluenceRelConfig)
    impacts_tpo: TPOImpactRelConfig = field(default_factory=TPOImpactRelConfig)
    mitigates: MitigatesRelConfig = field(default_factory=MitigatesRelConfig)
    
    # Custom Relationships (user-defined relationship types)
    custom_relationships: List[CustomRelationshipConfig] = field(default_factory=list)
    
    # Analysis
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    
    # UI
    ui: UIConfig = field(default_factory=UIConfig)

    # Helper properties for backward compatibility
    @property
    def risk_levels(self) -> List[str]:
        """Get risk level labels for backward compatibility."""
        return [level.label for level in self.risk.levels]
    
    @property
    def risk_categories(self) -> List[str]:
        """Get risk category labels for backward compatibility."""
        return [cat.label for cat in self.risk.categories]
    
    @property
    def risk_statuses(self) -> List[str]:
        """Get risk status labels for backward compatibility."""
        return [status.label for status in self.risk.statuses]
    
    @property
    def risk_origins(self) -> List[str]:
        """Get risk origin labels for backward compatibility."""
        return [origin.label for origin in self.risk.origins]
    
    @property
    def tpo_clusters(self) -> List[str]:
        """Get TPO cluster labels for backward compatibility."""
        return [cluster.label for cluster in self.tpo.clusters]
    
    @property
    def mitigation_types(self) -> List[str]:
        """Get mitigation type labels for backward compatibility."""
        return [t.label for t in self.mitigation.types]
    
    @property
    def mitigation_statuses(self) -> List[str]:
        """Get mitigation status labels for backward compatibility."""
        return [s.label for s in self.mitigation.statuses]
    
    @property
    def influence_strengths(self) -> List[str]:
        """Get influence strength labels for backward compatibility."""
        return [s.label for s in self.influences.strengths]
    
    @property
    def impact_levels(self) -> List[str]:
        """Get impact level labels for backward compatibility."""
        return [il.label for il in self.impacts_tpo.impact_levels]
    
    @property
    def effectiveness_levels(self) -> List[str]:
        """Get effectiveness level labels for backward compatibility."""
        return [e.label for e in self.mitigates.effectiveness_levels]


# =============================================================================
# SCHEMA LOADER CLASS
# =============================================================================

class SchemaLoader:
    """Load and parse YAML schema files into typed dataclasses."""
    
    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialize the schema loader.
        
        Args:
            schemas_dir: Path to schemas directory. Defaults to project's schemas/ folder.
        """
        if schemas_dir is None:
            # Default to schemas/ directory relative to this file's parent's parent
            self.schemas_dir = Path(__file__).parent.parent / "schemas"
        else:
            self.schemas_dir = Path(schemas_dir)
        
        self._current_schema: Optional[SchemaConfig] = None
        self._current_schema_name: Optional[str] = None
    
    def list_schemas(self) -> List[str]:
        """
        List all available schema directories.
        
        Returns:
            List of schema directory names.
        """
        if not self.schemas_dir.exists():
            return []
        
        schemas = []
        for item in self.schemas_dir.iterdir():
            if item.is_dir() and (item / "schema.yaml").exists():
                schemas.append(item.name)
        return sorted(schemas)
    
    def get_schema_path(self, schema_name: str) -> Path:
        """Get the path to a schema's YAML file."""
        return self.schemas_dir / schema_name / "schema.yaml"
    
    def load_schema(self, schema_name: str) -> SchemaConfig:
        """
        Load a schema from its YAML file.
        
        Args:
            schema_name: Name of the schema directory.
            
        Returns:
            Parsed SchemaConfig object.
            
        Raises:
            FileNotFoundError: If schema file doesn't exist.
            ValueError: If schema is invalid.
        """
        schema_path = self.get_schema_path(schema_name)
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        schema = self._parse_schema(data)
        self._current_schema = schema
        self._current_schema_name = schema_name
        
        return schema
    
    def get_current_schema(self) -> Optional[SchemaConfig]:
        """Get the currently loaded schema."""
        return self._current_schema
    
    def get_current_schema_name(self) -> Optional[str]:
        """Get the name of the currently loaded schema."""
        return self._current_schema_name
    
    def reload_schema(self) -> Optional[SchemaConfig]:
        """Reload the current schema from disk."""
        if self._current_schema_name:
            return self.load_schema(self._current_schema_name)
        return None
    
    def _parse_schema(self, data: Dict[str, Any]) -> SchemaConfig:
        """Parse raw YAML data into a SchemaConfig object."""
        schema = SchemaConfig(
            version=data.get("version", "1.0"),
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
        )
        
        # Parse core entities
        entities = data.get("entities", {})
        schema.risk = self._parse_risk_entity(entities.get("risk", {}))
        schema.tpo = self._parse_tpo_entity(entities.get("tpo", {}))
        schema.mitigation = self._parse_mitigation_entity(entities.get("mitigation", {}))
        
        # Parse custom entities
        for entity_data in entities.get("custom_entities", []):
            schema.custom_entities.append(self._parse_custom_entity(entity_data))
        
        # Parse core relationships
        relationships = data.get("relationships", {})
        schema.influences = self._parse_influences_rel(relationships.get("influences", {}))
        schema.impacts_tpo = self._parse_impacts_tpo_rel(relationships.get("impacts_tpo", {}))
        schema.mitigates = self._parse_mitigates_rel(relationships.get("mitigates", {}))
        
        # Parse custom relationships
        for rel_data in relationships.get("custom_relationships", []):
            schema.custom_relationships.append(self._parse_custom_relationship(rel_data))
        
        # Parse analysis config
        schema.analysis = self._parse_analysis(data.get("analysis", {}))
        
        # Parse UI config
        schema.ui = self._parse_ui(data.get("ui", {}))
        
        return schema
    
    def _parse_risk_entity(self, data: Dict[str, Any]) -> RiskEntityConfig:
        """Parse risk entity configuration."""
        entity = RiskEntityConfig(neo4j_label=data.get("neo4j_label", "Risk"))
        
        # Parse levels
        for level_data in data.get("levels", []):
            entity.levels.append(LevelConfig(
                id=level_data.get("id", ""),
                label=level_data.get("label", ""),
                description=level_data.get("description", ""),
                color=level_data.get("color", "#808080"),
                shape=level_data.get("shape", "dot"),
                emoji=level_data.get("emoji", "●"),
                size=level_data.get("size", 30),
            ))
        
        # Parse categories
        for cat_data in data.get("categories", []):
            entity.categories.append(CategoryConfig(
                id=cat_data.get("id", ""),
                label=cat_data.get("label", ""),
                description=cat_data.get("description", ""),
                color=cat_data.get("color", "#808080"),
            ))
        
        # Parse statuses
        for status_data in data.get("statuses", []):
            entity.statuses.append(StatusConfig(
                id=status_data.get("id", ""),
                label=status_data.get("label", ""),
                description=status_data.get("description", ""),
                is_active=status_data.get("is_active", True),
            ))
        
        # Parse origins
        for origin_data in data.get("origins", []):
            entity.origins.append(OriginConfig(
                id=origin_data.get("id", ""),
                label=origin_data.get("label", ""),
                description=origin_data.get("description", ""),
            ))
        
        # Parse attributes
        for attr_data in data.get("attributes", []):
            entity.attributes.append(AttributeConfig(
                name=attr_data.get("name", ""),
                type=attr_data.get("type", "string"),
                required=attr_data.get("required", False),
                default=attr_data.get("default"),
                description=attr_data.get("description", ""),
            ))
        
        # Parse custom attributes
        for cattr_data in data.get("custom_attributes", []):
            entity.custom_attributes.append(CustomAttributeConfig(
                id=cattr_data.get("id", ""),
                label=cattr_data.get("label", ""),
                type=cattr_data.get("type", "string"),
                required=cattr_data.get("required", False),
                default=cattr_data.get("default"),
                description=cattr_data.get("description", ""),
            ))
        
        return entity
    
    def _parse_tpo_entity(self, data: Dict[str, Any]) -> TPOEntityConfig:
        """Parse TPO entity configuration."""
        entity = TPOEntityConfig(neo4j_label=data.get("neo4j_label", "TPO"))
        
        # Parse clusters
        for cluster_data in data.get("clusters", []):
            entity.clusters.append(ClusterConfig(
                id=cluster_data.get("id", ""),
                label=cluster_data.get("label", ""),
                description=cluster_data.get("description", ""),
                color=cluster_data.get("color", "#f1c40f"),
            ))
        
        # Parse attributes
        for attr_data in data.get("attributes", []):
            entity.attributes.append(AttributeConfig(
                name=attr_data.get("name", ""),
                type=attr_data.get("type", "string"),
                required=attr_data.get("required", False),
                default=attr_data.get("default"),
                description=attr_data.get("description", ""),
            ))
        
        # Parse custom attributes
        for cattr_data in data.get("custom_attributes", []):
            entity.custom_attributes.append(CustomAttributeConfig(
                id=cattr_data.get("id", ""),
                label=cattr_data.get("label", ""),
                type=cattr_data.get("type", "string"),
                required=cattr_data.get("required", False),
                default=cattr_data.get("default"),
                description=cattr_data.get("description", ""),
            ))
        
        return entity
    
    def _parse_mitigation_entity(self, data: Dict[str, Any]) -> MitigationEntityConfig:
        """Parse mitigation entity configuration."""
        entity = MitigationEntityConfig(neo4j_label=data.get("neo4j_label", "Mitigation"))
        
        # Parse types
        for type_data in data.get("types", []):
            entity.types.append(TypeConfig(
                id=type_data.get("id", ""),
                label=type_data.get("label", ""),
                description=type_data.get("description", ""),
                color=type_data.get("color", "#808080"),
                line_style=type_data.get("line_style", "solid"),
            ))
        
        # Parse statuses
        for status_data in data.get("statuses", []):
            entity.statuses.append(StatusConfig(
                id=status_data.get("id", ""),
                label=status_data.get("label", ""),
                description=status_data.get("description", ""),
                is_active=status_data.get("is_active", True),
            ))
        
        # Parse attributes
        for attr_data in data.get("attributes", []):
            entity.attributes.append(AttributeConfig(
                name=attr_data.get("name", ""),
                type=attr_data.get("type", "string"),
                required=attr_data.get("required", False),
                default=attr_data.get("default"),
                description=attr_data.get("description", ""),
            ))
        
        # Parse custom attributes
        for cattr_data in data.get("custom_attributes", []):
            entity.custom_attributes.append(CustomAttributeConfig(
                id=cattr_data.get("id", ""),
                label=cattr_data.get("label", ""),
                type=cattr_data.get("type", "string"),
                required=cattr_data.get("required", False),
                default=cattr_data.get("default"),
                description=cattr_data.get("description", ""),
            ))
        
        return entity
    
    def _parse_custom_entity(self, data: Dict[str, Any]) -> CustomEntityConfig:
        """Parse custom entity configuration."""
        entity = CustomEntityConfig(
            id=data.get("id", ""),
            label=data.get("label", ""),
            neo4j_label=data.get("neo4j_label", data.get("label", "Custom")),
            description=data.get("description", ""),
            color=data.get("color", "#808080"),
            shape=data.get("shape", "box"),
            emoji=data.get("emoji", "📦"),
            size=data.get("size", 30),
        )
        
        # Parse attributes
        for attr_data in data.get("attributes", []):
            entity.attributes.append(AttributeConfig(
                name=attr_data.get("name", ""),
                type=attr_data.get("type", "string"),
                required=attr_data.get("required", False),
                default=attr_data.get("default"),
                description=attr_data.get("description", ""),
            ))
        
        # Parse custom attributes
        for cattr_data in data.get("custom_attributes", []):
            entity.custom_attributes.append(CustomAttributeConfig(
                id=cattr_data.get("id", ""),
                label=cattr_data.get("label", ""),
                type=cattr_data.get("type", "string"),
                required=cattr_data.get("required", False),
                default=cattr_data.get("default"),
                description=cattr_data.get("description", ""),
            ))
        
        return entity
    
    def _parse_custom_relationship(self, data: Dict[str, Any]) -> CustomRelationshipConfig:
        """Parse custom relationship configuration."""
        rel = CustomRelationshipConfig(
            id=data.get("id", ""),
            label=data.get("label", ""),
            neo4j_type=data.get("neo4j_type", data.get("label", "CUSTOM").upper().replace(" ", "_")),
            description=data.get("description", ""),
            from_entity=data.get("from_entity", ""),
            to_entity=data.get("to_entity", ""),
            color=data.get("color", "#808080"),
            line_style=data.get("line_style", "solid"),
            bidirectional=data.get("bidirectional", False),
        )
        
        # Parse attributes
        for attr_data in data.get("attributes", []):
            rel.attributes.append(AttributeConfig(
                name=attr_data.get("name", ""),
                type=attr_data.get("type", "string"),
                required=attr_data.get("required", False),
                default=attr_data.get("default"),
                description=attr_data.get("description", ""),
            ))
        
        return rel
    
    def _parse_influences_rel(self, data: Dict[str, Any]) -> InfluenceRelConfig:
        """Parse influences relationship configuration."""
        rel = InfluenceRelConfig(
            neo4j_type=data.get("neo4j_type", "INFLUENCES"),
            default_confidence=data.get("default_confidence", 0.8),
        )
        
        # Parse types
        for type_data in data.get("types", []):
            rel.types.append(TypeConfig(
                id=type_data.get("id", ""),
                label=type_data.get("label", ""),
                description=type_data.get("description", ""),
                color=type_data.get("color", "#808080"),
                line_style=type_data.get("line_style", "solid"),
            ))
        
        # Parse strengths
        for str_data in data.get("strengths", []):
            rel.strengths.append(StrengthConfig(
                id=str_data.get("id", ""),
                label=str_data.get("label", ""),
                value=str_data.get("value", 0.5),
                description=str_data.get("description", ""),
                color=str_data.get("color", "#808080"),
            ))
        
        return rel
    
    def _parse_impacts_tpo_rel(self, data: Dict[str, Any]) -> TPOImpactRelConfig:
        """Parse impacts_tpo relationship configuration."""
        rel = TPOImpactRelConfig(neo4j_type=data.get("neo4j_type", "IMPACTS_TPO"))
        
        # Parse impact levels
        for il_data in data.get("impact_levels", []):
            rel.impact_levels.append(ImpactLevelConfig(
                id=il_data.get("id", ""),
                label=il_data.get("label", ""),
                value=il_data.get("value", 1),
                description=il_data.get("description", ""),
                color=il_data.get("color", "#808080"),
            ))
        
        return rel
    
    def _parse_mitigates_rel(self, data: Dict[str, Any]) -> MitigatesRelConfig:
        """Parse mitigates relationship configuration."""
        rel = MitigatesRelConfig(neo4j_type=data.get("neo4j_type", "MITIGATES"))
        
        # Parse effectiveness levels
        for eff_data in data.get("effectiveness_levels", []):
            rel.effectiveness_levels.append(EffectivenessConfig(
                id=eff_data.get("id", ""),
                label=eff_data.get("label", ""),
                reduction=eff_data.get("reduction", 0.5),
                description=eff_data.get("description", ""),
            ))
        
        return rel
    
    def _parse_analysis(self, data: Dict[str, Any]) -> AnalysisConfig:
        """Parse analysis configuration."""
        exposure_data = data.get("exposure", {})
        exposure = ExposureConfig(
            base_formula=exposure_data.get("base_formula", "likelihood * impact"),
            max_base_value=exposure_data.get("max_base_value", 100.0),
            propagation_decay=exposure_data.get("propagation_decay", 0.85),
            convergence_multiplier=exposure_data.get("convergence_multiplier", 0.2),
        )
        
        return AnalysisConfig(
            exposure=exposure,
            cache_timeout_seconds=data.get("cache_timeout_seconds", 30),
            max_influence_depth=data.get("max_influence_depth", 10),
            high_exposure_threshold_multiplier=data.get("high_exposure_threshold_multiplier", 1.2),
        )
    
    def _parse_ui(self, data: Dict[str, Any]) -> UIConfig:
        """Parse UI configuration."""
        ui = UIConfig(
            app_title=data.get("app_title", "Risk Influence Map (RIM)"),
            app_icon=data.get("app_icon", "🎯"),
            layout=data.get("layout", "wide"),
            graph_height=data.get("graph_height", "700px"),
            graph_bgcolor=data.get("graph_bgcolor", "#ffffff"),
        )
        
        # Parse tabs
        for tab_data in data.get("tabs", []):
            ui.tabs.append(TabConfig(
                id=tab_data.get("id", ""),
                label=tab_data.get("label", ""),
                icon=tab_data.get("icon", ""),
                enabled=tab_data.get("enabled", True),
            ))
        
        # Parse presets
        for preset_data in data.get("presets", []):
            ui.presets.append(PresetConfig(
                id=preset_data.get("id", ""),
                name=preset_data.get("name", ""),
                description=preset_data.get("description", ""),
                filters=preset_data.get("filters", {}),
            ))
        
        return ui
    
    def save_schema(self, schema: SchemaConfig, schema_name: str) -> Path:
        """
        Save a schema to its YAML file.
        
        Args:
            schema: SchemaConfig object to save.
            schema_name: Name of the schema directory.
            
        Returns:
            Path to the saved schema file.
        """
        schema_dir = self.schemas_dir / schema_name
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema_path = schema_dir / "schema.yaml"
        
        data = self._schema_to_dict(schema)
        
        with open(schema_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return schema_path
    
    def _schema_to_dict(self, schema: SchemaConfig) -> Dict[str, Any]:
        """Convert a SchemaConfig to a dictionary for YAML serialization."""
        result = {
            "version": schema.version,
            "name": schema.name,
            "description": schema.description,
            "entities": {
                "risk": self._risk_entity_to_dict(schema.risk),
                "tpo": self._tpo_entity_to_dict(schema.tpo),
                "mitigation": self._mitigation_entity_to_dict(schema.mitigation),
            },
            "relationships": {
                "influences": self._influences_rel_to_dict(schema.influences),
                "impacts_tpo": self._impacts_tpo_rel_to_dict(schema.impacts_tpo),
                "mitigates": self._mitigates_rel_to_dict(schema.mitigates),
            },
            "analysis": self._analysis_to_dict(schema.analysis),
            "ui": self._ui_to_dict(schema.ui),
        }
        
        # Add custom entities if any
        if schema.custom_entities:
            result["entities"]["custom_entities"] = [
                self._custom_entity_to_dict(ce) for ce in schema.custom_entities
            ]
        
        # Add custom relationships if any
        if schema.custom_relationships:
            result["relationships"]["custom_relationships"] = [
                self._custom_relationship_to_dict(cr) for cr in schema.custom_relationships
            ]
        
        return result
    
    def _risk_entity_to_dict(self, entity: RiskEntityConfig) -> Dict[str, Any]:
        """Convert RiskEntityConfig to dictionary."""
        return {
            "neo4j_label": entity.neo4j_label,
            "levels": [
                {"id": l.id, "label": l.label, "description": l.description,
                 "color": l.color, "shape": l.shape, "emoji": l.emoji, "size": l.size}
                for l in entity.levels
            ],
            "categories": [
                {"id": c.id, "label": c.label, "description": c.description, "color": c.color}
                for c in entity.categories
            ],
            "statuses": [
                {"id": s.id, "label": s.label, "description": s.description, "is_active": s.is_active}
                for s in entity.statuses
            ],
            "origins": [
                {"id": o.id, "label": o.label, "description": o.description}
                for o in entity.origins
            ],
            "attributes": [
                {"name": a.name, "type": a.type, "required": a.required,
                 "default": a.default, "description": a.description}
                for a in entity.attributes
            ],
            "custom_attributes": [
                {"id": ca.id, "label": ca.label, "type": ca.type,
                 "required": ca.required, "default": ca.default, "description": ca.description}
                for ca in entity.custom_attributes
            ],
        }
    
    def _tpo_entity_to_dict(self, entity: TPOEntityConfig) -> Dict[str, Any]:
        """Convert TPOEntityConfig to dictionary."""
        return {
            "neo4j_label": entity.neo4j_label,
            "clusters": [
                {"id": c.id, "label": c.label, "description": c.description, "color": c.color}
                for c in entity.clusters
            ],
            "attributes": [
                {"name": a.name, "type": a.type, "required": a.required,
                 "default": a.default, "description": a.description}
                for a in entity.attributes
            ],
            "custom_attributes": [
                {"id": ca.id, "label": ca.label, "type": ca.type,
                 "required": ca.required, "default": ca.default, "description": ca.description}
                for ca in entity.custom_attributes
            ],
        }
    
    def _mitigation_entity_to_dict(self, entity: MitigationEntityConfig) -> Dict[str, Any]:
        """Convert MitigationEntityConfig to dictionary."""
        return {
            "neo4j_label": entity.neo4j_label,
            "types": [
                {"id": t.id, "label": t.label, "description": t.description,
                 "color": t.color, "line_style": t.line_style}
                for t in entity.types
            ],
            "statuses": [
                {"id": s.id, "label": s.label, "description": s.description, "is_active": s.is_active}
                for s in entity.statuses
            ],
            "attributes": [
                {"name": a.name, "type": a.type, "required": a.required,
                 "default": a.default, "description": a.description}
                for a in entity.attributes
            ],
            "custom_attributes": [
                {"id": ca.id, "label": ca.label, "type": ca.type,
                 "required": ca.required, "default": ca.default, "description": ca.description}
                for ca in entity.custom_attributes
            ],
        }
    
    def _custom_entity_to_dict(self, entity: CustomEntityConfig) -> Dict[str, Any]:
        """Convert CustomEntityConfig to dictionary."""
        return {
            "id": entity.id,
            "label": entity.label,
            "neo4j_label": entity.neo4j_label,
            "description": entity.description,
            "color": entity.color,
            "shape": entity.shape,
            "emoji": entity.emoji,
            "size": entity.size,
            "attributes": [
                {"name": a.name, "type": a.type, "required": a.required,
                 "default": a.default, "description": a.description}
                for a in entity.attributes
            ],
            "custom_attributes": [
                {"id": ca.id, "label": ca.label, "type": ca.type,
                 "required": ca.required, "default": ca.default, "description": ca.description}
                for ca in entity.custom_attributes
            ],
        }
    
    def _custom_relationship_to_dict(self, rel: CustomRelationshipConfig) -> Dict[str, Any]:
        """Convert CustomRelationshipConfig to dictionary."""
        return {
            "id": rel.id,
            "label": rel.label,
            "neo4j_type": rel.neo4j_type,
            "description": rel.description,
            "from_entity": rel.from_entity,
            "to_entity": rel.to_entity,
            "color": rel.color,
            "line_style": rel.line_style,
            "bidirectional": rel.bidirectional,
            "attributes": [
                {"name": a.name, "type": a.type, "required": a.required,
                 "default": a.default, "description": a.description}
                for a in rel.attributes
            ],
        }
    
    def _influences_rel_to_dict(self, rel: InfluenceRelConfig) -> Dict[str, Any]:
        """Convert InfluenceRelConfig to dictionary."""
        return {
            "neo4j_type": rel.neo4j_type,
            "default_confidence": rel.default_confidence,
            "types": [
                {"id": t.id, "label": t.label, "description": t.description,
                 "color": t.color, "line_style": t.line_style}
                for t in rel.types
            ],
            "strengths": [
                {"id": s.id, "label": s.label, "value": s.value,
                 "description": s.description, "color": s.color}
                for s in rel.strengths
            ],
        }
    
    def _impacts_tpo_rel_to_dict(self, rel: TPOImpactRelConfig) -> Dict[str, Any]:
        """Convert TPOImpactRelConfig to dictionary."""
        return {
            "neo4j_type": rel.neo4j_type,
            "impact_levels": [
                {"id": il.id, "label": il.label, "value": il.value,
                 "description": il.description, "color": il.color}
                for il in rel.impact_levels
            ],
        }
    
    def _mitigates_rel_to_dict(self, rel: MitigatesRelConfig) -> Dict[str, Any]:
        """Convert MitigatesRelConfig to dictionary."""
        return {
            "neo4j_type": rel.neo4j_type,
            "effectiveness_levels": [
                {"id": e.id, "label": e.label, "reduction": e.reduction, "description": e.description}
                for e in rel.effectiveness_levels
            ],
        }
    
    def _analysis_to_dict(self, analysis: AnalysisConfig) -> Dict[str, Any]:
        """Convert AnalysisConfig to dictionary."""
        return {
            "exposure": {
                "base_formula": analysis.exposure.base_formula,
                "max_base_value": analysis.exposure.max_base_value,
                "propagation_decay": analysis.exposure.propagation_decay,
                "convergence_multiplier": analysis.exposure.convergence_multiplier,
            },
            "cache_timeout_seconds": analysis.cache_timeout_seconds,
            "max_influence_depth": analysis.max_influence_depth,
            "high_exposure_threshold_multiplier": analysis.high_exposure_threshold_multiplier,
        }
    
    def _ui_to_dict(self, ui: UIConfig) -> Dict[str, Any]:
        """Convert UIConfig to dictionary."""
        return {
            "app_title": ui.app_title,
            "app_icon": ui.app_icon,
            "layout": ui.layout,
            "graph_height": ui.graph_height,
            "graph_bgcolor": ui.graph_bgcolor,
            "tabs": [
                {"id": t.id, "label": t.label, "icon": t.icon, "enabled": t.enabled}
                for t in ui.tabs
            ],
            "presets": [
                {"id": p.id, "name": p.name, "description": p.description, "filters": p.filters}
                for p in ui.presets
            ],
        }
    
    def validate_schema(self, schema: SchemaConfig) -> List[str]:
        """
        Validate a schema configuration.
        
        Args:
            schema: SchemaConfig to validate.
            
        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []
        
        # Check required fields
        if not schema.name:
            errors.append("Schema name is required")
        
        # Check risk levels
        if not schema.risk.levels:
            errors.append("At least one risk level is required")
        
        for level in schema.risk.levels:
            if not level.id or not level.label:
                errors.append(f"Risk level must have id and label: {level}")
        
        # Check categories
        if not schema.risk.categories:
            errors.append("At least one risk category is required")
        
        # Check TPO clusters
        if not schema.tpo.clusters:
            errors.append("At least one TPO cluster is required")
        
        # Check influence strengths
        if not schema.influences.strengths:
            errors.append("At least one influence strength is required")
        
        # Check effectiveness levels
        if not schema.mitigates.effectiveness_levels:
            errors.append("At least one effectiveness level is required")
        
        return errors


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Global loader instance
_loader: Optional[SchemaLoader] = None


def get_loader() -> SchemaLoader:
    """Get or create the global SchemaLoader instance."""
    global _loader
    if _loader is None:
        _loader = SchemaLoader()
    return _loader


def list_schemas() -> List[str]:
    """List all available schemas."""
    return get_loader().list_schemas()


def get_schema(schema_name: str = "default") -> SchemaConfig:
    """Load and return a schema by name."""
    return get_loader().load_schema(schema_name)


def reload_schema() -> Optional[SchemaConfig]:
    """Reload the current schema from disk."""
    return get_loader().reload_schema()


def get_current_schema() -> Optional[SchemaConfig]:
    """Get the currently loaded schema."""
    return get_loader().get_current_schema()


def get_current_schema_name() -> Optional[str]:
    """Get the name of the currently loaded schema."""
    return get_loader().get_current_schema_name()


def save_schema(schema: SchemaConfig, schema_name: str) -> Path:
    """Save a schema to disk."""
    return get_loader().save_schema(schema, schema_name)


def validate_schema(schema: SchemaConfig) -> List[str]:
    """Validate a schema configuration."""
    return get_loader().validate_schema(schema)
