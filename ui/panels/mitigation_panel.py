"""
Mitigation Analysis Panel for RIM Application.

Renders the mitigation analysis panel with:
- Mode 1: Risk Treatment Explorer (Risk-centric view)
- Mode 2: Mitigation Impact Explorer (Mitigation-centric view)
- Mode 3: Coverage Gap Analysis (Transverse view)
"""

from typing import Dict, Any, Optional, Callable, List
import time


def render_mitigation_analysis_panel(
    analysis_data: Optional[Dict[str, Any]] = None,
    coverage_gaps: Optional[Dict[str, Any]] = None,
    get_analysis_fn: Optional[Callable] = None,
    get_coverage_gaps_fn: Optional[Callable] = None,
    get_all_risks_fn: Optional[Callable] = None,
    get_all_mitigations_fn: Optional[Callable] = None,
    get_risk_details_fn: Optional[Callable[[str], Dict]] = None,
    get_mitigation_details_fn: Optional[Callable[[str], Dict]] = None,
    get_mitigation_by_id_fn: Optional[Callable[[str], Dict]] = None,
    get_risks_for_mitigation_fn: Optional[Callable[[str], List]] = None,
    on_node_select: Optional[Callable[[str, str], None]] = None,
    cache_timeout: int = 30
):
    """
    Render the mitigation analysis panel.
    
    Args:
        analysis_data: Pre-computed mitigation analysis data
        coverage_gaps: Pre-computed coverage gap data
        get_analysis_fn: Function to get analysis data
        get_coverage_gaps_fn: Function to get coverage gap data
        get_all_risks_fn: Function to get all risks
        get_all_mitigations_fn: Function to get all mitigations
        get_risk_details_fn: Function to get risk mitigation details
        get_mitigation_details_fn: Function to get mitigation impact details
        get_mitigation_by_id_fn: Function to get mitigation by ID
        get_risks_for_mitigation_fn: Function to get risks for a mitigation
        on_node_select: Callback when user selects a node to explore
        cache_timeout: Seconds before cache expires
    """
    import streamlit as st
    
    # Initialize cache
    if "mitigation_analysis_cache" not in st.session_state:
        st.session_state.mitigation_analysis_cache = None
        st.session_state.mitigation_analysis_timestamp = None
    
    # Check cache validity
    current_time = time.time()
    cache_valid = (
        st.session_state.mitigation_analysis_cache is not None and
        st.session_state.mitigation_analysis_timestamp is not None and
        (current_time - st.session_state.mitigation_analysis_timestamp) < cache_timeout
    )
    
    with st.expander("🛡️ Mitigation Analysis", expanded=False):
        # Refresh button
        col_refresh, col_spacer = st.columns([1, 4])
        with col_refresh:
            if st.button("🔄 Refresh", key="refresh_mitigation_analysis", use_container_width=True):
                st.session_state.mitigation_analysis_cache = None
                cache_valid = False
        
        # Get or compute analysis
        analysis = analysis_data
        
        if analysis is None:
            if not cache_valid and get_analysis_fn:
                with st.spinner("Analyzing mitigation coverage..."):
                    try:
                        analysis = get_analysis_fn()
                        st.session_state.mitigation_analysis_cache = analysis
                        st.session_state.mitigation_analysis_timestamp = current_time
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
                        return
            else:
                analysis = st.session_state.mitigation_analysis_cache
        
        if not analysis:
            st.info("No data available for analysis. Create some risks and mitigations first.")
            return
        
        # Coverage overview metrics
        _render_coverage_metrics(analysis.get("coverage_stats", {}))
        
        st.markdown("---")
        
        # Analysis mode selection
        analysis_mode = st.radio(
            "Analysis Mode",
            ["risk_treatment", "mitigation_impact", "coverage_gaps"],
            format_func=lambda x: {
                "risk_treatment": "🎯 Risk Treatment",
                "mitigation_impact": "🛡️ Mitigation Impact",
                "coverage_gaps": "📊 Coverage Gaps"
            }.get(x, x),
            horizontal=True,
            key="mitigation_analysis_mode"
        )
        
        st.markdown("---")
        
        # Render selected mode
        if analysis_mode == "risk_treatment":
            _render_risk_treatment_mode(
                analysis,
                get_all_risks_fn,
                get_risk_details_fn,
                get_mitigation_by_id_fn,
                on_node_select
            )
        
        elif analysis_mode == "mitigation_impact":
            _render_mitigation_impact_mode(
                get_all_mitigations_fn,
                get_mitigation_details_fn,
                get_risks_for_mitigation_fn
            )
        
        elif analysis_mode == "coverage_gaps":
            gaps = coverage_gaps
            if gaps is None and get_coverage_gaps_fn:
                try:
                    gaps = get_coverage_gaps_fn()
                except Exception as e:
                    st.error(f"Error analyzing coverage gaps: {e}")
                    return
            
            if gaps:
                _render_coverage_gaps_mode(gaps, on_node_select)
            else:
                st.info("No coverage gap data available.")


