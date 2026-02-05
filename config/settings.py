"""
Application settings and constants for RIM (Risk Influence Map).

This module loads configuration from the active YAML schema, falling back
to hardcoded defaults if schema loading fails.

Schema changes require app restart to take effect.
"""

# =============================================================================
# SCHEMA LOADING
# =============================================================================

import os
from pathlib import Path

_active_schema = None
_active_schema_name = "default"

def _get_schema_name_from_config():
    """
    Determine which schema to load.
    
    Priority:
    1. RIM_SCHEMA environment variable
    2. .rim_schema file in project root
    3. Default to "default"
    """
    # Check environment variable first
    env_schema = os.environ.get("RIM_SCHEMA")
    if env_schema:
        return env_schema
    
    # Check for .rim_schema file
    project_root = Path(__file__).parent.parent
    schema_file = project_root / ".rim_schema"
    if schema_file.exists():
        try:
            return schema_file.read_text().strip()
        except Exception:
            pass
    
    return "default"


def _load_active_schema():
    """Load the active schema from disk."""
    global _active_schema, _active_schema_name
    _active_schema_name = _get_schema_name_from_config()
    try:
        from config.schema_loader import get_schema
        _active_schema = get_schema(_active_schema_name)
        return True
    except Exception as e:
        # Schema loading failed - use defaults
        _active_schema = None
        return False

# Try to load schema at module import
_schema_loaded = _load_active_schema()


def get_active_schema():
    """Get the currently active schema (may be None if loading failed)."""
    return _active_schema


def get_active_schema_name():
    """Get the name of the active schema."""
    return _active_schema_name


def set_active_schema(schema_name: str):
    """
    Set the active schema by name.
    
    Note: This requires reimporting the module or restarting the app
    for changes to take effect in module-level constants.
    """
    global _active_schema_name
    _active_schema_name = schema_name
    _load_active_schema()


# =============================================================================
# STREAMLIT PAGE CONFIGURATION
# =============================================================================

if _active_schema:
    APP_CONFIG = {
        "page_title": _active_schema.ui.app_title,
        "page_icon": _active_schema.ui.app_icon,
        "layout": _active_schema.ui.layout,
        "initial_sidebar_state": "expanded"
    }
else:
    APP_CONFIG = {
        "page_title": "Risk Influence Map (RIM)",
        "page_icon": "🎯",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }

# Convenience exports
APP_TITLE = APP_CONFIG["page_title"]
APP_ICON = APP_CONFIG["page_icon"]
LAYOUT_MODE = APP_CONFIG["layout"]

# =============================================================================
# RISK CONFIGURATION (from schema or defaults)
# =============================================================================

if _active_schema:
    RISK_LEVELS = _active_schema.risk_levels
    RISK_CATEGORIES = _active_schema.risk_categories
    RISK_STATUSES = _active_schema.risk_statuses
    RISK_ORIGINS = _active_schema.risk_origins
    
    # Build level config lookup for visualization
    RISK_LEVEL_CONFIG = {
        level.label: {
            "color": level.color,
            "shape": level.shape,
            "emoji": level.emoji,
            "size": level.size,
            "description": level.description
        }
        for level in _active_schema.risk.levels
    }
else:
    # Fallback defaults
    RISK_LEVELS = ["Business", "Operational"]
    RISK_CATEGORIES = ["Programme", "Produit", "Industriel", "Supply Chain"]
    RISK_STATUSES = ["Active", "Contingent", "Archived"]
    RISK_ORIGINS = ["New", "Legacy"]
    RISK_LEVEL_CONFIG = {
        "Business": {"color": "#9b59b6", "shape": "diamond", "emoji": "◆", "size": 35, "description": ""},
        "Operational": {"color": "#3498db", "shape": "dot", "emoji": "●", "size": 30, "description": ""}
    }

# =============================================================================
# TPO (TOP PROGRAM OBJECTIVES) CONFIGURATION
# =============================================================================

if _active_schema:
    TPO_CLUSTERS = _active_schema.tpo_clusters
    
    # Build cluster config lookup
    TPO_CLUSTER_CONFIG = {
        cluster.label: {
            "color": cluster.color,
            "description": cluster.description
        }
        for cluster in _active_schema.tpo.clusters
    }
else:
    TPO_CLUSTERS = [
        "Product Efficiency",
        "Business Efficiency",
        "Industrial Efficiency",
        "Sustainability",
        "Safety"
    ]
    TPO_CLUSTER_CONFIG = {}

# =============================================================================
# MITIGATION CONFIGURATION
# =============================================================================

if _active_schema:
    MITIGATION_TYPES = _active_schema.mitigation_types
    MITIGATION_STATUSES = _active_schema.mitigation_statuses
    MITIGATION_EFFECTIVENESS = _active_schema.effectiveness_levels
    
    # Build type config lookup
    MITIGATION_TYPE_CONFIG = {
        t.label: {
            "color": t.color,
            "line_style": t.line_style,
            "description": t.description
        }
        for t in _active_schema.mitigation.types
    }
