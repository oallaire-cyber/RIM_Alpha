"""
Tests for models/relationships.py

Tests the relationship dataclasses: Influence, TPOImpact, and MitigatesRelationship.
"""

import pytest
from models.relationships import Influence, TPOImpact, MitigatesRelationship
from models.enums import InfluenceType, InfluenceStrength, ImpactLevel, Effectiveness


class TestInfluenceCreation:
    """Tests for Influence dataclass creation."""
    
    def test_create_influence_with_required_fields(self):
        """Test creating an influence with required fields."""
        influence = Influence(
            id="inf-001",
            source_id="risk-001",
            target_id="risk-002"
        )
        
        assert influence.id == "inf-001"
        assert influence.source_id == "risk-001"
        assert influence.target_id == "risk-002"
    
    def test_create_influence_with_all_fields(self, sample_influence_data):
        """Test creating an influence with all fields."""
        influence = Influence.from_dict(sample_influence_data)
        
        assert influence.id == sample_influence_data["id"]
        assert influence.source_id == sample_influence_data["source_id"]
        assert influence.target_id == sample_influence_data["target_id"]
        assert influence.strength == InfluenceStrength.STRONG


class TestInfluencePostInit:
    """Tests for Influence __post_init__ processing."""
    
    def test_string_type_conversion(self):
        """Test that string type is converted to enum."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            influence_type="Level1_Op_to_Strat"
        )
        assert influence.influence_type == InfluenceType.LEVEL1_OP_TO_STRAT
    
    def test_string_strength_conversion(self):
        """Test that string strength is converted to enum."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            strength="Critical"
        )
        assert influence.strength == InfluenceStrength.CRITICAL


class TestInfluenceProperties:
    """Tests for Influence property methods."""
    
    def test_strength_score(self):
        """Test strength_score property returns numeric value."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            strength=InfluenceStrength.STRONG
        )
        
        assert influence.strength_score == InfluenceStrength.STRONG.value_score
        assert influence.strength_score > 0
    
    def test_weighted_score(self):
        """Test weighted_score combines strength and confidence."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            strength=InfluenceStrength.STRONG,
            confidence=0.8
        )
        
        expected = influence.strength_score * 0.8
        assert influence.weighted_score == expected
    
    def test_type_icon(self):
        """Test type_icon property returns emoji."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            influence_type=InfluenceType.LEVEL1_OP_TO_STRAT
        )
        
        assert isinstance(influence.type_icon, str)
    
    def test_color(self):
        """Test color property returns hex color."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            influence_type=InfluenceType.LEVEL1_OP_TO_STRAT
        )
        
        assert influence.color.startswith("#")
    
    def test_display_label(self):
        """Test display_label property."""
        influence = Influence(
            id="inf-001",
            source_id="r1",
            target_id="r2",
            strength=InfluenceStrength.STRONG
        )
        
        # display_label shows source → target names (not strength)
        assert isinstance(influence.display_label, str)
        assert "→" in influence.display_label


class TestInfluenceMethods:
    """Tests for Influence instance methods."""
    
    def test_to_dict(self, sample_influence_data):
        """Test to_dict serialization."""
        influence = Influence.from_dict(sample_influence_data)
        
        result = influence.to_dict()
        
        assert result["id"] == sample_influence_data["id"]
        assert result["source_id"] == sample_influence_data["source_id"]
        assert result["target_id"] == sample_influence_data["target_id"]
        assert result["strength"] == "Strong"  # String, not enum
    
    def test_from_dict(self, sample_influence_data):
        """Test from_dict deserialization."""
        influence = Influence.from_dict(sample_influence_data)
        
        assert influence.id == sample_influence_data["id"]
        assert influence.strength == InfluenceStrength.STRONG
        assert influence.confidence == sample_influence_data["confidence"]
    
    def test_from_neo4j_record(self, sample_influence_data):
        """Test from_neo4j_record creates Influence correctly."""
        influence = Influence.from_neo4j_record(sample_influence_data)
        
        assert influence.id == sample_influence_data["id"]


# =============================================================================
# TPO IMPACT TESTS
# =============================================================================

