"""
Graph Visual Behaviour Panel (F32).

Consolidated visual settings panel for the RIM graph canvas.
Supersedes the scatter-shot F20/F21 toggles that lived in the Display Options
expander inside ui/home.py.

Features
--------
- Four named presets: Clean / Analysis / Lifecycle Audit / Sandbox Edit
- Exposure-Driven Opacity (F20 — moved here)
- Lifecycle Opacity per status (F21 upgraded — granular per-status sliders)
- Quadrant Border Encoding (new — uses risk_quadrant field from U13)
- Save as Schema Default — persists current settings to schema.yaml
"""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st


# ---------------------------------------------------------------------------
# Preset definitions
# ---------------------------------------------------------------------------

_PRESETS: Dict[str, Dict[str, Any]] = {
    "clean": {
        "label": "Clean",
        "icon": "✨",
        "help": "No opacity effects or border encoding — pure topology view.",
        "vp_exposure_opacity": False,
        "vp_lifecycle_opacity_enabled": False,
        "vp_quadrant_borders": False,
    },
    "analysis": {
        "label": "Analysis",
        "icon": "🔬",
        "help": "Exposure opacity + quadrant border encoding for risk deep-dive.",
        "vp_exposure_opacity": True,
        "vp_lifecycle_opacity_enabled": False,
        "vp_quadrant_borders": True,
    },
    "lifecycle": {
        "label": "Lifecycle Audit",
        "icon": "🔄",
        "help": "Per-status opacity highlights lifecycle state across the canvas.",
        "vp_exposure_opacity": False,
        "vp_lifecycle_opacity_enabled": True,
        "vp_quadrant_borders": True,
    },
    "sandbox": {
        "label": "Sandbox Edit",
        "icon": "🏖️",
        "help": "Minimal effects; sandbox dimming (F29) handles scope context.",
        "vp_exposure_opacity": False,
        "vp_lifecycle_opacity_enabled": True,
        "vp_quadrant_borders": False,
    },
}

_PRESET_ORDER = ["clean", "analysis", "lifecycle", "sandbox"]


def _apply_preset(preset_id: str) -> None:
    """Write preset defaults into session state."""
    if preset_id not in _PRESETS:
        return
    preset = _PRESETS[preset_id]
    st.session_state["vp_preset"] = preset_id
    for key in ("vp_exposure_opacity", "vp_lifecycle_opacity_enabled", "vp_quadrant_borders"):
        st.session_state[key] = preset[key]


