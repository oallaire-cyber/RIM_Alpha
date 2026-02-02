"""
Tests for services/exposure_calculator.py

Tests the ExposureCalculator service and related data classes.
"""

import pytest
from services.exposure_calculator import (
    ExposureCalculator,
    RiskExposureResult,
    GlobalExposureResult,
)


class TestRiskExposureResult:
    """Tests for RiskExposureResult dataclass."""
    
    def test_create_result(self):
        """Test creating a risk exposure result."""
        result = RiskExposureResult(
            risk_id="risk-001",
            risk_name="Test Risk",
            level="Strategic",
            likelihood=5.0,
            impact=8.0,
            base_exposure=40.0,
            mitigation_factor=0.7,
            mitigated_exposure=28.0,
            mitigation_count=1,
            influence_limitation=0.2,
            effective_mitigation_factor=0.76,
            upstream_risk_count=1,
            final_exposure=30.4,
        )
        
        assert result.risk_id == "risk-001"
        assert result.base_exposure == 40.0
        assert result.final_exposure == 30.4
    
    def test_to_dict(self):
        """Test to_dict serialization."""
        result = RiskExposureResult(
            risk_id="risk-001",
            risk_name="Test Risk",
            level="Strategic",
            likelihood=5.0,
            impact=8.0,
            base_exposure=40.0,
            mitigation_factor=0.7,
            mitigated_exposure=28.0,
            mitigation_count=1,
            influence_limitation=0.2,
            effective_mitigation_factor=0.76,
            upstream_risk_count=1,
            final_exposure=30.4,
        )
        
        data = result.to_dict()
        
        assert data["risk_id"] == "risk-001"
        assert data["risk_name"] == "Test Risk"
        assert data["base_exposure"] == 40.0
        assert data["final_exposure"] == 30.4


class TestGlobalExposureResult:
    """Tests for GlobalExposureResult dataclass."""
    
    def test_create_result(self):
        """Test creating a global exposure result."""
        result = GlobalExposureResult(
            residual_risk_percentage=45.5,
            weighted_risk_score=35.0,
            max_single_exposure=48.0,
            max_exposure_risk_id="risk-001",
            max_exposure_risk_name="High Risk",
            total_base_exposure=200.0,
            total_final_exposure=91.0,
            total_risks=5,
            risks_with_data=4,
            mitigated_risks_count=3,
            unmitigated_risks_count=2,
            calculated_at="2025-01-15T10:00:00",
            risk_results=[],
        )
        
        assert result.residual_risk_percentage == 45.5
        assert result.weighted_risk_score == 35.0
    
    def test_to_dict(self):
        """Test to_dict serialization."""
        result = GlobalExposureResult(
            residual_risk_percentage=45.5,
            weighted_risk_score=35.0,
            max_single_exposure=48.0,
            max_exposure_risk_id="risk-001",
            max_exposure_risk_name="High Risk",
            total_base_exposure=200.0,
            total_final_exposure=91.0,
            total_risks=5,
            risks_with_data=4,
            mitigated_risks_count=3,
            unmitigated_risks_count=2,
            calculated_at="2025-01-15T10:00:00",
            risk_results=[],
        )
        
        data = result.to_dict()
        
        assert data["residual_risk_percentage"] == 45.5
        assert "calculated_at" in data
    
    def test_get_health_status_excellent(self):
        """Test health status for low risk score."""
        result = GlobalExposureResult(
            residual_risk_percentage=10.0,
            weighted_risk_score=5.0,
            max_single_exposure=10.0,
            max_exposure_risk_id="",
            max_exposure_risk_name="",
            total_base_exposure=100.0,
            total_final_exposure=10.0,
            total_risks=1,
            risks_with_data=1,
            mitigated_risks_count=1,
            unmitigated_risks_count=0,
            calculated_at="",
            risk_results=[],
        )
        
        label, color = result.get_health_status()
        assert label == "Excellent"
    
    def test_get_health_status_critical(self):
        """Test health status for high risk score."""
        result = GlobalExposureResult(
            residual_risk_percentage=90.0,
            weighted_risk_score=85.0,
            max_single_exposure=90.0,
            max_exposure_risk_id="",
            max_exposure_risk_name="",
            total_base_exposure=100.0,
            total_final_exposure=90.0,
            total_risks=1,
            risks_with_data=1,
            mitigated_risks_count=0,
            unmitigated_risks_count=1,
            calculated_at="",
            risk_results=[],
        )
        
        label, color = result.get_health_status()
        assert label == "Critical"


