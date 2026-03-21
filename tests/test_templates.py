"""
Tests for U14 Generic Risk Template Architecture.

Covers:
  - Risk.is_template field: from_dict, to_dict, is_generic_template property
  - get_all_risks exclude_templates filter (via Cypher WHERE clause logic)
  - AlertThresholdsConfig dataclass defaults and parsing pattern
All tests are pure unit tests — no database dependency.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ---------------------------------------------------------------------------
# Risk model
# ---------------------------------------------------------------------------

class TestRiskTemplateField:
    """Tests for is_template field on Risk model."""

    def test_default_is_false(self):
        from models.risk import Risk
        from models.enums import RiskLevel
        r = Risk(id="1", name="Test", level=RiskLevel.OPERATIONAL)
        assert r.is_template is False

    def test_is_generic_template_property(self):
        from models.risk import Risk
        from models.enums import RiskLevel
        r = Risk(id="1", name="Test", level=RiskLevel.OPERATIONAL, is_template=True)
        assert r.is_generic_template is True

    def test_is_generic_template_false_when_not_template(self):
        from models.risk import Risk
        from models.enums import RiskLevel
        r = Risk(id="1", name="Test", level=RiskLevel.OPERATIONAL)
        assert r.is_generic_template is False

    def test_to_dict_includes_is_template(self):
        from models.risk import Risk
        from models.enums import RiskLevel
        r = Risk(id="1", name="Test", level=RiskLevel.OPERATIONAL, is_template=True)
        d = r.to_dict()
        assert d["is_template"] is True

    def test_to_dict_false_by_default(self):
        from models.risk import Risk
        from models.enums import RiskLevel
        r = Risk(id="1", name="Test", level=RiskLevel.OPERATIONAL)
        d = r.to_dict()
        assert d["is_template"] is False

    def test_from_dict_reads_is_template(self):
        from models.risk import Risk
        r = Risk.from_dict({
            "id": "2",
            "name": "Template Risk",
            "level": "Business",
            "is_template": True,
        })
        assert r.is_template is True

    def test_from_dict_defaults_false_when_missing(self):
        from models.risk import Risk
        r = Risk.from_dict({
            "id": "3",
            "name": "Regular Risk",
            "level": "Operational",
        })
        assert r.is_template is False

    def test_from_dict_coerces_truthy_values(self):
        from models.risk import Risk
        r = Risk.from_dict({
            "id": "4",
            "name": "Risk",
            "level": "Operational",
            "is_template": 1,  # truthy non-bool
        })
        assert r.is_template is True

    def test_round_trip(self):
        from models.risk import Risk
        from models.enums import RiskLevel
        original = Risk(id="5", name="T", level=RiskLevel.BUSINESS, is_template=True)
        restored = Risk.from_dict(original.to_dict())
        assert restored.is_template is True

    def test_is_template_independent_of_is_inactive(self):
        """Templates are not lifecycle-inactive; they are a different exclusion axis."""
        from models.risk import Risk
        from models.enums import RiskLevel
        r = Risk(id="6", name="T", level=RiskLevel.OPERATIONAL, is_template=True)
        # Templates have Active status by default — not lifecycle-inactive
        assert r.is_inactive is False
        assert r.is_template is True


# ---------------------------------------------------------------------------
# AlertThresholdsConfig
# ---------------------------------------------------------------------------

class TestAlertThresholdsConfig:
    """Tests for AlertThresholdsConfig dataclass."""

    def test_defaults(self):
        from config.schema_loader import AlertThresholdsConfig
        cfg = AlertThresholdsConfig()
        assert cfg.high_exposure_threshold == 50.0
        assert cfg.tail_risk_indicator_threshold == 25.0
        assert cfg.enabled is True

    def test_custom_values(self):
        from config.schema_loader import AlertThresholdsConfig
        cfg = AlertThresholdsConfig(
            high_exposure_threshold=30.0,
            tail_risk_indicator_threshold=15.0,
            enabled=False,
        )
        assert cfg.high_exposure_threshold == 30.0
        assert cfg.tail_risk_indicator_threshold == 15.0
        assert cfg.enabled is False

    def test_analysis_config_has_alert_thresholds(self):
        from config.schema_loader import AnalysisConfig, AlertThresholdsConfig
        cfg = AnalysisConfig()
        assert isinstance(cfg.alert_thresholds, AlertThresholdsConfig)
        assert cfg.alert_thresholds.enabled is True

    def test_parse_analysis_populates_alert_thresholds(self):
        """_parse_analysis should hydrate alert_thresholds from a YAML dict."""
        from config.schema_loader import SchemaLoader
        loader = SchemaLoader()
        analysis_data = {
            "alert_thresholds": {
                "high_exposure_threshold": 40.0,
                "tail_risk_indicator_threshold": 20.0,
                "enabled": False,
            }
        }
        cfg = loader._parse_analysis(analysis_data)
        assert cfg.alert_thresholds.high_exposure_threshold == 40.0
        assert cfg.alert_thresholds.tail_risk_indicator_threshold == 20.0
        assert cfg.alert_thresholds.enabled is False

    def test_parse_analysis_uses_defaults_when_block_missing(self):
        from config.schema_loader import SchemaLoader
        loader = SchemaLoader()
        cfg = loader._parse_analysis({})  # no alert_thresholds key
        assert cfg.alert_thresholds.high_exposure_threshold == 50.0
        assert cfg.alert_thresholds.enabled is True


# ---------------------------------------------------------------------------
# Template exclusion logic (pure unit — no DB)
# ---------------------------------------------------------------------------

class TestTemplateExclusionQuery:
    """Verify the WHERE clause constant used for template exclusion."""

    def test_inactive_statuses_constant_exists(self):
        from database.queries.risks import _INACTIVE_STATUSES
        assert isinstance(_INACTIVE_STATUSES, list)
        assert "Accepted" in _INACTIVE_STATUSES

    def test_get_all_risks_signature_has_exclude_templates(self):
        import inspect
        from database.queries.risks import get_all_risks
        sig = inspect.signature(get_all_risks)
        assert "exclude_templates" in sig.parameters
        assert sig.parameters["exclude_templates"].default is True

    def test_get_risks_with_filters_signature_has_exclude_templates(self):
        import inspect
        from database.queries.risks import get_risks_with_filters
        sig = inspect.signature(get_risks_with_filters)
        assert "exclude_templates" in sig.parameters
        assert sig.parameters["exclude_templates"].default is True

    def test_create_risk_signature_has_is_template(self):
        import inspect
        from database.queries.risks import create_risk
        sig = inspect.signature(create_risk)
        assert "is_template" in sig.parameters
        assert sig.parameters["is_template"].default is False

    def test_get_all_templates_function_exists(self):
        from database.queries.risks import get_all_templates
        assert callable(get_all_templates)

    def test_create_instantiates_rel_function_exists(self):
        from database.queries.risks import create_instantiates_rel
        assert callable(create_instantiates_rel)

    def test_get_instances_of_template_function_exists(self):
        from database.queries.risks import get_instances_of_template
        assert callable(get_instances_of_template)

    def test_get_template_of_instance_function_exists(self):
        from database.queries.risks import get_template_of_instance
        assert callable(get_template_of_instance)

    def test_manager_has_template_methods(self):
        from database.manager import RiskGraphManager
        assert hasattr(RiskGraphManager, "get_all_templates")
        assert hasattr(RiskGraphManager, "create_instantiates_rel")
        assert hasattr(RiskGraphManager, "get_instances_of_template")
        assert hasattr(RiskGraphManager, "get_template_of_instance")
