"""
Helper utility functions for RIM application.
"""

from typing import Optional


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a decimal value as a percentage string.
    
    Args:
        value: Value to format (0-100 or 0-1)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string (e.g., "75.5%")
    """
    if value is None:
        return "N/A"
    
    # If value is between 0 and 1, assume it's a ratio
    if 0 <= value <= 1:
        value = value * 100
    
    return f"{value:.{decimal_places}f}%"


def format_exposure(exposure: Optional[float], decimal_places: int = 1) -> str:
    """
    Format an exposure score for display.
    
    Args:
        exposure: Exposure value to format
        decimal_places: Number of decimal places
    
    Returns:
        Formatted exposure string
    """
    if exposure is None:
        return "N/A"
    return f"{exposure:.{decimal_places}f}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def wrap_text_multiline(text: str, max_width: int = 20, max_lines: int = 3) -> str:
    """
    Wrap text to multiple lines for graph node labels.
    
    Args:
        text: Text to wrap
        max_width: Maximum characters per line
        max_lines: Maximum number of lines
    
    Returns:
        Wrapped text with newlines
    """
    if not text:
        return ""
    
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        
        # Check if adding this word exceeds the line width
        if current_length + word_length + (1 if current_line else 0) <= max_width:
            current_line.append(word)
            current_length += word_length + (1 if len(current_line) > 1 else 0)
        else:
            # Start a new line
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    # Limit to max_lines
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        # Add ellipsis to last line if truncated
        if len(lines[max_lines - 1]) > max_width - 3:
            lines[max_lines - 1] = lines[max_lines - 1][:max_width - 3] + "..."
        else:
            lines[max_lines - 1] = lines[max_lines - 1] + "..."
    
    return '\n'.join(lines)


def safe_get(data: dict, key: str, default=None):
    """
    Safely get a value from a dictionary.
    
    Args:
        data: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found or value is None
    
    Returns:
        Value or default
    """
    value = data.get(key)
    return value if value is not None else default


def calculate_exposure(probability: Optional[float], impact: Optional[float]) -> Optional[float]:
    """
    Calculate risk exposure from probability and impact.
    
    Args:
        probability: Probability score (0-10)
        impact: Impact score (0-10)
    
    Returns:
        Exposure score or None if inputs are invalid
    """
    if probability is not None and impact is not None:
        return probability * impact
    return None


def get_color_for_value(value: float, min_val: float = 0, max_val: float = 100,
                        low_color: str = "#27ae60", high_color: str = "#e74c3c") -> str:
    """
    Get a color interpolated between two colors based on a value.
    
    Args:
        value: Value to get color for
        min_val: Minimum value (maps to low_color)
        max_val: Maximum value (maps to high_color)
        low_color: Color for minimum value (hex)
        high_color: Color for maximum value (hex)
    
    Returns:
        Interpolated hex color
    """
    # Normalize value to 0-1
    if max_val == min_val:
        ratio = 0.5
    else:
        ratio = (value - min_val) / (max_val - min_val)
        ratio = max(0, min(1, ratio))  # Clamp to [0, 1]
    
    # Parse hex colors
    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(rgb: tuple) -> str:
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    low_rgb = hex_to_rgb(low_color)
    high_rgb = hex_to_rgb(high_color)
    
    # Interpolate
    result_rgb = tuple(
        int(low + (high - low) * ratio)
        for low, high in zip(low_rgb, high_rgb)
    )
    
    return rgb_to_hex(result_rgb)


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """
    Return singular or plural form based on count.
    
    Args:
        count: Number to check
        singular: Singular form
        plural: Plural form (defaults to singular + 's')
    
    Returns:
        Appropriate form with count
    """
    if plural is None:
        plural = singular + "s"
    
    word = singular if count == 1 else plural
    return f"{count} {word}"
