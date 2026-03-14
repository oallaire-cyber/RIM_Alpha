"""
Import/Export Tab for RIM Application.

Provides Excel import/export and JSON backup/restore functionality.

Sheet naming convention for Excel context data:
  - CN_{type_id}   — one sheet per ContextNode type
  - CE_{rel_id}    — one sheet per ContextEdge type
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import os


def render_import_export_tab(
    export_fn: Callable[[str], None],
    import_fn: Callable[[str], Dict[str, Any]],
    export_bytes_fn: Optional[Callable[[], bytes]] = None,
    export_json_fn: Optional[Callable[[], Dict[str, Any]]] = None,
    import_json_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
):
    """
    Render the Import/Export tab.

    Args:
        export_fn: Function to export data to a file path
        import_fn: Function to import data from a file path
        export_bytes_fn: Optional function to export data as bytes (for download)
        export_json_fn: Optional function to export full graph as JSON dict
        import_json_fn: Optional function to restore from a JSON dict
    """
    import streamlit as st

    st.markdown("### 📥 Excel Import / Export")
    st.markdown(
        "*Covers all entity types: Risks, Influences, TPOs, TPO Impacts, Mitigations, "
        "Mitigates — plus all schema-defined Context Nodes (`CN_*`) and Context Edges (`CE_*`).*"
    )

    col1, col2 = st.columns(2)

    with col1:
        _render_export_section(export_fn, export_bytes_fn)

    with col2:
        _render_import_section(import_fn)

    # JSON Backup / Restore (shown only when callbacks are supplied)
    if export_json_fn or import_json_fn:
        st.divider()
        _render_json_backup_section(export_json_fn, import_json_fn)


def _render_export_section(
    export_fn: Callable[[str], None],
    export_bytes_fn: Optional[Callable[[], bytes]] = None,
):
    """Render the Excel export section."""
    import streamlit as st
    import tempfile

    st.markdown("#### Export to Excel")
    st.markdown(
        "*Exports all core and context data. "
        "Use the exported file as a template for bulk data entry or migration.*"
    )

    if st.button("📤 Export data", use_container_width=True):
        try:
            if export_bytes_fn:
                excel_bytes = export_bytes_fn()
                st.download_button(
                    "⬇️ Download Excel file",
                    excel_bytes,
                    file_name=f"RIM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            else:
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, "rim_export.xlsx")
                export_fn(filepath)
                with open(filepath, "rb") as f:
                    st.download_button(
                        "⬇️ Download Excel file",
                        f.read(),
                        file_name=f"RIM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
        except Exception as e:
            st.error(f"Export error: {e}")


def _render_import_section(import_fn: Callable[[str], Dict[str, Any]]):
    """Render the Excel import section."""
    import streamlit as st
    import tempfile

    st.markdown("#### Import from Excel")
    st.markdown(
        "*Imports all core and context data from sheets in the file. "
        "Context Node sheets must be named `CN_{type_id}`, "
        "Context Edge sheets `CE_{rel_type_id}`. "
        "Unknown types are skipped — check the warnings log for `[SCHEMA]` messages.*"
    )

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

    if uploaded_file is not None:
        if st.button("📥 Import data", use_container_width=True):
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getvalue())

            with st.spinner("Importing data…"):
                try:
                    result = import_fn(filepath)
                    _display_import_results(result)
                except Exception as e:
                    st.error(f"Import error: {e}")


def _render_json_backup_section(
    export_json_fn: Optional[Callable[[], Dict[str, Any]]],
    import_json_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]],
):
    """Render the JSON Backup / Restore section."""
    import streamlit as st
    import json

    st.markdown("### 🗄️ JSON Backup / Restore")
    st.markdown(
        "*Full-graph backup including all context data. "
        "The JSON file captures `schema_version`, `exported_at`, and every entity "
        "and relationship collection. Restore upserts by name — existing records are skipped.*"
    )

    col_bk, col_rs = st.columns(2)

    # -- Backup --
    with col_bk:
        st.markdown("#### 📦 Backup")
        if export_json_fn and st.button("💾 Create JSON Backup", use_container_width=True):
            try:
                with st.spinner("Preparing backup…"):
                    data = export_json_fn()
                json_bytes = json.dumps(data, indent=2, default=str).encode("utf-8")
                st.download_button(
                    "⬇️ Download Backup",
                    json_bytes,
                    file_name=f"RIM_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
                st.success(
                    f"Backup created — schema v{data.get('schema_version', '?')}, "
                    f"exported at {data.get('exported_at', '?')}"
                )
            except Exception as e:
                st.error(f"Backup error: {e}")

    # -- Restore --
    with col_rs:
        st.markdown("#### ♻️ Restore")
        uploaded_json = st.file_uploader("Choose a JSON Backup file", type=["json"], key="json_restore_uploader")
        if import_json_fn and uploaded_json is not None:
            st.warning(
                "⚠️ Restore will **add** missing records (upsert by name). "
                "Existing records are never overwritten or deleted."
            )
            if st.button("♻️ Restore from Backup", use_container_width=True, type="primary"):
                try:
                    import json as _json
                    data = _json.loads(uploaded_json.getvalue().decode("utf-8"))
                    with st.spinner("Restoring…"):
                        summary = import_json_fn(data)
                    _display_json_restore_results(summary)
                except Exception as e:
                    st.error(f"Restore error: {e}")


def _display_import_results(result: Dict[str, Any]):
    """Display import results summary for Excel import."""
    import streamlit as st

    # Calculate totals (core + context)
    total_created = (
        result.get("risks_created", 0)
        + result.get("influences_created", 0)
        + result.get("tpos_created", 0)
        + result.get("tpo_impacts_created", 0)
        + result.get("mitigations_created", 0)
        + result.get("mitigates_created", 0)
        + result.get("context_nodes_created", 0)
        + result.get("context_edges_created", 0)
    )
    total_skipped = (
        result.get("risks_skipped", 0)
        + result.get("influences_skipped", 0)
        + result.get("tpos_skipped", 0)
        + result.get("tpo_impacts_skipped", 0)
        + result.get("mitigations_skipped", 0)
        + result.get("mitigates_skipped", 0)
        + result.get("context_nodes_skipped", 0)
        + result.get("context_edges_skipped", 0)
    )

    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    schema_warnings = [w for w in warnings if "[SCHEMA]" in w]

    if errors:
        st.error(f"⚠️ Import completed with {len(errors)} error(s)")
    elif schema_warnings:
        st.warning(
            f"✅ Import completed — {total_created} created, {total_skipped} skipped. "
            f"**{len(schema_warnings)} schema warning(s)** — see log below for YAML snippets."
        )
    elif total_skipped > 0:
        st.warning(f"✅ Import completed with {total_skipped} item(s) skipped")
    else:
        st.success(f"✅ Import successful! {total_created} item(s) created")

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
        cn_c = result.get("context_nodes_created", 0)
        ce_c = result.get("context_edges_created", 0)
        if cn_c or ce_c:
            st.markdown(f"- Context Nodes: **{cn_c}**\n- Context Edges: **{ce_c}**")

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
        cn_s = result.get("context_nodes_skipped", 0)
        ce_s = result.get("context_edges_skipped", 0)
        if cn_s or ce_s:
            st.markdown(f"- Context Nodes: **{cn_s}**\n- Context Edges: **{ce_s}**")

    # Schema warnings — shown prominently so users can fix schema.yaml
    if schema_warnings:
        with st.expander(f"🔧 Schema Warnings — Action Required ({len(schema_warnings)})", expanded=True):
            st.info(
                "These sheets were skipped because their type is not yet declared in "
                "`schema.yaml`. Each warning below includes a ready-to-paste YAML snippet. "
                "After adding the type, re-export to get the correct sheet template, then re-import."
            )
            for w in schema_warnings:
                st.code(w.strip(), language="yaml")

    # Other errors
    other_errors = [e for e in errors]
    if other_errors:
        with st.expander(f"❌ Errors ({len(other_errors)})", expanded=True):
            for error in other_errors:
                st.error(error)

    # Non-schema warnings
    non_schema_warnings = [w for w in warnings if "[SCHEMA]" not in w]
    if non_schema_warnings:
        with st.expander(f"⚠️ Other Warnings ({len(non_schema_warnings)})", expanded=False):
            for w in non_schema_warnings:
                st.warning(w)

    # Detailed logs
    logs = result.get("logs", [])
    if logs:
        with st.expander(f"📋 Detailed Logs ({len(logs)} entries)", expanded=False):
            st.code("\n".join(logs), language="text")

    if total_created > 0:
        if st.button("🔄 Refresh to see imported data", type="primary"):
            st.rerun()


def _display_json_restore_results(summary: Dict[str, Any]):
    """Display JSON restore results summary."""
    import streamlit as st

    errors = summary.get("errors", [])
    total_created = (
        summary.get("risks_created", 0)
        + summary.get("tpos_created", 0)
        + summary.get("mitigations_created", 0)
        + summary.get("influences_created", 0)
        + summary.get("tpo_impacts_created", 0)
        + summary.get("mitigates_created", 0)
        + summary.get("context_nodes_created", 0)
        + summary.get("context_edges_created", 0)
    )

    schema_errors = [e for e in errors if "[SCHEMA]" in e]
    other_errors = [e for e in errors if "[SCHEMA]" not in e]

    if other_errors:
        st.error(f"Restore completed with {len(other_errors)} error(s)")
    elif schema_errors:
        st.warning(
            f"✅ Restore completed — {total_created} record(s) inserted. "
            f"**{len(schema_errors)} schema issue(s)** — see below."
        )
    else:
        st.success(f"✅ Restore complete — {total_created} record(s) inserted")

    st.markdown("##### Restore Summary")
    for key in ("risks", "tpos", "mitigations", "influences", "tpo_impacts",
                 "mitigates", "context_nodes", "context_edges"):
        c = summary.get(f"{key}_created", 0)
        s = summary.get(f"{key}_skipped", 0)
        if c or s:
            st.markdown(f"- **{key.replace('_', ' ').title()}**: {c} created, {s} skipped")

    if schema_errors:
        with st.expander("🔧 Schema Issues", expanded=True):
            for e in schema_errors:
                st.code(e, language="yaml")

    if other_errors:
        with st.expander("❌ Other Errors", expanded=True):
            for e in other_errors:
                st.error(e)

    if total_created > 0:
        if st.button("🔄 Refresh to see restored data", type="primary", key="json_restore_refresh"):
            st.rerun()
