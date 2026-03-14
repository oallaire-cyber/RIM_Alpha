"""
Tests for core/validation.py

Tests dynamic Pydantic model generation and validation.
"""

import pytest
from core.attribute import AttributeDefinition, AttributeType
from core.entity import EntityTypeDefinition
from core.validation import create_entity_model, validate_entity_data_pydantic


@pytest.fixture
def sample_entity_type():
    """Create a sample entity type for testing."""
    attrs = [
        AttributeDefinition(name="name", type=AttributeType.STRING, required=True),
        AttributeDefinition(name="age", type=AttributeType.INT, min_value=0, max_value=120),
        AttributeDefinition(name="score", type=AttributeType.FLOAT, required=False, default=0.0),
        AttributeDefinition(name="is_active", type=AttributeType.BOOL, default=True),
    ]
    return EntityTypeDefinition(
        id="person",
        label="Person",
        neo4j_label="Person",
        attributes=attrs
    )


class TestValidationPydantic:
    """Tests for dynamic Pydantic validation."""

    def test_create_entity_model(self, sample_entity_type):
        """Test creating a Pydantic model from an EntityTypeDefinition."""
        ModelClass = create_entity_model(sample_entity_type)
        
        # Test valid data
        instance = ModelClass(name="Alice", age=30)
        assert instance.name == "Alice"
        assert instance.age == 30
        assert instance.score == 0.0  # Default applied
        assert instance.is_active is True

    def test_validate_valid_data(self, sample_entity_type):
        """Test validate_entity_data_pydantic with valid data."""
        data = {"name": "Bob", "age": 45, "score": 95.5}
        is_valid, errors = validate_entity_data_pydantic(sample_entity_type, data)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_required(self, sample_entity_type):
        """Test validate_entity_data_pydantic with missing required field."""
        data = {"age": 25}  # Missing 'name'
        is_valid, errors = validate_entity_data_pydantic(sample_entity_type, data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("name" in err for err in errors)

    def test_validate_invalid_type(self, sample_entity_type):
        """Test validate_entity_data_pydantic with invalid type."""
        data = {"name": "Charlie", "age": "not-a-number"}
        is_valid, errors = validate_entity_data_pydantic(sample_entity_type, data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("age" in err for err in errors)

    def test_validate_out_of_bounds(self, sample_entity_type):
        """Test validate_entity_data_pydantic with out-of-bounds value."""
        data = {"name": "Dave", "age": 150}  # max_value is 120
        is_valid, errors = validate_entity_data_pydantic(sample_entity_type, data)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("age" in err for err in errors)
