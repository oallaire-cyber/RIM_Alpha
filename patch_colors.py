#!/usr/bin/env python3
"""
Patch script to fix visualization/colors.py for Business risks.
Run this script from the rim_app directory.
"""

from pathlib import Path


def patch_colors():
    """Patch visualization/colors.py to use Business instead of Strategic."""
    
    file_path = Path("visualization/colors.py")
    content = file_path.read_text(encoding='utf-8')
    
    replacements = [
        # Dictionary keys (lowercase)
        ('"strategic":', '"business":'),
        ("'strategic':", "'business':"),
        ('["strategic"]', '["business"]'),
        ("['strategic']", "['business']"),
        
        # LEVEL_COLORS keys (capitalized - these are the display labels)
        ('"Strategic":', '"Business":'),
        ("'Strategic':", "'Business':"),
        ('["Strategic"]', '["Business"]'),
        ("['Strategic']", "['Business']"),
        
        # Comments
        ("strategic", "business"),  # Be careful - this is broad
    ]
    
    count = 0
    for old, new in replacements:
        if old in content:
            c = content.count(old)
            content = content.replace(old, new)
            count += c
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Patched {file_path} ({count} replacements)")


def patch_node_styles_shapes():
    """Patch RISK_SHAPES dictionary in node_styles.py."""
    
    file_path = Path("visualization/node_styles.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Fix RISK_SHAPES dictionary key
    old_shapes = '''RISK_SHAPES = {
    "strategic": {
        "default": "diamond",      # Pointed = danger, high-level
        "contingent": "diamond"    # Hollow diamond for potential
    },'''
    
    new_shapes = '''RISK_SHAPES = {
    "business": {
        "default": "diamond",      # Pointed = danger, high-level
        "contingent": "diamond"    # Hollow diamond for potential
    },'''
    
    if old_shapes in content:
        content = content.replace(old_shapes, new_shapes)
        print("✓ Fixed RISK_SHAPES dictionary key")
    
    # Fix NODE_SIZES keys
    content = content.replace('"strategic_risk":', '"business_risk":')
    content = content.replace('NODE_SIZES["strategic_risk"]', 'NODE_SIZES["business_risk"]')
    
    # Fix any remaining RISK_COLORS references
    content = content.replace('RISK_COLORS["strategic"]', 'RISK_COLORS["business"]')
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ Patched visualization/node_styles.py")


def verify():
    """Verify patches applied correctly."""
    
    # Check colors.py
    colors_content = Path("visualization/colors.py").read_text(encoding='utf-8')
    if '"business":' in colors_content and '"Business":' in colors_content:
        print("✓ colors.py: 'business' keys present")
    else:
        print("⚠️ colors.py: May need manual verification")
    
    if '"strategic"' in colors_content.lower():
        print("⚠️ colors.py: Still contains 'strategic' references")
    
    # Check node_styles.py
    styles_content = Path("visualization/node_styles.py").read_text(encoding='utf-8')
    if 'level == "Business"' in styles_content:
        print("✓ node_styles.py: Level comparisons use 'Business'")
    
    if 'RISK_COLORS["business"]' in styles_content:
        print("✓ node_styles.py: RISK_COLORS uses 'business' key")


def main():
    print("=" * 60)
    print("RIM Colors Patch for Business Risks")
    print("=" * 60)
    print()
    
    if not Path("visualization/colors.py").exists():
        print("ERROR: Run this script from the rim_app directory")
        return 1
    
    try:
        patch_colors()
        patch_node_styles_shapes()
        print()
        verify()
        
        print()
        print("=" * 60)
        print("✓ Patch complete! Restart the app to see purple diamonds.")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