def _render_coverage_metrics(stats: Dict[str, Any]):
    """Render coverage overview metrics."""
    import streamlit as st
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Risks", stats.get("total_risks", 0))
    with col2:
        coverage_pct = stats.get("coverage_percentage", 0)
        st.metric("Coverage", f"{coverage_pct}%")
    with col3:
        st.metric("Mitigated", stats.get("mitigated_risks", 0))
    with col4:
        unmitigated = stats.get("unmitigated_risks", 0)
        st.metric("⚠️ Unmitigated", unmitigated)


def _render_risk_treatment_mode(
    analysis: Dict[str, Any],
    get_all_risks_fn: Optional[Callable],
    get_risk_details_fn: Optional[Callable],
    get_mitigation_by_id_fn: Optional[Callable],
    on_node_select: Optional[Callable]
):
    """Render the Risk Treatment Explorer mode."""
    import streamlit as st
    
    st.markdown("**Select a risk to see its mitigation coverage**")
    
    # Get all risks
    if not get_all_risks_fn:
        st.warning("Risk data not available.")
        return
    
    all_risks = get_all_risks_fn()
    if not all_risks:
        st.info("No risks available.")
        return
    
    # Create risk options with status indicators
    risk_options = {}
    risk_summary = {rs["id"]: rs for rs in analysis.get("risk_mitigation_summary", [])}
    
    for r in all_risks:
        risk_id = r["id"]
        summary = risk_summary.get(risk_id, {})
        mit_count = summary.get("mitigation_count", 0)
        impl_count = summary.get("implemented_count", 0)
        
        # Status emoji
        if mit_count == 0:
            status_emoji = "⚠️"
        elif impl_count == 0:
            status_emoji = "📋"
        elif impl_count >= 2:
            status_emoji = "✅"
        else:
            status_emoji = "🔶"
        
        level_icon = "🟣" if r["level"] == "Business" else "🔵"
        label = f"{status_emoji} {level_icon} {r['name']} ({mit_count} mitigations)"
        risk_options[label] = risk_id
    
    selected_label = st.selectbox(
        "Select Risk",
        options=list(risk_options.keys()),
        key="risk_treatment_selector"
    )
    
    if selected_label and get_risk_details_fn:
        selected_risk_id = risk_options[selected_label]
        details = get_risk_details_fn(selected_risk_id)
        
        if details:
            _render_risk_treatment_details(
                details,
                get_mitigation_by_id_fn,
                on_node_select
            )


