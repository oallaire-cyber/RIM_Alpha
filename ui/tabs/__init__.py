"""
Tab Pages for RIM Application.

Contains all the main application tabs for CRUD operations.
"""

from ui.tabs.unified_crud_tab import render_unified_crud_tab
from ui.tabs.risk_mitigations_tab import render_risk_mitigations_tab
from ui.tabs.import_export_tab import render_import_export_tab

__all__ = [
    "render_unified_crud_tab",
    "render_risk_mitigations_tab",
    "render_import_export_tab",
]
