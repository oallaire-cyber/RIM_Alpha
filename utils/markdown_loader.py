"""
Markdown documentation loader for RIM application.

Loads .md files from the docs/ directory with caching to avoid
re-reading on every Streamlit rerun.
"""

import streamlit as st
from pathlib import Path

_DOCS_DIR = Path(__file__).parent.parent / "docs"


@st.cache_data
def load_doc(filename: str) -> str:
    """
    Load a markdown file from the docs/ directory (cached).

    Args:
        filename: Name of the .md file to load (e.g. 'help_overview.md').

    Returns:
        The file content as a string, or a fallback warning message
        if the file is not found.
    """
    filepath = _DOCS_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return f"> ⚠️ Documentation file `{filename}` not found."
