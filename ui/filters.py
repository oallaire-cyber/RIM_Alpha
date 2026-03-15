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
        Build schema-driven presets based on entity/relationship types in the registry.
        All presets are derived from registry contents — zero hardcoded IDs.
        """
        registry = self.registry
        risk_type = registry.get_risk_type()

        # --- Always available ---
        presets = [
            FilterPreset(
                "full_view", "🌐 Full View", "Show all entities and relationships", {}
            )
        ]

        if not risk_type:
            return presets

        # --- Risks Only: disable all non-risk entities ---
        non_risk_entities = [
            eid for eid, et in registry.entity_types.items()
            if not et.is_risk_type
        ]
        presets.append(FilterPreset(
            "risks_only", "🎯 Risks Only",
            "Show only risks and their influence edges",
            {"disable_entities": non_risk_entities, "disable_rels": [
                rid for rid in registry.relationship_types
                if rid != registry.get_influence_type().id
            ]}
        ))

        # --- Level-based presets: one per defined risk level ---
        levels = risk_type.categorical_groups.get("levels", [])
        if len(levels) >= 2:
            # First level (typically Business / Strategic)
            lvl0 = levels[0]
            presets.append(FilterPreset(
                f"level_{lvl0.get('id', 'level0')}",
                f"{lvl0.get('emoji', '🔷')} {lvl0.get('label', 'Level 1')} Only",
                f"Show only {lvl0.get('label', 'level-1')} risks",
                {"risk_level_filter": [lvl0.get("label", lvl0.get("id", ""))]}
            ))
            # Second level (typically Operational)
            lvl1 = levels[1]
            presets.append(FilterPreset(
                f"level_{lvl1.get('id', 'level1')}",
                f"{lvl1.get('emoji', '⚙️')} {lvl1.get('label', 'Level 2')} Only",
                f"Show only {lvl1.get('label', 'level-2')} risks",
                {"risk_level_filter": [lvl1.get("label", lvl1.get("id", ""))]}
            ))

        # --- Active risks only (if "statuses" group exists and has an "Active" entry) ---
        statuses = risk_type.categorical_groups.get("statuses", [])
        active_labels = [
            s.get("label", s.get("id", ""))
            for s in statuses
            if s.get("id", "").lower() == "active" or s.get("label", "").lower() == "active"
        ]
        if active_labels:
            presets.append(FilterPreset(
                "active_only", "✅ Active Only",
                "Show only risks with Active status",
                {"risk_status_filter": active_labels}
            ))

        # --- No Mitigations: show risks + TPOs, hide mitigations ---
        mit_type = registry.get_mitigation_type()
        if mit_type:
            presets.append(FilterPreset(
                "no_mitigations", "🚫 Hide Mitigations",
                "Show risks and objectives, hide mitigation nodes",
                {"disable_entities": [mit_type.id]}
            ))

        return presets

    def apply_preset(self, preset_key: str) -> bool:
        """
        Apply a predefined filter preset.
        All logic is schema-driven — no hardcoded entity or relationship IDs.
        """
        registry = self.registry
        risk_type = registry.get_risk_type()

        if preset_key == "full_view":
            self.reset_to_default()
            return True

        # Find the matching preset to get its config
        preset = next((p for p in self.get_presets() if p.key == preset_key), None)
        if preset is None:
            return False

        config = preset.config
        self.reset_to_default()

        # Disable specified entities
        for eid in config.get("disable_entities", []):
            if eid in self.filters["entities"]:
                self.filters["entities"][eid]["enabled"] = False

        # Disable specified relationships
        for rid in config.get("disable_rels", []):
            if rid in self.filters["relationships"]:
                self.filters["relationships"][rid]["enabled"] = False

        # Filter risk by level
        if "risk_level_filter" in config and risk_type:
            rid = risk_type.id
            if rid in self.filters["entities"]:
                self.filters["entities"][rid]["attributes"]["levels"] = config["risk_level_filter"]

        # Filter risk by status
        if "risk_status_filter" in config and risk_type:
            rid = risk_type.id
            if rid in self.filters["entities"]:
                self.filters["entities"][rid]["attributes"]["statuses"] = config["risk_status_filter"]

        return True
    
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
        """Add a node ID to a specific active scope and persist if possible. Returns True if added."""
        added = False
        for scope in self.active_scopes:
            if scope.id == scope_id and node_id not in scope.node_ids:
                scope.node_ids.append(node_id)
                added = True
                break # Node added to active_scopes, exit loop
        
        # Also try to update the schema file if the scope exists there.
        # Use config.settings helpers (not the bare schema_loader) which know
        # the active schema name and already hold the loaded schema object.
        if added:
            try:
                from config.settings import get_active_schema, get_active_schema_name
                from config.schema_loader import save_schema
                schema = get_active_schema()
                schema_name = get_active_schema_name() or "default"
                if schema and schema.scopes:
                    for s in schema.scopes:
                        if s.id == scope_id and node_id not in s.node_ids:
                            s.node_ids.append(node_id)
                    save_schema(schema, schema_name)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to persist scope update: {e}")
                
        return added

    def remove_node_from_scope(self, scope_id: str, node_id: str) -> bool:
        """Remove a node ID from a specific active scope and persist if possible. Returns True if removed."""
        removed = False
        for scope in self.active_scopes:
            if scope.id == scope_id:
                if node_id in scope.node_ids:
                    scope.node_ids.remove(node_id)
                    removed = True
                    break # Node removed from active_scopes, exit loop
                    
        # Also try to update the schema file if the scope exists there
        if removed:
            try:
                from config.schema_loader import load_schema, save_schema
                schema = load_schema()
                if schema and schema.scopes:
                    for s in schema.scopes:
                        if s.id == scope_id and node_id in s.node_ids:
                            s.node_ids.remove(node_id)
                    save_schema(schema)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to persist scope update: {e}")
                
        return removed
    
    def get_filters_for_query(self) -> Dict[str, Any]:
        """
        Convert schema-driven filters to the flat format expected by database queries.

        Uses registry type flags (is_risk_type, is_mitigation_type) and relationship
        IDs (influences, mitigates, impacts_tpo) to map filter state — no hardcoded
        entity IDs in the mapping logic.

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
        registry = self.registry
        query_filters = {}

        # ── Risk entity (kernel, is_risk_type) ────────────────────────────────
        risk_type = registry.get_risk_type()
        if risk_type:
            risk_filters = self.filters["entities"].get(risk_type.id, {})
            if not risk_filters.get("enabled", True):
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

        # ── Mitigation entity (kernel, is_mitigation_type) ───────────────────
        mit_type = registry.get_mitigation_type()
        if mit_type:
            mit_filters = self.filters["entities"].get(mit_type.id, {})
            query_filters["show_mitigations"] = mit_filters.get("enabled", True)
            if mit_filters.get("enabled", True):
                mit_attrs = mit_filters.get("attributes", {})
                if "types" in mit_attrs:
                    query_filters["mitigation_types"] = mit_attrs["types"]
                if "statuses" in mit_attrs:
                    query_filters["mitigation_statuses"] = mit_attrs["statuses"]
        else:
            query_filters["show_mitigations"] = False

        # ── Additional entity types (TPO and any custom types) ────────────────
        for entity_id, entity_type in registry.get_additional_entity_types().items():
            entity_filters = self.filters["entities"].get(entity_id, {})
            entity_enabled = entity_filters.get("enabled", True)
            entity_attrs = entity_filters.get("attributes", {})

            if entity_id == "tpo":
                # Keep legacy flat keys for backward compatibility with db queries
                query_filters["show_tpos"] = entity_enabled
                if entity_enabled and "clusters" in entity_attrs:
                    query_filters["tpo_clusters"] = entity_attrs["clusters"]
            else:
                # Generic additional entity: show_<entity_id>
                query_filters[f"show_{entity_id}"] = entity_enabled
                if entity_enabled:
                    for group_name, values in entity_attrs.items():
                        query_filters[f"{entity_id}_{group_name}"] = values

        # ── Influence relationship (kernel) ────────────────────────────────────
        inf_type = registry.get_influence_type()
        if inf_type:
            inf_filters = self.filters["relationships"].get(inf_type.id, {})
            query_filters["show_influences"] = inf_filters.get("enabled", True)
            if inf_filters.get("enabled", True):
                inf_attrs = inf_filters.get("attributes", {})
            if "strengths" in inf_attrs:
                query_filters["influence_strengths"] = inf_attrs["strengths"]

        # ── Mitigates relationship (kernel) ────────────────────────────────────
        mit_rel_type = registry.get_mitigates_type()
        mitigates_filters = self.filters["relationships"].get(mit_rel_type.id if mit_rel_type else "mitigates", {})
        query_filters["show_mitigates"] = mitigates_filters.get("enabled", True)
        if mitigates_filters.get("enabled", True):
            mitigates_attrs = mitigates_filters.get("attributes", {})
            if "effectiveness_levels" in mitigates_attrs:
                query_filters["mitigation_effectiveness"] = mitigates_attrs["effectiveness_levels"]

        # ── Additional relationship types (impacts_tpo and any custom) ─────────
        for rel_id, rel_type in registry.get_additional_relationship_types().items():
            rel_filters = self.filters["relationships"].get(rel_id, {})
            rel_enabled = rel_filters.get("enabled", True)
            rel_attrs = rel_filters.get("attributes", {})

            if rel_id == "impacts_tpo":
                query_filters["show_tpo_impacts"] = rel_enabled
                if rel_enabled and "impact_levels" in rel_attrs:
                    query_filters["tpo_impact_levels"] = rel_attrs["impact_levels"]
            else:
                query_filters[f"show_{rel_id}"] = rel_enabled
                if rel_enabled:
                    for group_name, values in rel_attrs.items():
                        query_filters[f"{rel_id}_{group_name}"] = values

        # ── Scope filtering ────────────────────────────────────────────────────
        scope_ids = self.get_scope_node_ids()
        if scope_ids is not None:
            query_filters["scope_node_ids"] = scope_ids
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
