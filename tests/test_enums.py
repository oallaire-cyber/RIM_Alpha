"""
Tests for models/enums.py

Tests all enum classes and their properties including icons, colors, and value scores.
"""

import pytest
from models.enums import (
    RiskLevel,
    RiskStatus,
    RiskOrigin,
    RiskCategory,
    TPOCluster,
    MitigationType,
    MitigationStatus,
    Effectiveness,
    InfluenceStrength,
    ImpactLevel,
    InfluenceType,
)


class TestRiskLevel:
    """Tests for RiskLevel enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert RiskLevel.STRATEGIC.value == "Strategic"
        assert RiskLevel.OPERATIONAL.value == "Operational"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(RiskLevel.STRATEGIC) == "Strategic"
        assert str(RiskLevel.OPERATIONAL) == "Operational"
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert RiskLevel.STRATEGIC.icon == "🟣"
        assert RiskLevel.OPERATIONAL.icon == "🔵"
    
    def test_color_property(self):
        """Test color property returns hex color."""
        assert RiskLevel.STRATEGIC.color.startswith("#")
        assert RiskLevel.OPERATIONAL.color.startswith("#")


class TestRiskStatus:
    """Tests for RiskStatus enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert RiskStatus.ACTIVE.value == "Active"
        assert RiskStatus.CONTINGENT.value == "Contingent"
        assert RiskStatus.ARCHIVED.value == "Archived"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(RiskStatus.ACTIVE) == "Active"
        assert str(RiskStatus.CONTINGENT) == "Contingent"
    
    def test_icon_property(self):
        """Test icon property returns appropriate emoji."""
        # Each status should return an icon string
        assert isinstance(RiskStatus.ACTIVE.icon, str)
        assert isinstance(RiskStatus.CONTINGENT.icon, str)
        assert isinstance(RiskStatus.ARCHIVED.icon, str)


class TestRiskOrigin:
    """Tests for RiskOrigin enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert RiskOrigin.NEW.value == "New"
        assert RiskOrigin.LEGACY.value == "Legacy"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(RiskOrigin.NEW) == "New"
        assert str(RiskOrigin.LEGACY) == "Legacy"
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert isinstance(RiskOrigin.NEW.icon, str)
        assert isinstance(RiskOrigin.LEGACY.icon, str)


class TestRiskCategory:
    """Tests for RiskCategory enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert RiskCategory.PROGRAMME.value == "Programme"
        assert RiskCategory.PRODUIT.value == "Produit"
        assert RiskCategory.INDUSTRIEL.value == "Industriel"
        assert RiskCategory.SUPPLY_CHAIN.value == "Supply Chain"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(RiskCategory.PROGRAMME) == "Programme"


class TestTPOCluster:
    """Tests for TPOCluster enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert TPOCluster.PRODUCT_EFFICIENCY.value == "Product Efficiency"
        assert TPOCluster.BUSINESS_EFFICIENCY.value == "Business Efficiency"
        assert TPOCluster.INDUSTRIAL_EFFICIENCY.value == "Industrial Efficiency"
        assert TPOCluster.SUSTAINABILITY.value == "Sustainability"
        assert TPOCluster.SAFETY.value == "Safety"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(TPOCluster.SAFETY) == "Safety"


class TestMitigationType:
    """Tests for MitigationType enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert MitigationType.DEDICATED.value == "Dedicated"
        assert MitigationType.INHERITED.value == "Inherited"
        assert MitigationType.BASELINE.value == "Baseline"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(MitigationType.DEDICATED) == "Dedicated"
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert isinstance(MitigationType.DEDICATED.icon, str)
        assert isinstance(MitigationType.INHERITED.icon, str)
        assert isinstance(MitigationType.BASELINE.icon, str)
    
    def test_color_property(self):
        """Test color property returns hex color."""
        assert MitigationType.DEDICATED.color.startswith("#")
        assert MitigationType.INHERITED.color.startswith("#")
        assert MitigationType.BASELINE.color.startswith("#")


