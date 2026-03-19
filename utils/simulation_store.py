"""
Simulation Results Store for RIM.

Defines SimulationRecord — an in-memory record of a completed simulation run.
Records are stored in st.session_state.saved_simulations (list) and are not
persisted to disk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

import pandas as pd


@dataclass
class SimulationRecord:
    """A saved simulation run."""

    id: str                     # Short UUID prefix, e.g. "a1b2c3d4"
    timestamp: datetime
    mode: str                   # "Monte Carlo (Random)" | "Mitigation Path" | "Scope-Based (Real Data)"
    scope_label: str            # Active scope names joined, or "Full Graph"
    params: Dict[str, Any]      # Sidebar parameter snapshot
    key_metrics: Dict[str, Any] # Summary stats over the results DataFrame
    df: pd.DataFrame = field(repr=False)  # Full results DataFrame
