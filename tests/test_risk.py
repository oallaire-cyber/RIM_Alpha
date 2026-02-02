"""
Tests for models/risk.py

Tests the Risk dataclass including creation, properties, and serialization.
"""

import pytest
from models.risk import Risk
from models.enums import RiskLevel, RiskStatus, RiskOrigin


class TestRiskCreation:
    """Tests for Risk dataclass creation."""
    
    def test_create_risk_with_required_fields(self):
        """Test creating a risk with only required fields."""
        risk = Risk(id="test-001", name="Test Risk", level=RiskLevel.STRATEGIC)
        
        assert risk.id == "test-001"
        assert risk.name == "Test Risk"
        assert risk.level == RiskLevel.STRATEGIC
    
    def test_create_risk_with_all_fields(self, sample_risk_data):
        """Test creating a risk with all fields."""
        risk = Risk.from_dict(sample_risk_data)
        
        assert risk.id == sample_risk_data["id"]
        assert risk.name == sample_risk_data["name"]
        assert risk.level == RiskLevel.STRATEGIC
        assert risk.status == RiskStatus.ACTIVE
        assert risk.origin == RiskOrigin.NEW
    
    def test_default_values(self):
        """Test default values are applied correctly."""
        risk = Risk(id="test-001", name="Test Risk", level=RiskLevel.OPERATIONAL)
        
        assert risk.categories == []
        assert risk.status == RiskStatus.ACTIVE
        assert risk.origin == RiskOrigin.NEW
        assert risk.description == ""
        assert risk.owner == ""
        assert risk.probability is None
        assert risk.impact is None


class TestRiskPostInit:
    """Tests for Risk __post_init__ processing."""
    
    def test_string_level_conversion(self):
        """Test that string level is converted to enum."""
        risk = Risk(id="test-001", name="Test Risk", level="Strategic")
        assert risk.level == RiskLevel.STRATEGIC
    
    def test_string_status_conversion(self):
        """Test that string status is converted to enum."""
        risk = Risk(id="test-001", name="Test Risk", level="Strategic", status="Contingent")
        assert risk.status == RiskStatus.CONTINGENT
    
    def test_string_origin_conversion(self):
        """Test that string origin is converted to enum."""
        risk = Risk(id="test-001", name="Test Risk", level="Strategic", origin="Legacy")
        assert risk.origin == RiskOrigin.LEGACY
    
    def test_exposure_calculation(self):
        """Test that exposure is auto-calculated if not provided."""
        risk = Risk(
            id="test-001",
            name="Test Risk",
            level=RiskLevel.STRATEGIC,
            probability=5.0,
            impact=8.0
        )
        assert risk.exposure == 40.0
    
    def test_exposure_not_overwritten(self):
        """Test that provided exposure is not overwritten."""
        risk = Risk(
            id="test-001",
            name="Test Risk",
            level=RiskLevel.STRATEGIC,
            probability=5.0,
            impact=8.0,
            exposure=50.0  # Different from calculated
        )
        # The __post_init__ only calculates if exposure is None
        assert risk.exposure == 50.0


