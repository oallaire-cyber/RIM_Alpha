"""
Schema-aware compatibility layer for enumeration types.

This module provides schema-driven replacements for the hardcoded enums,
while maintaining backward compatibility with existing code.

DEPRECATION NOTICE:
The enums in models/enums.py are deprecated. Use these schema-aware
accessors instead, which dynamically retrieve values from the loaded schema.
"""

from typing import List, Dict, Any, Optional
from functools import lru_cache
import warnings


def _get_registry():
    """Get the schema registry, importing lazily."""
    from core import get_registry
    return get_registry()


# =============================================================================
# RISK LEVELS (Dynamic)
# =============================================================================

class SchemaRiskLevels:
    """
    Schema-driven risk level accessor.
    
    Replaces the hardcoded RiskLevel enum with dynamic values from schema.
    
    Usage:
        levels = SchemaRiskLevels()
        for level in levels:
            print(level)
        
        # Or access specific levels
        levels.get_by_id("operational")  # -> {"id": "operational", "label": "Operational", ...}
    """
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def __iter__(self):
        """Iterate over all risk levels."""
        return iter(self.all())
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all risk levels from schema."""
        return self.registry.get_risk_levels()
    
    def labels(self) -> List[str]:
        """Get all level labels (e.g., ['Strategic', 'Operational'])."""
        return self.registry.get_risk_level_labels()
    
    def ids(self) -> List[str]:
        """Get all level IDs (e.g., ['strategic', 'operational'])."""
        return self.registry.get_risk_level_ids()
    
    def get_by_id(self, level_id: str) -> Optional[Dict[str, Any]]:
        """Get level details by ID."""
        for level in self.all():
            if level.get("id", "").lower() == level_id.lower():
                return level
        return None
    
    def get_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        """Get level details by label."""
        for level in self.all():
            if level.get("label", "").lower() == label.lower():
                return level
        return None


# =============================================================================
# RISK STATUSES (Dynamic)
# =============================================================================

class SchemaRiskStatuses:
    """Schema-driven risk status accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all risk statuses from schema."""
        risk_type = self.registry.get_risk_type()
        return risk_type.categorical_groups.get("statuses", [])
    
    def labels(self) -> List[str]:
        """Get all status labels."""
        return [s.get("label", s.get("id")) for s in self.all()]
    
    def get_by_id(self, status_id: str) -> Optional[Dict[str, Any]]:
        """Get status by ID."""
        for status in self.all():
            if status.get("id", "").lower() == status_id.lower():
                return status
        return None


# =============================================================================
# RISK CATEGORIES (Dynamic)
# =============================================================================

class SchemaRiskCategories:
    """Schema-driven risk category accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all risk categories from schema."""
        risk_type = self.registry.get_risk_type()
        return risk_type.categorical_groups.get("categories", [])
    
    def labels(self) -> List[str]:
        """Get all category labels."""
        return [c.get("label", c.get("id")) for c in self.all()]


# =============================================================================
# MITIGATION TYPES (Dynamic)
# =============================================================================

class SchemaMitigationTypes:
    """Schema-driven mitigation type accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all mitigation types from schema."""
        mit_type = self.registry.get_mitigation_type()
        return mit_type.categorical_groups.get("types", [])
    
    def labels(self) -> List[str]:
        """Get all type labels."""
        return [t.get("label", t.get("id")) for t in self.all()]


# =============================================================================
# MITIGATION STATUSES (Dynamic)
# =============================================================================

class SchemaMitigationStatuses:
    """Schema-driven mitigation status accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all mitigation statuses from schema."""
        mit_type = self.registry.get_mitigation_type()
        return mit_type.categorical_groups.get("statuses", [])
    
    def labels(self) -> List[str]:
        """Get all status labels."""
        return [s.get("label", s.get("id")) for s in self.all()]


# =============================================================================
# INFLUENCE STRENGTHS (Dynamic)
# =============================================================================

class SchemaInfluenceStrengths:
    """Schema-driven influence strength accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all influence strengths from schema."""
        return self.registry.get_influence_strengths()
    
    def labels(self) -> List[str]:
        """Get all strength labels."""
        return [s.get("label", s.get("id")) for s in self.all()]
    
    def get_score(self, strength_label: str) -> int:
        """Get numeric score for a strength."""
        for strength in self.all():
            if strength.get("label", strength.get("id")) == strength_label:
                return strength.get("value_score", 2)
        return 2


# =============================================================================
# INFLUENCE TYPES (Dynamic)
# =============================================================================

class SchemaInfluenceTypes:
    """Schema-driven influence type accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all influence types from schema."""
        return self.registry.get_influence_types()
    
    def labels(self) -> List[str]:
        """Get all type labels."""
        return [t.get("label", t.get("id")) for t in self.all()]
    
    def from_levels(self, source_level: str, target_level: str) -> Optional[str]:
        """
        Determine influence type from source and target levels.
        
        Uses schema constraints to find the appropriate type.
        """
        influence_type = self.registry.get_influence_type()
        return influence_type.get_influence_type_for_levels(source_level, target_level)


# =============================================================================
# EFFECTIVENESS LEVELS (Dynamic)
# =============================================================================

class SchemaEffectivenessLevels:
    """Schema-driven effectiveness level accessor."""
    
    def __init__(self, registry=None):
        self._registry = registry
    
    @property
    def registry(self):
        return self._registry or _get_registry()
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all effectiveness levels from schema."""
        mitigates_type = self.registry.get_mitigates_type()
        return mitigates_type.categorical_groups.get("effectiveness_levels", [])
    
    def labels(self) -> List[str]:
        """Get all effectiveness labels."""
        return [e.get("label", e.get("id")) for e in self.all()]
    
    def get_score(self, effectiveness_label: str) -> int:
        """Get numeric score for an effectiveness level."""
        for eff in self.all():
            if eff.get("label", eff.get("id")) == effectiveness_label:
                return eff.get("value_score", 2)
        return 2


