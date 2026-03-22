"""
Data Management Page for RIM Application.

Provides a 4-tab unified interface for managing all nodes and edges:
- Core Nodes (Risks, Mitigations)
- Core Edges (Influences, Mitigates)
- Context Nodes (TPOs, Business Units, etc)
- Context Edges
"""

from datetime import datetime

import streamlit as st
from config import APP_TITLE, APP_ICON, LAYOUT_MODE
from ui import inject_styles
from ui.sidebar import render_filter_sidebar
from ui.home import init_session_state, render_connection_sidebar, render_welcome_page, render_complexity_toggle, render_scope_selector
from ui.tabs import render_unified_crud_tab, render_import_export_tab
from core import get_registry
from utils.state_manager import init_lifecycle_state


# ---------------------------------------------------------------------------
# Lifecycle Engine UI
# ---------------------------------------------------------------------------

def _render_lifecycle_engine_section(manager) -> None:
    """Render the on-demand Lifecycle Engine panel.

    Displays three sub-sections after a 'Run Lifecycle Check' button is pressed:
      1. Trigger review  — Watching/Suppressed risks with their trigger conditions.
      2. Auto-acceptance — Eligible vs. blocked Active risks.
      3. Archive alerts  — Accepted/Closed risks past the retention window.

    Also renders the 'Show Accepted Risks' toggle independently of the engine run.
    """
    from services.trigger_engine import TriggerEngine
    from services.auto_acceptance_engine import AutoAcceptanceEngine
    from services.archive_engine import ArchiveEngine
    from database.queries.risks import get_archive_candidates, get_all_risks

    st.markdown("---")
    with st.expander("⚙️ Lifecycle Engine", expanded=False):
        # Active scope info — read from filter_manager (same pattern as Simulation page)
        scope_node_ids = None
        fm = st.session_state.get("filter_manager")
        if fm is not None:
            scope_node_ids = fm.get_scope_node_ids()
        if scope_node_ids is not None:
            scope_names = [s.name for s in fm.active_scopes] if fm and fm.active_scopes else []
            scope_label = ", ".join(scope_names) if scope_names else "Active scope"
            st.info(
                f"📍 Scope: **{scope_label}** ({len(scope_node_ids)} nodes) — "
                "lifecycle check restricted to this scope."
            )
        else:
            st.caption("No scope active — evaluating full graph.")

        # --- Run button ---
        col_run, col_ts = st.columns([2, 3])
        with col_run:
            run_clicked = st.button("▶️ Run Lifecycle Check", key="lifecycle_run_btn")
        with col_ts:
            last_run = st.session_state.get("lifecycle_last_run")
            if last_run:
                st.caption(f"Last run: {last_run.strftime('%Y-%m-%d %H:%M')}")

        if run_clicked:
            with st.spinner("Running lifecycle check…"):
                # Load lifecycle rules from active schema
                try:
                    from config.schema_loader import SchemaRegistry
                    schema_name = st.session_state.get("active_schema_name", "default")
                    registry = SchemaRegistry()
                    schema = registry.load_schema(schema_name)
                    lifecycle_rules = schema.lifecycle_rules
                except Exception:
                    from config.schema_loader import LifecycleRulesConfig
                    lifecycle_rules = LifecycleRulesConfig()

                # Fetch all risks (include inactive for lifecycle purposes)
                conn = manager._connection
                all_risks = get_all_risks(conn, exclude_inactive=False)

                # Run engines
                trigger_result = TriggerEngine(all_risks, scope_node_ids).evaluate_all()
                acceptance_result = AutoAcceptanceEngine(
                    all_risks, lifecycle_rules, scope_node_ids
                ).evaluate_all()
                archive_candidates = get_archive_candidates(
                    conn,
                    retention_days=lifecycle_rules.archive_retention_days,
                    scope_node_ids=scope_node_ids,
                )
                archive_result = ArchiveEngine(
                    archive_candidates, lifecycle_rules, scope_node_ids
                ).generate_alerts()

                # Store in session state
                st.session_state["lifecycle_trigger_result"] = trigger_result
                st.session_state["lifecycle_acceptance_result"] = acceptance_result
                st.session_state["lifecycle_archive_alerts"] = archive_result
                st.session_state["lifecycle_last_run"] = datetime.now()

        # --- Render cached results ---
        trigger_result = st.session_state.get("lifecycle_trigger_result")
        acceptance_result = st.session_state.get("lifecycle_acceptance_result")
        archive_result = st.session_state.get("lifecycle_archive_alerts")

        if trigger_result is None and acceptance_result is None:
            st.caption("Press 'Run Lifecycle Check' to evaluate the current graph.")
            # Still show accepted risks toggle even before first run
            _render_accepted_risks_toggle(manager, scope_node_ids)
            return

        # 1. Trigger Review
        st.markdown("#### 👁️ Trigger Review")
        if trigger_result and trigger_result.evaluated_count > 0:
            st.caption(f"Evaluated {trigger_result.evaluated_count} Watching/Suppressed risk(s).")
            trigger_data = [
                {
                    "Risk": d.risk_name,
                    "Status": d.current_status,
                    "Trigger Condition": d.trigger_condition or "—",
                    "Note": d.evaluation_note,
                    "_id": d.risk_id,
                }
                for d in trigger_result.trigger_details
                if d.trigger_condition
            ]
            if trigger_data:
                for item in trigger_data:
                    with st.container():
                        st.markdown(f"**{item['Risk']}** ({item['Status']})")
                        st.markdown(f"*Condition:* {item['Trigger Condition']}")
                        if st.button(
                            "✅ Mark as Triggered → Active",
                            key=f"trigger_activate_{item['_id']}",
                        ):
                            from database.queries.risks import get_risk_by_id
                            risk = get_risk_by_id(manager._connection, item["_id"])
                            if risk:
                                from database.queries.risks import update_risk
                                update_risk(
                                    manager._connection,
                                    risk_id=item["_id"],
                                    name=risk.get("name", ""),
                                    level=risk.get("level", "Business"),
                                    categories=risk.get("categories", []),
                                    description=risk.get("description", ""),
                                    status="Active",
                                    origin=risk.get("origin", "New"),
                                    owner=risk.get("owner", ""),
                                    probability=risk.get("probability"),
                                    severity=risk.get("severity"),
                                )
                                st.success(f"'{item['Risk']}' transitioned to Active.")
                                st.rerun()
            else:
                st.info("No Watching/Suppressed risks have a trigger condition defined.")
        else:
            st.info("No Watching or Suppressed risks found.")

        st.markdown("---")

        # 2. Auto-Acceptance
        st.markdown("#### ✔️ Auto-Acceptance")
        if acceptance_result:
            col_e, col_b = st.columns(2)
            with col_e:
                st.markdown(f"**Eligible** ({len(acceptance_result.eligible)})")
                for c in acceptance_result.eligible:
                    st.markdown(
                        f"• **{c.risk_name}** — EL {c.final_exposure:.1f}, "
                        f"S {c.severity:.1f}, quadrant: {c.quadrant}"
                    )
                if acceptance_result.eligible:
                    selected_ids = [c.risk_id for c in acceptance_result.eligible]
                    if st.button(
                        f"Accept All Eligible ({len(selected_ids)})",
                        key="accept_all_eligible",
                    ):
                        today_iso = datetime.now().date().isoformat()
                        for risk_id in selected_ids:
                            from database.queries.risks import get_risk_by_id, update_risk
                            risk = get_risk_by_id(manager._connection, risk_id)
                            if risk:
                                update_risk(
                                    manager._connection,
                                    risk_id=risk_id,
                                    name=risk.get("name", ""),
                                    level=risk.get("level", "Business"),
                                    categories=risk.get("categories", []),
                                    description=risk.get("description", ""),
                                    status="Accepted",
                                    origin=risk.get("origin", "New"),
                                    owner=risk.get("owner", ""),
                                    probability=risk.get("probability"),
                                    severity=risk.get("severity"),
                                    acceptance_date=today_iso,
                                )
                        st.success(f"Accepted {len(selected_ids)} risk(s).")
                        st.rerun()
            with col_b:
                st.markdown(f"**Blocked** ({len(acceptance_result.blocked)})")
                st.caption("These risks exceed one or more auto-acceptance guards. "
                           "A human reviewer can override and accept them individually.")
                for c in acceptance_result.blocked:
                    with st.container():
                        st.markdown(f"**{c.risk_name}**")
                        st.caption(f"🚫 {c.blocked_reason}")
                        if st.button(
                            "🔓 Force Accept",
                            key=f"force_accept_{c.risk_id}",
                            help="Override auto-acceptance guards and accept this risk manually.",
                        ):
                            today_iso = datetime.now().date().isoformat()
                            from database.queries.risks import get_risk_by_id, update_risk
                            risk = get_risk_by_id(manager._connection, c.risk_id)
                            if risk:
                                update_risk(
                                    manager._connection,
                                    risk_id=c.risk_id,
                                    name=risk.get("name", ""),
                                    level=risk.get("level", "Business"),
                                    categories=risk.get("categories", []),
                                    description=risk.get("description", ""),
                                    status="Accepted",
                                    origin=risk.get("origin", "New"),
                                    owner=risk.get("owner", ""),
                                    probability=risk.get("probability"),
                                    severity=risk.get("severity"),
                                    acceptance_date=today_iso,
                                )
                                st.success(f"'{c.risk_name}' accepted (manual override).")
                                st.rerun()
        else:
            st.info("No acceptance evaluation results available.")

        st.markdown("---")

        # 3. Archive Alerts
        st.markdown("#### 📦 Archive Alerts")
        if archive_result and archive_result.alert_count > 0:
            st.warning(
                f"{archive_result.alert_count} risk(s) past the "
                f"{archive_result.alerts[0].retention_threshold}-day retention window."
            )
            for alert in archive_result.alerts:
                with st.container():
                    st.markdown(f"**{alert.risk_name}** — {alert.current_status} "
                                f"({alert.days_since_acceptance} days)")
                    st.caption(alert.message)
                    if st.button(
                        "📦 Archive Now",
                        key=f"archive_{alert.risk_id}",
                    ):
                        today_iso = datetime.now().date().isoformat()
                        from database.queries.risks import get_risk_by_id, update_risk
                        risk = get_risk_by_id(manager._connection, alert.risk_id)
                        if risk:
                            update_risk(
                                manager._connection,
                                risk_id=alert.risk_id,
                                name=risk.get("name", ""),
                                level=risk.get("level", "Business"),
                                categories=risk.get("categories", []),
                                description=risk.get("description", ""),
                                status="Archived",
                                origin=risk.get("origin", "New"),
                                owner=risk.get("owner", ""),
                                probability=risk.get("probability"),
                                severity=risk.get("severity"),
                                archive_date=today_iso,
                            )
                        st.success(f"'{alert.risk_name}' archived.")
                        st.rerun()
        else:
            st.success("No risks require archiving at this time.")

        st.markdown("---")

        # 4. Accepted Risks toggle (always shown)
        _render_accepted_risks_toggle(manager, scope_node_ids)