else:
    MITIGATION_TYPES = ["Dedicated", "Inherited", "Baseline"]
    MITIGATION_STATUSES = ["Proposed", "In Progress", "Implemented", "Deferred"]
    MITIGATION_EFFECTIVENESS = ["Low", "Medium", "High", "Critical"]
    MITIGATION_TYPE_CONFIG = {
        "Dedicated": {"color": "#27ae60", "line_style": "solid", "description": ""},
        "Inherited": {"color": "#3498db", "line_style": "dotted", "description": ""},
        "Baseline": {"color": "#9b59b6", "line_style": "thick", "description": ""}
    }

# =============================================================================
# INFLUENCE CONFIGURATION
# =============================================================================

if _active_schema:
    INFLUENCE_STRENGTHS = _active_schema.influence_strengths
    IMPACT_LEVELS = _active_schema.impact_levels
    DEFAULT_CONFIDENCE = _active_schema.influences.default_confidence
    
    # Build strength config lookup with values
    STRENGTH_VALUES = {
        s.label: int(s.value * 4)  # Convert 0-1 to 1-4 scale
        for s in _active_schema.influences.strengths
    }
    
    # Build impact values
    IMPACT_VALUES = {
        il.label: il.value
        for il in _active_schema.impacts_tpo.impact_levels
    }
    
    # Build effectiveness values
    EFFECTIVENESS_VALUES = {
        e.label: int(e.reduction * 4) + 1  # Convert 0-1 to 1-4 scale
        for e in _active_schema.mitigates.effectiveness_levels
    }
else:
    INFLUENCE_STRENGTHS = ["Weak", "Moderate", "Strong", "Critical"]
    IMPACT_LEVELS = ["Low", "Medium", "High", "Critical"]
    DEFAULT_CONFIDENCE = 0.8
    
    STRENGTH_VALUES = {
        "Critical": 4,
        "Strong": 3,
        "Moderate": 2,
        "Weak": 1
    }
    
    IMPACT_VALUES = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1
    }
    
    EFFECTIVENESS_VALUES = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

# =============================================================================
# VISUALIZATION DEFAULTS
# =============================================================================

if _active_schema:
    GRAPH_DEFAULTS = {
        "height": _active_schema.ui.graph_height,
        "width": "100%",
        "bgcolor": _active_schema.ui.graph_bgcolor,
        "font_color": "#333333"
    }
else:
    GRAPH_DEFAULTS = {
        "height": "700px",
        "width": "100%",
        "bgcolor": "#ffffff",
        "font_color": "#333333"
    }

# Node colors by level (dynamically built from schema)
if _active_schema:
    NODE_COLORS = {
        level.label: level.color
        for level in _active_schema.risk.levels
    }
    NODE_COLORS["TPO"] = "#f1c40f"
    NODE_COLORS["Mitigation"] = {
        t.label: t.color
        for t in _active_schema.mitigation.types
    }
else:
    NODE_COLORS = {
        "Strategic": "#9b59b6",
        "Operational": "#3498db",
        "TPO": "#f1c40f",
        "Mitigation": {
            "Dedicated": "#27ae60",
            "Inherited": "#3498db",
            "Baseline": "#9b59b6"
        }
    }

# Edge colors by type
EDGE_COLORS = {
    "Level1_Op_to_Strat": "#e74c3c",
    "Level2_Strat_to_Strat": "#9b59b6",
    "Level3_Op_to_Op": "#3498db",
    "IMPACTS_TPO": "#3498db",
    "MITIGATES": "#27ae60"
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

if _active_schema:
    ANALYSIS_CACHE_TIMEOUT = _active_schema.analysis.cache_timeout_seconds
    MAX_INFLUENCE_DEPTH = _active_schema.analysis.max_influence_depth
    PROPAGATION_DECAY = _active_schema.analysis.exposure.propagation_decay
    CONVERGENCE_MULTIPLIER_FACTOR = _active_schema.analysis.exposure.convergence_multiplier
    HIGH_EXPOSURE_THRESHOLD_MULTIPLIER = _active_schema.analysis.high_exposure_threshold_multiplier
else:
    ANALYSIS_CACHE_TIMEOUT = 30
    MAX_INFLUENCE_DEPTH = 10
    PROPAGATION_DECAY = 0.85
    CONVERGENCE_MULTIPLIER_FACTOR = 0.2
    HIGH_EXPOSURE_THRESHOLD_MULTIPLIER = 1.2

# =============================================================================
# REVIEW SCHEDULE
# =============================================================================

DEFAULT_REVIEW_INTERVAL_DAYS = 90

# =============================================================================
# NEO4J DEFAULT CONNECTION
# =============================================================================

NEO4J_DEFAULTS = {
    "uri": "bolt://localhost:7687",
    "username": "neo4j",
    "password": ""
}

# Convenience exports for backward compatibility
NEO4J_DEFAULT_URI = NEO4J_DEFAULTS["uri"]
NEO4J_DEFAULT_USER = NEO4J_DEFAULTS["username"]

# =============================================================================
# FILE PATHS
# =============================================================================

LAYOUTS_FILE = "graph_layouts.json"