class TestExposureCalculatorInit:
    """Tests for ExposureCalculator initialization."""
    
    def test_init_empty_data(self):
        """Test initialization with empty data."""
        calc = ExposureCalculator(
            risks=[],
            influences=[],
            mitigations=[],
            mitigates_relationships=[]
        )
        
        assert calc is not None
        assert len(calc.risks) == 0
    
    def test_init_with_sample_data(self, sample_risk_network):
        """Test initialization with sample network data."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        assert calc is not None
        # risks is a dict keyed by id
        assert len(calc.risks) == 3
        # mitigations is a dict keyed by id
        assert len(calc.mitigations) == 2


class TestExposureCalculatorCalculations:
    """Tests for ExposureCalculator calculation methods."""
    
    def test_calculate_base_exposure(self, sample_risk_network):
        """Test base exposure calculation (likelihood × impact)."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        # Test with strat-001: probability=6, impact=8 => base=48
        risk = calc.risks.get("strat-001")
        if risk:
            base = calc._calculate_base_exposure(risk)
            assert base == 48.0
    
    def test_calculate_base_exposure_with_missing_data(self, sample_risk_network):
        """Test base exposure returns 0 for missing data."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=[],
            mitigates_relationships=[]
        )
        
        # Risk with missing probability/impact
        risk = {"id": "test", "name": "Test", "probability": None, "impact": 5.0}
        base = calc._calculate_base_exposure(risk)
        
        assert base == 0.0
    
    def test_calculate_mitigation_factor_no_mitigations(self, sample_risk_network):
        """Test mitigation factor is 1.0 when no mitigations."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=[],
            mitigates_relationships=[]
        )
        
        # op-002 has no mitigations in sample data
        factor, count = calc._calculate_mitigation_factor("op-002")
        
        assert factor == 1.0
        assert count == 0
    
    def test_calculate_mitigation_factor_with_mitigations(self, sample_risk_network):
        """Test mitigation factor with mitigations applied."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        # strat-001 has one High effectiveness mitigation
        factor, count = calc._calculate_mitigation_factor("strat-001")
        
        assert factor < 1.0  # Should be reduced
        assert count == 1
    
    def test_calculate_all_returns_results(self, sample_risk_network):
        """Test calculate_all returns global results."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        results = calc.calculate_all()
        
        assert isinstance(results, GlobalExposureResult)
        assert results.total_risks == 3
        assert len(results.risk_results) > 0
    
    def test_calculate_all_empty_risks(self):
        """Test calculate_all handles empty risks."""
        calc = ExposureCalculator(
            risks=[],
            influences=[],
            mitigations=[],
            mitigates_relationships=[]
        )
        
        results = calc.calculate_all()
        
        assert results.total_risks == 0
        assert results.residual_risk_percentage == 0.0


class TestExposureCalculatorIntegration:
    """Integration tests for full exposure calculation."""
    
    def test_mitigated_risks_have_lower_exposure(self, sample_risk_network):
        """Test that mitigated risks have lower final exposure."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        results = calc.calculate_all()
        
        # Find the mitigated risk result
        strat_result = next(
            (r for r in results.risk_results if r.risk_id == "strat-001"),
            None
        )
        
        if strat_result:
            # Final exposure should be less than or equal to base
            assert strat_result.final_exposure <= strat_result.base_exposure
    
    def test_residual_percentage_is_valid(self, sample_risk_network):
        """Test residual percentage is between 0 and 100."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        results = calc.calculate_all()
        
        assert 0 <= results.residual_risk_percentage <= 100
    
    def test_weighted_score_is_valid(self, sample_risk_network):
        """Test weighted risk score is between 0 and 100."""
        calc = ExposureCalculator(
            risks=sample_risk_network["risks"],
            influences=sample_risk_network["influences"],
            mitigations=sample_risk_network["mitigations"],
            mitigates_relationships=sample_risk_network["mitigates_relationships"]
        )
        
        results = calc.calculate_all()
        
        assert 0 <= results.weighted_risk_score <= 100
