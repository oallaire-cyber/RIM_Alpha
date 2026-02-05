"""
Visualization module for RIM application.

Contains PyVis graph rendering, styling, and layout utilities.

Enhanced visualization with semantic shapes and colors:
- Risks: Diamonds (business) and Circles (operational)
- Mitigations: Rounded boxes (shield-like)
- TPOs: Hexagons (objectives)

Color families:
- Warm colors (red/orange/purple) for risks/threats
- Cool colors (teal/green) for mitigations/protection
- Gold for TPOs/objectives

Edge differentiation:
- Standard arrows for influence relationships
- Bar-end arrows for mitigation (blocking metaphor)
- Vee arrows for TPO impacts (targeting metaphor)
"""

from visualization.colors import (
    # New structured color dictionaries
    RISK_COLORS,
    MITIGATION_COLORS,
    MITIGATION_BORDER_COLORS,
    
    # Legacy compatibility
    LEVEL_COLORS,
    EXPOSURE_COLORS,
    TPO_COLORS,
    MITIGATION_TYPE_COLORS,
    INFLUENCE_TYPE_COLORS,
    EFFECTIVENESS_COLORS,
    IMPACT_COLORS,
    HIGHLIGHT_COLOR,
    SELECTION_GLOW,
    
    # Utility functions
    get_color_by_level,
    get_color_by_exposure,
    get_mitigation_color,
    get_mitigation_border_color,
    get_influence_color,
    get_effectiveness_color,
    get_impact_color,
    interpolate_color,
    get_exposure_gradient_position,
)

from visualization.node_styles import (
    # Shape configurations
    RISK_SHAPES,
    MITIGATION_SHAPE,
    TPO_SHAPE,
    NODE_SIZES,
    BORDER_STYLES,
    
    # Helper functions
    wrap_label,
    truncate_label,
    
    # Node configuration functions
    create_tpo_node_config,
    create_mitigation_node_config,
    create_risk_node_config,
    create_node_config,
    
    # Legend helper
    get_legend_items,
)

from visualization.edge_styles import (
    # Arrow configurations
    ARROW_STYLES,
    
    # Width configurations
    STRENGTH_WIDTH_MULTIPLIERS,
    INFLUENCE_BASE_WIDTHS,
    EFFECTIVENESS_WIDTHS,
    IMPACT_WIDTHS,
    
    # Dash patterns
    DASH_PATTERNS,
    
    # Edge configuration functions
    create_influence_edge_config,
    create_tpo_impact_edge_config,
    create_mitigates_edge_config,
    create_edge_config,
    
    # Filtering functions
    filter_edges_by_score,
    filter_edges_by_type,
    
    # Legend helper
    get_edge_legend_items,
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
    # Colors - new
    "RISK_COLORS",
    "MITIGATION_COLORS",
    "MITIGATION_BORDER_COLORS",
    "SELECTION_GLOW",
    "get_mitigation_border_color",
    "get_exposure_gradient_position",
    
    # Colors - legacy compatibility
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
    
    # Node styles - new
    "RISK_SHAPES",
    "MITIGATION_SHAPE",
    "TPO_SHAPE",
    "NODE_SIZES",
    "BORDER_STYLES",
    "get_legend_items",
    
    # Node styles - existing
    "wrap_label",
    "truncate_label",
    "create_tpo_node_config",
    "create_mitigation_node_config",
    "create_risk_node_config",
    "create_node_config",
    
    # Edge styles - new
    "ARROW_STYLES",
    "DASH_PATTERNS",
    "filter_edges_by_type",
    "get_edge_legend_items",
    
    # Edge styles - existing
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
