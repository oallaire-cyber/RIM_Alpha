"""
Visualization module for RIM application.

Contains PyVis graph rendering, styling, and layout utilities.
"""

from visualization.colors import (
    LEVEL_COLORS,
    EXPOSURE_COLORS,
    TPO_COLORS,
    MITIGATION_TYPE_COLORS,
    INFLUENCE_TYPE_COLORS,
    EFFECTIVENESS_COLORS,
    IMPACT_COLORS,
    HIGHLIGHT_COLOR,
    get_color_by_level,
    get_color_by_exposure,
    get_mitigation_color,
    get_influence_color,
    get_effectiveness_color,
    get_impact_color,
    interpolate_color,
)

from visualization.node_styles import (
    wrap_label,
    truncate_label,
    create_tpo_node_config,
    create_mitigation_node_config,
    create_risk_node_config,
    create_node_config,
)

from visualization.edge_styles import (
    STRENGTH_WIDTH_MULTIPLIERS,
    INFLUENCE_BASE_WIDTHS,
    EFFECTIVENESS_WIDTHS,
    IMPACT_WIDTHS,
    create_influence_edge_config,
    create_tpo_impact_edge_config,
    create_mitigates_edge_config,
    create_edge_config,
    filter_edges_by_score,
)

from visualization.graph_options import (
    get_network_options,
    get_position_capture_js,
    get_fullscreen_js,
)

from visualization.graph_renderer import (
    render_graph,
    render_graph_streamlit,
    render_subgraph,
)

__all__ = [
    # Colors
    "LEVEL_COLORS",
    "EXPOSURE_COLORS",
    "TPO_COLORS",
    "MITIGATION_TYPE_COLORS",
    "INFLUENCE_TYPE_COLORS",
    "EFFECTIVENESS_COLORS",
    "IMPACT_COLORS",
    "HIGHLIGHT_COLOR",
    "get_color_by_level",
    "get_color_by_exposure",
    "get_mitigation_color",
    "get_influence_color",
    "get_effectiveness_color",
    "get_impact_color",
    "interpolate_color",
    # Node styles
    "wrap_label",
    "truncate_label",
    "create_tpo_node_config",
    "create_mitigation_node_config",
    "create_risk_node_config",
    "create_node_config",
    # Edge styles
    "STRENGTH_WIDTH_MULTIPLIERS",
    "INFLUENCE_BASE_WIDTHS",
    "EFFECTIVENESS_WIDTHS",
    "IMPACT_WIDTHS",
    "create_influence_edge_config",
    "create_tpo_impact_edge_config",
    "create_mitigates_edge_config",
    "create_edge_config",
    "filter_edges_by_score",
    # Graph options
    "get_network_options",
    "get_position_capture_js",
    "get_fullscreen_js",
    # Renderer
    "render_graph",
    "render_graph_streamlit",
    "render_subgraph",
]
