
import streamlit as st
from database import RiskGraphManager
from config import NEO4J_DEFAULT_URI, NEO4J_DEFAULT_USER, NEO4J_DEFAULT_PASSWORD

# Re-export for backward compatibility — canonical source is state_manager.
from utils.state_manager import init_connection_state  # noqa: F401

@st.cache_resource
def get_risk_graph_manager(uri, user, password):
    """
    Get a cached instance of RiskGraphManager.
    This ensures that the connection is established only once (singleton pattern via cache).
    """
    manager = RiskGraphManager(uri, user, password)
    return manager

def get_active_manager():
    """
    Retrieve the active manager from session state or cache.
    Useful for pages to get the connection established in main app.
    """
    if "manager" in st.session_state and st.session_state.manager:
        return st.session_state.manager
    return None
