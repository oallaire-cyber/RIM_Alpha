"""
Application settings and constants for RIM (Risk Influence Map).

This module contains all configuration values, constants, and default settings
used throughout the application.
"""

# =============================================================================
# STREAMLIT PAGE CONFIGURATION
# =============================================================================

APP_CONFIG = {
    "page_title": "Risk Influence Map (RIM)",
    "page_icon": "🎯",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# =============================================================================
# RISK CONFIGURATION
# =============================================================================

# Risk hierarchy levels
RISK_LEVELS = ["Strategic", "Operational"]

# Risk categories (domain areas)
RISK_CATEGORIES = ["Programme", "Produit", "Industriel", "Supply Chain"]

# Risk lifecycle statuses
RISK_STATUSES = ["Active", "Contingent", "Archived"]

# Risk origin types
RISK_ORIGINS = ["New", "Legacy"]

# =============================================================================
# TPO (TOP PROGRAM OBJECTIVES) CONFIGURATION
# =============================================================================

# TPO cluster categories
TPO_CLUSTERS = [
    "Product Efficiency",
    "Business Efficiency",
    "Industrial Efficiency",
    "Sustainability",
    "Safety"
]

# =============================================================================
# MITIGATION CONFIGURATION
# =============================================================================

# Mitigation types
MITIGATION_TYPES = ["Dedicated", "Inherited", "Baseline"]

# Mitigation statuses
MITIGATION_STATUSES = ["Proposed", "In Progress", "Implemented", "Deferred"]

# Mitigation effectiveness levels
MITIGATION_EFFECTIVENESS = ["Low", "Medium", "High", "Critical"]

# =============================================================================
# INFLUENCE CONFIGURATION
# =============================================================================

# Influence strength levels
INFLUENCE_STRENGTHS = ["Weak", "Moderate", "Strong", "Critical"]

# Impact levels (for TPO impacts)
IMPACT_LEVELS = ["Low", "Medium", "High", "Critical"]

# Default confidence value for influences
DEFAULT_CONFIDENCE = 0.8

# =============================================================================
# SCORING VALUES (for analysis calculations)
# =============================================================================

# Strength values for influence scoring
STRENGTH_VALUES = {
    "Critical": 4,
    "Strong": 3,
    "Moderate": 2,
    "Weak": 1
}

# Impact values for TPO impact scoring
IMPACT_VALUES = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

# Effectiveness values for mitigation scoring
EFFECTIVENESS_VALUES = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

# =============================================================================
# VISUALIZATION DEFAULTS
# =============================================================================

# Default graph settings
GRAPH_DEFAULTS = {
    "height": "700px",
    "width": "100%",
    "bgcolor": "#ffffff",
    "font_color": "#333333"
}

# Node colors by level
NODE_COLORS = {
    "Strategic": "#9b59b6",  # Purple
    "Operational": "#3498db",  # Blue
    "TPO": "#f1c40f",  # Yellow
    "Mitigation": {
        "Dedicated": "#27ae60",  # Green
        "Inherited": "#3498db",  # Blue
        "Baseline": "#9b59b6"   # Purple
    }
}

# Edge colors by type
EDGE_COLORS = {
    "Level1_Op_to_Strat": "#e74c3c",  # Red
    "Level2_Strat_to_Strat": "#9b59b6",  # Purple
    "Level3_Op_to_Op": "#3498db",  # Blue
    "IMPACTS_TPO": "#3498db",  # Blue (dashed)
    "MITIGATES": "#27ae60"  # Green (dashed)
}

# Node sizes
NODE_SIZES = {
    "min": 20,
    "max": 50,
    "default": 30,
    "tpo": 35,
    "mitigation": 30
}

# =============================================================================
# ANALYSIS CONFIGURATION
# =============================================================================

# Analysis cache timeout in seconds
ANALYSIS_CACHE_TIMEOUT = 30

# Maximum depth for influence traversal
MAX_INFLUENCE_DEPTH = 10

# Decay factor for propagation scoring
PROPAGATION_DECAY = 0.85

# Convergence multiplier factor
CONVERGENCE_MULTIPLIER_FACTOR = 0.2

# High exposure threshold multiplier (relative to average)
HIGH_EXPOSURE_THRESHOLD_MULTIPLIER = 1.2

# =============================================================================
# REVIEW SCHEDULE
# =============================================================================

# Default days until next review
DEFAULT_REVIEW_INTERVAL_DAYS = 90

# =============================================================================
# NEO4J DEFAULT CONNECTION
# =============================================================================

NEO4J_DEFAULTS = {
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": ""
}

# =============================================================================
# FILE PATHS
# =============================================================================

# Layout storage file
LAYOUTS_FILE = "graph_layouts.json"
