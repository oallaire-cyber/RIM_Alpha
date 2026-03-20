"""
Trigger Engine — U12 Risk Lifecycle Engine.

Evaluates trigger conditions on Watching and Suppressed risks and surfaces
them for human review. For U12, trigger conditions are free-text strings
that require manual confirmation — they are NOT auto-evaluated against
live system data.

NOTE on future programmatic evaluation:
  If you need to auto-evaluate condition expressions, consider using the
  `simpleeval` library (pip install simpleeval) which provides a safe
  sandboxed expression evaluator. Do NOT use Python's built-in eval() or
  exec() — these are security risks when evaluating user-supplied strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


# Statuses that are candidates for trigger evaluation
_TRIGGER_CANDIDATE_STATUSES = {"Watching", "Suppressed"}


@dataclass
class TriggerDetail:
    """Result for a single risk's trigger evaluation."""
    risk_id: str
    risk_name: str
    current_status: str
    trigger_condition: str
    triggered: bool
    evaluation_note: str


@dataclass
class TriggerEvaluationResult:
    """Aggregate result of a trigger evaluation run."""
    triggered_risk_ids: List[str]
    evaluated_count: int
    trigger_details: List[TriggerDetail]
    evaluated_at: datetime = field(default_factory=datetime.now)


class TriggerEngine:
    """
    Evaluates trigger conditions across Watching and Suppressed risks.

    Receives pre-fetched plain dicts from the DB layer (same pattern as
    MitigationAnalyzer). Makes no database calls.

    Args:
        risks: List of risk dicts (exclude_inactive=False expected from caller).
        scope_node_ids: If provided, only risks whose id is in this set are evaluated.
    """

    def __init__(
        self,
        risks: List[Dict[str, Any]],
        scope_node_ids: Optional[List[str]] = None,
    ) -> None:
        self._scope_set = set(scope_node_ids) if scope_node_ids is not None else None

        # Filter to trigger candidates
        self._candidates: List[Dict[str, Any]] = [
            r for r in risks
            if r.get("status") in _TRIGGER_CANDIDATE_STATUSES
            and (self._scope_set is None or r.get("id") in self._scope_set)
        ]

    def evaluate_all(self) -> TriggerEvaluationResult:
        """
        Evaluate trigger conditions for all candidate risks.

        U12 design decision: trigger_condition is a free-text string written by
        a risk owner (e.g., "Supplier X delivers Phase 2 components"). There is
        no integration with external systems to auto-detect if the condition is
        true. All risks are returned as 'pending manual review'.

        The UI layer presents this list so the user can manually confirm which
        triggers have fired, then writes the status transition via update_risk().

        Returns:
            TriggerEvaluationResult with details for each candidate risk.
        """
        details: List[TriggerDetail] = []
        triggered_ids: List[str] = []

        for risk in self._candidates:
            condition = risk.get("trigger_condition") or ""
            has_condition = bool(condition.strip())

            note = (
                "Pending manual review — confirm if trigger condition has been met."
                if has_condition
                else "No trigger condition defined for this risk."
            )

            details.append(TriggerDetail(
                risk_id=risk.get("id", ""),
                risk_name=risk.get("name", ""),
                current_status=risk.get("status", ""),
                trigger_condition=condition,
                triggered=False,  # Always False in U12 — human confirms in UI
                evaluation_note=note,
            ))

        return TriggerEvaluationResult(
            triggered_risk_ids=triggered_ids,
            evaluated_count=len(self._candidates),
            trigger_details=details,
            evaluated_at=datetime.now(),
        )