class TestTPOImpactCreation:
    """Tests for TPOImpact dataclass creation."""
    
    def test_create_tpo_impact_with_required_fields(self):
        """Test creating a TPO impact with required fields."""
        impact = TPOImpact(
            id="impact-001",
            risk_id="risk-001",
            tpo_id="tpo-001"
        )
        
        assert impact.id == "impact-001"
        assert impact.risk_id == "risk-001"
        assert impact.tpo_id == "tpo-001"
    
    def test_create_tpo_impact_with_all_fields(self, sample_tpo_impact_data):
        """Test creating a TPO impact with all fields."""
        impact = TPOImpact.from_dict(sample_tpo_impact_data)
        
        assert impact.id == sample_tpo_impact_data["id"]
        assert impact.risk_id == sample_tpo_impact_data["risk_id"]
        assert impact.tpo_id == sample_tpo_impact_data["tpo_id"]
        assert impact.impact_level == ImpactLevel.HIGH


class TestTPOImpactPostInit:
    """Tests for TPOImpact __post_init__ processing."""
    
    def test_string_impact_level_conversion(self):
        """Test that string impact_level is converted to enum."""
        impact = TPOImpact(
            id="impact-001",
            risk_id="r1",
            tpo_id="t1",
            impact_level="Critical"
        )
        assert impact.impact_level == ImpactLevel.CRITICAL


class TestTPOImpactProperties:
    """Tests for TPOImpact property methods."""
    
    def test_impact_score(self):
        """Test impact_score property returns numeric value."""
        impact = TPOImpact(
            id="impact-001",
            risk_id="r1",
            tpo_id="t1",
            impact_level=ImpactLevel.HIGH
        )
        
        assert impact.impact_score == ImpactLevel.HIGH.value_score
        assert impact.impact_score > 0
    
    def test_impact_icon(self):
        """Test impact_icon property returns emoji."""
        impact = TPOImpact(
            id="impact-001",
            risk_id="r1",
            tpo_id="t1",
            impact_level=ImpactLevel.HIGH
        )
        
        assert isinstance(impact.impact_icon, str)
    
    def test_display_label(self):
        """Test display_label property."""
        impact = TPOImpact(
            id="impact-001",
            risk_id="r1",
            tpo_id="t1",
            impact_level=ImpactLevel.HIGH
        )
        
        # display_label shows risk → TPO names (not impact level)
        assert isinstance(impact.display_label, str)
        assert "→" in impact.display_label


class TestTPOImpactMethods:
    """Tests for TPOImpact instance methods."""
    
    def test_to_dict(self, sample_tpo_impact_data):
        """Test to_dict serialization."""
        impact = TPOImpact.from_dict(sample_tpo_impact_data)
        
        result = impact.to_dict()
        
        assert result["id"] == sample_tpo_impact_data["id"]
        assert result["risk_id"] == sample_tpo_impact_data["risk_id"]
        assert result["tpo_id"] == sample_tpo_impact_data["tpo_id"]
        assert result["impact_level"] == "High"  # String, not enum
    
    def test_from_dict(self, sample_tpo_impact_data):
        """Test from_dict deserialization."""
        impact = TPOImpact.from_dict(sample_tpo_impact_data)
        
        assert impact.id == sample_tpo_impact_data["id"]
        assert impact.impact_level == ImpactLevel.HIGH


# =============================================================================
# MITIGATES RELATIONSHIP TESTS
# =============================================================================

class TestMitigatesRelationshipCreation:
    """Tests for MitigatesRelationship dataclass creation."""
    
    def test_create_mitigates_with_required_fields(self):
        """Test creating a mitigates relationship with required fields."""
        mitigates = MitigatesRelationship(
            id="mitigates-001",
            mitigation_id="mit-001",
            risk_id="risk-001"
        )
        
        assert mitigates.id == "mitigates-001"
        assert mitigates.mitigation_id == "mit-001"
        assert mitigates.risk_id == "risk-001"
    
    def test_create_mitigates_with_all_fields(self, sample_mitigates_data):
        """Test creating a mitigates relationship with all fields."""
        mitigates = MitigatesRelationship.from_dict(sample_mitigates_data)
        
        assert mitigates.id == sample_mitigates_data["id"]
        assert mitigates.mitigation_id == sample_mitigates_data["mitigation_id"]
        assert mitigates.risk_id == sample_mitigates_data["risk_id"]
        assert mitigates.effectiveness == Effectiveness.HIGH


