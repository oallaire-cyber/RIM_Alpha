#!/usr/bin/env python3
"""
Comprehensive patch to replace all Strategic/Strat references with Business/Bus.
Run this script from the rim_app directory.
"""

from pathlib import Path


def patch_file(file_path: Path, replacements: list, description: str):
    """Apply replacements to a file."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return 0
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    count = 0
    
    for old, new in replacements:
        if old in content:
            c = content.count(old)
            content = content.replace(old, new)
            count += c
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print(f"✓ {description}: {count} replacements in {file_path.name}")
    else:
        print(f"  {description}: No changes needed in {file_path.name}")
    
    return count


def patch_enums():
    """Patch models/enums.py - the InfluenceType enum."""
    return patch_file(
        Path("models/enums.py"),
        [
            # RiskLevel enum
            ('STRATEGIC = "Strategic"', 'BUSINESS = "Business"'),
            
            # InfluenceType enum values
            ('LEVEL1_OP_TO_STRAT = "Level1_Op_to_Strat"', 'LEVEL1_OP_TO_BUS = "Level1_Op_to_Bus"'),
            ('LEVEL2_STRAT_TO_STRAT = "Level2_Strat_to_Strat"', 'LEVEL2_BUS_TO_BUS = "Level2_Bus_to_Bus"'),
            
            # Any string references
            ('"Level1_Op_to_Strat"', '"Level1_Op_to_Bus"'),
            ('"Level2_Strat_to_Strat"', '"Level2_Bus_to_Bus"'),
            ("'Level1_Op_to_Strat'", "'Level1_Op_to_Bus'"),
            ("'Level2_Strat_to_Strat'", "'Level2_Bus_to_Bus'"),
        ],
        "InfluenceType enum"
    )


def patch_edge_styles():
    """Patch visualization/edge_styles.py - edge labels and comments."""
    return patch_file(
        Path("visualization/edge_styles.py"),
        [
            # Labels
            ('"Level 1: Op → Strat"', '"Level 1: Op → Bus"'),
            ('"Level 2: Strat → Strat"', '"Level 2: Bus → Bus"'),
            ("'Level 1: Op → Strat'", "'Level 1: Op → Bus'"),
            ("'Level 2: Strat → Strat'", "'Level 2: Bus → Bus'"),
            
            # Comments
            ("Op→Strat", "Op→Bus"),
            ("Strat→Strat", "Bus→Bus"),
            ("Op → Strat", "Op → Bus"),
            ("Strat → Strat", "Bus → Bus"),
        ],
        "Edge styles"
    )


def patch_colors():
    """Patch visualization/colors.py."""
    return patch_file(
        Path("visualization/colors.py"),
        [
            ('"strategic":', '"business":'),
            ("'strategic':", "'business':"),
            ('["strategic"]', '["business"]'),
            ("['strategic']", "['business']"),
            ('"Strategic":', '"Business":'),
            ("'Strategic':", "'Business':"),
            ('["Strategic"]', '["Business"]'),
            ("['Strategic']", "['Business']"),
            ("Op→Strat", "Op→Bus"),
            ("Strat→Strat", "Bus→Bus"),
        ],
        "Colors"
    )


def patch_node_styles():
    """Patch visualization/node_styles.py."""
    return patch_file(
        Path("visualization/node_styles.py"),
        [
            # Dictionary keys
            ('"strategic":', '"business":'),
            ("'strategic':", "'business':"),
            ('["strategic"]', '["business"]'),
            ("['strategic']", "['business']"),
            ('"strategic_risk":', '"business_risk":'),
            ('["strategic_risk"]', '["business_risk"]'),
            
            # Level comparisons
            ('level == "Strategic"', 'level == "Business"'),
            ("level == 'Strategic'", "level == 'Business'"),
            
            # Labels and comments
            ('"Strategic Risk"', '"Business Risk"'),
            ("'Strategic Risk'", "'Business Risk'"),
            ("Strategic Risks", "Business Risks"),
            ("strategic risks", "business risks"),
            ("strategic risk", "business risk"),
        ],
        "Node styles"
    )


def patch_risk_model():
    """Patch models/risk.py."""
    return patch_file(
        Path("models/risk.py"),
        [
            ('level: Strategic', 'level: Business'),
            ('"Strategic"', '"Business"'),
            ("'Strategic'", "'Business'"),
            ("is_strategic", "is_business"),
            ("strategic level", "business level"),
        ],
        "Risk model"
    )


def patch_relationships_model():
    """Patch models/relationships.py."""
    return patch_file(
        Path("models/relationships.py"),
        [
            ('"Level1_Op_to_Strat"', '"Level1_Op_to_Bus"'),
            ('"Level2_Strat_to_Strat"', '"Level2_Bus_to_Bus"'),
            ("strategic risk", "business risk"),
        ],
        "Relationships model"
    )


def patch_graph_renderer():
    """Patch visualization/graph_renderer.py."""
    return patch_file(
        Path("visualization/graph_renderer.py"),
        [
            ('"Strategic"', '"Business"'),
            ("'Strategic'", "'Business'"),
        ],
        "Graph renderer"
    )


def patch_init():
    """Patch visualization/__init__.py."""
    return patch_file(
        Path("visualization/__init__.py"),
        [
            ("strategic", "business"),
            ("Strategic", "Business"),
        ],
        "Visualization init"
    )


def verify_remaining():
    """Check for any remaining references."""
    print("\n" + "=" * 60)
    print("Verification - checking for remaining references...")
    print("=" * 60)
    
    files_to_check = [
        "models/enums.py",
        "models/risk.py",
        "models/relationships.py",
        "visualization/colors.py",
        "visualization/node_styles.py",
        "visualization/edge_styles.py",
        "visualization/graph_renderer.py",
    ]
    
    found = []
    for f in files_to_check:
        path = Path(f)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            # Check for functional code (not comments)
            for line_num, line in enumerate(content.split('\n'), 1):
                line_lower = line.lower()
                if ('strat' in line_lower or 'strategic' in line_lower) and not line.strip().startswith('#'):
                    # Skip if it's the new "business" version
                    if 'bus' in line_lower or 'business' in line_lower:
                        continue
                    found.append((f, line_num, line.strip()[:70]))
    
    if found:
        print("\n⚠️  Remaining references found:")
        for f, line_num, line in found[:15]:
            print(f"   {f}:{line_num}: {line}...")
        if len(found) > 15:
            print(f"   ... and {len(found) - 15} more")
    else:
        print("\n✓ No remaining 'strategic/strat' references in core files!")


def main():
    print("=" * 60)
    print("Comprehensive Strategic → Business Patch")
    print("=" * 60)
    print()
    
    if not Path("app.py").exists():
        print("ERROR: Run this script from the rim_app directory")
        return 1
    
    total = 0
    try:
        total += patch_enums()
        total += patch_edge_styles()
        total += patch_colors()
        total += patch_node_styles()
        total += patch_risk_model()
        total += patch_relationships_model()
        total += patch_graph_renderer()
        total += patch_init()
        
        verify_remaining()
        
        print()
        print("=" * 60)
        print(f"✓ Complete! {total} total replacements made.")
        print()
        print("Next steps:")
        print("1. Restart the app: streamlit run app.py")
        print("2. If edges still show 'Strat', clear browser cache (Ctrl+Shift+R)")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
