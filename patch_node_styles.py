#!/usr/bin/env python3
"""
Patch script to fix visualization/node_styles.py for Business risks.
Run this script from the rim_app directory.
"""

from pathlib import Path


def patch_node_styles():
    """Patch visualization/node_styles.py to use schema-driven level names."""
    
    file_path = Path("visualization/node_styles.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Count replacements for reporting
    replacements = 0
    
    # 1. Update the RISK_COLORS dictionary key
    if '"strategic":' in content:
        content = content.replace('"strategic":', '"business":')
        replacements += 1
    
    # 2. Update NODE_SIZES key
    if '"strategic_risk":' in content:
        content = content.replace('"strategic_risk":', '"business_risk":')
        replacements += 1
    
    # 3. Update all level comparisons from "Strategic" to "Business"
    strategic_comparisons = [
        ('level == "Strategic"', 'level == "Business"'),
        ("level == 'Strategic'", "level == 'Business'"),
        ('level == \"Strategic\"', 'level == \"Business\"'),
    ]
    
    for old, new in strategic_comparisons:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            replacements += count
    
    # 4. Update NODE_SIZES reference
    if 'NODE_SIZES["strategic_risk"]' in content:
        content = content.replace('NODE_SIZES["strategic_risk"]', 'NODE_SIZES["business_risk"]')
        replacements += 1
    
    # 5. Update RISK_COLORS references
    if 'RISK_COLORS["strategic"]' in content:
        count = content.count('RISK_COLORS["strategic"]')
        content = content.replace('RISK_COLORS["strategic"]', 'RISK_COLORS["business"]')
        replacements += count
    
    # 6. Update documentation/comments
    doc_replacements = [
        ("Strategic Risks", "Business Risks"),
        ("Strategic Risk", "Business Risk"),
        ("strategic risks", "business risks"),
        ("strategic risk", "business risk"),
    ]
    
    for old, new in doc_replacements:
        if old in content:
            content = content.replace(old, new)
            replacements += 1
    
    # Write the patched content
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Patched {file_path} ({replacements} replacements)")
    
    return replacements


def verify_patch():
    """Verify no Strategic references remain."""
    file_path = Path("visualization/node_styles.py")
    content = file_path.read_text(encoding='utf-8')
    
    remaining = []
    for line_num, line in enumerate(content.split('\n'), 1):
        if 'Strategic' in line or 'strategic' in line.lower():
            # Ignore comments that are just documentation
            if not line.strip().startswith('#'):
                remaining.append((line_num, line.strip()))
    
    if remaining:
        print("\n⚠️  Warning: Some 'strategic' references may remain:")
        for line_num, line in remaining[:5]:
            print(f"   Line {line_num}: {line[:80]}...")
    else:
        print("✓ No functional 'Strategic' references remaining")


def main():
    print("=" * 60)
    print("RIM Node Styles Patch for Business Risks")
    print("=" * 60)
    print()
    
    # Check we're in the right directory
    if not Path("visualization/node_styles.py").exists():
        print("ERROR: Run this script from the rim_app directory")
        return 1
    
    try:
        patch_node_styles()
        verify_patch()
        
        print()
        print("=" * 60)
        print("✓ Patch complete! Restart the app to see changes.")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
