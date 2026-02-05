"""
Risk data model.

Represents a risk entity in the Risk Influence Map system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from models.enums import RiskLevel, RiskStatus, RiskOrigin


@dataclass
class Risk:
    """
    Represents a risk in the RIM system.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Risk name/title
        level: Strategic or Operational
        origin: New (program-specific) or Legacy (inherited)
        categories: List of domain categories
        status: Active, Contingent, or Archived
        description: Detailed risk description
        owner: Risk owner/responsible party
        probability: Probability score (0-10)
        impact: Impact score (0-10)
        exposure: Calculated exposure (probability × impact)
        activation_condition: Condition for contingent risks
        activation_decision_date: Decision date for contingent risks
        current_score_type: Type of scoring used
        created_at: Creation timestamp
        updated_at: Last update timestamp
        last_review_date: Last review date
        next_review_date: Next scheduled review date
    """
    
    id: str
    name: str
    level: RiskLevel
    categories: List[str] = field(default_factory=list)
    status: RiskStatus = RiskStatus.ACTIVE
    origin: RiskOrigin = RiskOrigin.NEW
    description: str = ""
    owner: str = ""
    probability: Optional[float] = None
    impact: Optional[float] = None
    exposure: Optional[float] = None
    activation_condition: Optional[str] = None
    activation_decision_date: Optional[str] = None
    current_score_type: str = "None"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_review_date: Optional[str] = None
    next_review_date: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string level to enum if needed
        if isinstance(self.level, str):
            self.level = RiskLevel(self.level)
        
        # Convert string status to enum if needed
        if isinstance(self.status, str):
            self.status = RiskStatus(self.status)
        
        # Convert string origin to enum if needed
        if isinstance(self.origin, str):
            self.origin = RiskOrigin(self.origin)
        
        # Calculate exposure if not provided
        if self.exposure is None and self.probability and self.impact:
            self.exposure = self.probability * self.impact
    
    @property
    def is_strategic(self) -> bool:
        """Check if risk is strategic level."""
        return self.level == RiskLevel.STRATEGIC
    
    @property
    def is_operational(self) -> bool:
        """Check if risk is operational level."""
        return self.level == RiskLevel.OPERATIONAL
    
    @property
    def is_contingent(self) -> bool:
        """Check if risk is contingent."""
        return self.status == RiskStatus.CONTINGENT
    
    @property
    def is_legacy(self) -> bool:
        """Check if risk is legacy/inherited."""
        return self.origin == RiskOrigin.LEGACY
    
    @property
    def level_icon(self) -> str:
        """Get emoji icon for level."""
        return self.level.icon
    
    @property
    def origin_icon(self) -> str:
        """Get emoji icon for origin."""
        return self.origin.icon
    
    @property
    def display_name(self) -> str:
        """Get display name with legacy prefix if applicable."""
        if self.is_legacy:
            return f"[L] {self.name}"
        return self.name
    
    def calculate_exposure(self) -> Optional[float]:
        """Calculate and return exposure score."""
        if self.probability is not None and self.impact is not None:
            self.exposure = self.probability * self.impact
            return self.exposure
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "level": str(self.level),
            "origin": str(self.origin),
            "categories": self.categories,
            "status": str(self.status),
            "description": self.description,
            "owner": self.owner,
            "probability": self.probability,
            "impact": self.impact,
            "exposure": self.exposure,
            "activation_condition": self.activation_condition,
            "activation_decision_date": self.activation_decision_date,
            "current_score_type": self.current_score_type,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Risk":
        """Create Risk instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            level=data.get("level", "Strategic"),
            origin=data.get("origin", "New"),
            categories=data.get("categories", []),
            status=data.get("status", "Active"),
            description=data.get("description", ""),
            owner=data.get("owner", ""),
            probability=data.get("probability"),
            impact=data.get("impact"),
            exposure=data.get("exposure"),
            activation_condition=data.get("activation_condition"),
            activation_decision_date=data.get("activation_decision_date"),
            current_score_type=data.get("current_score_type", "None"),
        )
    
    @classmethod
    def from_neo4j_record(cls, record: dict) -> "Risk":
        """Create Risk instance from Neo4j query result."""
        return cls.from_dict(dict(record))
