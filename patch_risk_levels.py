#!/usr/bin/env python3
"""
Quick patch script to make app.py and analysis.py schema-aware for risk levels.
Run this script from the rim_app directory.

This makes the code dynamic so it works with any schema (Strategic, Business, etc.)
"""

import re
from pathlib import Path


def patch_analysis_py():
    """Patch database/queries/analysis.py to use schema-driven level names."""
    
    file_path = Path("database/queries/analysis.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Add import at the top (after existing imports)
    if "from config import RISK_LEVELS" not in content:
        # Find the import section and add our import
        import_insert = '''from config import RISK_LEVELS

'''
        # Insert after the existing imports
        content = re.sub(
            r'(from database\.queries import risks, tpos, mitigations, influences)',
            r'\1\n\n# Schema-driven configuration\nfrom config import RISK_LEVELS',
            content
        )
    
    # Replace hardcoded Strategic/Operational with schema values
    old_code = '''    stats["strategic_risks"] = risks.get_risk_count_by_level(conn, "Strategic")
    stats["operational_risks"] = risks.get_risk_count_by_level(conn, "Operational")'''
    
    new_code = '''    # Use schema-driven level names
    if len(RISK_LEVELS) >= 1:
        stats["level1_risks"] = risks.get_risk_count_by_level(conn, RISK_LEVELS[0])
        stats["level1_name"] = RISK_LEVELS[0]
    if len(RISK_LEVELS) >= 2:
        stats["level2_risks"] = risks.get_risk_count_by_level(conn, RISK_LEVELS[1])
        stats["level2_name"] = RISK_LEVELS[1]
    # Keep backward compatibility keys
    stats["strategic_risks"] = stats.get("level1_risks", 0)
    stats["operational_risks"] = stats.get("level2_risks", 0)'''
    
    content = content.replace(old_code, new_code)
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Patched {file_path}")


def patch_app_py():
    """Patch app.py to use schema-driven level display."""
    
    file_path = Path("app.py")
    content = file_path.read_text(encoding='utf-8')
    
    # 1. Update the imports to include RISK_LEVEL_CONFIG
    old_import = '''from config import (
    APP_TITLE,
    APP_ICON,
    LAYOUT_MODE,
    NEO4J_DEFAULT_URI,
    NEO4J_DEFAULT_USER,
    RISK_LEVELS,
    RISK_CATEGORIES,
    TPO_CLUSTERS,
)'''
    
    new_import = '''from config import (
    APP_TITLE,
    APP_ICON,
    LAYOUT_MODE,
    NEO4J_DEFAULT_URI,
    NEO4J_DEFAULT_USER,
    RISK_LEVELS,
    RISK_CATEGORIES,
    TPO_CLUSTERS,
    RISK_LEVEL_CONFIG,
)'''
    
    content = content.replace(old_import, new_import)
    
    # 2. Update the stats display (line ~404)
    old_stats = '''        with col2:
            st.metric("🟣 Strategic", stats.get("strategic_risks", 0))
        with col3:
            st.metric("🔵 Operational", stats.get("operational_risks", 0))'''
    
    new_stats = '''        with col2:
            # Schema-driven level 1 display
            level1_name = stats.get("level1_name", RISK_LEVELS[0] if RISK_LEVELS else "Business")
            level1_cfg = RISK_LEVEL_CONFIG.get(level1_name, {})
            st.metric(f"{level1_cfg.get('emoji', '◆')} {level1_name}", stats.get("level1_risks", 0))
        with col3:
            # Schema-driven level 2 display
            level2_name = stats.get("level2_name", RISK_LEVELS[1] if len(RISK_LEVELS) > 1 else "Operational")
            level2_cfg = RISK_LEVEL_CONFIG.get(level2_name, {})
            st.metric(f"{level2_cfg.get('emoji', '●')} {level2_name}", stats.get("level2_risks", 0))'''
    
    content = content.replace(old_stats, new_stats)
    
    # 3. Update the level icon comparison (line ~535)
    old_icon = '''level_icon = "🟣" if r.get("level") == "Strategic" else "🔵"'''
    
    new_icon = '''# Schema-driven level icon
                        risk_level = r.get("level", "")
                        level_cfg = RISK_LEVEL_CONFIG.get(risk_level, {})
                        level_icon = level_cfg.get("emoji", "●")'''
    
    content = content.replace(old_icon, new_icon)
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Patched {file_path}")


def update_help_text():
    """Update help text to be more generic or use schema terms."""
    
    file_path = Path("app.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Replace specific help text references
    replacements = [
        ("**Strategic Risks**", "**Business Risks**"),
        ("Strategic Risks", "Business Risks"),
        ("Operational → Strategic", "Operational → Business"),
        ("Strategic → Strategic", "Business → Business"),
        ("Strategic risk", "Business risk"),
        ("strategic and operational", "business and operational"),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    file_path.write_text(content, encoding='utf-8')
    print(f"✓ Updated help text in {file_path}")


def main():
    print("=" * 60)
    print("RIM Schema-Aware Patch for Risk Levels")
    print("=" * 60)
    print()
    
    # Check we're in the right directory
    if not Path("app.py").exists():
        print("ERROR: Run this script from the rim_app directory")
        return 1
    
    print("Patching files to use schema-driven risk level names...")
    print()
    
    try:
        patch_analysis_py()
        patch_app_py()
        update_help_text()
        
        print()
        print("=" * 60)
        print("✓ All patches applied successfully!")
        print()
        print("The app will now dynamically use level names from the schema.")
        print("Current schema has levels:", end=" ")
        
        try:
            from config import RISK_LEVELS
            print(RISK_LEVELS)
        except:
            print("[Could not load - restart app to see]")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
