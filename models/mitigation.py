"""
Mitigation data model.

Represents a mitigation action or control that addresses risks.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from models.enums import MitigationType, MitigationStatus


@dataclass
class Mitigation:
    """
    Represents a mitigation in the RIM system.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Mitigation name/title
        type: Dedicated, Inherited, or Baseline
        status: Proposed, In Progress, Implemented, or Deferred
        description: Detailed description
        owner: Mitigation owner/responsible party
        source_entity: Source for inherited/baseline mitigations
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    id: str
    name: str
    type: MitigationType = MitigationType.DEDICATED
    status: MitigationStatus = MitigationStatus.PROPOSED
    description: str = ""
    owner: str = ""
    source_entity: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string type to enum if needed
        if isinstance(self.type, str):
            self.type = MitigationType(self.type)
        
        # Convert string status to enum if needed
        if isinstance(self.status, str):
            self.status = MitigationStatus(self.status)
    
    @property
    def is_implemented(self) -> bool:
        """Check if mitigation is implemented."""
        return self.status == MitigationStatus.IMPLEMENTED
    
    @property
    def is_active(self) -> bool:
        """Check if mitigation is active (implemented or in progress)."""
        return self.status in [MitigationStatus.IMPLEMENTED, MitigationStatus.IN_PROGRESS]
    
    @property
    def is_dedicated(self) -> bool:
        """Check if mitigation is program-dedicated."""
        return self.type == MitigationType.DEDICATED
    
    @property
    def type_icon(self) -> str:
        """Get emoji icon for type."""
        return self.type.icon
    
    @property
    def status_icon(self) -> str:
        """Get emoji icon for status."""
        return self.status.icon
    
    @property
    def color(self) -> str:
        """Get color code based on type."""
        return self.type.color
    
    @property
    def display_name(self) -> str:
        """Get display name with shield prefix."""
        return f"🛡️ {self.name}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": str(self.type),
            "status": str(self.status),
            "description": self.description,
            "owner": self.owner,
            "source_entity": self.source_entity,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Mitigation":
        """Create Mitigation instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", "Dedicated"),
            status=data.get("status", "Proposed"),
            description=data.get("description", ""),
            owner=data.get("owner", ""),
            source_entity=data.get("source_entity", ""),
        )
    
    @classmethod
    def from_neo4j_record(cls, record: dict) -> "Mitigation":
        """Create Mitigation instance from Neo4j query result."""
        return cls.from_dict(dict(record))
