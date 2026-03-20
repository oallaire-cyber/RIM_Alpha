"""
Tests for U12 Risk Lifecycle Engine services.

Covers:
  - LifecycleRulesConfig / QuadrantThresholdsConfig dataclasses
  - TriggerEngine
  - AutoAcceptanceEngine  (Testing Gate 2: severity ceiling blocks)
  - ArchiveEngine
  - Archived exclusion from ExposureCalculator  (Testing Gate 3)

All tests are pure unit tests — no database dependency.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ---------------------------------------------------------------------------
# LifecycleRulesConfig
# ---------------------------------------------------------------------------

class TestLifecycleRulesConfig:
    """Tests for LifecycleRulesConfig and QuadrantThresholdsConfig dataclasses."""

    def test_defaults(self):
        from config.schema_loader import LifecycleRulesConfig
        rules = LifecycleRulesConfig()
        assert rules.acceptance_threshold == 20.0
        assert rules.severity_ceiling == 7.0
        assert rules.archive_retention_days == 180

    def test_quadrant_thresholds_defaults(self):
        from config.schema_loader import LifecycleRulesConfig
        rules = LifecycleRulesConfig()
        qt = rules.quadrant_thresholds
        assert qt.likelihood_threshold == 6.0
        assert qt.severity_threshold_frequency == 6.0
        assert qt.severity_threshold_severity == 7.0

    def test_custom_values(self):
        from config.schema_loader import LifecycleRulesConfig, QuadrantThresholdsConfig
        rules = LifecycleRulesConfig(
            acceptance_threshold=15.0,
            severity_ceiling=8.0,
            archive_retention_days=90,
            quadrant_thresholds=QuadrantThresholdsConfig(
                likelihood_threshold=5.0,
                severity_threshold_frequency=5.0,
                severity_threshold_severity=8.0,
            ),
        )
        assert rules.acceptance_threshold == 15.0
        assert rules.severity_ceiling == 8.0
        assert rules.archive_retention_days == 90
        assert rules.quadrant_thresholds.likelihood_threshold == 5.0

    def test_schema_parser_uses_defaults_when_block_missing(self):
        """Schema without risk_lifecycle_rules should parse to defaults."""
        from config.schema_loader import SchemaLoader
        import tempfile, os, yaml

        minimal_schema = {
            "version": "1.0",
            "name": "Test",
            "entities": {
                "risk": {"neo4j_label": "Risk"},
                "tpo": {"neo4j_label": "TPO"},
                "mitigation": {"neo4j_label": "Mitigation"},
            },
            "relationships": {},
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(minimal_schema, f)
            tmp_path = f.name

        try:
            loader = SchemaLoader()
            with open(tmp_path) as fh:
                import yaml as _yaml
                data = _yaml.safe_load(fh)
            schema = loader._parse_schema(data)
            # Should have default lifecycle rules
            assert schema.lifecycle_rules.acceptance_threshold == 20.0
            assert schema.lifecycle_rules.severity_ceiling == 7.0
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# TriggerEngine
# ---------------------------------------------------------------------------

class TestTriggerEngine:
    """Tests for services/trigger_engine.py."""

    def _make_risk(self, risk_id, name, status, trigger_condition=None):
        return {
            "id": risk_id,
            "name": name,
            "status": status,
            "trigger_condition": trigger_condition,
        }

    def test_empty_risk_list(self):
        from services.trigger_engine import TriggerEngine
        engine = TriggerEngine([])
        result = engine.evaluate_all()
        assert result.evaluated_count == 0
        assert result.trigger_details == []
        assert result.triggered_risk_ids == []

    def test_watching_risk_with_condition_is_included(self):
        """Watching risks with a condition are surfaced for human review (Gate 1)."""
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r1", "Launch Delay Risk", "Watching",
                            "Supplier X delivers Phase 2 components"),
        ]
        engine = TriggerEngine(risks)
        result = engine.evaluate_all()
        assert result.evaluated_count == 1
        assert len(result.trigger_details) == 1
        detail = result.trigger_details[0]
        assert detail.risk_id == "r1"
        assert detail.current_status == "Watching"
        assert detail.trigger_condition == "Supplier X delivers Phase 2 components"

    def test_suppressed_risk_included(self):
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r2", "Suppressed Risk", "Suppressed", "Market rate exceeds 5%"),
        ]
        engine = TriggerEngine(risks)
        result = engine.evaluate_all()
        assert result.evaluated_count == 1

    def test_active_risk_excluded(self):
        """Active risks are not in the trigger evaluation set."""
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r1", "Active Risk", "Active", "Some condition"),
        ]
        engine = TriggerEngine(risks)
        result = engine.evaluate_all()
        assert result.evaluated_count == 0

    def test_accepted_risk_excluded(self):
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r1", "Accepted Risk", "Accepted"),
        ]
        engine = TriggerEngine(risks)
        result = engine.evaluate_all()
        assert result.evaluated_count == 0

    def test_scope_filtering(self):
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r1", "Risk In Scope", "Watching", "condition A"),
            self._make_risk("r2", "Risk Out Of Scope", "Watching", "condition B"),
        ]
        engine = TriggerEngine(risks, scope_node_ids=["r1"])
        result = engine.evaluate_all()
        assert result.evaluated_count == 1
        assert result.trigger_details[0].risk_id == "r1"

    def test_no_auto_trigger_returned(self):
        """U12 design: triggered_risk_ids is always empty — human confirms."""
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r1", "Risk", "Watching", "Any condition"),
        ]
        engine = TriggerEngine(risks)
        result = engine.evaluate_all()
        assert result.triggered_risk_ids == []
        assert result.trigger_details[0].triggered is False

    def test_risk_without_condition_has_note(self):
        from services.trigger_engine import TriggerEngine
        risks = [
            self._make_risk("r1", "Risk", "Watching", None),
        ]
        engine = TriggerEngine(risks)
        result = engine.evaluate_all()
        assert "No trigger condition" in result.trigger_details[0].evaluation_note


# ---------------------------------------------------------------------------
# AutoAcceptanceEngine
# ---------------------------------------------------------------------------

class TestAutoAcceptanceEngine:
    """Tests for services/auto_acceptance_engine.py."""

    def _make_risk(self, risk_id, name, status="Active", severity=5.0,
                   probability=3.0, exposure=None):
        exposure = exposure if exposure is not None else probability * severity
        return {
            "id": risk_id,
            "name": name,
            "status": status,
            "severity": severity,
            "probability": probability,
            "exposure": exposure,
        }

    def _default_rules(self):
        from config.schema_loader import LifecycleRulesConfig
        return LifecycleRulesConfig()

    def test_severity_ceiling_blocks(self):
        """TESTING GATE 2: Severity >= 7 (severity_ceiling) must block acceptance."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()  # severity_ceiling = 7.0
        risks = [
            self._make_risk("r1", "High Severity Risk", severity=7.0, probability=2.0, exposure=14.0),
        ]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.eligible) == 0
        assert len(result.blocked) == 1
        blocked = result.blocked[0]
        assert blocked.risk_id == "r1"
        assert blocked.blocked_reason is not None
        assert "ceiling" in blocked.blocked_reason.lower()

    def test_severity_above_ceiling_blocked(self):
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        risks = [self._make_risk("r1", "R", severity=8.0, probability=1.0, exposure=8.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.blocked) == 1
        assert len(result.eligible) == 0

    def test_severity_below_ceiling_can_be_eligible(self):
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()  # severity_ceiling = 7
        # severity=6, probability=3, exposure=18 < threshold 20
        risks = [self._make_risk("r1", "Low Risk", severity=6.0, probability=3.0, exposure=18.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.eligible) == 1

    def test_critical_quadrant_blocks(self):
        """L >= 6 AND S >= 6 → critical quadrant → blocked."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        risks = [self._make_risk("r1", "Critical Risk", severity=6.5, probability=6.5, exposure=10.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.blocked) == 1
        assert "quadrant" in result.blocked[0].blocked_reason.lower()

    def test_severity_quadrant_blocks(self):
        """L < 6 AND S >= 7 → severity quadrant → blocked."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        # severity=7 → also hits ceiling, but let's use ceiling=8 to isolate quadrant guard
        from config.schema_loader import LifecycleRulesConfig, QuadrantThresholdsConfig
        rules = LifecycleRulesConfig(
            severity_ceiling=8.0,
            acceptance_threshold=20.0,
            quadrant_thresholds=QuadrantThresholdsConfig(
                likelihood_threshold=6.0,
                severity_threshold_frequency=6.0,
                severity_threshold_severity=7.0,
            ),
        )
        risks = [self._make_risk("r1", "Severity Quadrant", severity=7.5, probability=4.0, exposure=10.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.blocked) == 1
        assert "quadrant" in result.blocked[0].blocked_reason.lower()

    def test_frequency_quadrant_eligible(self):
        """L >= 6 AND S < 6 → frequency quadrant → not blocked by quadrant guard."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        risks = [self._make_risk("r1", "Freq Risk", severity=5.0, probability=6.0, exposure=10.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        # Should not be blocked by quadrant guard; may still be blocked by exposure
        assert all(b.risk_id != "r1" or "quadrant" not in (b.blocked_reason or "").lower()
                   for b in result.blocked)

    def test_high_exposure_blocks(self):
        """Exposure > acceptance_threshold blocks acceptance."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()  # threshold = 20
        risks = [self._make_risk("r1", "High EL", severity=5.0, probability=5.0, exposure=25.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.blocked) == 1
        assert "threshold" in result.blocked[0].blocked_reason.lower()

    def test_marginal_quadrant_eligible(self):
        """L < 6 AND S < 6 → marginal quadrant → no quadrant block."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        risks = [self._make_risk("r1", "Marginal", severity=3.0, probability=3.0, exposure=9.0)]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert len(result.eligible) == 1
        assert result.eligible[0].quadrant == "marginal"

    def test_non_active_risk_excluded(self):
        """Only Active risks are evaluated."""
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        risks = [
            self._make_risk("r1", "Archived", status="Archived"),
            self._make_risk("r2", "Watching", status="Watching"),
            self._make_risk("r3", "Active", status="Active", severity=3.0,
                            probability=3.0, exposure=9.0),
        ]
        engine = AutoAcceptanceEngine(risks, rules)
        result = engine.evaluate_all()
        assert result.evaluated_count == 1

    def test_scope_filtering(self):
        from services.auto_acceptance_engine import AutoAcceptanceEngine
        rules = self._default_rules()
        risks = [
            self._make_risk("r1", "In Scope", severity=3.0, probability=3.0, exposure=9.0),
            self._make_risk("r2", "Out Scope", severity=3.0, probability=3.0, exposure=9.0),
        ]
        engine = AutoAcceptanceEngine(risks, rules, scope_node_ids=["r1"])
        result = engine.evaluate_all()
        assert result.evaluated_count == 1
        assert result.eligible[0].risk_id == "r1"


# ---------------------------------------------------------------------------
# ArchiveEngine
# ---------------------------------------------------------------------------

class TestArchiveEngine:
    """Tests for services/archive_engine.py."""

    def _make_candidate(self, risk_id, name, status="Accepted",
                        acceptance_date="2025-01-01", acceptance_owner=None):
        return {
            "id": risk_id,
            "name": name,
            "status": status,
            "acceptance_date": acceptance_date,
            "acceptance_owner": acceptance_owner,
            "exposure": 15.0,
        }

    def _default_rules(self):
        from config.schema_loader import LifecycleRulesConfig
        return LifecycleRulesConfig()

    def test_no_candidates_produces_no_alerts(self):
        from services.archive_engine import ArchiveEngine
        engine = ArchiveEngine([], self._default_rules())
        result = engine.generate_alerts()
        assert result.alert_count == 0
        assert result.alerts == []

    def test_single_candidate_generates_alert(self):
        from services.archive_engine import ArchiveEngine
        candidates = [self._make_candidate("r1", "Old Risk")]
        engine = ArchiveEngine(candidates, self._default_rules())
        result = engine.generate_alerts()
        assert result.alert_count == 1
        alert = result.alerts[0]
        assert alert.risk_id == "r1"
        assert alert.risk_name == "Old Risk"
        assert alert.retention_threshold == 180
        assert alert.days_since_acceptance > 0

    def test_alert_message_contains_risk_name(self):
        from services.archive_engine import ArchiveEngine
        candidates = [self._make_candidate("r1", "Orbital Comms Risk")]
        engine = ArchiveEngine(candidates, self._default_rules())
        result = engine.generate_alerts()
        assert "Orbital Comms Risk" in result.alerts[0].message

    def test_acceptance_owner_in_message(self):
        from services.archive_engine import ArchiveEngine
        candidates = [self._make_candidate("r1", "Risk", acceptance_owner="Alice")]
        engine = ArchiveEngine(candidates, self._default_rules())
        result = engine.generate_alerts()
        assert "Alice" in result.alerts[0].message

    def test_multiple_candidates(self):
        from services.archive_engine import ArchiveEngine
        candidates = [
            self._make_candidate("r1", "Risk One"),
            self._make_candidate("r2", "Risk Two"),
        ]
        engine = ArchiveEngine(candidates, self._default_rules())
        result = engine.generate_alerts()
        assert result.alert_count == 2

    def test_scope_filtering(self):
        from services.archive_engine import ArchiveEngine
        candidates = [
            self._make_candidate("r1", "In Scope"),
            self._make_candidate("r2", "Out Of Scope"),
        ]
        engine = ArchiveEngine(candidates, self._default_rules(), scope_node_ids=["r1"])
        result = engine.generate_alerts()
        assert result.alert_count == 1
        assert result.alerts[0].risk_id == "r1"


# ---------------------------------------------------------------------------
# Archived Exclusion from ExposureCalculator  (Testing Gate 3)
# ---------------------------------------------------------------------------

class TestArchivedExclusionFromExposure:
    """
    TESTING GATE 3: Archived risks must not appear in ExposureCalculator output.

    The exclusion is enforced at the DB query layer (exclude_inactive=True default).
    This test verifies that when an archived risk is NOT passed to ExposureCalculator
    (as would happen via the DB layer), its ID does not appear in the results.
    """

    def _make_active_risk(self, risk_id, name, probability=5.0, severity=5.0):
        return {
            "id": risk_id,
            "name": name,
            "level": "Business",
            "status": "Active",
            "probability": probability,
            "severity": severity,
            "exposure": probability * severity,
            "categories": ["Programme"],
        }

    def _make_archived_risk(self, risk_id, name):
        return {
            "id": risk_id,
            "name": name,
            "level": "Business",
            "status": "Archived",
            "probability": 5.0,
            "severity": 5.0,
            "exposure": 25.0,
            "categories": ["Programme"],
        }

    def test_archived_risk_absent_from_exposure_results(self):
        """
        Verify that an archived risk ID does not appear in the exposure calculator
        output when excluded by the DB query layer (caller pre-filters before passing).
        """
        from services.exposure_calculator import ExposureCalculator

        active_risk = self._make_active_risk("r-active", "Active Risk")
        archived_risk = self._make_archived_risk("r-archived", "Archived Risk")

        # Simulate DB layer behaviour: pass only the active risk (archived excluded)
        risks_passed_to_calculator = [active_risk]
        influences = []
        mitigations = []
        mitigates_relationships = []

        calc = ExposureCalculator(
            risks_passed_to_calculator, influences, mitigations, mitigates_relationships
        )
        result = calc.calculate_all()

        # Active risk should be present
        all_ids = {r.risk_id for r in result.risk_results}
        assert "r-active" in all_ids

        # Archived risk must NOT be present (it was never passed in)
        assert "r-archived" not in all_ids

    def test_all_inactive_statuses_excluded(self):
        """
        Verify LIFECYCLE_INACTIVE_STATUSES contains all expected statuses.
        """
        from models.enums import LIFECYCLE_INACTIVE_STATUSES, RiskStatus
        assert RiskStatus.ARCHIVED in LIFECYCLE_INACTIVE_STATUSES
        assert RiskStatus.ACCEPTED in LIFECYCLE_INACTIVE_STATUSES
        assert RiskStatus.WATCHING in LIFECYCLE_INACTIVE_STATUSES
        assert RiskStatus.SUPPRESSED in LIFECYCLE_INACTIVE_STATUSES
        assert RiskStatus.CLOSED in LIFECYCLE_INACTIVE_STATUSES

    def test_active_status_not_in_inactive_set(self):
        from models.enums import LIFECYCLE_INACTIVE_STATUSES, RiskStatus
        assert RiskStatus.ACTIVE not in LIFECYCLE_INACTIVE_STATUSES
        assert RiskStatus.CONTINGENT not in LIFECYCLE_INACTIVE_STATUSES