# =============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# =============================================================================

def get_risk_level_values() -> List[str]:
    """
    Get risk level values for backward compatibility.
    
    DEPRECATED: Use SchemaRiskLevels().labels() instead.
    """
    warnings.warn(
        "get_risk_level_values() is deprecated. Use SchemaRiskLevels().labels()",
        DeprecationWarning,
        stacklevel=2
    )
    return SchemaRiskLevels().labels()


def get_risk_status_values() -> List[str]:
    """
    Get risk status values for backward compatibility.
    
    DEPRECATED: Use SchemaRiskStatuses().labels() instead.
    """
    warnings.warn(
        "get_risk_status_values() is deprecated. Use SchemaRiskStatuses().labels()",
        DeprecationWarning,
        stacklevel=2
    )
    return SchemaRiskStatuses().labels()


def get_risk_category_values() -> List[str]:
    """
    Get risk category values for backward compatibility.
    
    DEPRECATED: Use SchemaRiskCategories().labels() instead.
    """
    warnings.warn(
        "get_risk_category_values() is deprecated. Use SchemaRiskCategories().labels()",
        DeprecationWarning,
        stacklevel=2
    )
    return SchemaRiskCategories().labels()


def get_mitigation_type_values() -> List[str]:
    """
    Get mitigation type values for backward compatibility.
    
    DEPRECATED: Use SchemaMitigationTypes().labels() instead.
    """
    warnings.warn(
        "get_mitigation_type_values() is deprecated. Use SchemaMitigationTypes().labels()",
        DeprecationWarning,
        stacklevel=2
    )
    return SchemaMitigationTypes().labels()


def get_influence_strength_values() -> List[str]:
    """
    Get influence strength values for backward compatibility.
    
    DEPRECATED: Use SchemaInfluenceStrengths().labels() instead.
    """
    warnings.warn(
        "get_influence_strength_values() is deprecated. Use SchemaInfluenceStrengths().labels()",
        DeprecationWarning,
        stacklevel=2
    )
    return SchemaInfluenceStrengths().labels()


# =============================================================================
# GLOBAL ACCESSORS (Convenience)
# =============================================================================

# Create singleton instances for easy access
risk_levels = SchemaRiskLevels()
risk_statuses = SchemaRiskStatuses()
risk_categories = SchemaRiskCategories()
mitigation_types = SchemaMitigationTypes()
mitigation_statuses = SchemaMitigationStatuses()
influence_strengths = SchemaInfluenceStrengths()
influence_types = SchemaInfluenceTypes()
effectiveness_levels = SchemaEffectivenessLevels()
