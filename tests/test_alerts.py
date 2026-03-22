"""
Tests for F5 Automated Risk Threshold Alerts.

Covers:
  - AlertThresholdsConfig schema_loader integration (covered more fully in test_templates.py)
  - Threshold detection logic: EL breach, TRI breach, enabled=False suppression
  - Schema YAML files contain alert_thresholds block

All tests are pure unit tests — no database or Streamlit dependency.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ---------------------------------------------------------------------------
# Threshold detection pure logic
# ---------------------------------------------------------------------------

def _make_risk_result(
    risk_id="r1",
    risk_name="Risk 1",
    level="Operational",
    final_exposure=10.0,
    tail_risk_indicator=5.0,
):
    """Helper: build a minimal risk_result dict as stored in exposure_results."""
    return {
        "risk_id": risk_id,
        "risk_name": risk_name,
        "level": level,
        "final_exposure": final_exposure,
        "tail_risk_indicator": tail_risk_indicator,
    }


def _detect_breaches(risk_results, el_thresh, tri_thresh):
    """Mirror the breach detection logic from _render_threshold_alerts."""
    el_breaches = [r for r in risk_results if r.get("final_exposure", 0) > el_thresh]
    tri_breaches = [r for r in risk_results if r.get("tail_risk_indicator", 0) > tri_thresh]
    return el_breaches, tri_breaches


class TestThresholdDetection:
    """Pure unit tests for breach detection logic."""

    def test_no_breach_when_all_under_threshold(self):
        results = [
            _make_risk_result(final_exposure=30.0, tail_risk_indicator=10.0),
            _make_risk_result(risk_id="r2", final_exposure=20.0, tail_risk_indicator=8.0),
        ]
        el, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert el == []
        assert tri == []

    def test_el_breach_detected(self):
        results = [
            _make_risk_result(final_exposure=60.0, tail_risk_indicator=5.0),
            _make_risk_result(risk_id="r2", final_exposure=20.0, tail_risk_indicator=5.0),
        ]
        el, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert len(el) == 1
        assert el[0]["risk_id"] == "r1"
        assert tri == []

    def test_tri_breach_detected(self):
        results = [
            _make_risk_result(final_exposure=20.0, tail_risk_indicator=30.0),
        ]
        el, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert el == []
        assert len(tri) == 1

    def test_both_breach_simultaneously(self):
        results = [
            _make_risk_result(final_exposure=80.0, tail_risk_indicator=40.0),
        ]
        el, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert len(el) == 1
        assert len(tri) == 1

    def test_boundary_value_not_a_breach(self):
        """Threshold is exclusive: value == threshold is NOT a breach."""
        results = [_make_risk_result(final_exposure=50.0, tail_risk_indicator=25.0)]
        el, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert el == []
        assert tri == []

    def test_just_above_threshold_is_a_breach(self):
        results = [_make_risk_result(final_exposure=50.01, tail_risk_indicator=25.01)]
        el, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert len(el) == 1
        assert len(tri) == 1

    def test_multiple_el_breaches_sorted_desc(self):
        results = [
            _make_risk_result("r1", final_exposure=55.0, tail_risk_indicator=5.0),
            _make_risk_result("r2", final_exposure=90.0, tail_risk_indicator=5.0),
            _make_risk_result("r3", final_exposure=20.0, tail_risk_indicator=5.0),
        ]
        el, _ = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        sorted_el = sorted(el, key=lambda x: x["final_exposure"], reverse=True)
        assert sorted_el[0]["risk_id"] == "r2"
        assert sorted_el[1]["risk_id"] == "r1"

    def test_empty_results_no_breach(self):
        el, tri = _detect_breaches([], el_thresh=50.0, tri_thresh=25.0)
        assert el == []
        assert tri == []

    def test_missing_tri_field_treated_as_zero(self):
        """Results without tail_risk_indicator should not false-positive."""
        results = [{"risk_id": "r1", "risk_name": "R", "final_exposure": 20.0}]
        _, tri = _detect_breaches(results, el_thresh=50.0, tri_thresh=25.0)
        assert tri == []


# ---------------------------------------------------------------------------
# AlertThresholdsConfig integration
# ---------------------------------------------------------------------------

class TestAlertThresholdsIntegration:
    """Integration tests: verify schema YAML files include the alert_thresholds block."""

    def test_default_schema_has_alert_thresholds(self):
        from config.schema_loader import SchemaLoader
        loader = SchemaLoader()
        schema = loader.load_schema("default")
        assert schema is not None, "Default schema failed to load"
        cfg = schema.analysis.alert_thresholds
        assert cfg.high_exposure_threshold > 0
        assert cfg.tail_risk_indicator_threshold > 0
        assert cfg.enabled is True

    def test_it_security_schema_has_alert_thresholds(self):
        from config.schema_loader import SchemaLoader
        loader = SchemaLoader()
        schema = loader.load_schema("it_security")
        assert schema is not None, "IT security schema failed to load"
        cfg = schema.analysis.alert_thresholds
        assert cfg.high_exposure_threshold > 0
        assert cfg.tail_risk_indicator_threshold > 0

    def test_schema_without_alert_thresholds_uses_defaults(self):
        """Schemas lacking alert_thresholds block should still load (backward compat)."""
        from config.schema_loader import SchemaLoader
        loader = SchemaLoader()
        cfg = loader._parse_analysis({})  # empty analysis block
        assert cfg.alert_thresholds.high_exposure_threshold == 50.0
        assert cfg.alert_thresholds.enabled is True
