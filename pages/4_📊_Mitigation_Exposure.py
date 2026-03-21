"""
F6 Mitigation Exposure View — RIM

Ranks mitigations by their marginal contribution to EL and TRI reduction.
For each active mitigation, a counterfactual exposure is computed in-memory
(what would the portfolio look like without this mitigation?) to derive the
delta EL and delta TRI attributable to that mitigation.

Constraints:
- Scope-constrained: respects the active filter_manager scope.
- Lifecycle-aware: inactive risks excluded by default; option to include.
- No database writes — all computation is session-local.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import streamlit as st
import pandas as pd

# Add repo root to path (same pattern as other pages)
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_manager import get_active_manager
from utils.state_manager import init_mitigation_exposure_state
from utils.markdown_loader import load_doc
from services.exposure_calculator import calculate_exposure, GlobalExposureResult


# =============================================================================
# HELPERS
# =============================================================================

def _get_scope_info():
    """Return (scope_ids, scope_label) from the active FilterManager."""
    fm = st.session_state.get("filter_manager")
    if fm is not None:
        scope_ids = fm.get_scope_node_ids()
        if scope_ids is not None:
            scope_names = [s.name for s in (fm.active_scopes or [])]
            label = ", ".join(scope_names) if scope_names else "Active scope"
            return scope_ids, label
    return None, "Full Graph"


def _load_baseline(manager, scope_ids: Optional[List[str]], include_inactive: bool) -> None:
    """Fetch data from DB, apply scope + lifecycle filter, compute and cache baseline."""
    from database.queries.risks import get_all_risks

    conn = manager._connection

    risks = get_all_risks(conn, exclude_inactive=not include_inactive)
    influences = manager.get_semantic_influences()
    mitigations = manager.get_all_mitigations()
    mitigates_rels = manager.get_all_mitigates_relationships()

    # Apply scope filter
    if scope_ids is not None:
        scope_set = set(scope_ids)
        risk_ids = {r["id"] for r in risks if r["id"] in scope_set}
        risks = [r for r in risks if r["id"] in risk_ids]
        influences = [
            i for i in influences
            if i.get("source_id") in risk_ids and i.get("target_id") in risk_ids
        ]
        mitigates_rels = [mr for mr in mitigates_rels if mr.get("risk_id") in risk_ids]
        connected_mit_ids = {mr["mitigation_id"] for mr in mitigates_rels}
        mitigations = [m for m in mitigations if m["id"] in connected_mit_ids]

    # Cache raw data
    st.session_state.mitexp_raw_risks = risks
    st.session_state.mitexp_raw_influences = influences
    st.session_state.mitexp_raw_mitigations = mitigations
    st.session_state.mitexp_raw_mitigates = mitigates_rels

    # Compute baseline
    baseline = calculate_exposure(
        risks=risks,
        influences=influences,
        mitigations=mitigations,
        mitigates_relationships=mitigates_rels,
    )
    st.session_state.mitexp_baseline = baseline


def _compute_mitigation_impacts() -> List[Dict[str, Any]]:
    """For each mitigation, compute the counterfactual delta EL and TRI."""
    risks: List[Dict] = st.session_state.mitexp_raw_risks or []
    influences: List[Dict] = st.session_state.mitexp_raw_influences or []
    mitigations: List[Dict] = st.session_state.mitexp_raw_mitigations or []
    mitigates_rels: List[Dict] = st.session_state.mitexp_raw_mitigates or []
    baseline: GlobalExposureResult = st.session_state.mitexp_baseline

    baseline_tri = sum(r.tail_risk_indicator for r in baseline.risk_results)
    base_exposure = baseline.total_base_exposure

    results = []
    for mit in mitigations:
        mid = mit["id"]

        # Disable this single mitigation
        active_mits = [m for m in mitigations if m["id"] != mid]
        active_rels = [r for r in mitigates_rels if r.get("mitigation_id") != mid]

        # Risks covered by this mitigation
        risks_covered = len({r["risk_id"] for r in mitigates_rels if r.get("mitigation_id") == mid})

        # Risk level(s) covered
        covered_risk_ids = {r["risk_id"] for r in mitigates_rels if r.get("mitigation_id") == mid}
        risk_levels = {r.get("level", "") for r in risks if r["id"] in covered_risk_ids}
        level_label = _format_levels(risk_levels)

        # Counterfactual exposure without this mitigation
        without = calculate_exposure(
            risks=risks,
            influences=influences,
            mitigations=active_mits,
            mitigates_relationships=active_rels,
        )
        without_tri = sum(r.tail_risk_indicator for r in without.risk_results)

        delta_el = without.total_final_exposure - baseline.total_final_exposure
        delta_tri = without_tri - baseline_tri
        pct_portfolio = (delta_el / base_exposure * 100) if base_exposure > 0 else 0.0

        results.append({
            "id": mid,
            "name": mit.get("name", mid),
            "type": mit.get("type", ""),
            "status": mit.get("status", ""),
            "level": level_label,
            "risks_covered": risks_covered,
            "delta_el": delta_el,
            "delta_tri": delta_tri,
            "pct_portfolio": pct_portfolio,
        })

    return sorted(results, key=lambda x: x["delta_el"], reverse=True)


def _format_levels(levels: set) -> str:
    """Format a set of risk level strings into a compact label."""
    cleaned = {lv.strip() for lv in levels if lv.strip()}
    if not cleaned:
        return "—"
    if len(cleaned) == 1:
        return next(iter(cleaned))
    return "Mixed"


# =============================================================================
# RENDER HELPERS
# =============================================================================

def _render_summary(baseline: GlobalExposureResult, results: List[Dict]) -> None:
    """Portfolio-level summary metrics."""
    el_reduction = baseline.total_base_exposure - baseline.total_final_exposure
    baseline_tri = sum(r.tail_risk_indicator for r in baseline.risk_results)
    health_label, _ = baseline.get_health_status()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Active Mitigations",
            len(results),
            help="Number of active mitigations in the current scope.",
        )
    with c2:
        st.metric(
            "Portfolio EL",
            f"{baseline.total_final_exposure:.1f}",
            help="Total final exposure across all in-scope risks (after all mitigations).",
        )
    with c3:
        st.metric(
            "EL Reduction (all)",
            f"{el_reduction:.1f}",
            help="Total exposure reduction vs. unmitigated baseline (base − final).",
        )
    with c4:
        st.metric(
            "Portfolio TRI",
            f"{baseline_tri:.1f}",
            help="Sum of Tail Risk Indicators (L × S^1.5) across all risks.",
        )

    st.caption(f"Portfolio health: **{health_label}** · Residual Risk: **{baseline.residual_risk_percentage:.1f}%**")


def _render_table(results: List[Dict], level_filter: str) -> None:
    """Per-mitigation impact table sorted by EL delta descending."""
    if not results:
        st.info("No mitigations found in the current scope.")
        return

    # Level filter (display-only — deltas are computed at portfolio level)
    filtered = results
    if level_filter != "All":
        filtered = [r for r in results if r["level"] == level_filter or r["level"] == "Mixed"]

    if not filtered:
        st.info(f"No mitigations covering **{level_filter}** risks in the current scope.")
        return

    rows = []
    for r in filtered:
        rows.append({
            "Mitigation": r["name"],
            "Type": r["type"],
            "Status": r["status"],
            "Level": r["level"],
            "Risks Covered": r["risks_covered"],
            "EL Delta ↑": round(r["delta_el"], 2),
            "TRI Delta ↑": round(r["delta_tri"], 2),
            "% Portfolio EL": round(r["pct_portfolio"], 1),
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "EL Delta ↑": st.column_config.NumberColumn(
                "EL Delta ↑",
                format="%.2f",
                help="Exposure increase if this mitigation were removed (higher = more critical).",
            ),
            "TRI Delta ↑": st.column_config.NumberColumn(
                "TRI Delta ↑",
                format="%.2f",
                help="TRI increase if this mitigation were removed.",
            ),
            "% Portfolio EL": st.column_config.NumberColumn(
                "% Portfolio EL",
                format="%.1f%%",
                help="EL Delta as a percentage of total base exposure.",
            ),
        },
    )
    st.caption(
        f"Showing {len(filtered)} of {len(results)} mitigation(s). "
        "EL Delta ↑ = marginal exposure increase if the mitigation is removed."
    )


# =============================================================================
# MAIN
# =============================================================================

def main():
    st.set_page_config(
        page_title="Mitigation Exposure View — RIM",
        page_icon="📊",
        layout="wide",
    )

    init_mitigation_exposure_state()

    st.title("📊 Mitigation Exposure View")
    st.caption(
        "Rank mitigations by their marginal impact on portfolio EL and TRI. "
        "Each row shows how much exposure would increase if that mitigation were removed."
    )

    # ── Connection & scope ────────────────────────────────────────────────────
    manager = get_active_manager()
    scope_ids, scope_label = _get_scope_info()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.header("⚙️ Mitigation Exposure Parameters")

    if manager is None:
        st.sidebar.warning(
            "⚠️ No active DB connection.\n\n"
            "Navigate to the **dashboard** first to connect."
        )
    else:
        st.sidebar.success("✅ Connected")

    if scope_ids is not None:
        st.sidebar.info(f"📍 Scope: **{scope_label}** ({len(scope_ids)} nodes)")
    else:
        st.sidebar.info("📍 Scope: **Full Graph** (no scope active)")

    st.sidebar.markdown("---")

    include_inactive = st.sidebar.checkbox(
        "Include inactive risks (worst-case)",
        key="mitexp_include_inactive",
        help=(
            "When checked, Accepted / Watching / Suppressed / Closed risks "
            "are included. Use to reveal latent tail exposure."
        ),
    )

    level_filter = st.sidebar.selectbox(
        "Risk level",
        options=["All", "Business", "Operational"],
        key="mitexp_level_filter",
        help="Filter the table to mitigations covering only the selected risk level.",
    )

    compute_btn = st.sidebar.button(
        "🔄 Compute Mitigation Impact",
        type="primary",
        use_container_width=True,
        disabled=manager is None,
    )

    # ── Computation ───────────────────────────────────────────────────────────
    if compute_btn and manager is not None:
        with st.spinner("Loading data and computing counterfactual exposure…"):
            _load_baseline(manager, scope_ids, include_inactive)
            results = _compute_mitigation_impacts()
            st.session_state.mitexp_results = results
        st.success(
            f"Computed impact for {len(results)} mitigation(s)."
        )

    # ── Guard: no results yet ─────────────────────────────────────────────────
    if st.session_state.mitexp_baseline is None or st.session_state.mitexp_results is None:
        if manager is None:
            st.warning("Connect to a database from the dashboard first.")
        else:
            st.info("👈 Click **Compute Mitigation Impact** in the sidebar to begin.")
        _render_help()
        return

    # ── Results ───────────────────────────────────────────────────────────────
    baseline: GlobalExposureResult = st.session_state.mitexp_baseline
    results: List[Dict] = st.session_state.mitexp_results

    _render_summary(baseline, results)
    st.markdown("---")

    st.subheader("Per-Mitigation Impact")
    _render_table(results, level_filter)

    st.markdown("---")
    _render_help()


def _render_help() -> None:
    """Inline help expander."""
    with st.expander("ℹ️ About this view", expanded=False):
        content = load_doc("help_mitigation_exposure.md")
        if content:
            st.markdown(content)
        else:
            st.markdown(
                "**Mitigation Exposure View** ranks mitigations by their marginal contribution "
                "to portfolio EL and TRI reduction. "
                "For each mitigation, a counterfactual exposure is computed — "
                "*what would the portfolio look like without this mitigation?* — "
                "and the delta shows its individual protective value."
            )


if __name__ == "__main__":
    main()
