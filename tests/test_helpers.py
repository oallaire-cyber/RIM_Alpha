"""
Tests for utils/helpers.py

Tests all helper utility functions.
"""

import pytest
from utils.helpers import (
    format_percentage,
    format_exposure,
    truncate_text,
    wrap_text_multiline,
    safe_get,
    calculate_exposure,
    get_color_for_value,
    pluralize,
)


class TestFormatPercentage:
    """Tests for format_percentage function."""
    
    def test_percentage_value(self):
        """Test formatting a percentage value (0-100)."""
        assert format_percentage(75.5) == "75.5%"
        assert format_percentage(100) == "100.0%"
        assert format_percentage(0) == "0.0%"
    
    def test_ratio_value(self):
        """Test formatting a ratio value (0-1) is converted to percentage."""
        assert format_percentage(0.755) == "75.5%"
        assert format_percentage(0.5) == "50.0%"
        assert format_percentage(0.01) == "1.0%"
    
    def test_decimal_places(self):
        """Test custom decimal places."""
        assert format_percentage(75.555, decimal_places=2) == "75.56%"
        assert format_percentage(75.5, decimal_places=0) == "76%"
    
    def test_none_value(self):
        """Test None returns 'N/A'."""
        assert format_percentage(None) == "N/A"
    
    def test_boundary_values(self):
        """Test boundary values between ratio and percentage."""
        # Exactly 1 should be treated as a ratio
        assert format_percentage(1) == "100.0%"
        # Just over 1 should be treated as a percentage
        assert format_percentage(1.01) == "1.0%"  # This is actually a ratio too
        assert format_percentage(1.5) == "1.5%"  # Treated as 1.5%


class TestFormatExposure:
    """Tests for format_exposure function."""
    
    def test_format_exposure_value(self):
        """Test formatting exposure values."""
        assert format_exposure(40.5) == "40.5"
        assert format_exposure(100.0) == "100.0"
        assert format_exposure(0.0) == "0.0"
    
    def test_decimal_places(self):
        """Test custom decimal places."""
        assert format_exposure(40.555, decimal_places=2) == "40.56"
        assert format_exposure(40.5, decimal_places=0) == "40"
    
    def test_none_value(self):
        """Test None returns 'N/A'."""
        assert format_exposure(None) == "N/A"


class TestTruncateText:
    """Tests for truncate_text function."""
    
    def test_short_text_unchanged(self):
        """Test text shorter than max_length is unchanged."""
        assert truncate_text("Hello", max_length=10) == "Hello"
    
    def test_exact_length_unchanged(self):
        """Test text exactly at max_length is unchanged."""
        assert truncate_text("Hello", max_length=5) == "Hello"
    
    def test_long_text_truncated(self):
        """Test text longer than max_length is truncated with suffix."""
        result = truncate_text("Hello World", max_length=8)
        assert result == "Hello..."
        assert len(result) == 8
    
    def test_custom_suffix(self):
        """Test custom suffix."""
        result = truncate_text("Hello World", max_length=9, suffix=" [...]")
        assert result == "Hel [...]"
    
    def test_empty_string(self):
        """Test empty string returns empty."""
        assert truncate_text("") == ""
        assert truncate_text("", max_length=10) == ""
    
    def test_none_returns_empty(self):
        """Test None-like value returns empty."""
        assert truncate_text(None) == ""


class TestWrapTextMultiline:
    """Tests for wrap_text_multiline function."""
    
    def test_short_text_unchanged(self):
        """Test short text that fits in one line."""
        result = wrap_text_multiline("Hello", max_width=10)
        assert result == "Hello"
    
    def test_text_wrapping(self):
        """Test text is wrapped at word boundaries."""
        result = wrap_text_multiline("Hello World Test", max_width=10)
        lines = result.split('\n')
        assert len(lines) >= 2
    
    def test_max_lines_limit(self):
        """Test respects max_lines limit."""
        result = wrap_text_multiline("One Two Three Four Five Six", max_width=5, max_lines=2)
        lines = result.split('\n')
        assert len(lines) <= 2
        assert "..." in result
    
    def test_empty_string(self):
        """Test empty string returns empty."""
        assert wrap_text_multiline("") == ""
        assert wrap_text_multiline(None) == ""