class TestMitigatesRelationshipPostInit:
    """Tests for MitigatesRelationship __post_init__ processing."""
    
    def test_string_effectiveness_conversion(self):
        """Test that string effectiveness is converted to enum."""
        mitigates = MitigatesRelationship(
            id="mitigates-001",
            mitigation_id="m1",
            risk_id="r1",
            effectiveness="Critical"
        )
        assert mitigates.effectiveness == Effectiveness.CRITICAL


class TestMitigatesRelationshipProperties:
    """Tests for MitigatesRelationship property methods."""
    
    def test_effectiveness_score(self):
        """Test effectiveness_score property returns numeric value."""
        mitigates = MitigatesRelationship(
            id="mitigates-001",
            mitigation_id="m1",
            risk_id="r1",
            effectiveness=Effectiveness.HIGH
        )
        
        assert mitigates.effectiveness_score == Effectiveness.HIGH.value_score
        assert mitigates.effectiveness_score > 0
    
    def test_effectiveness_icon(self):
        """Test effectiveness_icon property returns emoji."""
        mitigates = MitigatesRelationship(
            id="mitigates-001",
            mitigation_id="m1",
            risk_id="r1",
            effectiveness=Effectiveness.HIGH
        )
        
        assert isinstance(mitigates.effectiveness_icon, str)
    
    def test_display_label(self):
        """Test display_label property."""
        mitigates = MitigatesRelationship(
            id="mitigates-001",
            mitigation_id="m1",
            risk_id="r1",
            effectiveness=Effectiveness.HIGH
        )
        
        # display_label shows mitigation → risk names (not effectiveness)
        assert isinstance(mitigates.display_label, str)
        assert "→" in mitigates.display_label


class TestMitigatesRelationshipMethods:
    """Tests for MitigatesRelationship instance methods."""
    
    def test_to_dict(self, sample_mitigates_data):
        """Test to_dict serialization."""
        mitigates = MitigatesRelationship.from_dict(sample_mitigates_data)
        
        result = mitigates.to_dict()
        
        assert result["id"] == sample_mitigates_data["id"]
        assert result["mitigation_id"] == sample_mitigates_data["mitigation_id"]
        assert result["risk_id"] == sample_mitigates_data["risk_id"]
        assert result["effectiveness"] == "High"  # String, not enum
    
    def test_from_dict(self, sample_mitigates_data):
        """Test from_dict deserialization."""
        mitigates = MitigatesRelationship.from_dict(sample_mitigates_data)
        
        assert mitigates.id == sample_mitigates_data["id"]
        assert mitigates.effectiveness == Effectiveness.HIGH


# =============================================================================
# ROUND TRIP TESTS
# =============================================================================

class TestRelationshipRoundTrips:
    """Tests for relationship serialization round-trips."""
    
    def test_influence_round_trip(self, sample_influence_data):
        """Test Influence to_dict -> from_dict preserves data."""
        original = Influence.from_dict(sample_influence_data)
        
        serialized = original.to_dict()
        restored = Influence.from_dict(serialized)
        
        assert restored.id == original.id
        assert restored.source_id == original.source_id
        assert restored.target_id == original.target_id
        assert restored.strength == original.strength
    
    def test_tpo_impact_round_trip(self, sample_tpo_impact_data):
        """Test TPOImpact to_dict -> from_dict preserves data."""
        original = TPOImpact.from_dict(sample_tpo_impact_data)
        
        serialized = original.to_dict()
        restored = TPOImpact.from_dict(serialized)
        
        assert restored.id == original.id
        assert restored.risk_id == original.risk_id
        assert restored.impact_level == original.impact_level
    
    def test_mitigates_round_trip(self, sample_mitigates_data):
        """Test MitigatesRelationship to_dict -> from_dict preserves data."""
        original = MitigatesRelationship.from_dict(sample_mitigates_data)
        
        serialized = original.to_dict()
        restored = MitigatesRelationship.from_dict(serialized)
        
        assert restored.id == original.id
        assert restored.mitigation_id == original.mitigation_id
        assert restored.effectiveness == original.effectiveness