def _render_risk_treatment_details(
    details: Dict[str, Any],
    get_mitigation_by_id_fn: Optional[Callable],
    on_node_select: Optional[Callable]
):
    """Render details for a selected risk in treatment mode."""
    import streamlit as st
    
    risk_data = details.get("risk", {})
    mits = details.get("mitigations", [])
    coverage_status = details.get("coverage_status", "unknown")
    influence_info = details.get("influence_info", {})
    
    # Coverage status badge
    status_badges = {
        "unmitigated": ("⚠️ No Mitigations", "error"),
        "proposed_only": ("📋 Only Proposed", "warning"),
        "partially_covered": ("🔶 Partially Covered", "info"),
        "well_covered": ("✅ Well Covered", "success")
    }
    badge_text, badge_type = status_badges.get(coverage_status, ("Unknown", "info"))
    
    # Display risk info
    col_risk1, col_risk2 = st.columns([2, 1])
    with col_risk1:
        st.markdown(f"**Risk:** {risk_data.get('name', 'Unknown')}")
        st.caption(f"Level: {risk_data.get('level', 'N/A')} | Exposure: {risk_data.get('exposure', 'N/A')}")
    with col_risk2:
        if badge_type == "error":
            st.error(badge_text)
        elif badge_type == "warning":
            st.warning(badge_text)
        elif badge_type == "success":
            st.success(badge_text)
        else:
            st.info(badge_text)
    
    # Show influence flags if any
    if influence_info:
        flags = []
        if influence_info.get("is_top_propagator"):
            flags.append(f"🎯 Top Propagator (Score: {influence_info.get('propagation_score', 'N/A')})")
        if influence_info.get("is_convergence_point"):
            flags.append(f"⚡ Convergence Point (Score: {influence_info.get('convergence_score', 'N/A')})")
        if influence_info.get("is_bottleneck"):
            flags.append(f"🚧 Bottleneck ({influence_info.get('path_percentage', 'N/A')}% of paths)")
        
        if flags:
            st.markdown("**📊 Influence Analysis Flags:**")
            for flag in flags:
                st.caption(flag)
    
    st.markdown("---")
    
    # List mitigations
    if mits:
        st.markdown(f"**Mitigations ({len(mits)}):**")
        for mit in mits:
            # Get full mitigation details if function available
            mit_detail = {}
            if get_mitigation_by_id_fn:
                mit_detail = get_mitigation_by_id_fn(mit.get("mitigation_id", mit.get("id", ""))) or {}
            
            status = mit_detail.get("status", mit.get("status", "Unknown"))
            mit_type = mit_detail.get("type", mit.get("mitigation_type", "Unknown"))
            effectiveness = mit.get("effectiveness", "Medium")
            
            # Status icon
            status_icons = {
                "Implemented": "🟢",
                "In Progress": "🟡",
                "Proposed": "📋",
                "Deferred": "⏸️"
            }
            status_icon = status_icons.get(status, "⚪")
            
            # Effectiveness icon
            eff_icons = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢"
            }
            eff_icon = eff_icons.get(effectiveness, "⚪")
            
            mit_name = mit.get("mitigation_name", mit.get("name", "Unknown"))
            st.markdown(f"- {status_icon} **{mit_name}** ({mit_type})")
            st.caption(f"  Status: {status} | Effectiveness: {eff_icon} {effectiveness}")
            
            if mit.get("description"):
                st.caption(f"  _{mit['description']}_")
    else:
        st.warning("⚠️ This risk has no mitigations assigned.")
        st.caption("💡 Consider adding mitigations via the 💊 Risk Mitigations tab.")
    
    # Button to visualize in graph
    if on_node_select:
        if st.button("🔍 Visualize in Graph", key="viz_risk_treatment", use_container_width=True):
            st.session_state.pending_explore_node = {
                "node_id": risk_data.get("id"),
                "direction": "both"
            }
            st.rerun()


def _render_mitigation_impact_mode(
    get_all_mitigations_fn: Optional[Callable],
    get_mitigation_details_fn: Optional[Callable],
    get_risks_for_mitigation_fn: Optional[Callable]
):
    """Render the Mitigation Impact Explorer mode."""
    import streamlit as st
    
    st.markdown("**Select a mitigation to see all risks it addresses**")
    
    if not get_all_mitigations_fn:
        st.warning("Mitigation data not available.")
        return
    
    all_mitigations = get_all_mitigations_fn()
    if not all_mitigations:
        st.info("No mitigations available.")
        return
    
    # Create mitigation options
    mit_options = {}
    for m in all_mitigations:
        risk_count = 0
        if get_risks_for_mitigation_fn:
            risks = get_risks_for_mitigation_fn(m["id"])
            risk_count = len(risks) if risks else 0
        
        type_icons = {
            "Dedicated": "🟢",
            "Inherited": "🔵",
            "Baseline": "🟣"
        }
        type_icon = type_icons.get(m.get("type", "Dedicated"), "⚪")
        
        status_icons = {
            "Implemented": "✅",
            "In Progress": "🔄",
            "Proposed": "📋",
            "Deferred": "⏸️"
        }
        status_icon = status_icons.get(m.get("status", "Proposed"), "⚪")
        
        label = f"{status_icon} {type_icon} {m['name']} ({risk_count} risks)"
        mit_options[label] = m["id"]
    
    selected_label = st.selectbox(
        "Select Mitigation",
        options=list(mit_options.keys()),
        key="mitigation_impact_selector"
    )
    
    if selected_label and get_mitigation_details_fn:
        selected_mit_id = mit_options[selected_label]
        details = get_mitigation_details_fn(selected_mit_id)
        
        if details:
            _render_mitigation_impact_details(details)