class TestSafeGet:
    """Tests for safe_get function."""
    
    def test_existing_key(self):
        """Test getting an existing key."""
        data = {"name": "Test", "value": 42}
        assert safe_get(data, "name") == "Test"
        assert safe_get(data, "value") == 42
    
    def test_missing_key_returns_default(self):
        """Test missing key returns default."""
        data = {"name": "Test"}
        assert safe_get(data, "missing") is None
        assert safe_get(data, "missing", "default") == "default"
    
    def test_none_value_returns_default(self):
        """Test None value returns default."""
        data = {"name": None}
        assert safe_get(data, "name") is None
        assert safe_get(data, "name", "default") == "default"
    
    def test_falsy_values_preserved(self):
        """Test falsy non-None values are preserved."""
        data = {"zero": 0, "empty": "", "false": False}
        # These should NOT return default since they're not None
        assert safe_get(data, "zero", 999) == 0
        assert safe_get(data, "empty", "default") == ""
        assert safe_get(data, "false", True) is False


class TestCalculateExposure:
    """Tests for calculate_exposure function."""
    
    def test_calculate_exposure_normal(self):
        """Test normal exposure calculation."""
        assert calculate_exposure(5.0, 8.0) == 40.0
        assert calculate_exposure(10.0, 10.0) == 100.0
        assert calculate_exposure(1.0, 1.0) == 1.0
    
    def test_calculate_exposure_zero(self):
        """Test exposure with zero values."""
        assert calculate_exposure(0.0, 8.0) == 0.0
        assert calculate_exposure(5.0, 0.0) == 0.0
    
    def test_calculate_exposure_none_probability(self):
        """Test None probability returns None."""
        assert calculate_exposure(None, 8.0) is None
    
    def test_calculate_exposure_none_impact(self):
        """Test None impact returns None."""
        assert calculate_exposure(5.0, None) is None
    
    def test_calculate_exposure_both_none(self):
        """Test both None returns None."""
        assert calculate_exposure(None, None) is None


class TestGetColorForValue:
    """Tests for get_color_for_value function."""
    
    def test_minimum_value_returns_low_color(self):
        """Test minimum value returns low_color."""
        result = get_color_for_value(0, min_val=0, max_val=100, 
                                      low_color="#00ff00", high_color="#ff0000")
        assert result.lower() == "#00ff00"
    
    def test_maximum_value_returns_high_color(self):
        """Test maximum value returns high_color."""
        result = get_color_for_value(100, min_val=0, max_val=100,
                                      low_color="#00ff00", high_color="#ff0000")
        assert result.lower() == "#ff0000"
    
    def test_middle_value_interpolates(self):
        """Test middle value interpolates colors."""
        result = get_color_for_value(50, min_val=0, max_val=100,
                                      low_color="#000000", high_color="#ffffff")
        # Should be around grey (#7f7f7f or similar)
        assert result.startswith("#")
        assert len(result) == 7
    
    def test_returns_hex_format(self):
        """Test returns valid hex color format."""
        result = get_color_for_value(50)
        assert result.startswith("#")
        assert len(result) == 7
    
    def test_clamped_values(self):
        """Test values outside range are clamped."""
        # Below minimum
        result_below = get_color_for_value(-10, min_val=0, max_val=100,
                                            low_color="#00ff00", high_color="#ff0000")
        result_min = get_color_for_value(0, min_val=0, max_val=100,
                                          low_color="#00ff00", high_color="#ff0000")
        assert result_below == result_min
        
        # Above maximum
        result_above = get_color_for_value(200, min_val=0, max_val=100,
                                            low_color="#00ff00", high_color="#ff0000")
        result_max = get_color_for_value(100, min_val=0, max_val=100,
                                          low_color="#00ff00", high_color="#ff0000")
        assert result_above == result_max
    
    def test_equal_min_max(self):
        """Test when min equals max returns middle-ish value."""
        result = get_color_for_value(50, min_val=50, max_val=50)
        assert result.startswith("#")


class TestPluralize:
    """Tests for pluralize function."""
    
    def test_singular(self):
        """Test singular form for count of 1."""
        assert pluralize(1, "item") == "1 item"
        assert pluralize(1, "risk") == "1 risk"
    
    def test_plural_default(self):
        """Test default plural adds 's'."""
        assert pluralize(0, "item") == "0 items"
        assert pluralize(2, "item") == "2 items"
        assert pluralize(100, "risk") == "100 risks"
    
    def test_plural_custom(self):
        """Test custom plural form."""
        assert pluralize(0, "child", "children") == "0 children"
        assert pluralize(2, "person", "people") == "2 people"
    
    def test_negative_uses_plural(self):
        """Test negative numbers use plural."""
        assert pluralize(-1, "item") == "-1 items"
