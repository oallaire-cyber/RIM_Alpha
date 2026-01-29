"""
Import/Export Tab for RIM Application.

Provides Excel import and export functionality.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import os


def render_import_export_tab(
    export_fn: Callable[[str], None],
    import_fn: Callable[[str], Dict[str, Any]],
    export_bytes_fn: Optional[Callable[[], bytes]] = None
):
    """
    Render the Import/Export tab.
    
    Args:
        export_fn: Function to export data to a file path
        import_fn: Function to import data from a file path
        export_bytes_fn: Optional function to export data as bytes (for download)
    """
    import streamlit as st
    
    st.markdown("### 📥 Excel Import/Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_export_section(export_fn, export_bytes_fn)
    
    with col2:
        _render_import_section(import_fn)


def _render_export_section(
    export_fn: Callable[[str], None],
    export_bytes_fn: Optional[Callable[[], bytes]] = None
):
    """Render the export section."""
    import streamlit as st
    import tempfile
    
    st.markdown("#### Export to Excel")
    st.markdown("*Exports Risks, Influences, TPOs, TPO Impacts, Mitigations, and Mitigates*")
    
    if st.button("📤 Export data", use_container_width=True):
        try:
            if export_bytes_fn:
                # Use bytes export if available
                excel_bytes = export_bytes_fn()
                st.download_button(
                    "⬇️ Download Excel file",
                    excel_bytes,
                    file_name=f"RIM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                # Fallback to file-based export
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, "rim_export.xlsx")
                export_fn(filepath)
                
                with open(filepath, 'rb') as f:
                    st.download_button(
                        "⬇️ Download Excel file",
                        f.read(),
                        file_name=f"RIM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Export error: {e}")


def _render_import_section(import_fn: Callable[[str], Dict[str, Any]]):
    """Render the import section."""
    import streamlit as st
    import tempfile
    
    st.markdown("#### Import from Excel")
    st.markdown("*Imports Risks, Influences, TPOs, TPO Impacts, Mitigations, and Mitigates*")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
    
    if uploaded_file is not None:
        if st.button("📥 Import data", use_container_width=True):
            # Save uploaded file to temp location
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, uploaded_file.name)
            with open(filepath, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            with st.spinner("Importing data..."):
                try:
                    result = import_fn(filepath)
                    _display_import_results(result)
                except Exception as e:
                    st.error(f"Import error: {e}")


def _display_import_results(result: Dict[str, Any]):
    """Display import results summary."""
    import streamlit as st
    
    # Calculate totals
    total_created = (
        result.get("risks_created", 0) +
        result.get("influences_created", 0) +
        result.get("tpos_created", 0) +
        result.get("tpo_impacts_created", 0) +
        result.get("mitigations_created", 0) +
        result.get("mitigates_created", 0)
    )
    total_skipped = (
        result.get("risks_skipped", 0) +
        result.get("influences_skipped", 0) +
        result.get("tpos_skipped", 0) +
        result.get("tpo_impacts_skipped", 0) +
        result.get("mitigations_skipped", 0) +
        result.get("mitigates_skipped", 0)
    )
    
    # Show status message
    errors = result.get("errors", [])
    if errors:
        st.error(f"⚠️ Import completed with {len(errors)} errors")
    elif total_skipped > 0:
        st.warning(f"✅ Import completed with {total_skipped} items skipped")
    else:
        st.success(f"✅ Import successful! {total_created} items created")
    
    # Detailed summary
    st.markdown("##### 📊 Import Summary")
    col_sum1, col_sum2 = st.columns(2)
    
    with col_sum1:
        st.markdown(f"""
        **Created:**
        - Risks: {result.get('risks_created', 0)}
        - TPOs: {result.get('tpos_created', 0)}
        - Influences: {result.get('influences_created', 0)}
        - TPO Impacts: {result.get('tpo_impacts_created', 0)}
        - Mitigations: {result.get('mitigations_created', 0)}
        - Mitigates: {result.get('mitigates_created', 0)}
        """)
    
    with col_sum2:
        st.markdown(f"""
        **Skipped:**
        - Risks: {result.get('risks_skipped', 0)}
        - TPOs: {result.get('tpos_skipped', 0)}
        - Influences: {result.get('influences_skipped', 0)}
        - TPO Impacts: {result.get('tpo_impacts_skipped', 0)}
        - Mitigations: {result.get('mitigations_skipped', 0)}
        - Mitigates: {result.get('mitigates_skipped', 0)}
        """)
    
    # Show errors if any
    if errors:
        with st.expander(f"❌ Errors ({len(errors)})", expanded=True):
            for error in errors:
                st.error(error)
    
    # Show warnings if any
    warnings = result.get("warnings", [])
    if warnings:
        with st.expander(f"⚠️ Warnings ({len(warnings)})", expanded=False):
            for warning in warnings:
                st.warning(warning)
    
    # Show detailed logs
    logs = result.get("logs", [])
    if logs:
        with st.expander(f"📋 Detailed Logs ({len(logs)} entries)", expanded=False):
            log_text = "\n".join(logs)
            st.code(log_text, language="text")
    
    # Offer to refresh if items were created
    if total_created > 0:
        if st.button("🔄 Refresh to see imported data", type="primary"):
            st.rerun()
