"""
Risk Influence Map (RIM) Application.

Thin entry point: handles Streamlit page-level configuration and
delegates all rendering to `ui.home`.
"""

import streamlit as st

# Configuration
from config import APP_TITLE, APP_ICON, LAYOUT_MODE

# UI Components
from ui import inject_styles

# Home page rendering (extracted from the former monolithic app.py)
from ui.home import (
    init_session_state,
    render_connection_sidebar,
    render_welcome_page,
    render_main_content,
)


def main():
    """Main application entry point."""
    # Page configuration (must be the first Streamlit call)
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=LAYOUT_MODE,
        initial_sidebar_state="expanded"
    )
    
    # Inject custom styles
    inject_styles()
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.markdown(f'<p class="main-header">{APP_ICON} {APP_TITLE}</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Dynamic visualization system for business and operational risk management</p>', unsafe_allow_html=True)
    
    # Connection sidebar
    render_connection_sidebar()
    
    # Check connection
    if not st.session_state.connected:
        render_welcome_page()
        return
    
    # Render main content (dashboard, visualization, analysis tabs)
    manager = st.session_state.manager
    render_main_content(manager)


if __name__ == "__main__":
    main()
