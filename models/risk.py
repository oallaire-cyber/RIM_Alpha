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
        level: Business or Operational
        origin: New (program-specific) or Legacy (inherited)
        categories: List of domain categories
        status: Active, Contingent, Archived, Accepted, Watching, Suppressed, or Closed
        description: Detailed risk description
        owner: Risk owner/responsible party
        probability: Probability score (0-10)
        severity: Severity score (0-10) — intrinsic intensity of the risk event
        exposure: Calculated exposure (probability × severity)
        trigger_condition: Condition string that, when met, activates a Watching/Suppressed risk
        acceptance_date: ISO date when risk was formally accepted
        acceptance_owner: Person who formally accepted the risk
        archive_date: ISO date when risk was archived
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
    severity: Optional[float] = None
    exposure: Optional[float] = None
    trigger_condition: Optional[str] = None
    acceptance_date: Optional[str] = None
    acceptance_owner: Optional[str] = None
    archive_date: Optional[str] = None
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
        if self.exposure is None and self.probability and self.severity:
            self.exposure = self.probability * self.severity

    @property
    def is_business(self) -> bool:
        """Check if risk is business level."""
        return self.level == RiskLevel.BUSINESS

    @property
    def is_operational(self) -> bool:
        """Check if risk is operational level."""
        return self.level == RiskLevel.OPERATIONAL

    @property
    def is_contingent(self) -> bool:
        """Check if risk is contingent (kept for backward compatibility)."""
        return self.status == RiskStatus.CONTINGENT

    @property
    def is_inactive(self) -> bool:
        """Check if risk is excluded from active exposure analysis."""
        from models.enums import LIFECYCLE_INACTIVE_STATUSES
        return self.status in LIFECYCLE_INACTIVE_STATUSES

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
        if self.probability is not None and self.severity is not None:
            self.exposure = self.probability * self.severity
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
            "severity": self.severity,
            "exposure": self.exposure,
            "trigger_condition": self.trigger_condition,
            "acceptance_date": self.acceptance_date,
            "acceptance_owner": self.acceptance_owner,
            "archive_date": self.archive_date,
            "current_score_type": self.current_score_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Risk":
        """Create Risk instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            level=data.get("level", "Business"),
            origin=data.get("origin", "New"),
            categories=data.get("categories", []),
            status=data.get("status", "Active"),
            description=data.get("description", ""),
            owner=data.get("owner", ""),
            probability=data.get("probability"),
            severity=data.get("severity"),
            exposure=data.get("exposure"),
            # Migration-safe fallbacks: read new key first, fall back to old key
            trigger_condition=data.get("trigger_condition") or data.get("activation_condition"),
            acceptance_date=data.get("acceptance_date") or data.get("activation_decision_date"),
            acceptance_owner=data.get("acceptance_owner"),
            archive_date=data.get("archive_date"),
            current_score_type=data.get("current_score_type", "None"),
        )

    @classmethod
    def from_neo4j_record(cls, record: dict) -> "Risk":
        """Create Risk instance from Neo4j query result."""
        return cls.from_dict(dict(record))
