"""
Export Service.

Provides functionality to export RIM data to various formats,
primarily Excel spreadsheets.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import io


def export_to_excel(
    filepath: str,
    risks: List[Dict[str, Any]],
    influences: List[Dict[str, Any]],
    tpos: List[Dict[str, Any]],
    tpo_impacts: List[Dict[str, Any]],
    mitigations: List[Dict[str, Any]],
    mitigates_relationships: List[Dict[str, Any]]
) -> bool:
    """
    Export all RIM data to an Excel file.
    
    Creates an Excel file with the following sheets:
    - Risks
    - Influences
    - TPOs
    - TPO_Impacts
    - Mitigations
    - Mitigates
    
    Args:
        filepath: Path to save the Excel file
        risks: List of risk dictionaries
        influences: List of influence relationship dictionaries
        tpos: List of TPO dictionaries
        tpo_impacts: List of TPO impact relationship dictionaries
        mitigations: List of mitigation dictionaries
        mitigates_relationships: List of MITIGATES relationship dictionaries
    
    Returns:
        True if export successful, False otherwise
    """
    try:
        import pandas as pd
        
        # Convert to DataFrames
        df_risks = pd.DataFrame([dict(r) for r in risks]) if risks else pd.DataFrame()
        df_influences = pd.DataFrame([dict(i) for i in influences]) if influences else pd.DataFrame()
        df_tpos = pd.DataFrame([dict(t) for t in tpos]) if tpos else pd.DataFrame()
        df_tpo_impacts = pd.DataFrame([dict(i) for i in tpo_impacts]) if tpo_impacts else pd.DataFrame()
        df_mitigations = pd.DataFrame([dict(m) for m in mitigations]) if mitigations else pd.DataFrame()
        df_mitigates = pd.DataFrame([dict(rel) for rel in mitigates_relationships]) if mitigates_relationships else pd.DataFrame()
        
        # Write to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if not df_risks.empty:
                df_risks.to_excel(writer, sheet_name='Risks', index=False)
            if not df_influences.empty:
                df_influences.to_excel(writer, sheet_name='Influences', index=False)
            if not df_tpos.empty:
                df_tpos.to_excel(writer, sheet_name='TPOs', index=False)
            if not df_tpo_impacts.empty:
                df_tpo_impacts.to_excel(writer, sheet_name='TPO_Impacts', index=False)
            if not df_mitigations.empty:
                df_mitigations.to_excel(writer, sheet_name='Mitigations', index=False)
            if not df_mitigates.empty:
                df_mitigates.to_excel(writer, sheet_name='Mitigates', index=False)
        
        return True
    
    except Exception as e:
        print(f"Export error: {e}")
        return False


def export_to_excel_bytes(
    risks: List[Dict[str, Any]],
    influences: List[Dict[str, Any]],
    tpos: List[Dict[str, Any]],
    tpo_impacts: List[Dict[str, Any]],
    mitigations: List[Dict[str, Any]],
    mitigates_relationships: List[Dict[str, Any]]
) -> Optional[bytes]:
    """
    Export all RIM data to Excel format and return as bytes.
    
    Useful for Streamlit downloads without writing to filesystem.
    
    Args:
        risks: List of risk dictionaries
        influences: List of influence relationship dictionaries
        tpos: List of TPO dictionaries
        tpo_impacts: List of TPO impact relationship dictionaries
        mitigations: List of mitigation dictionaries
        mitigates_relationships: List of MITIGATES relationship dictionaries
    
    Returns:
        Excel file content as bytes, or None if export failed
    """
    try:
        import pandas as pd
        
        # Convert to DataFrames
        df_risks = pd.DataFrame([dict(r) for r in risks]) if risks else pd.DataFrame()
        df_influences = pd.DataFrame([dict(i) for i in influences]) if influences else pd.DataFrame()
        df_tpos = pd.DataFrame([dict(t) for t in tpos]) if tpos else pd.DataFrame()
        df_tpo_impacts = pd.DataFrame([dict(i) for i in tpo_impacts]) if tpo_impacts else pd.DataFrame()
        df_mitigations = pd.DataFrame([dict(m) for m in mitigations]) if mitigations else pd.DataFrame()
        df_mitigates = pd.DataFrame([dict(rel) for rel in mitigates_relationships]) if mitigates_relationships else pd.DataFrame()
        
        # Write to BytesIO buffer
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            if not df_risks.empty:
                df_risks.to_excel(writer, sheet_name='Risks', index=False)
            if not df_influences.empty:
                df_influences.to_excel(writer, sheet_name='Influences', index=False)
            if not df_tpos.empty:
                df_tpos.to_excel(writer, sheet_name='TPOs', index=False)
            if not df_tpo_impacts.empty:
                df_tpo_impacts.to_excel(writer, sheet_name='TPO_Impacts', index=False)
            if not df_mitigations.empty:
                df_mitigations.to_excel(writer, sheet_name='Mitigations', index=False)
            if not df_mitigates.empty:
                df_mitigates.to_excel(writer, sheet_name='Mitigates', index=False)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        print(f"Export error: {e}")
        return None


def export_analysis_report(
    filepath: str,
    influence_analysis: Dict[str, Any],
    mitigation_analysis: Dict[str, Any],
    coverage_gaps: Dict[str, Any]
) -> bool:
    """
    Export analysis results to an Excel report.
    
    Creates an Excel file with analysis summaries:
    - Top Propagators
    - Convergence Points
    - Critical Paths
    - Bottlenecks
    - Coverage Statistics
    - Unmitigated Risks
    - Coverage Gaps
    
    Args:
        filepath: Path to save the Excel file
        influence_analysis: Influence analysis results
        mitigation_analysis: Mitigation analysis results
        coverage_gaps: Coverage gap analysis results
    
    Returns:
        True if export successful, False otherwise
    """
    try:
        import pandas as pd
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Top Propagators
            if influence_analysis.get("top_propagators"):
                df = pd.DataFrame(influence_analysis["top_propagators"])
                df.to_excel(writer, sheet_name='Top Propagators', index=False)
            
            # Convergence Points
            if influence_analysis.get("convergence_points"):
                df = pd.DataFrame(influence_analysis["convergence_points"])
                df.to_excel(writer, sheet_name='Convergence Points', index=False)
            
            # Critical Paths
            if influence_analysis.get("critical_paths"):
                paths = []
                for p in influence_analysis["critical_paths"]:
                    path_names = " → ".join(n["name"] for n in p["path"])
                    paths.append({
                        "path": path_names,
                        "strength": p["strength"],
                        "length": p["length"]
                    })
                df = pd.DataFrame(paths)
                df.to_excel(writer, sheet_name='Critical Paths', index=False)
            
            # Bottlenecks
            if influence_analysis.get("bottlenecks"):
                df = pd.DataFrame(influence_analysis["bottlenecks"])
                df.to_excel(writer, sheet_name='Bottlenecks', index=False)
            
            # Coverage Statistics
            if mitigation_analysis.get("coverage_stats"):
                df = pd.DataFrame([mitigation_analysis["coverage_stats"]])
                df.to_excel(writer, sheet_name='Coverage Stats', index=False)
            
            # Unmitigated Risks
            if mitigation_analysis.get("unmitigated_risks"):
                df = pd.DataFrame(mitigation_analysis["unmitigated_risks"])
                # Select key columns
                cols = ["name", "level", "exposure", "categories"]
                cols = [c for c in cols if c in df.columns]
                if cols:
                    df[cols].to_excel(writer, sheet_name='Unmitigated Risks', index=False)
            
            # High Priority Unmitigated
            if coverage_gaps.get("high_priority_unmitigated"):
                df = pd.DataFrame(coverage_gaps["high_priority_unmitigated"])
                df.to_excel(writer, sheet_name='High Priority Gaps', index=False)
            
            # Category Coverage
            if coverage_gaps.get("category_coverage"):
                rows = [
                    {"category": cat, **stats}
                    for cat, stats in coverage_gaps["category_coverage"].items()
                ]
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name='Category Coverage', index=False)
        
        return True
    
    except Exception as e:
        print(f"Export error: {e}")
        return False
