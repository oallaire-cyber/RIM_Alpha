"""
UI module for RIM application.

Contains Streamlit components, filters, layouts, and styling.
"""

from ui.styles import (
    CSS_STYLES,
    BADGE_CLASSES,
    inject_styles,
    get_badge_html,
    get_level_badge,
    get_status_badge,
    get_origin_badge,
    get_mitigation_type_badge,
    get_effectiveness_badge,
)

from ui.filters import (
    FilterManager,
    FilterPreset,
    FILTER_PRESETS,
    get_preset_list,
    get_preset_names,
)

from ui.layouts import (
    LayoutManager,
    generate_layered_layout,
    generate_category_layout,
    generate_tpo_cluster_layout,
    generate_auto_spread_layout,
    LAYOUT_GENERATORS,
    get_layout_options,
    generate_layout,
)

from ui.components import (
    render_statistics_cards,
    render_risk_badge,
    render_mitigation_badge,
    render_coverage_indicator,
    render_influence_flags,
    render_exposure_bar,
    render_category_chips,
    render_risk_card,
    render_mitigation_card,
    format_percentage,
    format_count,
    create_download_link,
)

from ui.sidebar import (
    render_filter_sidebar,
    render_graph_controls,
    render_layout_manager_sidebar,
    render_database_controls,
    render_export_import_sidebar,
)

from ui.panels import (
    render_influence_analysis_panel,
    render_mitigation_analysis_panel,
    get_level_icon,
)

from ui.tabs import (
    render_risks_tab,
    render_tpos_tab,
    render_mitigations_tab,
    render_influences_tab,
    render_tpo_impacts_tab,
    render_risk_mitigations_tab,
    render_import_export_tab,
)

from ui.legend import (
    render_graph_legend,
    render_compact_legend,
    render_sidebar_legend,
    render_node_legend,
    render_edge_legend,
    render_status_legend,
)

__all__ = [
    # Styles
    "CSS_STYLES",
    "BADGE_CLASSES",
    "inject_styles",
    "get_badge_html",
    "get_level_badge",
    "get_status_badge",
    "get_origin_badge",
    "get_mitigation_type_badge",
    "get_effectiveness_badge",
    # Filters
    "FilterManager",
    "FilterPreset",
    "FILTER_PRESETS",
    "get_preset_list",
    "get_preset_names",
    # Layouts
    "LayoutManager",
    "generate_layered_layout",
    "generate_category_layout",
    "generate_tpo_cluster_layout",
    "generate_auto_spread_layout",
    "LAYOUT_GENERATORS",
    "get_layout_options",
    "generate_layout",
    # Components
    "render_statistics_cards",
    "render_risk_badge",
    "render_mitigation_badge",
    "render_coverage_indicator",
    "render_influence_flags",
    "render_exposure_bar",
    "render_category_chips",
    "render_risk_card",
    "render_mitigation_card",
    "format_percentage",
    "format_count",
    "create_download_link",
    # Sidebar
    "render_filter_sidebar",
    "render_graph_controls",
    "render_layout_manager_sidebar",
    "render_database_controls",
    "render_export_import_sidebar",
    # Panels
    "render_influence_analysis_panel",
    "render_mitigation_analysis_panel",
    "get_level_icon",
    # Tabs
    "render_risks_tab",
    "render_tpos_tab",
    "render_mitigations_tab",
    "render_influences_tab",
    "render_tpo_impacts_tab",
    "render_risk_mitigations_tab",
    "render_import_export_tab",
    # Legend
    "render_graph_legend",
    "render_compact_legend",
    "render_sidebar_legend",
    "render_node_legend",
    "render_edge_legend",
    "render_status_legend",
]