def _render_accepted_risks_toggle(manager, scope_node_ids) -> None:
    """Render 'Show Accepted Risks' review table."""
    from database.queries.risks import get_all_risks

    show = st.toggle(
        "Show Accepted Risks",
        value=st.session_state.get("show_accepted_risks", False),
        key="show_accepted_risks_toggle",
    )
    st.session_state["show_accepted_risks"] = show

    if not show:
        return

    conn = manager._connection
    all_risks = get_all_risks(conn, exclude_inactive=False)
    accepted = [
        r for r in all_risks
        if r.get("status") == "Accepted"
        and (scope_node_ids is None or r.get("id") in scope_node_ids)
    ]

    if not accepted:
        st.info("No Accepted risks found.")
        return

    st.markdown(f"**{len(accepted)} Accepted risk(s)**")
    for r in accepted:
        with st.container():
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.markdown(f"**{r.get('name', '')}** ({r.get('level', '')})")
                st.caption(
                    f"Accepted: {r.get('acceptance_date') or '—'}  |  "
                    f"Owner: {r.get('acceptance_owner') or '—'}  |  "
                    f"EL: {r.get('exposure') or '—'}"
                )
            with cols[1]:
                if st.button("♻️ Re-open", key=f"reopen_{r['id']}"):
                    from database.queries.risks import get_risk_by_id, update_risk
                    risk = get_risk_by_id(conn, r["id"])
                    if risk:
                        update_risk(
                            conn,
                            risk_id=r["id"],
                            name=risk.get("name", ""),
                            level=risk.get("level", "Business"),
                            categories=risk.get("categories", []),
                            description=risk.get("description", ""),
                            status="Active",
                            origin=risk.get("origin", "New"),
                            owner=risk.get("owner", ""),
                            probability=risk.get("probability"),
                            severity=risk.get("severity"),
                        )
                    st.success(f"'{r.get('name')}' re-opened as Active.")
                    st.rerun()
            with cols[2]:
                if st.button("📦 Archive", key=f"archive_acc_{r['id']}"):
                    today_iso = datetime.now().date().isoformat()
                    from database.queries.risks import get_risk_by_id, update_risk
                    risk = get_risk_by_id(conn, r["id"])
                    if risk:
                        update_risk(
                            conn,
                            risk_id=r["id"],
                            name=risk.get("name", ""),
                            level=risk.get("level", "Business"),
                            categories=risk.get("categories", []),
                            description=risk.get("description", ""),
                            status="Archived",
                            origin=risk.get("origin", "New"),
                            owner=risk.get("owner", ""),
                            probability=risk.get("probability"),
                            severity=risk.get("severity"),
                            archive_date=today_iso,
                        )
                    st.success(f"'{r.get('name')}' archived.")
                    st.rerun()


