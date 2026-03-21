"""
F7 What-If Analysis — RIM

Toggle mitigations ON/OFF in-memory and observe EL + TRI deltas.
No database writes — all scenario exploration is session-local.

Constraints:
- Scope-constrained: respects the active filter_manager scope.
- Lifecycle-aware: inactive risks excluded by default; option to include.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import streamlit as st
import pandas as pd

# Add repo root to path (same pattern as other pages)
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_manager import get_active_manager
from utils.state_manager import init_whatif_state
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

    # Fetch raw data — bypass manager.get_all_risks() to pass exclude_inactive
    risks = get_all_risks(conn, exclude_inactive=not include_inactive)
    influences = manager.get_semantic_influences()
    mitigations = manager.get_all_mitigations()
    mitigates_rels = manager.get_all_mitigates_relationships()

    # Apply scope filter (mirrors manager.calculate_exposure logic)
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

    # Cache raw data for recomputation
    st.session_state.whatif_raw_risks = risks
    st.session_state.whatif_raw_influences = influences
    st.session_state.whatif_raw_mitigations = mitigations
    st.session_state.whatif_raw_mitigates = mitigates_rels

    # Compute baseline
    baseline = calculate_exposure(
        risks=risks,
        influences=influences,
        mitigations=mitigations,
        mitigates_relationships=mitigates_rels,
    )
    st.session_state.whatif_baseline = baseline
    st.session_state.whatif_modified = baseline  # starts identical to baseline

    # Initialise per-mitigation toggle keys (all enabled by default)
    for m in mitigations:
        key = f"whatif_toggle_{m['id']}"
        if key not in st.session_state:
            st.session_state[key] = True


def _recompute_modified() -> None:
    """Recompute modified exposure from current toggle state (pure in-memory)."""
    mitigations: List[Dict] = st.session_state.whatif_raw_mitigations or []
    mitigates_rels: List[Dict] = st.session_state.whatif_raw_mitigates or []

    disabled = {
        m["id"]
        for m in mitigations
        if not st.session_state.get(f"whatif_toggle_{m['id']}", True)
    }

    active_mits = [m for m in mitigations if m["id"] not in disabled]
    active_rels = [r for r in mitigates_rels if r.get("mitigation_id") not in disabled]

    modified = calculate_exposure(
        risks=st.session_state.whatif_raw_risks,
        influences=st.session_state.whatif_raw_influences,
        mitigations=active_mits,
        mitigates_relationships=active_rels,
    )
    st.session_state.whatif_modified = modified


# =============================================================================
# RENDER HELPERS
# =============================================================================

def _render_summary(baseline: GlobalExposureResult, modified: GlobalExposureResult) -> None:
    """Side-by-side portfolio metrics with Streamlit delta indicators."""
    st.subheader("Portfolio Impact")

    c1, c2, c3 = st.columns(3)

    rr_delta = modified.residual_risk_percentage - baseline.residual_risk_percentage
    with c1:
        st.metric(
            "Residual Risk %",
            f"{modified.residual_risk_percentage:.1f}%",
            delta=f"{rr_delta:+.1f}%",
            delta_color="inverse",
            help="Total final exposure / base exposure × 100",
        )

    wrs_delta = modified.weighted_risk_score - baseline.weighted_risk_score
    with c2:
        st.metric(
            "Weighted Risk Score",
            f"{modified.weighted_risk_score:.1f}",
            delta=f"{wrs_delta:+.1f}",
            delta_color="inverse",
            help="Severity²-weighted portfolio metric (0–100)",
        )

    baseline_tri = sum(r.tail_risk_indicator for r in baseline.risk_results)
    modified_tri = sum(r.tail_risk_indicator for r in modified.risk_results)
    tri_delta = modified_tri - baseline_tri
    with c3:
        st.metric(
            "Total TRI",
            f"{modified_tri:.1f}",
            delta=f"{tri_delta:+.1f}",
            delta_color="inverse",
            help="Sum of Tail Risk Indicators (L × S^1.5) across all risks",
        )

    baseline_health, _ = baseline.get_health_status()
    modified_health, modified_color = modified.get_health_status()
    if baseline_health != modified_health:
        st.warning(f"Health status changed: **{baseline_health}** → **{modified_health}**")
    else:
        st.caption(f"Health status: **{modified_health}** (unchanged from baseline)")

    # Show count of disabled mitigations
    mitigations: List[Dict] = st.session_state.whatif_raw_mitigations or []
    disabled_count = sum(
        1 for m in mitigations
        if not st.session_state.get(f"whatif_toggle_{m['id']}", True)
    )
    if disabled_count:
        st.info(f"**{disabled_count}** mitigation(s) currently disabled in this scenario.")
    else:
        st.caption("All mitigations active — scenario matches baseline.")


def _render_per_risk_table(
    baseline: GlobalExposureResult, modified: GlobalExposureResult
) -> None:
    """Per-risk delta table (EL + TRI), sorted by largest EL increase."""
    st.subheader("Per-Risk Exposure Delta")

    baseline_map = {r.risk_id: r for r in baseline.risk_results}
    modified_map = {r.risk_id: r for r in modified.risk_results}

    rows = []
    for risk_id, b in baseline_map.items():
        m = modified_map.get(risk_id, b)
        rows.append({
            "Risk": b.risk_name,
            "Level": b.level,
            "Baseline EL": round(b.final_exposure, 2),
            "Modified EL": round(m.final_exposure, 2),
            "Δ EL": round(m.final_exposure - b.final_exposure, 2),
            "Baseline TRI": round(b.tail_risk_indicator, 2),
            "Modified TRI": round(m.tail_risk_indicator, 2),
            "Δ TRI": round(m.tail_risk_indicator - b.tail_risk_indicator, 2),
            "Quadrant": m.risk_quadrant,
        })

    if not rows:
        st.info("No risk data available in the current scope.")
        return

    df = pd.DataFrame(rows).sort_values("Δ EL", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Δ EL": st.column_config.NumberColumn("Δ EL", format="%.2f"),
            "Δ TRI": st.column_config.NumberColumn("Δ TRI", format="%.2f"),
            "Baseline EL": st.column_config.NumberColumn("Baseline EL", format="%.2f"),
            "Modified EL": st.column_config.NumberColumn("Modified EL", format="%.2f"),
        },
    )


def _render_mitigation_toggles(mitigations: List[Dict[str, Any]]) -> None:
    """Render per-mitigation enable/disable checkboxes, grouped by type."""
    if not mitigations:
        st.info("No mitigations in the current scope.")
        return

    # Group by type
    by_type: Dict[str, List[Dict]] = {}
    for m in mitigations:
        t = m.get("type", "Unknown")
        by_type.setdefault(t, []).append(m)

    for mit_type, mits in sorted(by_type.items()):
        enabled_count = sum(
            1 for m in mits if st.session_state.get(f"whatif_toggle_{m['id']}", True)
        )
        label = f"**{mit_type}** — {enabled_count}/{len(mits)} enabled"
        with st.expander(label, expanded=True):
            for m in mits:
                key = f"whatif_toggle_{m['id']}"
                name = m.get("name", m["id"])
                status = m.get("status", "")
                suffix = f" *({status})*" if status else ""
                st.checkbox(
                    f"{name}{suffix}",
                    key=key,
                )


# =============================================================================
# MAIN
# =============================================================================

def main():
    st.set_page_config(
        page_title="What-If Analysis — RIM",
        page_icon="🔬",
        layout="wide",
    )

    init_whatif_state()

    st.title("🔬 What-If Analysis")
    st.caption(
        "Toggle mitigations ON/OFF in-memory to explore EL and TRI deltas. "
        "No database changes are made."
    )

    # ── Connection & scope ────────────────────────────────────────────────────
    manager = get_active_manager()
    scope_ids, scope_label = _get_scope_info()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.header("⚙️ What-If Parameters")

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
        key="whatif_include_inactive",
        help=(
            "When checked, Accepted / Watching / Suppressed / Closed risks "
            "are included. Use to reveal latent tail exposure."
        ),
    )

    compute_btn = st.sidebar.button(
        "🔄 Compute Baseline",
        type="primary",
        use_container_width=True,
        disabled=manager is None,
    )

    reset_btn = st.sidebar.button(
        "↺ Reset Scenario",
        use_container_width=True,
        disabled=st.session_state.whatif_baseline is None,
        help="Re-enable all mitigations (restore to baseline scenario).",
    )

    # ── Baseline computation ──────────────────────────────────────────────────
    if compute_btn and manager is not None:
        with st.spinner("Computing baseline exposure…"):
            _load_baseline(manager, scope_ids, include_inactive)
        st.success("Baseline computed.")

    # ── Reset scenario ────────────────────────────────────────────────────────
    if reset_btn and st.session_state.whatif_raw_mitigations:
        for m in st.session_state.whatif_raw_mitigations:
            st.session_state[f"whatif_toggle_{m['id']}"] = True
        st.rerun()

    # ── Guard: no baseline yet ────────────────────────────────────────────────
    if st.session_state.whatif_baseline is None:
        if manager is None:
            st.warning("Connect to a database from the dashboard first.")
        else:
            st.info("👈 Click **Compute Baseline** in the sidebar to begin.")
        return

    # ── Recompute modified from current toggles ───────────────────────────────
    _recompute_modified()

    baseline: GlobalExposureResult = st.session_state.whatif_baseline
    modified: GlobalExposureResult = st.session_state.whatif_modified
    mitigations: List[Dict] = st.session_state.whatif_raw_mitigations or []

    # ── Layout: toggles left, results right ───────────────────────────────────
    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.subheader("Mitigation Toggles")
        risk_count = len(st.session_state.whatif_raw_risks or [])
        st.caption(
            f"{len(mitigations)} mitigation(s) · {risk_count} risk(s) in scope. "
            "Uncheck to disable a mitigation."
        )
        _render_mitigation_toggles(mitigations)

    with col_right:
        _render_summary(baseline, modified)
        st.markdown("---")
        _render_per_risk_table(baseline, modified)


if __name__ == "__main__":
    main()