def _save_visual_config_to_schema(schema_config: Any, db_manager: Any) -> None:
    """Persist current vp_* session state into the active schema YAML."""
    try:
        from config.schema_loader import get_loader

        # Update the in-memory schema object
        gvc = schema_config.graph_visual_config
        gvc.lifecycle_opacity = dict(
            st.session_state.get("vp_lifecycle_opacity", gvc.lifecycle_opacity)
        )
        gvc.quadrant_border_encoding = st.session_state.get(
            "vp_quadrant_borders", gvc.quadrant_border_encoding
        )
        gvc.default_preset = st.session_state.get("vp_preset", gvc.default_preset)

        # Identify which schema is active
        active_schema_name = st.session_state.get("active_schema_name", "default")
        get_loader().save_schema(schema_config, active_schema_name)
        st.success("Visual settings saved as schema default.")
    except Exception as exc:  # pragma: no cover
        st.error(f"Failed to save visual settings: {exc}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_graph_visual_panel(schema_config: Any = None, db_manager: Any = None) -> None:
    """Render the consolidated Graph Visual Behaviour panel.

    Designed to be called from the sidebar (or any panel column).

    Parameters
    ----------
    schema_config:
        The active ``SchemaConfig`` instance — used by the Save button to
        persist settings.  Pass ``None`` to disable the save button.
    db_manager:
        Reserved for future schema-write flows; currently unused.
    """
    st.markdown("#### 🖼️ Graph Visual Behaviour")

    # ── Preset row ──────────────────────────────────────────────────────────
    active_preset = st.session_state.get("vp_preset", "analysis")
    cols = st.columns(len(_PRESET_ORDER))
    for col, pid in zip(cols, _PRESET_ORDER):
        p = _PRESETS[pid]
        is_active = active_preset == pid
        label = f"**{p['icon']} {p['label']}**" if is_active else f"{p['icon']} {p['label']}"
        if col.button(
            label,
            key=f"vp_preset_btn_{pid}",
            help=p["help"],
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            _apply_preset(pid)
            st.rerun()

    st.divider()

    # ── Exposure-Driven Opacity (F20) ────────────────────────────────────
    with st.expander("🌫️ Exposure Opacity", expanded=False):
        exposure_opacity = st.toggle(
            "Enable Exposure Opacity",
            value=st.session_state.get("vp_exposure_opacity", False),
            key="vp_exposure_opacity_toggle",
            help="High-exposure risks stay solid; low-exposure risks fade.",
        )
        st.session_state["vp_exposure_opacity"] = exposure_opacity

        if exposure_opacity:
            threshold = st.slider(
                "High Exposure Threshold",
                min_value=10,
                max_value=100,
                value=int(st.session_state.get("vp_exposure_threshold", 60)),
                step=5,
                format="%d",
                key="vp_exposure_threshold_slider",
                help="Risks at or above this score are 100% opaque.",
            )
            st.session_state["vp_exposure_threshold"] = float(threshold)

    # ── Lifecycle Opacity (F21 upgraded) ────────────────────────────────
    with st.expander("👻 Lifecycle Opacity", expanded=False):
        lc_enabled = st.toggle(
            "Enable Lifecycle Opacity",
            value=st.session_state.get("vp_lifecycle_opacity_enabled", False),
            key="vp_lifecycle_opacity_toggle",
            help="Fade nodes based on their lifecycle status.",
        )
        st.session_state["vp_lifecycle_opacity_enabled"] = lc_enabled

        if lc_enabled:
            current_opacity: Dict[str, float] = dict(
                st.session_state.get(
                    "vp_lifecycle_opacity",
                    {"watching": 0.35, "suppressed": 0.15, "accepted": 0.40, "closed": 0.20},
                )
            )
            status_labels = {
                "watching": "Watching",
                "suppressed": "Suppressed",
                "accepted": "Accepted",
                "closed": "Closed / Archived",
            }
            for status_key, label in status_labels.items():
                val = st.slider(
                    label,
                    min_value=0.05,
                    max_value=1.0,
                    value=float(current_opacity.get(status_key, 0.35)),
                    step=0.05,
                    format="%.2f",
                    key=f"vp_lc_opacity_{status_key}",
                )
                current_opacity[status_key] = val
            st.session_state["vp_lifecycle_opacity"] = current_opacity

    # ── Quadrant Border Encoding ─────────────────────────────────────────
    qb_enabled = st.toggle(
        "Quadrant Border Encoding",
        value=st.session_state.get("vp_quadrant_borders", False),
        key="vp_quadrant_borders_toggle",
        help=(
            "Draw a coloured border around risk nodes indicating their "
            "quadrant (Critical/High/Moderate/Low)."
        ),
    )
    st.session_state["vp_quadrant_borders"] = qb_enabled

    if qb_enabled:
        st.caption(
            "🟥 Critical  🟠 Frequency  🟡 Severity  🟢 Marginal"
        )

    # ── Save as Default ──────────────────────────────────────────────────
    st.divider()
    save_disabled = schema_config is None
    if st.button(
        "💾 Save as Schema Default",
        key="vp_save_defaults_btn",
        disabled=save_disabled,
        help=(
            "Persist current visual settings to the active schema YAML so they "
            "apply as defaults on the next application load."
        ),
        use_container_width=True,
    ):
        _save_visual_config_to_schema(schema_config, db_manager)
