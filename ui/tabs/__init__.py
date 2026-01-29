"""
Tab Pages for RIM Application.

Contains all the main application tabs for CRUD operations.
"""

from ui.tabs.risks_tab import render_risks_tab
from ui.tabs.tpos_tab import render_tpos_tab
from ui.tabs.mitigations_tab import render_mitigations_tab
from ui.tabs.influences_tab import render_influences_tab
from ui.tabs.tpo_impacts_tab import render_tpo_impacts_tab
from ui.tabs.risk_mitigations_tab import render_risk_mitigations_tab
from ui.tabs.import_export_tab import render_import_export_tab

__all__ = [
    "render_risks_tab",
    "render_tpos_tab",
    "render_mitigations_tab",
    "render_influences_tab",
    "render_tpo_impacts_tab",
    "render_risk_mitigations_tab",
    "render_import_export_tab",
]
