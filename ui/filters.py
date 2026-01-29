"""
Filter Management for RIM Application.

Provides centralized filter management with presets,
filter state tracking, and query conversion.
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from config.settings import (
    RISK_LEVELS, RISK_CATEGORIES, RISK_STATUSES, RISK_ORIGINS,
    TPO_CLUSTERS, MITIGATION_TYPES, MITIGATION_STATUSES
)


@dataclass
class FilterPreset:
    """A predefined filter configuration."""
    key: str
    name: str
    description: str
    config: Dict[str, Any]


# Define all filter presets
FILTER_PRESETS: Dict[str, FilterPreset] = {
    "full_view": FilterPreset(
        key="full_view",
        name="🌐 Full View",
        description="Show all risks and TPOs (no mitigations)",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "strategic_only": FilterPreset(
        key="strategic_only",
        name="🟣 Strategic Focus",
        description="Strategic risks and TPOs only",
        config={
            "risks": {
                "levels": ["Strategic"],
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "operational_only": FilterPreset(
        key="operational_only",
        name="🔵 Operational Focus",
        description="Operational risks only, no TPOs",
        config={
            "risks": {
                "levels": ["Operational"],
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": False,
                "clusters": []
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "active_only": FilterPreset(
        key="active_only",
        name="✅ Active Risks Only",
        description="Only active risks (no contingent)",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "contingent_only": FilterPreset(
        key="contingent_only",
        name="⚠️ Contingent Risks",
        description="Only contingent/future risks",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": False,
                "clusters": []
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "risks_no_tpo": FilterPreset(
        key="risks_no_tpo",
        name="🎯 Risks Only",
        description="All risks without TPOs",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": False,
                "clusters": []
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "new_risks_only": FilterPreset(
        key="new_risks_only",
        name="🆕 New Risks Only",
        description="Program-specific new risks",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": ["New"]
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "legacy_risks_only": FilterPreset(
        key="legacy_risks_only",
        name="📜 Legacy Risks Only",
        description="Inherited/Enterprise level risks",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": ["Legacy"]
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": False,
                "types": [],
                "statuses": []
            }
        }
    ),
    "with_mitigations": FilterPreset(
        key="with_mitigations",
        name="🛡️ Risks + Mitigations",
        description="Show risks with their mitigations",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": False,
                "clusters": []
            },
            "mitigations": {
                "enabled": True,
                "types": MITIGATION_TYPES.copy(),
                "statuses": MITIGATION_STATUSES.copy()
            }
        }
    ),
    "mitigations_focus": FilterPreset(
        key="mitigations_focus",
        name="🛡️ Mitigations Focus",
        description="Focus on mitigations and mitigated risks",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": False,
                "clusters": []
            },
            "mitigations": {
                "enabled": True,
                "types": MITIGATION_TYPES.copy(),
                "statuses": ["Implemented", "In Progress"]
            }
        }
    ),
    "full_map": FilterPreset(
        key="full_map",
        name="🗺️ Full Map",
        description="Everything: Risks, TPOs, and Mitigations",
        config={
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": True,
                "types": MITIGATION_TYPES.copy(),
                "statuses": MITIGATION_STATUSES.copy()
            }
        }
    )
}


class FilterManager:
    """
    Centralized filter management for the Risk Influence Map.
    
    Handles filter state, presets, and conversion to query format.
    """
    
    # Class attribute referencing module-level presets
    PRESETS = FILTER_PRESETS
    
    def __init__(self):
        """Initialize with default filter state."""
        self.reset_to_default()
    
    def reset_to_default(self):
        """Reset filters to full map view (show everything)."""
        self.filters = {
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"],
                "origins": RISK_ORIGINS.copy()
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            },
            "mitigations": {
                "enabled": True,
                "types": MITIGATION_TYPES.copy(),
                "statuses": MITIGATION_STATUSES.copy()
            }
        }
    
    def apply_preset(self, preset_key: str) -> bool:
        """
        Apply a predefined filter preset.
        
        Args:
            preset_key: Key of the preset to apply
        
        Returns:
            True if preset was applied, False if not found
        """
        if preset_key not in FILTER_PRESETS:
            return False
        
        preset = FILTER_PRESETS[preset_key]
        config = preset.config
        
        self.filters = {
            "risks": {
                "levels": config["risks"]["levels"].copy(),
                "categories": config["risks"]["categories"].copy(),
                "statuses": config["risks"]["statuses"].copy(),
                "origins": config["risks"].get("origins", RISK_ORIGINS.copy()).copy()
            },
            "tpos": {
                "enabled": config["tpos"]["enabled"],
                "clusters": config["tpos"]["clusters"].copy()
            },
            "mitigations": {
                "enabled": config.get("mitigations", {}).get("enabled", False),
                "types": config.get("mitigations", {}).get("types", []).copy() or MITIGATION_TYPES.copy(),
                "statuses": config.get("mitigations", {}).get("statuses", []).copy() or MITIGATION_STATUSES.copy()
            }
        }
        return True
    
    # Risk filter setters
    def set_risk_levels(self, levels: List[str]):
        """Set risk level filter."""
        self.filters["risks"]["levels"] = levels
    
    def set_risk_categories(self, categories: List[str]):
        """Set risk category filter."""
        self.filters["risks"]["categories"] = categories
    
    def set_risk_statuses(self, statuses: List[str]):
        """Set risk status filter."""
        self.filters["risks"]["statuses"] = statuses
    
    def set_risk_origins(self, origins: List[str]):
        """Set risk origin filter."""
        self.filters["risks"]["origins"] = origins
    
    # TPO filter setters
    def set_tpo_enabled(self, enabled: bool):
        """Enable or disable TPO display."""
        self.filters["tpos"]["enabled"] = enabled
        if not enabled:
            self.filters["tpos"]["clusters"] = []
    
    def set_tpo_clusters(self, clusters: List[str]):
        """Set TPO cluster filter."""
        self.filters["tpos"]["clusters"] = clusters
    
    # Mitigation filter setters
    def set_mitigations_enabled(self, enabled: bool):
        """Enable or disable mitigation display."""
        self.filters["mitigations"]["enabled"] = enabled
        if not enabled:
            self.filters["mitigations"]["types"] = []
            self.filters["mitigations"]["statuses"] = []
    
    def set_mitigation_types(self, types: List[str]):
        """Set mitigation type filter."""
        self.filters["mitigations"]["types"] = types
    
    def set_mitigation_statuses(self, statuses: List[str]):
        """Set mitigation status filter."""
        self.filters["mitigations"]["statuses"] = statuses
    
    # Select/Deselect all helpers
    def select_all_levels(self):
        """Select all risk levels."""
        self.filters["risks"]["levels"] = RISK_LEVELS.copy()
    
    def deselect_all_levels(self):
        """Deselect all risk levels."""
        self.filters["risks"]["levels"] = []
    
    def select_all_categories(self):
        """Select all risk categories."""
        self.filters["risks"]["categories"] = RISK_CATEGORIES.copy()
    
    def deselect_all_categories(self):
        """Deselect all risk categories."""
        self.filters["risks"]["categories"] = []
    
    def select_all_statuses(self):
        """Select all risk statuses."""
        self.filters["risks"]["statuses"] = RISK_STATUSES.copy()
    
    def deselect_all_statuses(self):
        """Deselect all risk statuses."""
        self.filters["risks"]["statuses"] = []
    
    def select_all_origins(self):
        """Select all risk origins."""
        self.filters["risks"]["origins"] = RISK_ORIGINS.copy()
    
    def deselect_all_origins(self):
        """Deselect all risk origins."""
        self.filters["risks"]["origins"] = []
    
    def select_all_clusters(self):
        """Select all TPO clusters."""
        self.filters["tpos"]["clusters"] = TPO_CLUSTERS.copy()
    
    def deselect_all_clusters(self):
        """Deselect all TPO clusters."""
        self.filters["tpos"]["clusters"] = []
    
    def select_all_mitigation_types(self):
        """Select all mitigation types."""
        self.filters["mitigations"]["types"] = MITIGATION_TYPES.copy()
    
    def deselect_all_mitigation_types(self):
        """Deselect all mitigation types."""
        self.filters["mitigations"]["types"] = []
    
    def select_all_mitigation_statuses(self):
        """Select all mitigation statuses."""
        self.filters["mitigations"]["statuses"] = MITIGATION_STATUSES.copy()
    
    def deselect_all_mitigation_statuses(self):
        """Deselect all mitigation statuses."""
        self.filters["mitigations"]["statuses"] = []
    
    def get_filters_for_query(self) -> Dict[str, Any]:
        """
        Convert filters to format expected by database queries.
        
        Returns:
            Dictionary with query-compatible filter parameters
        """
        query_filters = {
            "show_tpos": self.filters["tpos"]["enabled"],
            "show_mitigations": self.filters.get("mitigations", {}).get("enabled", False)
        }
        
        if self.filters["risks"]["levels"]:
            query_filters["level"] = self.filters["risks"]["levels"]
        
        if self.filters["risks"]["categories"]:
            query_filters["categories"] = self.filters["risks"]["categories"]
        
        if self.filters["risks"]["statuses"]:
            query_filters["status"] = self.filters["risks"]["statuses"]
        
        if self.filters["risks"].get("origins"):
            query_filters["origins"] = self.filters["risks"]["origins"]
        
        if self.filters["tpos"]["enabled"] and self.filters["tpos"]["clusters"]:
            query_filters["tpo_clusters"] = self.filters["tpos"]["clusters"]
        
        # Mitigation filters
        if self.filters.get("mitigations", {}).get("enabled"):
            if self.filters["mitigations"].get("types"):
                query_filters["mitigation_types"] = self.filters["mitigations"]["types"]
            if self.filters["mitigations"].get("statuses"):
                query_filters["mitigation_statuses"] = self.filters["mitigations"]["statuses"]
        
        return query_filters
    
    def get_filter_summary(self) -> str:
        """
        Get a human-readable summary of current filters.
        
        Returns:
            Summary string
        """
        parts = []
        
        # Risk levels
        if len(self.filters["risks"]["levels"]) == len(RISK_LEVELS):
            parts.append("All levels")
        elif self.filters["risks"]["levels"]:
            parts.append(f"Levels: {', '.join(self.filters['risks']['levels'])}")
        else:
            parts.append("No levels selected")
        
        # Risk categories
        if len(self.filters["risks"]["categories"]) == len(RISK_CATEGORIES):
            parts.append("All categories")
        elif self.filters["risks"]["categories"]:
            parts.append(f"{len(self.filters['risks']['categories'])} categories")
        else:
            parts.append("No categories")
        
        # Risk origins
        origins = self.filters["risks"].get("origins", RISK_ORIGINS.copy())
        if len(origins) == len(RISK_ORIGINS):
            pass  # Don't show if all selected (default)
        elif origins:
            parts.append(f"Origins: {', '.join(origins)}")
        else:
            parts.append("No origins selected")
        
        # TPOs
        if self.filters["tpos"]["enabled"]:
            if len(self.filters["tpos"]["clusters"]) == len(TPO_CLUSTERS):
                parts.append("All TPOs")
            elif self.filters["tpos"]["clusters"]:
                parts.append(f"{len(self.filters['tpos']['clusters'])} TPO clusters")
            else:
                parts.append("No TPO clusters")
        else:
            parts.append("TPOs hidden")
        
        # Mitigations
        if self.filters.get("mitigations", {}).get("enabled"):
            mit_types = self.filters["mitigations"].get("types", [])
            mit_statuses = self.filters["mitigations"].get("statuses", [])
            if len(mit_types) == len(MITIGATION_TYPES) and len(mit_statuses) == len(MITIGATION_STATUSES):
                parts.append("All Mitigations")
            else:
                parts.append(f"{len(mit_types)} mit. types, {len(mit_statuses)} statuses")
        else:
            parts.append("Mitigations hidden")
        
        return " | ".join(parts)
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate current filter configuration.
        
        Returns:
            Tuple of (is_valid, message)
        """
        origins = self.filters["risks"].get("origins", RISK_ORIGINS.copy())
        has_risks = (
            len(self.filters["risks"]["levels"]) > 0 and
            len(self.filters["risks"]["categories"]) > 0 and
            len(self.filters["risks"]["statuses"]) > 0 and
            len(origins) > 0
        )
        has_tpos = (
            self.filters["tpos"]["enabled"] and
            len(self.filters["tpos"]["clusters"]) > 0
        )
        
        if not has_risks and not has_tpos:
            return False, "No data to display. Please select at least one filter option."
        
        if not has_risks and has_tpos:
            return True, "Showing TPOs only (no risk filters match)."
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert current filter state to dictionary."""
        return self.filters.copy()
    
    def from_dict(self, filters: Dict[str, Any]):
        """Load filter state from dictionary."""
        self.filters = filters.copy()


def get_preset_list() -> List[Dict[str, str]]:
    """
    Get list of presets for UI display.
    
    Returns:
        List of preset info dictionaries
    """
    return [
        {
            "key": preset.key,
            "name": preset.name,
            "description": preset.description
        }
        for preset in FILTER_PRESETS.values()
    ]


def get_preset_names() -> Dict[str, str]:
    """
    Get mapping of preset keys to names.
    
    Returns:
        Dictionary of key -> name
    """
    return {preset.key: preset.name for preset in FILTER_PRESETS.values()}
