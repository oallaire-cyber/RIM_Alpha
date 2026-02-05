"""
TPO (Top Program Objective) data model.

Represents a program objective that risks may impact.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from models.enums import TPOCluster


@dataclass
class TPO:
    """
    Represents a Top Program Objective in the RIM system.
    
    Attributes:
        id: Unique identifier (UUID)
        reference: Short reference code (e.g., "TPO-01")
        name: TPO name/title
        cluster: Cluster category
        description: Detailed description
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    id: str
    reference: str
    name: str
    cluster: str
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Validate cluster if it's a known value
        valid_clusters = [e.value for e in TPOCluster]
        if self.cluster and self.cluster not in valid_clusters:
            # Keep the value but could log a warning
            pass
    
    @property
    def display_label(self) -> str:
        """Get display label combining reference and name."""
        return f"{self.reference}: {self.name}"
    
    @property
    def short_label(self) -> str:
        """Get short label (reference only)."""
        return self.reference
    
    @property
    def icon(self) -> str:
        """Get emoji icon for TPO."""
        return "🟡"
    
    @property
    def color(self) -> str:
        """Get color code for TPO."""
        return "#f1c40f"
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "reference": self.reference,
            "name": self.name,
            "cluster": self.cluster,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TPO":
        """Create TPO instance from dictionary."""
        return cls(
            id=data.get("id", ""),
            reference=data.get("reference", ""),
            name=data.get("name", ""),
            cluster=data.get("cluster", "Business Efficiency"),
            description=data.get("description", ""),
        )
    
    @classmethod
    def from_neo4j_record(cls, record: dict) -> "TPO":
        """Create TPO instance from Neo4j query result."""
        return cls.from_dict(dict(record))
