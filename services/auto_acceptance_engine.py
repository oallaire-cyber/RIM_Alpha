"""
Auto-Acceptance Engine — U12 Risk Lifecycle Engine.

Evaluates Active risks for eligibility for auto-acceptance, applying guards
defined in the schema's risk_lifecycle_rules block.

Guards (applied in order — first guard that fires wins):
  1. Severity ceiling: severity >= severity_ceiling → blocked (black swan protection)
  2. Quadrant: critical or severity quadrant → blocked (requires human decision)
  3. Exposure threshold: exposure > acceptance_threshold → blocked
  4. Otherwise → eligible

The engine makes no database calls. The caller is responsible for fetching
risks and supplying the LifecycleRulesConfig instance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from config.schema_loader import LifecycleRulesConfig


@dataclass
class AcceptanceCandidate:
    """Eligibility result for a single risk."""
    risk_id: str
    risk_name: str
    final_exposure: float
    severity: float
    likelihood: float
    quadrant: str
    is_eligible: bool
    blocked_reason: Optional[str]  # None when eligible


@dataclass
class AutoAcceptanceResult:
    """Aggregate result of an auto-acceptance evaluation run."""
    eligible: List[AcceptanceCandidate]
    blocked: List[AcceptanceCandidate]
    evaluated_count: int
    evaluated_at: datetime = field(default_factory=datetime.now)


def _classify_quadrant(
    likelihood: float,
    severity: float,
    lk_threshold: float,
    sev_freq_threshold: float,
    sev_sev_threshold: float,
) -> str:
    """Classify risk into one of four quadrants based on L×S coordinates."""
    high_l = likelihood >= lk_threshold
    high_s_freq = severity >= sev_freq_threshold
    high_s_sev = severity >= sev_sev_threshold

    if high_l and high_s_freq:
        return "critical"
    if not high_l and high_s_sev:
        return "severity"
    if high_l and not high_s_freq:
        return "frequency"
    return "marginal"


class AutoAcceptanceEngine:
    """
    Evaluates Active risks for auto-acceptance eligibility.

    Args:
        risks: List of risk dicts (all statuses — engine filters to Active).
        lifecycle_rules: LifecycleRulesConfig from the active schema.
        scope_node_ids: If provided, only risks in this set are evaluated.
    """

    def __init__(
        self,
        risks: List[Dict[str, Any]],
        lifecycle_rules: "LifecycleRulesConfig",
        scope_node_ids: Optional[List[str]] = None,
    ) -> None:
        self._rules = lifecycle_rules
        self._scope_set = set(scope_node_ids) if scope_node_ids is not None else None

        # Filter to Active risks only
        self._candidates: List[Dict[str, Any]] = [
            r for r in risks
            if r.get("status") == "Active"
            and (self._scope_set is None or r.get("id") in self._scope_set)
        ]

    def evaluate_all(self) -> AutoAcceptanceResult:
        """
        Evaluate all Active risks for auto-acceptance eligibility.

        Returns:
            AutoAcceptanceResult with eligible and blocked candidate lists.
        """
        eligible: List[AcceptanceCandidate] = []
        blocked: List[AcceptanceCandidate] = []

        qt = self._rules.quadrant_thresholds

        for risk in self._candidates:
            candidate = self._evaluate_one(risk, qt)
            if candidate.is_eligible:
                eligible.append(candidate)
            else:
                blocked.append(candidate)

        return AutoAcceptanceResult(
            eligible=eligible,
            blocked=blocked,
            evaluated_count=len(self._candidates),
            evaluated_at=datetime.now(),
        )

    def _evaluate_one(self, risk: Dict[str, Any], qt: Any) -> AcceptanceCandidate:
        """Apply eligibility guards to a single risk dict."""
        # Use "severity" key; fall back to "impact" for backward compat with pre-U13 nodes
        severity = float(risk.get("severity") or risk.get("impact") or 0)
        likelihood = float(risk.get("probability") or risk.get("likelihood") or 0)
        exposure = float(risk.get("exposure") or 0)

        quadrant = _classify_quadrant(
            likelihood=likelihood,
            severity=severity,
            lk_threshold=qt.likelihood_threshold,
            sev_freq_threshold=qt.severity_threshold_frequency,
            sev_sev_threshold=qt.severity_threshold_severity,
        )

        # Guard 1: severity ceiling (black swan protection)
        if severity >= self._rules.severity_ceiling:
            return AcceptanceCandidate(
                risk_id=risk.get("id", ""),
                risk_name=risk.get("name", ""),
                final_exposure=exposure,
                severity=severity,
                likelihood=likelihood,
                quadrant=quadrant,
                is_eligible=False,
                blocked_reason=(
                    f"Severity {severity:.1f} \u2265 ceiling {self._rules.severity_ceiling:.1f} "
                    f"— requires explicit human decision (black swan guard)."
                ),
            )

        # Guard 2: high-severity quadrant (critical or severity)
        if quadrant in ("critical", "severity"):
            return AcceptanceCandidate(
                risk_id=risk.get("id", ""),
                risk_name=risk.get("name", ""),
                final_exposure=exposure,
                severity=severity,
                likelihood=likelihood,
                quadrant=quadrant,
                is_eligible=False,
                blocked_reason=(
                    f"Quadrant '{quadrant}' — high-severity risks require explicit human decision."
                ),
            )

        # Guard 3: exposure threshold
        if exposure > self._rules.acceptance_threshold:
            return AcceptanceCandidate(
                risk_id=risk.get("id", ""),
                risk_name=risk.get("name", ""),
                final_exposure=exposure,
                severity=severity,
                likelihood=likelihood,
                quadrant=quadrant,
                is_eligible=False,
                blocked_reason=(
                    f"Exposure {exposure:.1f} > threshold {self._rules.acceptance_threshold:.1f}."
                ),
            )

        # All guards passed — eligible
        return AcceptanceCandidate(
            risk_id=risk.get("id", ""),
            risk_name=risk.get("name", ""),
            final_exposure=exposure,
            severity=severity,
            likelihood=likelihood,
            quadrant=quadrant,
            is_eligible=True,
            blocked_reason=None,
        )