class TestMitigationStatus:
    """Tests for MitigationStatus enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert MitigationStatus.PROPOSED.value == "Proposed"
        assert MitigationStatus.IN_PROGRESS.value == "In Progress"
        assert MitigationStatus.IMPLEMENTED.value == "Implemented"
        assert MitigationStatus.DEFERRED.value == "Deferred"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(MitigationStatus.IMPLEMENTED) == "Implemented"
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert isinstance(MitigationStatus.PROPOSED.icon, str)
        assert isinstance(MitigationStatus.IN_PROGRESS.icon, str)
        assert isinstance(MitigationStatus.IMPLEMENTED.icon, str)
        assert isinstance(MitigationStatus.DEFERRED.icon, str)


class TestEffectiveness:
    """Tests for Effectiveness enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert Effectiveness.LOW.value == "Low"
        assert Effectiveness.MEDIUM.value == "Medium"
        assert Effectiveness.HIGH.value == "High"
        assert Effectiveness.CRITICAL.value == "Critical"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(Effectiveness.HIGH) == "High"
    
    def test_value_score_property(self):
        """Test value_score returns numeric scores in ascending order."""
        assert Effectiveness.LOW.value_score < Effectiveness.MEDIUM.value_score
        assert Effectiveness.MEDIUM.value_score < Effectiveness.HIGH.value_score
        assert Effectiveness.HIGH.value_score < Effectiveness.CRITICAL.value_score
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert isinstance(Effectiveness.LOW.icon, str)
        assert isinstance(Effectiveness.HIGH.icon, str)


class TestInfluenceStrength:
    """Tests for InfluenceStrength enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert InfluenceStrength.WEAK.value == "Weak"
        assert InfluenceStrength.MODERATE.value == "Moderate"
        assert InfluenceStrength.STRONG.value == "Strong"
        assert InfluenceStrength.CRITICAL.value == "Critical"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(InfluenceStrength.STRONG) == "Strong"
    
    def test_value_score_property(self):
        """Test value_score returns numeric scores in ascending order."""
        assert InfluenceStrength.WEAK.value_score < InfluenceStrength.MODERATE.value_score
        assert InfluenceStrength.MODERATE.value_score < InfluenceStrength.STRONG.value_score
        assert InfluenceStrength.STRONG.value_score < InfluenceStrength.CRITICAL.value_score


class TestImpactLevel:
    """Tests for ImpactLevel enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert ImpactLevel.LOW.value == "Low"
        assert ImpactLevel.MEDIUM.value == "Medium"
        assert ImpactLevel.HIGH.value == "High"
        assert ImpactLevel.CRITICAL.value == "Critical"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(ImpactLevel.HIGH) == "High"
    
    def test_value_score_property(self):
        """Test value_score returns numeric scores in ascending order."""
        assert ImpactLevel.LOW.value_score < ImpactLevel.MEDIUM.value_score
        assert ImpactLevel.MEDIUM.value_score < ImpactLevel.HIGH.value_score
        assert ImpactLevel.HIGH.value_score < ImpactLevel.CRITICAL.value_score
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert isinstance(ImpactLevel.LOW.icon, str)
        assert isinstance(ImpactLevel.CRITICAL.icon, str)


class TestInfluenceType:
    """Tests for InfluenceType enum."""
    
    def test_values(self):
        """Test enum values exist."""
        assert InfluenceType.LEVEL1_OP_TO_STRAT.value == "Level1_Op_to_Strat"
        assert InfluenceType.LEVEL2_STRAT_TO_STRAT.value == "Level2_Strat_to_Strat"
        assert InfluenceType.LEVEL3_OP_TO_OP.value == "Level3_Op_to_Op"
    
    def test_str_conversion(self):
        """Test string conversion."""
        assert str(InfluenceType.LEVEL1_OP_TO_STRAT) == "Level1_Op_to_Strat"
    
    def test_icon_property(self):
        """Test icon property returns emoji."""
        assert isinstance(InfluenceType.LEVEL1_OP_TO_STRAT.icon, str)
    
    def test_color_property(self):
        """Test color property returns hex color."""
        assert InfluenceType.LEVEL1_OP_TO_STRAT.color.startswith("#")
        assert InfluenceType.LEVEL2_STRAT_TO_STRAT.color.startswith("#")
        assert InfluenceType.LEVEL3_OP_TO_OP.color.startswith("#")
