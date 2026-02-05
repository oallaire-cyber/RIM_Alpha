"""
Relationship data models.

Represents the relationships (edges) between nodes in the Risk Influence Map.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from models.enums import InfluenceType, InfluenceStrength, ImpactLevel, Effectiveness


@dataclass
class Influence:
    """
    Represents an INFLUENCES relationship between two risks.
    
    Attributes:
        id: Unique identifier (UUID)
        source_id: Source risk ID
        target_id: Target risk ID
        source_name: Source risk name (for display)
        target_name: Target risk name (for display)
        source_level: Source risk level
        target_level: Target risk level
        influence_type: Type determined by source/target levels
        strength: Influence strength
        confidence: Confidence score (0-1)
        description: Description of the influence
        created_at: Creation timestamp
        last_validated: Last validation timestamp
    """
    
    id: str
    source_id: str
    target_id: str
    influence_type: InfluenceType = InfluenceType.UNKNOWN
    strength: InfluenceStrength = InfluenceStrength.MODERATE
    confidence: float = 0.8
    source_name: str = ""
    target_name: str = ""
    source_level: str = ""
    target_level: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    last_validated: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string influence_type to enum if needed
        if isinstance(self.influence_type, str):
            try:
                self.influence_type = InfluenceType(self.influence_type)
            except ValueError:
                # Handle legacy format like "Level1_Op_to_Strat"
                for it in InfluenceType:
                    if it.value in self.influence_type or self.influence_type in it.value:
                        self.influence_type = it
                        break
                else:
                    self.influence_type = InfluenceType.UNKNOWN
        
        # Convert string strength to enum if needed
        if isinstance(self.strength, str):
            self.strength = InfluenceStrength(self.strength)
    
    @property
    def strength_score(self) -> int:
        """Get numeric score for strength."""
        return self.strength.value_score
    
    @property
    def weighted_score(self) -> float:
        """Get weighted score (strength × confidence)."""
        return self.strength_score * self.confidence
    
    @property
    def type_icon(self) -> str:
        """Get emoji icon for influence type."""
        return self.influence_type.icon
    
    @property
    def color(self) -> str:
        """Get color code for influence type."""
        return self.influence_type.color
    
    @property
    def display_label(self) -> str:
        """Get display label."""
        return f"{self.source_name} → {self.target_name}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "source_name": self.source_name,
            "target_name": self.target_name,
            "source_level": self.source_level,
            "target_level": self.target_level,
            "influence_type": str(self.influence_type),
            "strength": str(self.strength),
            "confidence": self.confidence,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Influence":
        """Create Influence instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            source_id=data.get("source_id", ""),
            target_id=data.get("target_id", ""),
            source_name=data.get("source_name", ""),
            target_name=data.get("target_name", ""),
            source_level=data.get("source_level", ""),
            target_level=data.get("target_level", ""),
            influence_type=data.get("influence_type", "Unknown"),
            strength=data.get("strength", "Moderate"),
            confidence=data.get("confidence", 0.8),
            description=data.get("description", ""),
        )
    
    @classmethod
    def from_neo4j_record(cls, record: dict) -> "Influence":
        """Create Influence instance from Neo4j query result."""
        return cls.from_dict(dict(record))


@dataclass
class TPOImpact:
    """
    Represents an IMPACTS_TPO relationship between a strategic risk and a TPO.
    
    Attributes:
        id: Unique identifier (UUID)
        risk_id: Risk ID
        tpo_id: TPO ID
        risk_name: Risk name (for display)
        tpo_reference: TPO reference (for display)
        tpo_name: TPO name (for display)
        impact_level: Impact level
        description: Description of the impact
        created_at: Creation timestamp
    """
    
    id: str
    risk_id: str
    tpo_id: str
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    risk_name: str = ""
    tpo_reference: str = ""
    tpo_name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string impact_level to enum if needed
        if isinstance(self.impact_level, str):
            self.impact_level = ImpactLevel(self.impact_level)
    
    @property
    def impact_score(self) -> int:
        """Get numeric score for impact level."""
        return self.impact_level.value_score
    
    @property
    def impact_icon(self) -> str:
        """Get emoji icon for impact level."""
        return self.impact_level.icon
    
    @property
    def display_label(self) -> str:
        """Get display label."""
        return f"{self.risk_name} → {self.tpo_reference}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "risk_id": self.risk_id,
            "tpo_id": self.tpo_id,
            "risk_name": self.risk_name,
            "tpo_reference": self.tpo_reference,
            "tpo_name": self.tpo_name,
            "impact_level": str(self.impact_level),
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TPOImpact":
        """Create TPOImpact instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            risk_id=data.get("risk_id", ""),
            tpo_id=data.get("tpo_id", ""),
            risk_name=data.get("risk_name", ""),
            tpo_reference=data.get("tpo_reference", ""),
            tpo_name=data.get("tpo_name", ""),
            impact_level=data.get("impact_level", "Medium"),
            description=data.get("description", ""),
        )
    
    @classmethod
    def from_neo4j_record(cls, record: dict) -> "TPOImpact":
        """Create TPOImpact instance from Neo4j query result."""
        return cls.from_dict(dict(record))


@dataclass
class MitigatesRelationship:
    """
    Represents a MITIGATES relationship between a mitigation and a risk.
    
    Attributes:
        id: Unique identifier (UUID)
        mitigation_id: Mitigation ID
        risk_id: Risk ID
        mitigation_name: Mitigation name (for display)
        mitigation_type: Mitigation type (for display)
        risk_name: Risk name (for display)
        risk_level: Risk level (for display)
        effectiveness: Effectiveness level
        description: Description of how mitigation addresses risk
        created_at: Creation timestamp
    """
    
    id: str
    mitigation_id: str
    risk_id: str
    effectiveness: Effectiveness = Effectiveness.MEDIUM
    mitigation_name: str = ""
    mitigation_type: str = ""
    risk_name: str = ""
    risk_level: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string effectiveness to enum if needed
        if isinstance(self.effectiveness, str):
            self.effectiveness = Effectiveness(self.effectiveness)
    
    @property
    def effectiveness_score(self) -> int:
        """Get numeric score for effectiveness."""
        return self.effectiveness.value_score
    
    @property
    def effectiveness_icon(self) -> str:
        """Get emoji icon for effectiveness."""
        return self.effectiveness.icon
    
    @property
    def display_label(self) -> str:
        """Get display label."""
        return f"{self.mitigation_name} → {self.risk_name}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "mitigation_id": self.mitigation_id,
            "risk_id": self.risk_id,
            "mitigation_name": self.mitigation_name,
            "mitigation_type": self.mitigation_type,
            "risk_name": self.risk_name,
            "risk_level": self.risk_level,
            "effectiveness": str(self.effectiveness),
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MitigatesRelationship":
        """Create MitigatesRelationship instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            mitigation_id=data.get("mitigation_id", ""),
            risk_id=data.get("risk_id", ""),
            mitigation_name=data.get("mitigation_name", ""),
            mitigation_type=data.get("mitigation_type", ""),
            risk_name=data.get("risk_name", ""),
            risk_level=data.get("risk_level", ""),
            effectiveness=data.get("effectiveness", "Medium"),
            description=data.get("description", ""),
        )
    
    @classmethod
    def from_neo4j_record(cls, record: dict) -> "MitigatesRelationship":
        """Create MitigatesRelationship instance from Neo4j query result."""
        return cls.from_dict(dict(record))
