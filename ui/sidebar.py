"""
Filter Sidebar for RIM Application (schema-driven).

render_filter_sidebar is a legacy entry point that delegates to the
schema-driven render_visualization_filters in home.py.  New code should
call render_visualization_filters directly.  This module is kept for
backward compatibility with any external callers.
"""

from typing import Dict, List, Any, Optional, Callable
from ui.filters import FilterManager
from core import get_registry


def render_filter_sidebar(
    filter_manager: FilterManager,
    on_filter_change: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Render the complete filter sidebar using Streamlit (schema-driven).

    Iterates all entity and relationship types from the active registry —
    no hardcoded IDs or constant imports.  Replaces the previous
    implementation that used the legacy filters["risks"] API.

    Args:
        filter_manager: FilterManager instance to update
        on_filter_change: Optional callback when filters change

    Returns:
        Dictionary with current filter state (query format)
    """
    import streamlit as st

    registry = get_registry()

    st.sidebar.header("\U0001f39b\ufe0f Filters")

    # ── Preset buttons ───────────────────────────────────────────────────────
    with st.sidebar.expander("\u26a1 Quick Presets", expanded=False):
        presets = filter_manager.get_presets()
        cols = st.columns(2)
        for i, preset in enumerate(presets):
            with cols[i % 2]:
                if st.button(preset.name, key=f"sidebar_preset_{preset.key}",
                             use_container_width=True, help=preset.description):
                    filter_manager.apply_preset(preset.key)
                    if on_filter_change:
                        on_filter_change()
                    st.rerun()

    st.sidebar.divider()

    # ── Kernel entity: risk ───────────────────────────────────────────────────
    risk_type = registry.get_risk_type()
    if risk_type:
        with st.sidebar.expander(
            f"{risk_type.emoji} {risk_type.label} Filters", expanded=True
        ):
            _render_entity_sidebar(filter_manager, risk_type.id, risk_type, st)

    # ── Kernel entity: mitigation ─────────────────────────────────────────────
    mit_type = registry.get_mitigation_type()
    if mit_type:
        with st.sidebar.expander(
            f"{mit_type.emoji} {mit_type.label} Filters", expanded=False
        ):
            _render_entity_sidebar(filter_manager, mit_type.id, mit_type, st)

    # ── Kernel relationships ──────────────────────────────────────────────────
    for rel_type in [registry.get_influence_type(), registry.get_mitigates_type()]:
        if rel_type:
            with st.sidebar.expander(f"\U0001f517 {rel_type.label} Filters", expanded=False):
                _render_relationship_sidebar(filter_manager, rel_type.id, rel_type, st)

    st.sidebar.divider()

    # ── Additional entity types (TPO, custom) ─────────────────────────────────
    for entity_id, entity_type in registry.get_additional_entity_types().items():
        with st.sidebar.expander(
            f"{entity_type.emoji} {entity_type.label} Filters", expanded=False
        ):
            _render_entity_sidebar(filter_manager, entity_id, entity_type, st)

    # ── Additional relationship types (impacts_tpo, custom) ───────────────────
    for rel_id, rel_type in registry.get_additional_relationship_types().items():
        with st.sidebar.expander(f"\U0001f517 {rel_type.label} Filters", expanded=False):
            _render_relationship_sidebar(filter_manager, rel_id, rel_type, st)

    # ── Validation & summary ──────────────────────────────────────────────────
    is_valid, message = filter_manager.validate()
    if not is_valid:
        st.sidebar.error(message)
    elif message:
        st.sidebar.warning(message)

    st.sidebar.divider()
    st.sidebar.caption(f"**Active filters:** {filter_manager.get_filter_summary()}")

    return filter_manager.get_filters_for_query()


# ── Private helpers ───────────────────────────────────────────────────────────

def _render_entity_sidebar(filter_manager, entity_id, entity_type, st):
    """Render multiselect filters for one entity type inside an expander."""
    is_enabled = st.checkbox(
        f"Show {entity_type.label}s",
        value=filter_manager.filters["entities"].get(entity_id, {}).get("enabled", True),
        key=f"sb_enabled_{entity_id}"
    )
    filter_manager.set_entity_enabled(entity_id, is_enabled)

    if is_enabled:
        for group_name, group_items in entity_type.categorical_groups.items():
            if group_items:
                choices = [item.get("label", item.get("id", "")) for item in group_items]
                if choices:
                    col_label, col_all, col_none = st.columns([3, 1, 1])
                    with col_label:
                        st.markdown(f"**{group_name.replace('_', ' ').title()}**")
                    with col_all:
                        if st.button("All", key=f"sb_all_{entity_id}_{group_name}",
                                     use_container_width=True):
                            filter_manager.set_entity_attribute_filter(entity_id, group_name, choices)
                            st.rerun()
                    with col_none:
                        if st.button("None", key=f"sb_none_{entity_id}_{group_name}",
                                     use_container_width=True):
                            filter_manager.set_entity_attribute_filter(entity_id, group_name, [])
                            st.rerun()
                    current = filter_manager.filters["entities"][entity_id]["attributes"].get(
                        group_name, choices
                    )
                    selected = st.multiselect(
                        group_name.replace('_', ' ').title(),
                        choices,
                        default=current if isinstance(current, list) else choices,
                        key=f"sb_filter_{entity_id}_{group_name}",
                        label_visibility="collapsed"
                    )
                    filter_manager.set_entity_attribute_filter(entity_id, group_name, selected)


def _render_relationship_sidebar(filter_manager, rel_id, rel_type, st):
    """Render multiselect filters for one relationship type inside an expander."""
    is_enabled = st.checkbox(
        f"Show {rel_type.label}",
        value=filter_manager.filters["relationships"].get(rel_id, {}).get("enabled", True),
        key=f"sb_enabled_rel_{rel_id}"
    )
    filter_manager.set_relationship_enabled(rel_id, is_enabled)

    if is_enabled:
        for group_name, group_items in rel_type.categorical_groups.items():
            if group_items:
                choices = [item.get("label", item.get("id", "")) for item in group_items]
                if choices:
                    col_label, col_all, col_none = st.columns([3, 1, 1])
                    with col_label:
                        st.markdown(f"**{group_name.replace('_', ' ').title()}**")
                    with col_all:
                        if st.button("All", key=f"sb_all_rel_{rel_id}_{group_name}",
                                     use_container_width=True):
                            filter_manager.set_relationship_attribute_filter(rel_id, group_name, choices)
                            st.rerun()
                    with col_none:
                        if st.button("None", key=f"sb_none_rel_{rel_id}_{group_name}",
                                     use_container_width=True):
                            filter_manager.set_relationship_attribute_filter(rel_id, group_name, [])
                            st.rerun()
                    current = filter_manager.filters["relationships"][rel_id]["attributes"].get(
                        group_name, choices
                    )
                    selected = st.multiselect(
                        group_name.replace('_', ' ').title(),
                        choices,
                        default=current if isinstance(current, list) else choices,
                        key=f"sb_filter_rel_{rel_id}_{group_name}",
                        label_visibility="collapsed"
                    )
                    filter_manager.set_relationship_attribute_filter(rel_id, group_name, selected)