def _render_mitigation_impact_details(details: Dict[str, Any]):
    """Render details for a selected mitigation in impact mode."""
    import streamlit as st
    
    mit_data = details.get("mitigation", {})
    risks = details.get("risks", [])
    business_impacts = details.get("business_impacts", [])
    
    # Display mitigation info
    col_mit1, col_mit2 = st.columns([2, 1])
    with col_mit1:
        st.markdown(f"**Mitigation:** {mit_data.get('name', 'Unknown')}")
        st.caption(f"Type: {mit_data.get('type', 'N/A')} | Status: {mit_data.get('status', 'N/A')}")
        if mit_data.get("owner"):
            st.caption(f"Owner: {mit_data['owner']}")
    with col_mit2:
        st.metric("Risks Addressed", details.get("risk_count", 0))
        if details.get("total_exposure_covered", 0) > 0:
            st.metric("Total Exposure Covered", f"{details['total_exposure_covered']:.1f}")
    
    # Show strategic impact if any
    if business_impacts:
        st.markdown("**🎯 Business Impact:**")
        for impact in business_impacts:
            flags_str = ", ".join(impact.get("flags", []))
            st.caption(f"  • {impact.get('risk_name', 'Unknown')} - {flags_str}")
    
    st.markdown("---")
    
    # List addressed risks
    if risks:
        st.markdown(f"**Risks Addressed ({len(risks)}):**")
        
        col_strat, col_op = st.columns(2)
        with col_strat:
            st.markdown(f"🟣 **Strategic:** {details.get('business_count', 0)}")
        with col_op:
            st.markdown(f"🔵 **Operational:** {details.get('operational_count', 0)}")
        
        for risk in risks:
            level_icon = "🟣" if risk.get("level") == "Business" else "🔵"
            effectiveness = risk.get("effectiveness", "Medium")
            exposure = risk.get("exposure", 0) or 0
            
            # Effectiveness icon
            eff_icons = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢"
            }
            eff_icon = eff_icons.get(effectiveness, "⚪")
            
            # Check if high-priority
            is_high_priority = any(
                si.get("risk_id") == risk.get("id")
                for si in business_impacts
            )
            priority_badge = " ⭐" if is_high_priority else ""
            
            st.markdown(f"- {level_icon} **{risk.get('name', 'Unknown')}**{priority_badge}")
            st.caption(f"  Effectiveness: {eff_icon} {effectiveness} | Exposure: {exposure:.1f}")
    else:
        st.info("This mitigation is not linked to any risks yet.")


def _render_coverage_gaps_mode(
    gaps: Dict[str, Any],
    on_node_select: Optional[Callable]
):
    """Render the Coverage Gap Analysis mode."""
    import streamlit as st
    
    st.markdown("**Identify gaps in your mitigation strategy**")
    
    # Create sub-tabs for different gap views
    gap_tabs = st.tabs([
        "🚨 High Priority",
        "⚠️ Unmitigated",
        "📋 Proposed Only",
        "🟣 Business Gaps",
        "📊 By Category"
    ])
    
    # Tab 1: High Priority Unmitigated
    with gap_tabs[0]:
        _render_high_priority_gaps(gaps.get("high_priority_unmitigated", []), on_node_select)
    
    # Tab 2: Critical Unmitigated
    with gap_tabs[1]:
        _render_critical_unmitigated(gaps.get("critical_unmitigated", []), on_node_select)
    
    # Tab 3: Proposed Only
    with gap_tabs[2]:
        _render_proposed_only_gaps(gaps.get("proposed_only_high_exposure", []), on_node_select)
    
    # Tab 4: Business Gaps
    with gap_tabs[3]:
        _render_business_gaps(gaps.get("business_gaps", []), on_node_select)
    
    # Tab 5: Category Coverage
    with gap_tabs[4]:
        _render_category_coverage(gaps.get("category_coverage", {}))


def _render_high_priority_gaps(
    high_priority: List[Dict[str, Any]],
    on_node_select: Optional[Callable],
    limit: int = 5
):
    """Render high priority unmitigated risks."""
    import streamlit as st
    
    st.markdown("**Unmitigated risks that are Top Propagators, Convergence Points, or Bottlenecks**")
    
    if not high_priority:
        st.success("✅ All high-priority risks have mitigations!")
        return
    
    for risk in high_priority[:limit]:
        level_icon = "🟣" if risk.get("level") == "Business" else "🔵"
        flags = risk.get("influence_flags", [])
        flags_str = " | ".join(f"⚡ {f}" for f in flags)
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{level_icon} {risk.get('name', 'Unknown')}**")
            st.caption(f"Exposure: {risk.get('exposure', 0):.1f} | {flags_str}")
        with col_btn:
            if st.button("🔍", key=f"gap_high_{risk.get('id')}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": risk["id"],
                    "direction": "both"
                }
                st.rerun()


