"""
Archive Engine — U12 Risk Lifecycle Engine.

Detects risks that have been in Accepted or Closed status beyond the
retention window defined in risk_lifecycle_rules and generates archive
alerts for human review.

The engine makes no database calls and writes nothing to Neo4j.
The caller fetches archive candidates via get_archive_candidates() and
passes them in. After the user confirms, the UI calls update_risk() to
write status="Archived" and archive_date=<today>.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from config.schema_loader import LifecycleRulesConfig


@dataclass
class ArchiveAlert:
    """Alert record for a single archive candidate risk."""
    risk_id: str
    risk_name: str
    current_status: str
    acceptance_date: str
    days_since_acceptance: int
    retention_threshold: int
    message: str


@dataclass
class ArchiveAlertResult:
    """Aggregate result of an archive alert generation run."""
    alerts: List[ArchiveAlert]
    alert_count: int
    generated_at: datetime = field(default_factory=datetime.now)


class ArchiveEngine:
    """
    Generates archive alerts for risks past their retention window.

    Args:
        archive_candidates: List of risk dicts from get_archive_candidates().
        lifecycle_rules: LifecycleRulesConfig from the active schema.
        scope_node_ids: If provided, further restrict alerts to risks in this set.
    """

    def __init__(
        self,
        archive_candidates: List[Dict[str, Any]],
        lifecycle_rules: "LifecycleRulesConfig",
        scope_node_ids: Optional[List[str]] = None,
    ) -> None:
        self._rules = lifecycle_rules
        self._scope_set = set(scope_node_ids) if scope_node_ids is not None else None

        # Apply scope filter if provided (DB query already filters by retention;
        # scope filter is an additional in-memory restriction)
        self._candidates: List[Dict[str, Any]] = [
            c for c in archive_candidates
            if self._scope_set is None or c.get("id") in self._scope_set
        ]

    def generate_alerts(self) -> ArchiveAlertResult:
        """
        Generate an alert for each archive candidate.

        Returns:
            ArchiveAlertResult containing all alert records.
        """
        alerts: List[ArchiveAlert] = []
        now = datetime.now().date()

        for risk in self._candidates:
            acceptance_date_str = risk.get("acceptance_date") or ""
            days_elapsed = 0

            if acceptance_date_str:
                try:
                    acceptance_date = datetime.fromisoformat(
                        acceptance_date_str.split("T")[0]
                    ).date()
                    days_elapsed = (now - acceptance_date).days
                except (ValueError, AttributeError):
                    days_elapsed = 0

            owner_note = (
                f" (accepted by {risk['acceptance_owner']})"
                if risk.get("acceptance_owner")
                else ""
            )
            message = (
                f"Risk '{risk.get('name', '')}' has been in {risk.get('status', '')} "
                f"status for {days_elapsed} days{owner_note}, exceeding the "
                f"{self._rules.archive_retention_days}-day retention window. "
                f"Consider archiving or re-opening."
            )

            alerts.append(ArchiveAlert(
                risk_id=risk.get("id", ""),
                risk_name=risk.get("name", ""),
                current_status=risk.get("status", ""),
                acceptance_date=acceptance_date_str,
                days_since_acceptance=days_elapsed,
                retention_threshold=self._rules.archive_retention_days,
                message=message,
            ))

        return ArchiveAlertResult(
            alerts=alerts,
            alert_count=len(alerts),
            generated_at=datetime.now(),
        )
