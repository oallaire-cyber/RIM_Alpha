"""
Tests for models/mitigation.py

Tests the Mitigation dataclass including creation, properties, and serialization.
"""

import pytest
from models.mitigation import Mitigation
from models.enums import MitigationType, MitigationStatus


class TestMitigationCreation:
    """Tests for Mitigation dataclass creation."""
    
    def test_create_mitigation_with_required_fields(self):
        """Test creating a mitigation with only required fields."""
        mitigation = Mitigation(id="mit-001", name="Test Mitigation")
        
        assert mitigation.id == "mit-001"
        assert mitigation.name == "Test Mitigation"
        assert mitigation.type == MitigationType.DEDICATED  # Default
        assert mitigation.status == MitigationStatus.PROPOSED  # Default
    
    def test_create_mitigation_with_all_fields(self, sample_mitigation_data):
        """Test creating a mitigation with all fields."""
        mitigation = Mitigation.from_dict(sample_mitigation_data)
        
        assert mitigation.id == sample_mitigation_data["id"]
        assert mitigation.name == sample_mitigation_data["name"]
        assert mitigation.type == MitigationType.DEDICATED
        assert mitigation.status == MitigationStatus.IMPLEMENTED
    
    def test_default_values(self):
        """Test default values are applied correctly."""
        mitigation = Mitigation(id="mit-001", name="Test Mitigation")
        
        assert mitigation.type == MitigationType.DEDICATED
        assert mitigation.status == MitigationStatus.PROPOSED
        assert mitigation.description == ""
        assert mitigation.owner == ""
        assert mitigation.source_entity == ""


class TestMitigationPostInit:
    """Tests for Mitigation __post_init__ processing."""
    
    def test_string_type_conversion(self):
        """Test that string type is converted to enum."""
        mitigation = Mitigation(id="mit-001", name="Test", type="Inherited")
        assert mitigation.type == MitigationType.INHERITED
    
    def test_string_status_conversion(self):
        """Test that string status is converted to enum."""
        mitigation = Mitigation(id="mit-001", name="Test", status="In Progress")
        assert mitigation.status == MitigationStatus.IN_PROGRESS


class TestMitigationProperties:
    """Tests for Mitigation property methods."""
    
    def test_is_implemented(self):
        """Test is_implemented property."""
        implemented = Mitigation(id="1", name="M", status=MitigationStatus.IMPLEMENTED)
        proposed = Mitigation(id="2", name="M", status=MitigationStatus.PROPOSED)
        
        assert implemented.is_implemented is True
        assert proposed.is_implemented is False
    
    def test_is_active(self):
        """Test is_active property."""
        implemented = Mitigation(id="1", name="M", status=MitigationStatus.IMPLEMENTED)
        in_progress = Mitigation(id="2", name="M", status=MitigationStatus.IN_PROGRESS)
        proposed = Mitigation(id="3", name="M", status=MitigationStatus.PROPOSED)
        deferred = Mitigation(id="4", name="M", status=MitigationStatus.DEFERRED)
        
        assert implemented.is_active is True
        assert in_progress.is_active is True
        assert proposed.is_active is False
        assert deferred.is_active is False
    
    def test_is_dedicated(self):
        """Test is_dedicated property."""
        dedicated = Mitigation(id="1", name="M", type=MitigationType.DEDICATED)
        inherited = Mitigation(id="2", name="M", type=MitigationType.INHERITED)
        baseline = Mitigation(id="3", name="M", type=MitigationType.BASELINE)
        
        assert dedicated.is_dedicated is True
        assert inherited.is_dedicated is False
        assert baseline.is_dedicated is False
    
    def test_type_icon(self):
        """Test type_icon property returns emoji."""
        mitigation = Mitigation(id="1", name="M", type=MitigationType.DEDICATED)
        assert isinstance(mitigation.type_icon, str)
    
    def test_status_icon(self):
        """Test status_icon property returns emoji."""
        mitigation = Mitigation(id="1", name="M", status=MitigationStatus.IMPLEMENTED)
        assert isinstance(mitigation.status_icon, str)
    
    def test_color(self):
        """Test color property returns hex color."""
        dedicated = Mitigation(id="1", name="M", type=MitigationType.DEDICATED)
        inherited = Mitigation(id="2", name="M", type=MitigationType.INHERITED)
        
        assert dedicated.color.startswith("#")
        assert inherited.color.startswith("#")
    
    def test_display_name(self):
        """Test display_name property includes shield emoji."""
        mitigation = Mitigation(id="1", name="Test Mitigation")
        assert "🛡️" in mitigation.display_name
        assert "Test Mitigation" in mitigation.display_name


class TestMitigationMethods:
    """Tests for Mitigation instance methods."""
    
    def test_to_dict(self, sample_mitigation_data):
        """Test to_dict serialization."""
        mitigation = Mitigation.from_dict(sample_mitigation_data)
        
        result = mitigation.to_dict()
        
        assert result["id"] == sample_mitigation_data["id"]
        assert result["name"] == sample_mitigation_data["name"]
        assert result["type"] == "Dedicated"  # String, not enum
        assert result["status"] == "Implemented"
    
    def test_from_dict(self, sample_mitigation_data):
        """Test from_dict deserialization."""
        mitigation = Mitigation.from_dict(sample_mitigation_data)
        
        assert mitigation.id == sample_mitigation_data["id"]
        assert mitigation.name == sample_mitigation_data["name"]
        assert mitigation.type == MitigationType.DEDICATED
        assert mitigation.status == MitigationStatus.IMPLEMENTED
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal data uses defaults."""
        data = {"id": "mit-001", "name": "Minimal Mitigation"}
        
        mitigation = Mitigation.from_dict(data)
        
        assert mitigation.id == "mit-001"
        assert mitigation.type == MitigationType.DEDICATED  # Default
        assert mitigation.status == MitigationStatus.PROPOSED  # Default
    
    def test_from_neo4j_record(self, sample_mitigation_data):
        """Test from_neo4j_record creates Mitigation correctly."""
        mitigation = Mitigation.from_neo4j_record(sample_mitigation_data)
        
        assert mitigation.id == sample_mitigation_data["id"]
        assert mitigation.name == sample_mitigation_data["name"]


class TestMitigationRoundTrip:
    """Tests for Mitigation serialization round-trips."""
    
    def test_dict_round_trip(self, sample_mitigation_data):
        """Test that to_dict -> from_dict preserves data."""
        original = Mitigation.from_dict(sample_mitigation_data)
        
        serialized = original.to_dict()
        restored = Mitigation.from_dict(serialized)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.type == original.type
        assert restored.status == original.status
