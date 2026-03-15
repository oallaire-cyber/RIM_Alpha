"""
Scope Filter Panel — F28 Advanced Scope Filter UI.

Provides two public entry points:

* render_scope_filter_panel(manager, filter_mgr, active_scope)
    Used by home.py (Data Management > Risks tab). Persists changes via FilterManager.

* render_scope_node_editor(manager, scope, on_add, on_remove, key_prefix)
    Used by the Configuration page (scope creation / modification). Persists
    via caller-supplied callbacks so no FilterManager is required.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import streamlit as st
from core import get_registry

if TYPE_CHECKING:
    from database import RiskGraphManager
    from ui.filters import FilterManager


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_schema_options() -> tuple[list[str], list[str], dict[str, str]]:
    """Return (level_options, subtype_options, subtype_id_to_label) from registry."""
    raw = get_registry().get_raw_schema()
    risk_raw = raw.get("entities", {}).get("risk", {})

    level_options = [lv["label"] for lv in risk_raw.get("levels", [])]

    subtypes_raw = risk_raw.get("subtypes", [])
    subtype_options = [s["label"] for s in subtypes_raw if s.get("label")]
    subtype_id_to_label: dict[str, str] = {
        s["id"]: s.get("label", s["id"]) for s in subtypes_raw
    }
    return level_options, subtype_options, subtype_id_to_label


def _load_exposure_context() -> tuple[dict[str, float], object]:
    """Return (exposure_map, exposure_results) from session state."""
    exposure_map: dict[str, float] = {}
    exposure_results = st.session_state.get("exposure_results")
    if exposure_results:
        for r in exposure_results.risk_results:
            exposure_map[r.risk_id] = r.final_exposure
    return exposure_map, exposure_results


def _render_filter_table(
    all_risks: list[dict],
    scope,                              # AnalysisScopeConfig
    on_add: Callable[[str], None],      # called with node_id when a node is added
    on_remove: Callable[[str], None],   # called with node_id when a node is removed
    key_prefix: str,
    exposure_map: dict[str, float],
    exposure_results,
) -> bool:
    """
    Core filter UI + data_editor.

    Renders filter controls, bulk-action buttons, and a st.data_editor table.
    Calls on_add / on_remove for any scope membership changes.

    Returns True if any changes were made (caller should call st.rerun()).
    """
    level_options, subtype_options, subtype_id_to_label = _load_schema_options()

    # ── Filter controls ───────────────────────────────────────────────────────
    col_s, col_lv, col_sub, col_exp = st.columns([2, 1, 2, 2])

    text_query: str = col_s.text_input(
        "Search by name",
        key=f"{key_prefix}_text",
        placeholder="Partial name match...",
        label_visibility="collapsed",
    )
    col_s.caption("🔍 Name search")

    sel_levels: list[str] = col_lv.multiselect(
        "Level",
        options=level_options,
        default=level_options,
        key=f"{key_prefix}_levels",
    )

    sel_subtypes: list[str] | None = (
        col_sub.multiselect(
            "Subtype",
            options=subtype_options,
            default=subtype_options,
            key=f"{key_prefix}_subtypes",
        )
        if subtype_options
        else None
    )

    exp_range: tuple[float, float] | None = None
    if exposure_results:
        vals = list(exposure_map.values())
        hi = max(vals) if vals and max(vals) > 0 else 1.0
        exp_range = col_exp.slider(
            "Final Exposure",
            min_value=0.0,
            max_value=hi,
            value=(0.0, hi),
            step=round(hi / 20, 3) if hi > 0 else 0.05,
            key=f"{key_prefix}_exp",
        )
    else:
        col_exp.caption("Run Exposure Calculation to enable this filter.")

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = list(all_risks)

    if text_query:
        q = text_query.lower()
        filtered = [r for r in filtered if q in r.get("name", "").lower()]

    if sel_levels is not None:
        filtered = (
            [r for r in filtered if r.get("level", "") in sel_levels]
            if sel_levels
            else []
        )

    if sel_subtypes is not None:
        if sel_subtypes:
            filtered = [
                r
                for r in filtered
                if subtype_id_to_label.get(r.get("subtype", ""), "Generic")
                in sel_subtypes
                or r.get("subtype") is None
            ]
        else:
            filtered = []

    if exp_range is not None:
        lo, hi = exp_range
        filtered = [
            r for r in filtered if lo <= exposure_map.get(r["id"], 0.0) <= hi
        ]

    # ── Summary caption ───────────────────────────────────────────────────────
    scope_set = set(scope.node_ids)
    filtered_ids = [r["id"] for r in filtered]

    st.caption(
        f"Editing scope **{scope.name}** · "
        f"Showing **{len(filtered)}** of **{len(all_risks)}** risks · "
        f"**{len(scope_set)}** currently in scope"
    )

    # ── Bulk action buttons ───────────────────────────────────────────────────
    col_add, col_rem, _ = st.columns([1, 1, 4])

    if col_add.button("✅ Select All Filtered", key=f"{key_prefix}_sel_all"):
        changed = False
        for nid in filtered_ids:
            if nid not in scope_set:
                on_add(nid)
                changed = True
        if changed:
            return True

    if col_rem.button("🔲 Deselect All Filtered", key=f"{key_prefix}_desel_all"):
        changed = False
        for nid in filtered_ids:
            if nid in scope_set:
                on_remove(nid)
                changed = True
        if changed:
            return True

    # ── Build table rows ──────────────────────────────────────────────────────
    rows = []
    for r in filtered:
        row: dict = {
            "In Scope": r["id"] in scope_set,
            "Name":     r.get("name", ""),
            "Level":    r.get("level", ""),
            "Subtype":  subtype_id_to_label.get(r.get("subtype", ""), "Generic"),
            "Status":   r.get("status", ""),
            "_id":      r["id"],
        }
        if exposure_results:
            row["Exposure"] = round(exposure_map.get(r["id"], 0.0), 3)
        rows.append(row)

    # ── Render st.data_editor ─────────────────────────────────────────────────
    col_cfg: dict = {
        "In Scope": st.column_config.CheckboxColumn(
            "In Scope",
            help="Check to include this risk in the active scope",
            default=False,
        ),
        "Name":    st.column_config.TextColumn("Name", disabled=True),
        "Level":   st.column_config.TextColumn("Level", disabled=True),
        "Subtype": st.column_config.TextColumn("Subtype", disabled=True),
        "Status":  st.column_config.TextColumn("Status", disabled=True),
    }
    if exposure_results:
        col_cfg["Exposure"] = st.column_config.NumberColumn(
            "Exposure", disabled=True, format="%.3f"
        )

    col_order = (
        ["In Scope", "Name", "Level", "Subtype", "Status"]
        + (["Exposure"] if exposure_results else [])
        # _id intentionally omitted — present in returned data but not rendered
    )

    edited: list[dict] = st.data_editor(
        rows,
        column_config=col_cfg,
        column_order=col_order,
        hide_index=True,
        use_container_width=True,
        key=f"{key_prefix}_editor",
    )

    # ── Sync checkbox edits back via callbacks ────────────────────────────────
    changed = False
    for orig, ed in zip(rows, edited):
        nid = orig["_id"]
        was_in = orig["In Scope"]
        is_now = ed["In Scope"]
        if not was_in and is_now:
            on_add(nid)
            changed = True
        elif was_in and not is_now:
            on_remove(nid)
            changed = True

    return changed


# ─────────────────────────────────────────────────────────────────────────────
# Public entry points
# ─────────────────────────────────────────────────────────────────────────────

def render_scope_filter_panel(
    manager: "RiskGraphManager",
    filter_mgr: "FilterManager",
    active_scope,  # AnalysisScopeConfig
) -> None:
    """
    Render the Advanced Scope Filter UI for home.py (Data Management > Risks tab).

    Changes are persisted via FilterManager (add_node_to_scope /
    remove_node_from_scope), which updates both in-memory state and YAML.
    """
    all_risks = manager.get_unified_entities("risk")
    exposure_map, exposure_results = _load_exposure_context()

    def on_add(nid: str) -> None:
        filter_mgr.add_node_to_scope(active_scope.id, nid)

    def on_remove(nid: str) -> None:
        filter_mgr.remove_node_from_scope(active_scope.id, nid)

    if _render_filter_table(
        all_risks, active_scope, on_add, on_remove,
        "sfp", exposure_map, exposure_results,
    ):
        st.rerun()


def render_scope_node_editor(
    manager: "RiskGraphManager",
    scope,                          # AnalysisScopeConfig
    on_add: Callable[[str], None],
    on_remove: Callable[[str], None],
    key_prefix: str = "sne",
) -> None:
    """
    Render the Advanced Scope Filter UI for any context (e.g. Configuration page).

    The caller supplies on_add / on_remove callbacks that handle persistence
    (e.g. direct YAML save). No FilterManager dependency.
    """
    all_risks = manager.get_unified_entities("risk")
    exposure_map, exposure_results = _load_exposure_context()

    if _render_filter_table(
        all_risks, scope, on_add, on_remove,
        key_prefix, exposure_map, exposure_results,
    ):
        st.rerun()
