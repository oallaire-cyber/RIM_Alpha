"""
Filter Management for RIM Application.

Provides centralized filter management with presets,
filter state tracking, and query conversion.
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
import warnings
from core import get_registry


@dataclass
class FilterPreset:
    """A predefined filter configuration."""
    key: str
    name: str
    description: str
    config: Dict[str, Any]


class FilterManager:
    """
    Centralized filter management for the Risk Influence Map.
    
    Handles filter state, presets, and conversion to query format.
    Now schema-driven, discovering filterable types from registry.
    """
    
    def __init__(self, registry=None):
        """Initialize with default filter state."""
        self._registry = registry or get_registry()
        self.active_scopes = []  # List of AnalysisScopeConfig
        self.reset_to_default()
    
    @property
    def registry(self):
        return self._registry or get_registry()
    
    def reset_to_default(self):
        """Reset filters to full map view (show everything)."""
        registry = self.registry
        
        self.filters = {
            "entities": {},      # type_id -> {attr_id -> List[values]}
            "relationships": {}, # type_id -> {enabled: bool, attr_id -> List[values]}
        }
        
        # Initialize entity filters
        for entity_id, entity_type in registry.entity_types.items():
            self.filters["entities"][entity_id] = {
                "enabled": True,
                "attributes": {}
            }
            # Add filters for categorical groups (levels, categories, statuses, etc.)
            for group_name, group_items in entity_type.categorical_groups.items():
                if group_items:
                    # Extract labels from group items
                    choices = [item.get("label", item.get("id", "")) for item in group_items]
                    if choices:
                        self.filters["entities"][entity_id]["attributes"][group_name] = choices
        
        # Initialize relationship filters
        for rel_id, rel_type in registry.relationship_types.items():
            self.filters["relationships"][rel_id] = {
                "enabled": True,
                "attributes": {}
            }
            # Add filters for categorical groups
            for group_name, group_items in rel_type.categorical_groups.items():
                if group_items:
                    choices = [item.get("label", item.get("id", "")) for item in group_items]
                    if choices:
                        self.filters["relationships"][rel_id]["attributes"][group_name] = choices
    
    def get_presets(self) -> List[FilterPreset]:
        """
        Get list of available presets.
        In the future, these could also come from the schema.
        """
        registry = self.registry
        risk_type = registry.get_risk_type()
        
        # Basic presets that work with any schema
        presets = [
            FilterPreset(
                "full_view", "🌐 Full View", "Show all entities and relationships",
                {} # Config applied by resetting
            )
        ]
        
        # Add a "Risk Only" preset if risk exists
        if risk_type:
            presets.append(FilterPreset(
                "risks_only", "🎯 Risks Only", "Show only risks and their influences",
                {"entities": {risk_type.id: {"enabled": True}}, "hide_others": True}
            ))
            
        return presets

    def apply_preset(self, preset_key: str) -> bool:
        """Apply a predefined filter preset."""
        if preset_key == "full_view":
            self.reset_to_default()
            return True
        
        if preset_key == "risks_only":
            # Keep risks enabled, disable everything else
            self.reset_to_default()
            for entity_id in self.filters["entities"]:
                if entity_id == "risk":
                    self.filters["entities"][entity_id]["enabled"] = True
                else:
                    self.filters["entities"][entity_id]["enabled"] = False
            return True
            
        return False
    
    # Generic setters for schema-driven UI
    def set_entity_enabled(self, entity_id: str, enabled: bool):
        if entity_id in self.filters["entities"]:
            self.filters["entities"][entity_id]["enabled"] = enabled
            
    def set_entity_attribute_filter(self, entity_id: str, attr_id: str, values: List[Any]):
        if entity_id in self.filters["entities"]:
            self.filters["entities"][entity_id]["attributes"][attr_id] = values
            
    def set_relationship_enabled(self, rel_id: str, enabled: bool):
        if rel_id in self.filters["relationships"]:
            self.filters["relationships"][rel_id]["enabled"] = enabled

    def set_relationship_attribute_filter(self, rel_id: str, attr_id: str, values: List[Any]):
        if rel_id in self.filters["relationships"]:
            self.filters["relationships"][rel_id]["attributes"][attr_id] = values
    
    # ── Scope management ────────────────────────────────────────────────
    
    def set_active_scopes(self, scopes: list):
        """Set the active analysis scopes. Accepts list of AnalysisScopeConfig."""
        self.active_scopes = list(scopes)
    
    def clear_scopes(self):
        """Remove all active scopes (show full graph)."""
        self.active_scopes = []
    
    def get_scope_node_ids(self) -> Optional[List[str]]:
        """Get the union of all active scope node IDs, or None if no scope active."""
        if not self.active_scopes:
            return None
        ids = set()
        for scope in self.active_scopes:
            ids.update(scope.node_ids)
        return list(ids)
    
    def add_node_to_scope(self, scope_id: str, node_id: str) -> bool:
        """Add a node ID to a specific active scope. Returns True if added."""
        for scope in self.active_scopes:
            if scope.id == scope_id and node_id not in scope.node_ids:
                scope.node_ids.append(node_id)
                return True
        return False
    
    def remove_node_from_scope(self, scope_id: str, node_id: str) -> bool:
        """Remove a node ID from a specific active scope. Returns True if removed."""
        for scope in self.active_scopes:
            if scope.id == scope_id and node_id in scope.node_ids:
                scope.node_ids.remove(node_id)
                return True
        return False
    
    def get_filters_for_query(self) -> Dict[str, Any]:
        """
        Convert schema-driven filters to the flat format expected by database queries.
        
        The database queries expect:
            - level: List of risk levels
            - categories: List of categories
            - status: List of statuses
            - origins: List of origins
            - show_tpos: Boolean
            - tpo_clusters: List of TPO clusters
            - show_mitigations: Boolean
            - mitigation_types: List of mitigation types
            - mitigation_statuses: List of mitigation statuses
            - show_influences: Boolean
            - show_tpo_impacts: Boolean
            - show_mitigates: Boolean
        """
        query_filters = {}
        
        # Risk entity filters
        risk_filters = self.filters["entities"].get("risk", {})
        if not risk_filters.get("enabled", True):
            # If risks are disabled, return empty level filter (no risks shown)
            query_filters["level"] = []
        else:
            risk_attrs = risk_filters.get("attributes", {})
            if "levels" in risk_attrs:
                query_filters["level"] = risk_attrs["levels"]
            if "categories" in risk_attrs:
                query_filters["categories"] = risk_attrs["categories"]
            if "statuses" in risk_attrs:
                query_filters["status"] = risk_attrs["statuses"]
            if "origins" in risk_attrs:
                query_filters["origins"] = risk_attrs["origins"]
        
        # TPO entity filters
        tpo_filters = self.filters["entities"].get("tpo", {})
        query_filters["show_tpos"] = tpo_filters.get("enabled", True)
        if tpo_filters.get("enabled", True):
            tpo_attrs = tpo_filters.get("attributes", {})
            if "clusters" in tpo_attrs:
                query_filters["tpo_clusters"] = tpo_attrs["clusters"]
        
        # Mitigation entity filters
        mit_filters = self.filters["entities"].get("mitigation", {})
        query_filters["show_mitigations"] = mit_filters.get("enabled", True)
        if mit_filters.get("enabled", True):
            mit_attrs = mit_filters.get("attributes", {})
            if "types" in mit_attrs:
                query_filters["mitigation_types"] = mit_attrs["types"]
            if "statuses" in mit_attrs:
                query_filters["mitigation_statuses"] = mit_attrs["statuses"]
        
        # Relationship filters
        influences_filters = self.filters["relationships"].get("influences", {})
        query_filters["show_influences"] = influences_filters.get("enabled", True)
        if influences_filters.get("enabled", True):
            influences_attrs = influences_filters.get("attributes", {})
            if "strengths" in influences_attrs:
                query_filters["influence_strengths"] = influences_attrs["strengths"]
        
        impacts_tpo_filters = self.filters["relationships"].get("impacts_tpo", {})
        query_filters["show_tpo_impacts"] = impacts_tpo_filters.get("enabled", True)
        if impacts_tpo_filters.get("enabled", True):
            impacts_attrs = impacts_tpo_filters.get("attributes", {})
            if "impact_levels" in impacts_attrs:
                query_filters["tpo_impact_levels"] = impacts_attrs["impact_levels"]
        
        mitigates_filters = self.filters["relationships"].get("mitigates", {})
        query_filters["show_mitigates"] = mitigates_filters.get("enabled", True)
        if mitigates_filters.get("enabled", True):
            mitigates_attrs = mitigates_filters.get("attributes", {})
            if "effectiveness_levels" in mitigates_attrs:
                query_filters["mitigation_effectiveness"] = mitigates_attrs["effectiveness_levels"]
        
        # Scope filtering — pass scope_node_ids if any scope is active
        scope_ids = self.get_scope_node_ids()
        if scope_ids is not None:
            query_filters["scope_node_ids"] = scope_ids
            # Check session state for neighbor expansion toggle
            try:
                import streamlit as st
                query_filters["scope_include_neighbors"] = st.session_state.get("scope_include_neighbors", False)
            except Exception:
                pass
        
        return query_filters
    
    def get_filter_summary(self) -> str:
        """Get a human-readable summary of current filters."""
        enabled_entities = [e_id for e_id, f in self.filters["entities"].items() if f["enabled"]]
        enabled_rels = [r_id for r_id, f in self.filters["relationships"].items() if f["enabled"]]
        
        scope_text = ""
        if self.active_scopes:
            scope_names = [s.name for s in self.active_scopes]
            scope_text = f" | Scopes: {', '.join(scope_names)}"
        
        return f"Entities: {len(enabled_entities)} | Relationships: {len(enabled_rels)}{scope_text}"
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate current filter configuration."""
        if not any(f["enabled"] for f in self.filters["entities"].values()):
            return False, "Please select at least one entity type to display."
        return True, None


# Backward compatibility functions
def get_preset_list() -> List[Dict[str, str]]:
    """Get list of presets for UI display."""
    manager = FilterManager()
    return [
        {
            "key": p.key,
            "name": p.name,
            "description": p.description
        }
        for p in manager.get_presets()
    ]


def get_preset_names() -> Dict[str, str]:
    """Get mapping of preset keys to names."""
    manager = FilterManager()
    return {p.key: p.name for p in manager.get_presets()}


# Backward-compatible constant (DEPRECATED: use FilterManager.get_presets())
# This is a static snapshot; new code should use get_preset_list() or FilterManager
FILTER_PRESETS: Dict[str, FilterPreset] = {}

def _init_filter_presets():
    """Initialize the FILTER_PRESETS dict for backward compatibility."""
    global FILTER_PRESETS
    try:
        manager = FilterManager()
        FILTER_PRESETS = {p.key: p for p in manager.get_presets()}
    except Exception:
        # If schema not loaded yet, provide minimal defaults
        FILTER_PRESETS = {
            "full_view": FilterPreset("full_view", "🌐 Full View", "Show all", {})
        }

# Initialize on import (lazy, will re-init if schema changes)
_init_filter_presets()
