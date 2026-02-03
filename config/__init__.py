"""
Configuration module for RIM application.
"""

from config.settings import (
    APP_CONFIG,
    TPO_CLUSTERS,
    RISK_CATEGORIES,
    RISK_LEVELS,
    RISK_STATUSES,
    RISK_ORIGINS,
    MITIGATION_TYPES,
    MITIGATION_STATUSES,
    MITIGATION_EFFECTIVENESS,
    INFLUENCE_STRENGTHS,
    IMPACT_LEVELS,
    NEO4J_DEFAULTS,
    GRAPH_DEFAULTS,
    ANALYSIS_CACHE_TIMEOUT,
    # New schema-related exports
    RISK_LEVEL_CONFIG,
    TPO_CLUSTER_CONFIG,
    MITIGATION_TYPE_CONFIG,
    get_active_schema,
    get_active_schema_name,
    set_active_schema,
)

# Convenience exports for app.py
APP_TITLE = APP_CONFIG["page_title"]
APP_ICON = APP_CONFIG["page_icon"]
LAYOUT_MODE = APP_CONFIG["layout"]
NEO4J_DEFAULT_URI = NEO4J_DEFAULTS["uri"]
NEO4J_DEFAULT_USER = NEO4J_DEFAULTS["username"]

__all__ = [
    "APP_CONFIG",
    "APP_TITLE",
    "APP_ICON",
    "LAYOUT_MODE",
    "TPO_CLUSTERS",
    "RISK_CATEGORIES",
    "RISK_LEVELS",
    "RISK_STATUSES",
    "RISK_ORIGINS",
    "MITIGATION_TYPES",
    "MITIGATION_STATUSES",
    "MITIGATION_EFFECTIVENESS",
    "INFLUENCE_STRENGTHS",
    "IMPACT_LEVELS",
    "NEO4J_DEFAULTS",
    "NEO4J_DEFAULT_URI",
    "NEO4J_DEFAULT_USER",
    "GRAPH_DEFAULTS",
    "ANALYSIS_CACHE_TIMEOUT",
    # Schema config items
    "RISK_LEVEL_CONFIG",
    "TPO_CLUSTER_CONFIG",
    "MITIGATION_TYPE_CONFIG",
    "get_active_schema",
    "get_active_schema_name",
    "set_active_schema",
]

# Optional schema loader imports (for new schema-based configuration)
try:
    from config.schema_loader import (
        SchemaLoader, SchemaConfig, get_schema, reload_schema, list_schemas,
        validate_schema, save_schema
    )
    __all__.extend([
        "SchemaLoader", "SchemaConfig", "get_schema", "reload_schema", 
        "list_schemas", "validate_schema", "save_schema"
    ])
except ImportError:
    pass  # Schema loader not available