def render_data_management_page():
    """Render the dedicated Data Management page."""
    # Check connection
    if not st.session_state.connected:
        st.warning("Please connect to the database on the Home page first.")
        return
        
    manager = st.session_state.manager
    registry = get_registry()
    
    st.title("💾 Data Management")
    st.markdown("Easily adapt and modify the structural objects powering the Risk Graph visualization and Exposure Engine calculation.")
    
    # ── Sidebar Configuration ───────────────────────────────────────────────
    render_complexity_toggle()
    render_scope_selector()
    
    # Render unified attribute filters (so we can filter the list in the CRUD tabs)
    render_filter_sidebar(st.session_state.filter_manager)
    
    # ── 4 Tabs Configuration ────────────────────────────────────────────────
    tab_names = [
        "🔵 Core Nodes", 
        "🔗 Core Edges", 
        "🟡 Context Nodes", 
        "🔗 Context Edges",
        "📥 Import / Export"
    ]
    
    tabs = st.tabs(tab_names)
    
    # 1. Core Nodes
    with tabs[0]:
        st.markdown("Manage hardcoded algorithmic objects required by the Exposure Engine.")
        core_node_subtabs = st.tabs(["🔥 Risks", "🛡️ Mitigations"])
        
        with core_node_subtabs[0]:
            render_unified_crud_tab(manager, registry.get_entity_type("risk"))
            
        with core_node_subtabs[1]:
            render_unified_crud_tab(manager, registry.get_entity_type("mitigation"))
            
    # 2. Core Edges
    with tabs[1]:
        st.markdown("Manage mathematical relationships used for propagation calculations.")
        core_edge_subtabs = st.tabs(["➡️ Influences", "🛡️ Mitigates"])
        
        with core_edge_subtabs[0]:
            render_unified_crud_tab(manager, registry.get_relationship_type("influences"))
            
        with core_edge_subtabs[1]:
            render_unified_crud_tab(manager, registry.get_relationship_type("mitigates"))
            
    # 3. Context Nodes
    with tabs[2]:
        st.markdown("Manage schema-driven organizational elements.")
        
        # Filter for custom context nodes
        context_node_defs = [
            d for d in registry.entity_types.values() 
            if d.id not in ("risk", "mitigation")
        ]
        
        if not context_node_defs:
            st.info("No custom Context Nodes defined in schema.yaml.")
        else:
            cn_tabs = st.tabs([f"{d.emoji or '📦'} {d.label}s" for d in context_node_defs])
            for i, d in enumerate(context_node_defs):
                with cn_tabs[i]:
                    render_unified_crud_tab(manager, d)
                    
    # 4. Context Edges
    with tabs[3]:
        st.markdown("Manage custom organizational links.")
        
        # Filter for custom context edges
        context_edge_defs = [
            d for d in registry.relationship_types.values() 
            if d.id not in ("influences", "mitigates")
        ]
        
        if not context_edge_defs:
            st.info("No custom Context Edges defined in schema.yaml.")
        else:
            ce_tabs = st.tabs([f"🔗 {d.label}" for d in context_edge_defs])
            for i, d in enumerate(context_edge_defs):
                with ce_tabs[i]:
                    render_unified_crud_tab(manager, d)
                    
    # 5. Import / Export
    with tabs[4]:
        st.markdown("Bulk manage graph definitions via Excel or JSON backup.")
        render_import_export_tab(
            export_fn=manager.export_to_excel,
            import_fn=manager.import_from_excel,
            export_bytes_fn=manager.export_to_excel_bytes,
            export_json_fn=manager.export_to_json,
            import_json_fn=manager.import_from_json,
        )

    # ── Lifecycle Engine (below tabs) ──────────────────────────────────────
    _render_lifecycle_engine_section(manager)


def main():
    """Page execution."""
    # Page configuration
    st.set_page_config(
        page_title=f"{APP_TITLE} - Data",
        page_icon="💾",
        layout=LAYOUT_MODE,
        initial_sidebar_state="expanded"
    )
    
    inject_styles()
    init_session_state()
    init_lifecycle_state()
    render_connection_sidebar()
    
    if not st.session_state.connected:
        render_welcome_page()
    else:
        render_data_management_page()

if __name__ == "__main__":
    main()
