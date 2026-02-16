
import streamlit as st
from database import RiskGraphManager
from config import NEO4J_DEFAULT_URI, NEO4J_DEFAULT_USER, NEO4J_DEFAULT_PASSWORD

@st.cache_resource
def get_risk_graph_manager(uri, user, password):
    """
    Get a cached instance of RiskGraphManager.
    This ensures that the connection is established only once (singleton pattern via cache).
    """
    manager = RiskGraphManager(uri, user, password)
    # Don't auto-connect here to allow lazy connection handling in UI
    # But for a singleton, we might want it ready. 
    # Let's return the manager instance. The app logic calls connect().
    # Actually, if we cache the manager, we should probably ensure it's connected or handle connection state.
    # The current app logic instantiates Manager and then calls connect().
    # If we cache the *instance*, we can reuse it.
    return manager

def get_active_manager():
    """
    Retrieve the active manager from session state or cache.
    Useful for pages to get the connection established in main app.
    """
    if "manager" in st.session_state and st.session_state.manager:
        return st.session_state.manager
    return None

def init_connection_state():
    """Initialize connection-related session state."""
    if "manager" not in st.session_state:
        st.session_state.manager = None
    if "connected" not in st.session_state:
        st.session_state.connected = False
