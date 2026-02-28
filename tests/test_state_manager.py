"""
Tests for the centralized state manager (utils/state_manager.py).

Uses a mock ``st.session_state`` implemented as a plain dict so the tests
run without starting a Streamlit server.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Ensure project root is on the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ---------------------------------------------------------------------------
# Helpers: mock ``st.session_state`` as a plain dict
# ---------------------------------------------------------------------------

class _FakeSessionState(dict):
    """Dict subclass that supports attribute access like Streamlit's session state."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


@pytest.fixture(autouse=True)
def mock_session_state():
    """Patch ``streamlit.session_state`` with a fresh dict for every test."""
    fake = _FakeSessionState()
    with patch("streamlit.session_state", fake):
        yield fake


# -- We also need a minimal streamlit stub so module-level imports in
#    state_manager don't fail.
@pytest.fixture(autouse=True)
def _ensure_streamlit():
    """Make sure `import streamlit as st` succeeds (it's installed as a dep)."""
    pass


# ---------------------------------------------------------------------------
# Tests: init_defaults
# ---------------------------------------------------------------------------

class TestInitDefaults:
    """Tests for the generic ``init_defaults()`` helper."""

    def test_sets_missing_keys(self, mock_session_state):
        from utils.state_manager import init_defaults

        init_defaults({"alpha": 1, "beta": "two"})

        assert mock_session_state["alpha"] == 1
        assert mock_session_state["beta"] == "two"

    def test_does_not_overwrite_existing(self, mock_session_state):
        from utils.state_manager import init_defaults

        mock_session_state["alpha"] = 999
        init_defaults({"alpha": 1, "beta": "two"})

        assert mock_session_state["alpha"] == 999  # preserved
        assert mock_session_state["beta"] == "two"  # new key created

    def test_empty_dict_is_noop(self, mock_session_state):
        from utils.state_manager import init_defaults

        init_defaults({})
        assert len(mock_session_state) == 0


# ---------------------------------------------------------------------------
# Tests: domain-specific init functions
# ---------------------------------------------------------------------------

class TestInitConnectionState:
    """Tests for ``init_connection_state()``."""

    def test_creates_connection_keys(self, mock_session_state):
        from utils.state_manager import init_connection_state

        init_connection_state()

        assert "manager" in mock_session_state
        assert mock_session_state["manager"] is None
        assert "connected" in mock_session_state
        assert mock_session_state["connected"] is False

    def test_preserves_existing_connection(self, mock_session_state):
        from utils.state_manager import init_connection_state

        sentinel = object()
        mock_session_state["manager"] = sentinel
        mock_session_state["connected"] = True

        init_connection_state()

        assert mock_session_state["manager"] is sentinel
        assert mock_session_state["connected"] is True


class TestInitHomeState:
    """Tests for ``init_home_state()``."""

    def test_creates_all_home_keys(self, mock_session_state):
        from utils.state_manager import init_home_state

        init_home_state()

        # Connection keys
        assert "manager" in mock_session_state
        assert "connected" in mock_session_state

        # Connection form keys
        assert "neo4j_uri" in mock_session_state
        assert "neo4j_user" in mock_session_state

        # UI keys
        assert mock_session_state["physics_enabled"] is True
        assert mock_session_state["color_by"] == "level"
        assert mock_session_state["capture_mode"] is False
        assert mock_session_state["influence_explorer_enabled"] is False
        assert mock_session_state["selected_node_id"] is None

        # FilterManager and LayoutManager are instances (not None)
        assert mock_session_state["filter_manager"] is not None
        assert mock_session_state["layout_manager"] is not None

    def test_idempotent(self, mock_session_state):
        from utils.state_manager import init_home_state

        init_home_state()
        fm = mock_session_state["filter_manager"]

        # Call again — same FilterManager instance should be kept
        init_home_state()
        assert mock_session_state["filter_manager"] is fm


class TestInitConfigPageState:
    """Tests for ``init_config_page_state()``."""

    def test_creates_all_config_keys(self, mock_session_state):
        from utils.state_manager import init_config_page_state

        init_config_page_state()

        # Connection keys (included by delegation)
        assert "manager" in mock_session_state
        assert "connected" in mock_session_state

        # Config-specific keys
        assert mock_session_state["config_connection"] is None
        assert mock_session_state["config_connected"] is False
        assert mock_session_state["active_schema_name"] == "default"
        assert mock_session_state["active_schema"] is None
        assert mock_session_state["schema_modified"] is False
        assert mock_session_state["db_stats"] is None
        assert mock_session_state["health_report"] is None


class TestInitAnalysisCacheState:
    """Tests for ``init_analysis_cache_state()``."""

    def test_creates_all_cache_keys(self, mock_session_state):
        from utils.state_manager import init_analysis_cache_state

        init_analysis_cache_state()

        assert mock_session_state["influence_analysis_cache"] is None
        assert mock_session_state["influence_analysis_timestamp"] is None
        assert mock_session_state["mitigation_analysis_cache"] is None
        assert mock_session_state["mitigation_analysis_timestamp"] is None
        assert mock_session_state["pending_explore_node"] is None


class TestInitAll:
    """Tests for the convenience ``init_all()``."""

    def test_all_registered_keys_present(self, mock_session_state):
        from utils.state_manager import (
            init_all,
            CONNECTION_DEFAULTS,
            HOME_UI_DEFAULTS,
            CONFIG_PAGE_DEFAULTS,
            ANALYSIS_CACHE_DEFAULTS,
        )

        init_all()

        expected_keys = set()
        expected_keys.update(CONNECTION_DEFAULTS.keys())
        expected_keys.update(HOME_UI_DEFAULTS.keys())
        expected_keys.update(CONFIG_PAGE_DEFAULTS.keys())
        expected_keys.update(ANALYSIS_CACHE_DEFAULTS.keys())
        # Connection form + FilterManager/LayoutManager
        expected_keys.update({"neo4j_uri", "neo4j_user"})
        expected_keys.update({"filter_manager", "layout_manager"})

        for key in expected_keys:
            assert key in mock_session_state, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Tests: get / set wrappers
# ---------------------------------------------------------------------------

class TestGetSet:
    """Tests for the thin ``get()`` / ``set()`` wrappers."""

    def test_get_returns_value(self, mock_session_state):
        from utils.state_manager import get

        mock_session_state["foo"] = 42
        assert get("foo") == 42

    def test_get_returns_default_for_missing_key(self, mock_session_state):
        from utils.state_manager import get

        assert get("nonexistent") is None
        assert get("nonexistent", "fallback") == "fallback"

    def test_set_writes_value(self, mock_session_state):
        from utils.state_manager import set as state_set

        state_set("bar", "hello")
        assert mock_session_state["bar"] == "hello"

    def test_set_overwrites_existing(self, mock_session_state):
        from utils.state_manager import set as state_set

        mock_session_state["bar"] = "old"
        state_set("bar", "new")
        assert mock_session_state["bar"] == "new"
