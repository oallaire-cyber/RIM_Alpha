"""
Utilities module for RIM application.

Contains helper functions and utility classes.
"""

from utils.helpers import (
    format_percentage,
    format_exposure,
    truncate_text,
    wrap_text_multiline,
)

from utils.state_manager import (
    init_connection_state,
    init_home_state,
    init_config_page_state,
    init_analysis_cache_state,
    init_all,
    get as state_get,
    set as state_set,
)

__all__ = [
    "format_percentage",
    "format_exposure",
    "truncate_text",
    "wrap_text_multiline",
    "init_connection_state",
    "init_home_state",
    "init_config_page_state",
    "init_analysis_cache_state",
    "init_all",
    "state_get",
    "state_set",
]

