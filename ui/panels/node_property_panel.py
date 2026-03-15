"""
Contextual Property Panel for the RIM graph canvas (F26).

Replaces the bare render_inline_editor call below the graph with a
structured 6-section panel.  Sections are implemented as a list of
Section dataclasses so new sections can be appended with zero
modification to existing ones.
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any

import streamlit as st

from database import RiskGraphManager
from ui.panels.editor_panel import get_entity_type_id, render_inline_editor


# ---------------------------------------------------------------------------
# Section dataclass
# ---------------------------------------------------------------------------

@dataclass
class Section:
    id: str
    title: str
    render_fn: Callable[[], None]
    expanded: bool = True


# ---------------------------------------------------------------------------
# Section render helpers (private)
# ---------------------------------------------------------------------------

def _render_identity(entity_data: Dict[str, Any], entity_type_id: Optional[str]) -> None:
    """Section 1 — basic node properties."""
    if not entity_data:
        st.caption("Node data unavailable.")
        return

    name = entity_data.get("name", "—")
    st.markdown(f"**Name:** {name}")

    label_map = {
        "risk": "Risk",
        "mitigation": "Mitigation",
    }
    type_display = label_map.get(entity_type_id or "", entity_type_id or "Context Node")
    st.markdown(f"**Type:** {type_display}")

    field_order = ["level", "subtype", "node_type", "status", "origin", "description"]
    shown = set()
    for key in field_order:
        val = entity_data.get(key)
        if val:
            st.markdown(f"**{key.replace('_', ' ').title()}:** {val}")
            shown.add(key)

    # Remaining fields (skip internal)
    skip = {"id", "_element_id", "name", "node_type"} | shown
    for key, val in entity_data.items():
        if key not in skip and val:
            st.markdown(f"**{key.replace('_', ' ').title()}:** {val}")


def _render_exposure(
    node_id: str,
    entity_type_id: Optional[str],
    exposure_results: Optional[Dict],
) -> None:
    """Section 2 — exposure metrics (risk nodes only)."""
    if entity_type_id != "risk":
        st.caption("Not applicable for this node type.")
        return

    if not exposure_results or "risk_results" not in exposure_results:
        st.caption("Run **Exposure Analysis** to see metrics.")
        return

    exp_lookup: Dict[str, Dict] = {
        r["risk_id"]: r for r in exposure_results.get("risk_results", [])
    }
    r = exp_lookup.get(node_id)
    if not r:
        st.caption("This node was not included in the last exposure calculation.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Likelihood", f"{r.get('likelihood', 0):.1f}")
        st.metric("Base Exposure", f"{r.get('base_exposure', 0):.1f}")
    with c2:
        st.metric("Impact", f"{r.get('impact', 0):.1f}")
        st.metric("Final Exposure", f"{r.get('final_exposure', 0):.1f}")
    with c3:
        base = r.get("base_exposure", 0)
        final = r.get("final_exposure", 0)
        residual_pct = (final / base * 100) if base else 0
        st.metric("Residual %", f"{residual_pct:.0f}%")
        mit_factor = r.get("mitigation_factor", 1.0)
        coverage_pct = round((1 - mit_factor) * 100)
        st.metric("Mit. Coverage", f"{coverage_pct}%")

    if r.get("trace"):
        with st.expander("Calculation trace", expanded=False):
            for line in r["trace"]:
                st.caption(line)


def _render_graph_position(
    manager: RiskGraphManager,
    node_id: str,
) -> None:
    """Section 3 — upstream/downstream counts."""
    try:
        upstream = manager.get_upstream_risks(node_id)
        downstream = manager.get_downstream_risks(node_id)
    except Exception as e:
        st.caption(f"Could not retrieve graph position: {e}")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Upstream influences", len(upstream))
    with c2:
        st.metric("Downstream influences", len(downstream))

    if upstream:
        with st.expander(f"Upstream nodes ({len(upstream)})", expanded=False):
            for n in upstream:
                depth_label = f" (depth {n['depth']})" if "depth" in n else ""
                st.caption(f"• {n.get('name', n.get('id', '?'))}{depth_label}")
    if downstream:
        with st.expander(f"Downstream nodes ({len(downstream)})", expanded=False):
            for n in downstream:
                depth_label = f" (depth {n['depth']})" if "depth" in n else ""
                st.caption(f"• {n.get('name', n.get('id', '?'))}{depth_label}")


def _render_influence(
    node_id: str,
    influence_results: Optional[Dict],
) -> None:
    """Section 4 — influence analysis metrics."""
    if not influence_results:
        st.caption("Run **Influence Analysis** to see metrics.")
        return

    # ── Critical path ──────────────────────────────────────────────────────
    on_critical_path = any(
        node_id in path.get("path", [])
        for path in influence_results.get("critical_paths", [])
    )

    # ── Bottleneck ─────────────────────────────────────────────────────────
    bottleneck_data = next(
        (b for b in influence_results.get("bottlenecks", []) if b.get("id") == node_id),
        None,
    )

    # ── Convergence ────────────────────────────────────────────────────────
    convergence_data = next(
        (c for c in influence_results.get("convergence_points", []) if c.get("id") == node_id),
        None,
    )

    # ── Propagation (top propagators) ──────────────────────────────────────
    propagator_data = next(
        (p for p in influence_results.get("top_propagators", []) if p.get("id") == node_id),
        None,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Critical path:** {'✅ Yes' if on_critical_path else '❌ No'}")
        st.markdown(f"**Bottleneck:** {'✅ Yes' if bottleneck_data else '❌ No'}")
    with c2:
        conv_score = convergence_data.get("score", "—") if convergence_data else "—"
        prop_score = propagator_data.get("score", "—") if propagator_data else "—"
        st.markdown(f"**Convergence score:** {conv_score}")
        st.markdown(f"**Propagation score:** {prop_score}")

    if bottleneck_data:
        pct = bottleneck_data.get("percentage", 0)
        paths = bottleneck_data.get("path_count", 0)
        st.caption(f"Sits on {paths} critical path(s) ({pct:.0f}% of total paths).")

    if propagator_data:
        reached = propagator_data.get("risks_reached", 0)
        st.caption(f"Propagates influence to {reached} downstream risk(s).")


def _render_mitigation_summary(
    manager: RiskGraphManager,
    node_id: str,
    entity_type_id: Optional[str],
) -> None:
    """Section 5 — mitigation summary (risk nodes only)."""
    if entity_type_id != "risk":
        st.caption("Not applicable for this node type.")
        return

    try:
        mitigations: List[Dict] = manager.get_mitigations_for_risk(node_id)
    except Exception as e:
        st.caption(f"Could not load mitigations: {e}")
        return

    if not mitigations:
        st.caption("No mitigations linked to this risk.")
        return

    total = len(mitigations)
    st.metric("Total mitigations", total)

    # Status breakdown
    status_counts: Dict[str, int] = {}
    effectiveness_sum = 0.0
    effectiveness_count = 0
    for m in mitigations:
        status = m.get("status") or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        eff = m.get("effectiveness")
        if eff is not None:
            try:
                effectiveness_sum += float(eff)
                effectiveness_count += 1
            except (TypeError, ValueError):
                pass

    st.markdown("**Status breakdown:**")
    for status, count in sorted(status_counts.items()):
        st.caption(f"• {status}: {count}")

    if effectiveness_count:
        avg_eff = effectiveness_sum / effectiveness_count
        st.metric("Avg. effectiveness", f"{avg_eff:.0f}%")

    with st.expander("Mitigation details", expanded=False):
        for m in mitigations:
            eff_label = f" ({m['effectiveness']}%)" if m.get("effectiveness") is not None else ""
            st.caption(f"• **{m.get('name', '?')}** — {m.get('status', '?')}{eff_label}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_node_property_panel(
    manager: RiskGraphManager,
    node_id: str,
    exposure_results: Optional[Dict] = None,
    influence_results: Optional[Dict] = None,
) -> None:
    """
    Render the 6-section contextual property panel for the selected graph node.

    Args:
        manager:          Active RiskGraphManager instance.
        node_id:          UUID of the selected node.
        exposure_results: Dict from st.session_state["exposure_results"], or None.
        influence_results: Dict from st.session_state["influence_analysis_cache"], or None.
    """
    # ── Resolve node type and data ─────────────────────────────────────────
    entity_type_id = get_entity_type_id(manager, node_id)
    entity_data: Dict[str, Any] = {}
    if entity_type_id:
        try:
            entity_data = manager.get_entity_by_id(entity_type_id, node_id) or {}
        except Exception:
            entity_data = {}

    node_name = entity_data.get("name", node_id[:8] + "…") if entity_data else node_id[:8] + "…"
    st.subheader(f"Properties — {node_name}")

    # ── Build section list ─────────────────────────────────────────────────
    sections: List[Section] = [
        Section(
            id="identity",
            title="🏷️ Identity",
            render_fn=lambda: _render_identity(entity_data, entity_type_id),
        ),
        Section(
            id="exposure",
            title="📊 Exposure Metrics",
            render_fn=lambda: _render_exposure(node_id, entity_type_id, exposure_results),
        ),
        Section(
            id="position",
            title="🗺️ Graph Position",
            render_fn=lambda: _render_graph_position(manager, node_id),
        ),
        Section(
            id="influence",
            title="🔄 Influence Analysis",
            render_fn=lambda: _render_influence(node_id, influence_results),
        ),
        Section(
            id="mitigations",
            title="🛡️ Mitigation Summary",
            render_fn=lambda: _render_mitigation_summary(manager, node_id, entity_type_id),
        ),
        Section(
            id="edit",
            title="✏️ Edit",
            render_fn=lambda: render_inline_editor(manager, node_id, key_prefix="prop_panel"),
            expanded=False,
        ),
    ]

    # ── Render sections ────────────────────────────────────────────────────
    for section in sections:
        with st.expander(section.title, expanded=section.expanded):
            section.render_fn()
