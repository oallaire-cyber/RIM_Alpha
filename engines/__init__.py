"""
Engine modularity for RIM analysis.

Provides:
- AnalysisEngine: Abstract base class for analysis engines
- EngineManager: Discovers and manages engine plugins
"""

from engines.base_engine import AnalysisEngine, EngineManager, EngineStatus
from engines.exposure_engine import ExposureEngine

__all__ = [
    "AnalysisEngine",
    "EngineManager",
    "EngineStatus",
    "ExposureEngine",
]