class TestRiskProperties:
    """Tests for Risk property methods."""
    
    def test_is_strategic(self):
        """Test is_strategic property."""
        strategic = Risk(id="1", name="R", level=RiskLevel.STRATEGIC)
        operational = Risk(id="2", name="R", level=RiskLevel.OPERATIONAL)
        
        assert strategic.is_strategic is True
        assert operational.is_strategic is False
    
    def test_is_operational(self):
        """Test is_operational property."""
        strategic = Risk(id="1", name="R", level=RiskLevel.STRATEGIC)
        operational = Risk(id="2", name="R", level=RiskLevel.OPERATIONAL)
        
        assert strategic.is_operational is False
        assert operational.is_operational is True
    
    def test_is_contingent(self):
        """Test is_contingent property."""
        active = Risk(id="1", name="R", level=RiskLevel.STRATEGIC, status=RiskStatus.ACTIVE)
        contingent = Risk(id="2", name="R", level=RiskLevel.STRATEGIC, status=RiskStatus.CONTINGENT)
        
        assert active.is_contingent is False
        assert contingent.is_contingent is True
    
    def test_is_legacy(self):
        """Test is_legacy property."""
        new = Risk(id="1", name="R", level=RiskLevel.STRATEGIC, origin=RiskOrigin.NEW)
        legacy = Risk(id="2", name="R", level=RiskLevel.STRATEGIC, origin=RiskOrigin.LEGACY)
        
        assert new.is_legacy is False
        assert legacy.is_legacy is True
    
    def test_level_icon(self):
        """Test level_icon property returns emoji."""
        risk = Risk(id="1", name="R", level=RiskLevel.STRATEGIC)
        assert risk.level_icon == "🟣"
    
    def test_origin_icon(self):
        """Test origin_icon property returns emoji."""
        risk = Risk(id="1", name="R", level=RiskLevel.STRATEGIC, origin=RiskOrigin.LEGACY)
        assert isinstance(risk.origin_icon, str)
    
    def test_display_name_new(self):
        """Test display_name for new risks."""
        risk = Risk(id="1", name="Test Risk", level=RiskLevel.STRATEGIC, origin=RiskOrigin.NEW)
        assert risk.display_name == "Test Risk"
    
    def test_display_name_legacy(self):
        """Test display_name for legacy risks has prefix."""
        risk = Risk(id="1", name="Test Risk", level=RiskLevel.STRATEGIC, origin=RiskOrigin.LEGACY)
        assert risk.display_name == "[L] Test Risk"


class TestRiskMethods:
    """Tests for Risk instance methods."""
    
    def test_calculate_exposure(self):
        """Test calculate_exposure method."""
        risk = Risk(
            id="test-001",
            name="Test Risk",
            level=RiskLevel.STRATEGIC,
            probability=6.0,
            impact=7.0
        )
        risk.exposure = None  # Reset
        
        result = risk.calculate_exposure()
        
        assert result == 42.0
        assert risk.exposure == 42.0
    
    def test_calculate_exposure_no_data(self):
        """Test calculate_exposure with missing data returns None."""
        risk = Risk(id="1", name="R", level=RiskLevel.STRATEGIC)
        
        result = risk.calculate_exposure()
        
        assert result is None
    
    def test_to_dict(self, sample_risk_data):
        """Test to_dict serialization."""
        risk = Risk.from_dict(sample_risk_data)
        
        result = risk.to_dict()
        
        assert result["id"] == sample_risk_data["id"]
        assert result["name"] == sample_risk_data["name"]
        assert result["level"] == "Strategic"  # String, not enum
        assert result["status"] == "Active"
        assert result["categories"] == sample_risk_data["categories"]
    
    def test_from_dict(self, sample_risk_data):
        """Test from_dict deserialization."""
        risk = Risk.from_dict(sample_risk_data)
        
        assert risk.id == sample_risk_data["id"]
        assert risk.name == sample_risk_data["name"]
        assert risk.level == RiskLevel.STRATEGIC
        assert risk.probability == sample_risk_data["probability"]
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal data uses defaults."""
        data = {"id": "test-001", "name": "Minimal Risk"}
        
        risk = Risk.from_dict(data)
        
        assert risk.id == "test-001"
        assert risk.level == RiskLevel.STRATEGIC  # Default
        assert risk.status == RiskStatus.ACTIVE  # Default
    
    def test_from_neo4j_record(self, sample_risk_data):
        """Test from_neo4j_record creates Risk correctly."""
        # Simulate a Neo4j record (dict-like)
        risk = Risk.from_neo4j_record(sample_risk_data)
        
        assert risk.id == sample_risk_data["id"]
        assert risk.name == sample_risk_data["name"]


class TestRiskRoundTrip:
    """Tests for Risk serialization round-trips."""
    
    def test_dict_round_trip(self, sample_risk_data):
        """Test that to_dict -> from_dict preserves data."""
        original = Risk.from_dict(sample_risk_data)
        
        serialized = original.to_dict()
        restored = Risk.from_dict(serialized)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.level == original.level
        assert restored.status == original.status
        assert restored.probability == original.probability