def _render_critical_unmitigated(
    critical: List[Dict[str, Any]],
    on_node_select: Optional[Callable],
    limit: int = 5
):
    """Render critical unmitigated risks (high exposure)."""
    import streamlit as st
    
    st.markdown("**Risks with high exposure and no mitigations**")
    
    if not critical:
        st.success("✅ No high-exposure unmitigated risks!")
        return
    
    for risk in critical[:limit]:
        level_icon = "🟣" if risk.get("level") == "Business" else "🔵"
        exposure = risk.get("exposure", 0)
        categories = risk.get("categories", [])
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{level_icon} {risk.get('name', 'Unknown')}**")
            st.caption(f"Exposure: **{exposure:.1f}** | Categories: {', '.join(categories)}")
        with col_btn:
            if st.button("🔍", key=f"gap_crit_{risk.get('id')}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": risk["id"],
                    "direction": "both"
                }
                st.rerun()


def _render_proposed_only_gaps(
    proposed_only: List[Dict[str, Any]],
    on_node_select: Optional[Callable],
    limit: int = 5
):
    """Render high-exposure risks with only proposed mitigations."""
    import streamlit as st
    
    st.markdown("**High-exposure risks with only proposed (not implemented) mitigations**")
    
    if not proposed_only:
        st.success("✅ All high-exposure risks have implemented mitigations!")
        return
    
    for risk in proposed_only[:limit]:
        level_icon = "🟣" if risk.get("level") == "Business" else "🔵"
        exposure = risk.get("exposure", 0)
        proposed_mits = risk.get("proposed_mitigations", [])
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**{level_icon} {risk.get('name', 'Unknown')}**")
            st.caption(f"Exposure: **{exposure:.1f}** | Proposed: {', '.join(proposed_mits[:3])}")
        with col_btn:
            if st.button("🔍", key=f"gap_prop_{risk.get('id')}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": risk["id"],
                    "direction": "both"
                }
                st.rerun()


def _render_business_gaps(
    business_gaps: List[Dict[str, Any]],
    on_node_select: Optional[Callable],
    limit: int = 5
):
    """Render business risks without adequate mitigation."""
    import streamlit as st
    
    st.markdown("**Business risks without adequate mitigation coverage**")
    
    if not business_gaps:
        st.success("✅ All business risks are well covered!")
        return
    
    for risk in business_gaps[:limit]:
        exposure = risk.get("exposure", 0)
        impl_eff = risk.get("implemented_effectiveness", 0)
        
        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"**🟣 {risk.get('name', 'Unknown')}**")
            if impl_eff > 0:
                st.caption(f"Exposure: {exposure:.1f} | Implemented effectiveness: {impl_eff}/4+")
            else:
                st.caption(f"Exposure: {exposure:.1f} | ⚠️ No implemented mitigations")
        with col_btn:
            if st.button("🔍", key=f"gap_strat_{risk.get('id')}", help="Explore in graph"):
                st.session_state.pending_explore_node = {
                    "node_id": risk["id"],
                    "direction": "both"
                }
                st.rerun()


def _render_category_coverage(category_coverage: Dict[str, Dict[str, Any]]):
    """Render category coverage breakdown."""
    import streamlit as st
    
    st.markdown("**Mitigation coverage breakdown by risk category**")
    
    if not category_coverage:
        st.info("No category coverage data available.")
        return
    
    for cat, cov_stats in category_coverage.items():
        coverage_pct = cov_stats.get("coverage_percentage", 0)
        total = cov_stats.get("total", 0)
        mitigated = cov_stats.get("mitigated", 0)
        unmitigated = cov_stats.get("unmitigated", 0)
        
        # Status emoji based on coverage
        if coverage_pct >= 80:
            status_emoji = "✅"
        elif coverage_pct >= 50:
            status_emoji = "🔶"
        else:
            status_emoji = "⚠️"
        
        st.markdown(f"**{cat}** {status_emoji}")
        col_prog, col_stats = st.columns([3, 1])
        with col_prog:
            st.progress(coverage_pct / 100)
        with col_stats:
            st.caption(f"{coverage_pct}% ({mitigated}/{total})")
        
        if unmitigated > 0:
            st.caption(f"  ⚠️ {unmitigated} risks without mitigations")
        st.markdown("---")
