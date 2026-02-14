"""
Enumeration types for RIM application.

Provides type-safe enumerations for all categorical values used in the system.

DEPRECATION WARNING:
====================
This module is DEPRECATED. The hardcoded enums here are being replaced by
schema-driven values from the SchemaRegistry.

For new code, use the schema-aware accessors in models/schema_compat.py:
    from models.schema_compat import (
        SchemaRiskLevels,
        SchemaRiskStatuses,
        SchemaInfluenceStrengths,
        # etc.
    )

The enums below are kept for backward compatibility with existing code.
They may be removed in a future version.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk hierarchy levels."""
    BUSINESS = "Business"
    OPERATIONAL = "Operational"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the level."""
        return "🟣" if self == RiskLevel.STRATEGIC else "🔵"
    
    @property
    def color(self) -> str:
        """Return color code for the level."""
        return "#9b59b6" if self == RiskLevel.STRATEGIC else "#3498db"


class RiskStatus(str, Enum):
    """Risk lifecycle statuses."""
    ACTIVE = "Active"
    CONTINGENT = "Contingent"
    ARCHIVED = "Archived"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the status."""
        icons = {
            RiskStatus.ACTIVE: "✅",
            RiskStatus.CONTINGENT: "⚠️",
            RiskStatus.ARCHIVED: "📦"
        }
        return icons.get(self, "⚪")


class RiskOrigin(str, Enum):
    """Risk origin types."""
    NEW = "New"
    LEGACY = "Legacy"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the origin."""
        return "🆕" if self == RiskOrigin.NEW else "📜"


class RiskCategory(str, Enum):
    """Risk domain categories."""
    PROGRAMME = "Programme"
    PRODUIT = "Produit"
    INDUSTRIEL = "Industriel"
    SUPPLY_CHAIN = "Supply Chain"
    
    def __str__(self) -> str:
        return self.value


class TPOCluster(str, Enum):
    """Top Program Objective cluster categories."""
    PRODUCT_EFFICIENCY = "Product Efficiency"
    BUSINESS_EFFICIENCY = "Business Efficiency"
    INDUSTRIAL_EFFICIENCY = "Industrial Efficiency"
    SUSTAINABILITY = "Sustainability"
    SAFETY = "Safety"
    
    def __str__(self) -> str:
        return self.value


class MitigationType(str, Enum):
    """Mitigation types."""
    DEDICATED = "Dedicated"
    INHERITED = "Inherited"
    BASELINE = "Baseline"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the type."""
        icons = {
            MitigationType.DEDICATED: "🟢",
            MitigationType.INHERITED: "🔵",
            MitigationType.BASELINE: "🟣"
        }
        return icons.get(self, "⚪")
    
    @property
    def color(self) -> str:
        """Return color code for the type."""
        colors = {
            MitigationType.DEDICATED: "#27ae60",
            MitigationType.INHERITED: "#3498db",
            MitigationType.BASELINE: "#9b59b6"
        }
        return colors.get(self, "#27ae60")


