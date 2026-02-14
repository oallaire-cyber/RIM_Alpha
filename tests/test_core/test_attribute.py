"""
Tests for core attribute module.
"""

import pytest
from datetime import date, datetime
from core.attribute import AttributeType, AttributeDefinition, AttributeValidator


class TestAttributeType:
    """Tests for AttributeType enum."""
    
    def test_all_types_defined(self):
        """Test all expected types are defined."""
        assert AttributeType.STRING.value == "string"
        assert AttributeType.INT.value == "int"
        assert AttributeType.FLOAT.value == "float"
        assert AttributeType.BOOL.value == "bool"
        assert AttributeType.DATE.value == "date"
        assert AttributeType.DATETIME.value == "datetime"
        assert AttributeType.ENUM.value == "enum"
        assert AttributeType.LIST_STRING.value == "list_string"


class TestAttributeDefinition:
    """Tests for AttributeDefinition."""
    
    def test_create_string_attribute(self):
        """Test creating a string attribute."""
        attr = AttributeDefinition(
            name="test_name",
            type=AttributeType.STRING,
            required=True,
            description="Test description"
        )
        assert attr.name == "test_name"
        assert attr.type == AttributeType.STRING
        assert attr.required is True
    
    def test_type_conversion_from_string(self):
        """Test type is converted from string."""
        attr = AttributeDefinition(
            name="test",
            type="float"  # String instead of enum
        )
        assert attr.type == AttributeType.FLOAT
    
    def test_validate_required_field(self):
        """Test validation of required fields."""
        attr = AttributeDefinition(
            name="required_field",
            type=AttributeType.STRING,
            required=True
        )
        
        is_valid, error = attr.validate(None)
        assert is_valid is False
        assert "required" in error.lower()
        
        is_valid, error = attr.validate("some value")
        assert is_valid is True
        assert error is None
    
    def test_validate_numeric_range(self):
        """Test numeric range validation."""
        attr = AttributeDefinition(
            name="score",
            type=AttributeType.FLOAT,
            min_value=0.0,
            max_value=10.0
        )
        
        is_valid, error = attr.validate(5.0)
        assert is_valid is True
        
        is_valid, error = attr.validate(-1.0)
        assert is_valid is False
        assert ">=" in error
        
        is_valid, error = attr.validate(15.0)
        assert is_valid is False
        assert "<=" in error
    
    def test_validate_enum_choices(self):
        """Test enum choices validation."""
        attr = AttributeDefinition(
            name="status",
            type=AttributeType.ENUM,
            choices=["Active", "Inactive", "Pending"]
        )
        
        is_valid, error = attr.validate("Active")
        assert is_valid is True
        
        is_valid, error = attr.validate("Unknown")
        assert is_valid is False
        assert "one of" in error.lower()
    
    def test_convert_values(self):
        """Test value conversion."""
        int_attr = AttributeDefinition(name="count", type=AttributeType.INT)
        assert int_attr.convert("42") == 42
        assert int_attr.convert(42.9) == 42
        
        float_attr = AttributeDefinition(name="score", type=AttributeType.FLOAT)
        assert float_attr.convert("3.14") == 3.14
        
        bool_attr = AttributeDefinition(name="active", type=AttributeType.BOOL)
        assert bool_attr.convert("true") is True
        assert bool_attr.convert("false") is False
        assert bool_attr.convert(True) is True
    
    def test_default_value_applied(self):
        """Test default value is applied."""
        attr = AttributeDefinition(
            name="priority",
            type=AttributeType.INT,
            default=5
        )
        assert attr.convert(None) == 5
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "name": "probability",
            "type": "float",
            "required": True,
            "min_value": 0.0,
            "max_value": 1.0,
            "description": "Probability value"
        }
        attr = AttributeDefinition.from_dict(data)
        
        assert attr.name == "probability"
        assert attr.type == AttributeType.FLOAT
        assert attr.required is True
        assert attr.min_value == 0.0
        assert attr.max_value == 1.0


class TestAttributeValidator:
    """Tests for AttributeValidator."""
    
    def test_validate_all(self):
        """Test validating multiple attributes."""
        definitions = [
            AttributeDefinition(name="name", type=AttributeType.STRING, required=True),
            AttributeDefinition(name="score", type=AttributeType.FLOAT, min_value=0.0),
        ]
        validator = AttributeValidator(definitions)
        
        # Valid data
        is_valid, errors = validator.validate_all({"name": "Test", "score": 5.0})
        assert is_valid is True
        assert len(errors) == 0
        
        # Missing required field
        is_valid, errors = validator.validate_all({"score": 5.0})
        assert is_valid is False
        assert len(errors) > 0
    
    def test_convert_all(self):
        """Test converting all values."""
        definitions = [
            AttributeDefinition(name="count", type=AttributeType.INT, default=0),
            AttributeDefinition(name="name", type=AttributeType.STRING),
        ]
        validator = AttributeValidator(definitions)
        
        result = validator.convert_all({"count": "42", "name": "Test"})
        assert result["count"] == 42
        assert result["name"] == "Test"
    
    def test_get_required_attributes(self):
        """Test getting required attribute names."""
        definitions = [
            AttributeDefinition(name="name", type=AttributeType.STRING, required=True),
            AttributeDefinition(name="optional", type=AttributeType.STRING, required=False),
        ]
        validator = AttributeValidator(definitions)
        
        required = validator.get_required_attributes()
        assert "name" in required
        assert "optional" not in required
    
    def test_get_engine_required_attributes(self):
        """Test getting engine-required attributes."""
        definitions = [
            AttributeDefinition(name="probability", type=AttributeType.FLOAT, engine_required=True),
            AttributeDefinition(name="impact", type=AttributeType.FLOAT, engine_required=True),
            AttributeDefinition(name="notes", type=AttributeType.STRING),
        ]
        validator = AttributeValidator(definitions)
        
        engine_attrs = validator.get_engine_required_attributes()
        assert "probability" in engine_attrs
        assert "impact" in engine_attrs
        assert "notes" not in engine_attrs
