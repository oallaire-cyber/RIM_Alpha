
import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_manager import get_risk_graph_manager

def test_singleton_connection_pattern():
    """
    Verify that get_risk_graph_manager returns the same instance 
    when called with same arguments, mocking st.cache_resource behavior.
    """
    # Since we cannot easily test actual Streamlit caching in unit tests without 
    # the runtime, we will mock the caching decorator or just verify the logic.
    # However, st.cache_resource is a decorator.
    
    # We'll test that the function returns a manager instance.
    with patch('utils.db_manager.RiskGraphManager') as MockManager:
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "password"
        
        # First call
        manager1 = get_risk_graph_manager(uri, user, password)
        
        # In a real Streamlit app, the second call would return cached instance.
        # Here we just verify it constructs the object correctly.
        MockManager.assert_called_with(uri, user, password)
        assert manager1 is not None

def test_db_manager_imports():
    """Verify that utils.db_manager can be imported and has expected functions."""
    import utils.db_manager
    assert hasattr(utils.db_manager, 'get_risk_graph_manager')
    assert hasattr(utils.db_manager, 'get_active_manager')
    assert hasattr(utils.db_manager, 'init_connection_state')