class MitigationStatus(str, Enum):
    """Mitigation lifecycle statuses."""
    PROPOSED = "Proposed"
    IN_PROGRESS = "In Progress"
    IMPLEMENTED = "Implemented"
    DEFERRED = "Deferred"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the status."""
        icons = {
            MitigationStatus.PROPOSED: "📋",
            MitigationStatus.IN_PROGRESS: "🔄",
            MitigationStatus.IMPLEMENTED: "✅",
            MitigationStatus.DEFERRED: "⏸️"
        }
        return icons.get(self, "⚪")


class Effectiveness(str, Enum):
    """Effectiveness levels for mitigations and impacts."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def value_score(self) -> int:
        """Return numeric score for the effectiveness."""
        scores = {
            Effectiveness.LOW: 1,
            Effectiveness.MEDIUM: 2,
            Effectiveness.HIGH: 3,
            Effectiveness.CRITICAL: 4
        }
        return scores.get(self, 2)
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the effectiveness."""
        icons = {
            Effectiveness.LOW: "🟢",
            Effectiveness.MEDIUM: "🟡",
            Effectiveness.HIGH: "🟠",
            Effectiveness.CRITICAL: "🔴"
        }
        return icons.get(self, "⚪")


class InfluenceStrength(str, Enum):
    """Influence strength levels."""
    WEAK = "Weak"
    MODERATE = "Moderate"
    STRONG = "Strong"
    CRITICAL = "Critical"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def value_score(self) -> int:
        """Return numeric score for the strength."""
        scores = {
            InfluenceStrength.WEAK: 1,
            InfluenceStrength.MODERATE: 2,
            InfluenceStrength.STRONG: 3,
            InfluenceStrength.CRITICAL: 4
        }
        return scores.get(self, 2)


class ImpactLevel(str, Enum):
    """Impact levels for TPO relationships."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def value_score(self) -> int:
        """Return numeric score for the impact."""
        scores = {
            ImpactLevel.LOW: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.HIGH: 3,
            ImpactLevel.CRITICAL: 4
        }
        return scores.get(self, 2)
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the impact level."""
        icons = {
            ImpactLevel.LOW: "🟢",
            ImpactLevel.MEDIUM: "🟡",
            ImpactLevel.HIGH: "🟠",
            ImpactLevel.CRITICAL: "🔴"
        }
        return icons.get(self, "⚪")


class InfluenceType(str, Enum):
    """Types of influence relationships between risks."""
    LEVEL1_OP_TO_BUS = "Level1_Op_to_Bus"
    LEVEL2_BUS_TO_BUS = "Level2_Bus_to_Bus"
    LEVEL3_OP_TO_OP = "Level3_Op_to_Op"
    UNKNOWN = "Unknown"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the influence type."""
        icons = {
            InfluenceType.LEVEL1_OP_TO_STRAT: "🔴",
            InfluenceType.LEVEL2_STRAT_TO_STRAT: "🟣",
            InfluenceType.LEVEL3_OP_TO_OP: "🔵",
            InfluenceType.UNKNOWN: "⚪"
        }
        return icons.get(self, "⚪")
    
    @property
    def color(self) -> str:
        """Return color code for the influence type."""
        colors = {
            InfluenceType.LEVEL1_OP_TO_STRAT: "#e74c3c",
            InfluenceType.LEVEL2_STRAT_TO_STRAT: "#9b59b6",
            InfluenceType.LEVEL3_OP_TO_OP: "#3498db",
            InfluenceType.UNKNOWN: "#95a5a6"
        }
        return colors.get(self, "#95a5a6")
    
    @classmethod
    def from_levels(cls, source_level: RiskLevel, target_level: RiskLevel) -> "InfluenceType":
        """Determine influence type based on source and target risk levels."""
        if source_level == RiskLevel.OPERATIONAL and target_level == RiskLevel.STRATEGIC:
            return cls.LEVEL1_OP_TO_STRAT
        elif source_level == RiskLevel.STRATEGIC and target_level == RiskLevel.STRATEGIC:
            return cls.LEVEL2_STRAT_TO_STRAT
        elif source_level == RiskLevel.OPERATIONAL and target_level == RiskLevel.OPERATIONAL:
            return cls.LEVEL3_OP_TO_OP
        else:
            return cls.UNKNOWN


class CoverageStatus(str, Enum):
    """Risk mitigation coverage status."""
    UNMITIGATED = "unmitigated"
    PROPOSED_ONLY = "proposed_only"
    PARTIALLY_COVERED = "partially_covered"
    WELL_COVERED = "well_covered"
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def icon(self) -> str:
        """Return emoji icon for the coverage status."""
        icons = {
            CoverageStatus.UNMITIGATED: "⚠️",
            CoverageStatus.PROPOSED_ONLY: "📋",
            CoverageStatus.PARTIALLY_COVERED: "🔶",
            CoverageStatus.WELL_COVERED: "✅"
        }
        return icons.get(self, "⚪")
    
    @property
    def label(self) -> str:
        """Return human-readable label."""
        labels = {
            CoverageStatus.UNMITIGATED: "No Mitigations",
            CoverageStatus.PROPOSED_ONLY: "Only Proposed",
            CoverageStatus.PARTIALLY_COVERED: "Partially Covered",
            CoverageStatus.WELL_COVERED: "Well Covered"
        }
        return labels.get(self, "Unknown")
