"""
Tests for models/tpo.py

Tests the TPO (Top Program Objective) dataclass including creation, properties, and serialization.
"""

import pytest
from models.tpo import TPO


class TestTPOCreation:
    """Tests for TPO dataclass creation."""
    
    def test_create_tpo_with_required_fields(self):
        """Test creating a TPO with required fields."""
        tpo = TPO(
            id="tpo-001",
            reference="TPO-01",
            name="Test Objective",
            cluster="Business Efficiency"
        )
        
        assert tpo.id == "tpo-001"
        assert tpo.reference == "TPO-01"
        assert tpo.name == "Test Objective"
        assert tpo.cluster == "Business Efficiency"
    
    def test_create_tpo_with_all_fields(self, sample_tpo_data):
        """Test creating a TPO with all fields."""
        tpo = TPO.from_dict(sample_tpo_data)
        
        assert tpo.id == sample_tpo_data["id"]
        assert tpo.reference == sample_tpo_data["reference"]
        assert tpo.name == sample_tpo_data["name"]
        assert tpo.cluster == sample_tpo_data["cluster"]
        assert tpo.description == sample_tpo_data["description"]
    
    def test_default_values(self):
        """Test default values are applied correctly."""
        tpo = TPO(
            id="tpo-001",
            reference="TPO-01",
            name="Test Objective",
            cluster="Safety"
        )
        
        assert tpo.description == ""
        assert tpo.created_at is None
        assert tpo.updated_at is None


class TestTPOPostInit:
    """Tests for TPO __post_init__ processing."""
    
    def test_valid_cluster_accepted(self):
        """Test that valid cluster values are accepted."""
        tpo = TPO(
            id="tpo-001",
            reference="TPO-01",
            name="Test",
            cluster="Business Efficiency"
        )
        assert tpo.cluster == "Business Efficiency"
    
    def test_invalid_cluster_accepted(self):
        """Test that invalid cluster values are still accepted (no strict validation)."""
        tpo = TPO(
            id="tpo-001",
            reference="TPO-01",
            name="Test",
            cluster="Unknown Cluster"
        )
        assert tpo.cluster == "Unknown Cluster"


class TestTPOProperties:
    """Tests for TPO property methods."""
    
    def test_display_label(self):
        """Test display_label combines reference and name."""
        tpo = TPO(
            id="tpo-001",
            reference="TPO-01",
            name="Cost Control",
            cluster="Business Efficiency"
        )
        
        assert tpo.display_label == "TPO-01: Cost Control"
    
    def test_short_label(self):
        """Test short_label returns only reference."""
        tpo = TPO(
            id="tpo-001",
            reference="TPO-01",
            name="Cost Control",
            cluster="Business Efficiency"
        )
        
        assert tpo.short_label == "TPO-01"
    
    def test_icon(self):
        """Test icon property returns emoji."""
        tpo = TPO(id="tpo-001", reference="TPO-01", name="Test", cluster="Safety")
        
        assert tpo.icon == "🟡"
    
    def test_color(self):
        """Test color property returns hex color."""
        tpo = TPO(id="tpo-001", reference="TPO-01", name="Test", cluster="Safety")
        
        assert tpo.color.startswith("#")
        assert tpo.color == "#f1c40f"  # Yellow


class TestTPOMethods:
    """Tests for TPO instance methods."""
    
    def test_to_dict(self, sample_tpo_data):
        """Test to_dict serialization."""
        tpo = TPO.from_dict(sample_tpo_data)
        
        result = tpo.to_dict()
        
        assert result["id"] == sample_tpo_data["id"]
        assert result["reference"] == sample_tpo_data["reference"]
        assert result["name"] == sample_tpo_data["name"]
        assert result["cluster"] == sample_tpo_data["cluster"]
        assert result["description"] == sample_tpo_data["description"]
    
    def test_from_dict(self, sample_tpo_data):
        """Test from_dict deserialization."""
        tpo = TPO.from_dict(sample_tpo_data)
        
        assert tpo.id == sample_tpo_data["id"]
        assert tpo.reference == sample_tpo_data["reference"]
        assert tpo.name == sample_tpo_data["name"]
        assert tpo.cluster == sample_tpo_data["cluster"]
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal data uses defaults."""
        data = {"id": "tpo-001", "reference": "TPO-01", "name": "Minimal TPO"}
        
        tpo = TPO.from_dict(data)
        
        assert tpo.id == "tpo-001"
        assert tpo.cluster == "Business Efficiency"  # Default
        assert tpo.description == ""
    
    def test_from_neo4j_record(self, sample_tpo_data):
        """Test from_neo4j_record creates TPO correctly."""
        tpo = TPO.from_neo4j_record(sample_tpo_data)
        
        assert tpo.id == sample_tpo_data["id"]
        assert tpo.reference == sample_tpo_data["reference"]


class TestTPORoundTrip:
    """Tests for TPO serialization round-trips."""
    
    def test_dict_round_trip(self, sample_tpo_data):
        """Test that to_dict -> from_dict preserves data."""
        original = TPO.from_dict(sample_tpo_data)
        
        serialized = original.to_dict()
        restored = TPO.from_dict(serialized)
        
        assert restored.id == original.id
        assert restored.reference == original.reference
        assert restored.name == original.name
        assert restored.cluster == original.cluster
        assert restored.description == original.description
