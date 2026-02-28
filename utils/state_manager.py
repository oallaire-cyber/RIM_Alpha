"""
Centralized State Manager for RIM Application.

Single source of truth for all `st.session_state` key definitions, default
values, and initialization.  Every module that previously scattered ad-hoc
``if key not in st.session_state`` checks should now delegate to this module.

Usage
-----
    from utils.state_manager import init_home_state, get, set

    init_home_state()          # called once per page load
    val = get("connected")     # typed read
    set("connected", True)     # typed write
"""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

# Lazy imports to avoid circular dependencies — resolved at call-time inside
# the factory functions below.

# ---------------------------------------------------------------------------
# Key registries — plain dicts mapping  key_name → default_value
# ---------------------------------------------------------------------------

CONNECTION_DEFAULTS: Dict[str, Any] = {
    "manager": None,
    "connected": False,
}

CONNECTION_FORM_DEFAULTS: Dict[str, Any] = {
    # Actual default values are injected at init-time from config so that
    # this module stays independent of ``config``.  The keys are registered
    # here with ``None`` as a placeholder; ``init_connection_form_state()``
    # fills in the real defaults.
    "neo4j_uri": None,
    "neo4j_user": None,
}

HOME_UI_DEFAULTS: Dict[str, Any] = {
    # FilterManager / LayoutManager are instantiated lazily — see
    # ``_home_ui_factory_defaults()``.
    "physics_enabled": True,
    "color_by": "level",
    "capture_mode": False,
    "influence_explorer_enabled": False,
    "selected_node_id": None,
    "complexity_mode": "Simple",
    "show_filters_in_simple_mode": False,
}

CONFIG_PAGE_DEFAULTS: Dict[str, Any] = {
    "config_connection": None,
    "config_connected": False,
    "active_schema_name": "default",
    "active_schema": None,
    "schema_modified": False,
    "db_stats": None,
    "health_report": None,
}

ANALYSIS_CACHE_DEFAULTS: Dict[str, Any] = {
    "influence_analysis_cache": None,
    "influence_analysis_timestamp": None,
    "mitigation_analysis_cache": None,
    "mitigation_analysis_timestamp": None,
    "pending_explore_node": None,
}


# ---------------------------------------------------------------------------
# Generic initializer
# ---------------------------------------------------------------------------

def init_defaults(defaults: Dict[str, Any]) -> None:
    """Write *defaults* into ``st.session_state`` without overwriting existing keys."""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Domain-specific convenience functions
# ---------------------------------------------------------------------------

def init_connection_state() -> None:
    """Initialise connection-related session keys."""
    init_defaults(CONNECTION_DEFAULTS)


def init_connection_form_state() -> None:
    """Initialise Neo4j connection form defaults (URI, user).

    Pulls actual default values from ``config`` so the state manager stays
    decoupled from the config package at import-time.
    """
    from config import NEO4J_DEFAULT_URI, NEO4J_DEFAULT_USER

    init_defaults({
        "neo4j_uri": NEO4J_DEFAULT_URI,
        "neo4j_user": NEO4J_DEFAULT_USER,
    })


def init_home_state() -> None:
    """Initialise all keys required by the Home page (``ui/home.py``).

    Includes connection keys, connection form keys, and UI-specific keys
    (FilterManager, LayoutManager, physics, etc.).
    """
    init_connection_state()
    init_connection_form_state()

    # FilterManager and LayoutManager need to be instantiated once only.
    from ui import FilterManager, LayoutManager

    if "filter_manager" not in st.session_state:
        st.session_state.filter_manager = FilterManager()
    if "layout_manager" not in st.session_state:
        st.session_state.layout_manager = LayoutManager()

    init_defaults(HOME_UI_DEFAULTS)


def init_config_page_state() -> None:
    """Initialise all keys required by the Configuration page."""
    init_connection_state()
    init_defaults(CONFIG_PAGE_DEFAULTS)


def init_analysis_cache_state() -> None:
    """Initialise analysis panel cache keys (influence & mitigation panels)."""
    init_defaults(ANALYSIS_CACHE_DEFAULTS)


def init_all() -> None:
    """Initialise every registered key.  Useful in test harnesses."""
    init_connection_state()
    init_connection_form_state()
    init_home_state()
    init_config_page_state()
    init_analysis_cache_state()


# ---------------------------------------------------------------------------
# Thin wrappers around st.session_state
# ---------------------------------------------------------------------------

def get(key: str, default: Any = None) -> Any:
    """Read a value from ``st.session_state``.

    Returns *default* if the key has not been set yet.
    """
    return st.session_state.get(key, default)


def set(key: str, value: Any) -> None:  # noqa: A001 — shadows built-in
    """Write a value into ``st.session_state``."""
    st.session_state[key] = value
