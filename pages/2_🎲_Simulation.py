"""
RIM Exposure Model Calibration Simulator

Monte Carlo simulation tool to validate and calibrate the exposure calculation model.
Generates random scenarios with varying likelihood, severity, and influence values
to visualize how risk exposure evolves along different mitigation paths.

Run with: streamlit run calibration_simulator.py
"""

import io
import uuid

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass, field
from typing import Any, List, Dict, Tuple, Optional
import random
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to allow imports from root
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_manager import get_active_manager
from utils.simulation_store import SimulationRecord
from utils.state_manager import init_simulation_state
from services.exposure_calculator import _compute_risk_quadrant, TRI_ALPHA


# =============================================================================
# CONFIGURATION - Same as exposure_calculator.py for consistency
# =============================================================================

EFFECTIVENESS_SCORES = {
    "Critical": 0.9,
    "High": 0.7,
    "Medium": 0.5,
    "Low": 0.3
}

INFLUENCE_STRENGTH_SCORES = {
    "Critical": 1.0,
    "Strong": 0.75,
    "Moderate": 0.5,
    "Weak": 0.25
}

EFFECTIVENESS_LEVELS = list(EFFECTIVENESS_SCORES.keys())
STRENGTH_LEVELS = list(INFLUENCE_STRENGTH_SCORES.keys())


# =============================================================================
# SIMULATION DATA STRUCTURES
# =============================================================================

@dataclass
class SimulatedRisk:
    """A simulated risk with random parameters."""
    id: str
    name: str
    level: str  # Strategic or Operational
    likelihood: float
    severity: float
    base_exposure: float = field(init=False)

    def __post_init__(self):
        self.base_exposure = self.likelihood * self.severity


@dataclass
class SimulatedInfluence:
    """A simulated influence relationship."""
    source_id: str
    target_id: str
    strength: str


@dataclass
class SimulatedMitigation:
    """A simulated mitigation."""
    id: str
    target_risk_id: str
    effectiveness: str


@dataclass
class SimulationScenario:
    """A complete simulation scenario."""
    risks: List[SimulatedRisk]
    influences: List[SimulatedInfluence]
    mitigations: List[SimulatedMitigation]
    
    # Calculated results
    risk_exposures: Dict[str, float] = field(default_factory=dict)
    global_residual_pct: float = 0.0
    global_risk_score: float = 0.0
    max_exposure: float = 0.0


# =============================================================================
# EXPOSURE CALCULATION (Simplified version for simulation)
# =============================================================================

def calculate_mitigation_factor(risk_id: str, mitigations: List[SimulatedMitigation]) -> float:
    """Calculate mitigation factor for a risk."""
    risk_mitigations = [m for m in mitigations if m.target_risk_id == risk_id]
    
    if not risk_mitigations:
        return 1.0
    
    factor = 1.0
    for m in risk_mitigations:
        eff_score = EFFECTIVENESS_SCORES.get(m.effectiveness, 0.5)
        factor *= (1.0 - eff_score)
    
    return factor


def calculate_influence_limitation(
    risk_id: str,
    risks: List[SimulatedRisk],
    influences: List[SimulatedInfluence],
    calculated_exposures: Dict[str, Tuple[float, float]]  # risk_id -> (base, final)
) -> float:
    """Calculate influence limitation factor."""
    upstream = [inf for inf in influences if inf.target_id == risk_id]
    
    if not upstream:
        return 0.0
    
    total_limitation = 0.0
    valid_count = 0
    
    for inf in upstream:
        if inf.source_id not in calculated_exposures:
            continue
        
        base, final = calculated_exposures[inf.source_id]
        if base > 0:
            residual_normalized = final / base
        else:
            residual_normalized = 1.0
        
        strength_score = INFLUENCE_STRENGTH_SCORES.get(inf.strength, 0.5)
        total_limitation += residual_normalized * strength_score
        valid_count += 1
    
    if valid_count == 0:
        return 0.0
    
    return total_limitation / valid_count


def calculate_scenario_exposures(scenario: SimulationScenario) -> SimulationScenario:
    """Calculate all exposures for a scenario."""
    risk_map = {r.id: r for r in scenario.risks}
    calculated = {}  # risk_id -> (base, final)
    
    # Build dependency order (simple: operational first, then strategic)
    operational = [r for r in scenario.risks if r.level == "Operational"]
    strategic = [r for r in scenario.risks if r.level == "Strategic"]
    ordered_risks = operational + strategic
    
    for risk in ordered_risks:
        base = risk.base_exposure
        mit_factor = calculate_mitigation_factor(risk.id, scenario.mitigations)
        inf_limitation = calculate_influence_limitation(
            risk.id, scenario.risks, scenario.influences, calculated
        )
        
        effective_factor = mit_factor + (1.0 - mit_factor) * inf_limitation
        final = base * effective_factor
        
        calculated[risk.id] = (base, final)
        scenario.risk_exposures[risk.id] = final
    
    # Global metrics
    total_base = sum(r.base_exposure for r in scenario.risks)
    total_final = sum(scenario.risk_exposures.values())
    
    scenario.global_residual_pct = (total_final / total_base * 100) if total_base > 0 else 0
    
    # Weighted score
    weighted_sum = sum(
        scenario.risk_exposures[r.id] * (r.severity ** 2)
        for r in scenario.risks
    )
    max_weighted = sum(100 * (r.severity ** 2) for r in scenario.risks)
    scenario.global_risk_score = (weighted_sum / max_weighted * 100) if max_weighted > 0 else 0
    
    scenario.max_exposure = max(scenario.risk_exposures.values()) if scenario.risk_exposures else 0
    
    return scenario


# =============================================================================
# SCENARIO GENERATION
# =============================================================================

def generate_risk_network(
    n_operational: int,
    n_strategic: int,
    influence_density: float,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float]
) -> Tuple[List[SimulatedRisk], List[SimulatedInfluence]]:
    """Generate a random risk network."""
    risks = []

    # Generate operational risks
    for i in range(n_operational):
        risks.append(SimulatedRisk(
            id=f"OR_{i+1}",
            name=f"Operational Risk {i+1}",
            level="Operational",
            likelihood=random.uniform(*likelihood_range),
            severity=random.uniform(*severity_range)
        ))

    # Generate strategic risks
    for i in range(n_strategic):
        risks.append(SimulatedRisk(
            id=f"SR_{i+1}",
            name=f"Strategic Risk {i+1}",
            level="Strategic",
            likelihood=random.uniform(*likelihood_range),
            severity=random.uniform(*severity_range)
        ))
    
    # Generate influences
    influences = []
    operational_ids = [r.id for r in risks if r.level == "Operational"]
    strategic_ids = [r.id for r in risks if r.level == "Strategic"]
    
    # Level 1: Operational -> Strategic
    for op_id in operational_ids:
        for st_id in strategic_ids:
            if random.random() < influence_density:
                influences.append(SimulatedInfluence(
                    source_id=op_id,
                    target_id=st_id,
                    strength=random.choice(STRENGTH_LEVELS)
                ))
    
    # Level 3: Operational -> Operational (less frequent)
    for i, op_id1 in enumerate(operational_ids):
        for op_id2 in operational_ids[i+1:]:
            if random.random() < influence_density * 0.5:
                influences.append(SimulatedInfluence(
                    source_id=op_id1,
                    target_id=op_id2,
                    strength=random.choice(STRENGTH_LEVELS)
                ))
    
    # Level 2: Strategic -> Strategic (rare)
    for i, st_id1 in enumerate(strategic_ids):
        for st_id2 in strategic_ids[i+1:]:
            if random.random() < influence_density * 0.3:
                influences.append(SimulatedInfluence(
                    source_id=st_id1,
                    target_id=st_id2,
                    strength=random.choice(STRENGTH_LEVELS)
                ))
    
    return risks, influences


def generate_mitigation_scenarios(
    risks: List[SimulatedRisk],
    influences: List[SimulatedInfluence],
    n_scenarios: int,
    mitigation_coverage_range: Tuple[float, float]
) -> List[SimulationScenario]:
    """Generate multiple scenarios with varying mitigation coverage."""
    scenarios = []
    
    for i in range(n_scenarios):
        # Random mitigation coverage for this scenario
        coverage = random.uniform(*mitigation_coverage_range)
        
        mitigations = []
        for risk in risks:
            if random.random() < coverage:
                # Add 1-2 mitigations per covered risk
                n_mits = random.randint(1, 2)
                for j in range(n_mits):
                    mitigations.append(SimulatedMitigation(
                        id=f"M_{risk.id}_{j+1}",
                        target_risk_id=risk.id,
                        effectiveness=random.choice(EFFECTIVENESS_LEVELS)
                    ))
        
        scenario = SimulationScenario(
            risks=risks.copy(),
            influences=influences.copy(),
            mitigations=mitigations
        )
        
        # Calculate exposures
        calculate_scenario_exposures(scenario)
        scenarios.append(scenario)
    
    return scenarios


def generate_mitigation_path_scenarios(
    risks: List[SimulatedRisk],
    influences: List[SimulatedInfluence],
    n_steps: int
) -> List[SimulationScenario]:
    """
    Generate scenarios along a mitigation path.
    Starts with no mitigations and progressively adds them.
    """
    scenarios = []
    current_mitigations = []
    
    # Sort risks by influence (upstream first) then by exposure
    risk_priority = []
    
    # Calculate initial exposures
    initial_scenario = SimulationScenario(
        risks=risks.copy(),
        influences=influences.copy(),
        mitigations=[]
    )
    calculate_scenario_exposures(initial_scenario)
    scenarios.append(initial_scenario)
    
    # Priority: risks that influence others should be mitigated first
    influenced_counts = {}
    for inf in influences:
        influenced_counts[inf.source_id] = influenced_counts.get(inf.source_id, 0) + 1
    
    for risk in risks:
        priority_score = (
            initial_scenario.risk_exposures.get(risk.id, 0) * 
            (1 + influenced_counts.get(risk.id, 0))
        )
        risk_priority.append((risk, priority_score))
    
    risk_priority.sort(key=lambda x: -x[1])
    
    # Progressively add mitigations
    step_size = max(1, len(risks) // n_steps)
    
    for step in range(1, n_steps + 1):
        # Add mitigations for next batch of risks
        start_idx = (step - 1) * step_size
        end_idx = min(step * step_size, len(risks))
        
        for risk, _ in risk_priority[start_idx:end_idx]:
            effectiveness = random.choice(EFFECTIVENESS_LEVELS)
            current_mitigations.append(SimulatedMitigation(
                id=f"M_{risk.id}_step{step}",
                target_risk_id=risk.id,
                effectiveness=effectiveness
            ))
        
        scenario = SimulationScenario(
            risks=risks.copy(),
            influences=influences.copy(),
            mitigations=current_mitigations.copy()
        )
        calculate_scenario_exposures(scenario)
        scenarios.append(scenario)
    
    return scenarios


# =============================================================================
# MONTE CARLO SIMULATION
# =============================================================================

def run_monte_carlo(
    n_simulations: int,
    n_operational: int,
    n_strategic: int,
    influence_density: float,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float],
    mitigation_coverage_range: Tuple[float, float],
    progress_callback=None
) -> pd.DataFrame:
    """
    Run Monte Carlo simulation with random parameters.

    Returns DataFrame with results for each simulation.
    """
    results = []

    for i in range(n_simulations):
        # Generate random network
        risks, influences = generate_risk_network(
            n_operational, n_strategic, influence_density,
            likelihood_range, severity_range
        )
        
        # Generate scenario with random mitigations
        coverage = random.uniform(*mitigation_coverage_range)
        mitigations = []
        
        for risk in risks:
            if random.random() < coverage:
                n_mits = random.randint(1, 2)
                for j in range(n_mits):
                    mitigations.append(SimulatedMitigation(
                        id=f"M_{risk.id}_{j+1}",
                        target_risk_id=risk.id,
                        effectiveness=random.choice(EFFECTIVENESS_LEVELS)
                    ))
        
        scenario = SimulationScenario(
            risks=risks,
            influences=influences,
            mitigations=mitigations
        )
        calculate_scenario_exposures(scenario)
        
        # Calculate metrics
        total_base = sum(r.base_exposure for r in risks)
        total_final = sum(scenario.risk_exposures.values())
        n_mitigated = len(set(m.target_risk_id for m in mitigations))
        n_influences = len(influences)
        
        # Average influence strength
        avg_strength = np.mean([
            INFLUENCE_STRENGTH_SCORES.get(inf.strength, 0.5) 
            for inf in influences
        ]) if influences else 0
        
        results.append({
            "simulation_id": i + 1,
            "n_risks": len(risks),
            "n_operational": n_operational,
            "n_strategic": n_strategic,
            "n_influences": n_influences,
            "avg_influence_strength": avg_strength,
            "n_mitigations": len(mitigations),
            "n_risks_mitigated": n_mitigated,
            "mitigation_coverage": n_mitigated / len(risks) if risks else 0,
            "total_base_exposure": total_base,
            "total_final_exposure": total_final,
            "residual_risk_pct": scenario.global_residual_pct,
            "weighted_risk_score": scenario.global_risk_score,
            "max_single_exposure": scenario.max_exposure,
            "avg_likelihood": np.mean([r.likelihood for r in risks]),
            "avg_severity": np.mean([r.severity for r in risks]),
        })
        
        if progress_callback and (i + 1) % 100 == 0:
            progress_callback(i + 1, n_simulations)
    
    return pd.DataFrame(results)


def run_mitigation_path_simulation(
    n_paths: int,
    n_steps: int,
    n_operational: int,
    n_strategic: int,
    influence_density: float,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float],
    progress_callback=None
) -> pd.DataFrame:
    """
    Run simulation of mitigation paths.

    Returns DataFrame with results for each step of each path.
    """
    results = []

    for path_id in range(n_paths):
        # Generate random network (fixed for this path)
        risks, influences = generate_risk_network(
            n_operational, n_strategic, influence_density,
            likelihood_range, severity_range
        )
        
        # Generate mitigation path
        path_scenarios = generate_mitigation_path_scenarios(
            risks, influences, n_steps
        )
        
        total_base = sum(r.base_exposure for r in risks)
        
        for step, scenario in enumerate(path_scenarios):
            n_mitigated = len(set(m.target_risk_id for m in scenario.mitigations))
            
            results.append({
                "path_id": path_id + 1,
                "step": step,
                "mitigation_coverage": n_mitigated / len(risks) if risks else 0,
                "n_mitigations": len(scenario.mitigations),
                "total_base_exposure": total_base,
                "total_final_exposure": sum(scenario.risk_exposures.values()),
                "residual_risk_pct": scenario.global_residual_pct,
                "weighted_risk_score": scenario.global_risk_score,
                "max_single_exposure": scenario.max_exposure,
            })
        
        if progress_callback and (path_id + 1) % 10 == 0:
            progress_callback(path_id + 1, n_paths)
    
    return pd.DataFrame(results)


# =============================================================================
# STREAMLIT APP
# =============================================================================

def main():
    st.set_page_config(
        page_title="RIM Exposure Model Calibrator",
        page_icon="🎲",
        layout="wide"
    )

    # ── State initialisation ──────────────────────────────────────────────────
    init_simulation_state()
    if st.session_state.saved_simulations is None:
        st.session_state.saved_simulations = []

    st.title("🎲 RIM Exposure Model Calibration Simulator")
    st.markdown("""
    Monte Carlo simulation tool to validate and calibrate the exposure calculation model.
    Generate random scenarios to visualize how risk exposure evolves with different parameters.
    """)

    # ── Top-level tabs ────────────────────────────────────────────────────────
    tab_sim, tab_saved = st.tabs(["🎲 Simulator", "📊 Saved Results"])

    # ── Sidebar configuration ─────────────────────────────────────────────────
    st.sidebar.header("⚙️ Simulation Parameters")

    sim_mode = st.sidebar.radio(
        "Simulation Mode",
        ["Monte Carlo (Random)", "Mitigation Path", "Scope-Based (Real Data)", "TRI α Calibration"],
        help=(
            "Monte Carlo: random scenarios. "
            "Mitigation Path: progressive mitigation. "
            "Scope-Based: real graph data from the active DB connection. "
            "TRI α Calibration: sweep the TRI exponent (α) to validate domain-appropriate value."
        )
    )

    # ── Scope-Based / TRI α Calibration sidebar (both require DB) ────────────
    if sim_mode in ("Scope-Based (Real Data)", "TRI α Calibration"):
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 DB Connection")

        manager = get_active_manager()
        run_button_disabled = False

        if manager is None:
            st.sidebar.warning(
                "⚠️ No active DB connection.\n\n"
                "Navigate to the **dashboard** first to connect."
            )
            run_button_disabled = True
        else:
            st.sidebar.success("✅ Connected")

        # Active scope
        fm = st.session_state.get("filter_manager")
        if fm is not None and fm.get_scope_node_ids() is not None:
            scope_names = [s.name for s in fm.active_scopes] if fm.active_scopes else []
            scope_label = ", ".join(scope_names) if scope_names else "Active scope"
            scope_ids = fm.get_scope_node_ids()
            st.sidebar.info(f"📍 Scope: **{scope_label}**")
        else:
            scope_label = "Full Graph"
            scope_ids = None
            st.sidebar.info("📍 Scope: **Full Graph** (no scope active)")

        st.sidebar.markdown("---")

        # ── F31c: Worst-Case Canvas toggle (shared by both DB modes) ─────────
        include_inactive = st.sidebar.checkbox(
            "🧟 Worst-Case Canvas",
            value=False,
            help=(
                "Re-activates lifecycle-inactive risks (accepted / watching / suppressed / closed) "
                "to reveal latent tail exposure. Results are labelled as worst-case."
            ),
            key="sb_include_inactive",
        )
        if include_inactive and scope_label != "Full Graph":
            scope_label = scope_label + " [Worst-Case]"
        elif include_inactive:
            scope_label = "Full Graph [Worst-Case]"

        if sim_mode == "Scope-Based (Real Data)":
            # ── Scope-Based settings ──────────────────────────────────────────
            st.sidebar.subheader("⚙️ Scope-Based Settings")

            param_mode = st.sidebar.radio(
                "Parameter mode",
                ["Real L×I values", "Random L×I (calibration)"],
                help=(
                    "Real L×I: use actual likelihood/severity from the DB each run. "
                    "Random L×I: randomise likelihood/severity within ranges while keeping real topology."
                )
            )

            n_simulations_sb = st.sidebar.slider(
                "Number of Simulations", 100, 5000, 500, step=100,
                key="sb_n_sims"
            )
            coverage_variance = st.sidebar.slider(
                "Mitigation Variance %", 0, 100, 30,
                help="How much mitigation coverage varies around the real value each run.",
                key="sb_cov_var"
            ) / 100

            if param_mode == "Random L×I (calibration)":
                st.sidebar.markdown("---")
                st.sidebar.subheader("📈 L×I Ranges")
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    sb_likelihood_min = st.number_input("Likelihood Min", 1.0, 10.0, 1.0, key="sb_lmin")
                    sb_severity_min = st.number_input("Severity Min", 1.0, 10.0, 1.0, key="sb_imin")
                with col2:
                    sb_likelihood_max = st.number_input("Likelihood Max", 1.0, 10.0, 10.0, key="sb_lmax")
                    sb_severity_max = st.number_input("Severity Max", 1.0, 10.0, 10.0, key="sb_imax")
                sb_likelihood_range = (sb_likelihood_min, sb_likelihood_max)
                sb_severity_range = (sb_severity_min, sb_severity_max)
            else:
                sb_likelihood_range = (1.0, 10.0)
                sb_severity_range = (1.0, 10.0)

            st.sidebar.markdown("---")
            run_button = st.sidebar.button(
                "🚀 Run Simulation", type="primary", use_container_width=True,
                disabled=run_button_disabled
            )

            with tab_sim:
                # Run compute when button clicked (clears then fills ss["last_sb_result"])
                if run_button and not run_button_disabled:
                    _compute_sb_and_store(
                        manager, scope_ids, scope_label,
                        n_simulations_sb, coverage_variance,
                        param_mode == "Random L×I (calibration)",
                        sb_likelihood_range, sb_severity_range,
                        include_inactive=include_inactive,
                    )

                # Always render from stored state — this is what makes the save button work:
                # even when run_button is False (e.g. after clicking 💾 Save Results),
                # the results and save button are still rendered and their clicks processed.
                stored_sb = st.session_state.get("last_sb_result")
                if stored_sb is not None:
                    _render_sb_results(stored_sb)
                elif not run_button:
                    st.info("👈 Configure parameters in the sidebar and click **Run Simulation** to start.")
                    _render_about_expander()

        else:
            # ── TRI α Calibration settings (F31d) ────────────────────────────
            st.sidebar.subheader("⚙️ TRI α Calibration Settings")

            st.sidebar.markdown(f"*Current schema default: α = {TRI_ALPHA}*")

            alpha_col1, alpha_col2 = st.sidebar.columns(2)
            with alpha_col1:
                alpha_min = st.number_input("α Min", 0.5, 5.0, 1.0, step=0.25, key="tac_alpha_min")
            with alpha_col2:
                alpha_max = st.number_input("α Max", 0.5, 5.0, 3.0, step=0.25, key="tac_alpha_max")
            alpha_step = st.sidebar.select_slider(
                "α Step", options=[0.1, 0.25, 0.5, 1.0], value=0.25, key="tac_alpha_step"
            )
            runs_per_alpha = st.sidebar.slider(
                "Runs per α", 50, 500, 200, step=50, key="tac_runs_per_alpha"
            )

            st.sidebar.markdown("---")
            tac_param_mode = st.sidebar.radio(
                "Parameter mode",
                ["Real L×I values", "Random L×I (calibration)"],
                key="tac_param_mode",
                help=(
                    "Real L×I: use actual likelihood/severity from the DB. "
                    "Random L×I: randomise L×I within ranges."
                )
            )
            if tac_param_mode == "Random L×I (calibration)":
                st.sidebar.markdown("---")
                st.sidebar.subheader("📈 L×I Ranges")
                tac_col1, tac_col2 = st.sidebar.columns(2)
                with tac_col1:
                    tac_lmin = st.number_input("Likelihood Min", 1.0, 10.0, 1.0, key="tac_lmin")
                    tac_imin = st.number_input("Severity Min", 1.0, 10.0, 1.0, key="tac_imin")
                with tac_col2:
                    tac_lmax = st.number_input("Likelihood Max", 1.0, 10.0, 10.0, key="tac_lmax")
                    tac_imax = st.number_input("Severity Max", 1.0, 10.0, 10.0, key="tac_imax")
                tac_likelihood_range = (tac_lmin, tac_lmax)
                tac_severity_range = (tac_imin, tac_imax)
            else:
                tac_likelihood_range = (1.0, 10.0)
                tac_severity_range = (1.0, 10.0)

            st.sidebar.markdown("---")
            run_button = st.sidebar.button(
                "🚀 Run Calibration", type="primary", use_container_width=True,
                disabled=run_button_disabled
            )

            with tab_sim:
                # Compute when button clicked
                if run_button and not run_button_disabled:
                    _compute_tac_and_store(
                        manager, scope_ids, scope_label,
                        alpha_min=alpha_min,
                        alpha_max=alpha_max,
                        alpha_step=alpha_step,
                        runs_per_alpha=runs_per_alpha,
                        randomize_params=tac_param_mode == "Random L×I (calibration)",
                        likelihood_range=tac_likelihood_range,
                        severity_range=tac_severity_range,
                        include_inactive=include_inactive,
                    )

                # Always render from stored state — makes 💾 Save Calibration Results work
                stored_tac = st.session_state.get("last_tac_result")
                if stored_tac is not None:
                    _render_tac_results(stored_tac)
                elif not run_button:
                    st.info("👈 Configure α range in the sidebar and click **Run Calibration** to start.")
                    _render_tri_alpha_about_expander()

        with tab_saved:
            _render_saved_results_tab()

        return  # DB-based modes handled above; skip rest of main()

    # ── Random / Mitigation Path sidebar ─────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Risk Network")

    n_operational = st.sidebar.slider("Operational Risks", 2, 20, 5)
    n_strategic = st.sidebar.slider("Strategic Risks", 1, 10, 3)
    influence_density = st.sidebar.slider(
        "Influence Density", 0.1, 1.0, 0.4,
        help="Probability of influence link between eligible risk pairs"
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Parameter Ranges")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        likelihood_min = st.number_input("Likelihood Min", 1.0, 10.0, 1.0)
        severity_min = st.number_input("Severity Min", 1.0, 10.0, 1.0)
    with col2:
        likelihood_max = st.number_input("Likelihood Max", 1.0, 10.0, 10.0)
        severity_max = st.number_input("Severity Max", 1.0, 10.0, 10.0)

    likelihood_range = (likelihood_min, likelihood_max)
    severity_range = (severity_min, severity_max)

    if sim_mode == "Monte Carlo (Random)":
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎲 Monte Carlo Settings")

        n_simulations = st.sidebar.slider("Number of Simulations", 100, 10000, 1000, step=100)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            coverage_min = st.number_input("Coverage Min %", 0, 100, 0) / 100
        with col2:
            coverage_max = st.number_input("Coverage Max %", 0, 100, 100) / 100

        mitigation_coverage_range = (coverage_min, coverage_max)

    else:  # Mitigation Path
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛤️ Path Settings")

        n_paths = st.sidebar.slider("Number of Paths", 10, 500, 100)
        n_steps = st.sidebar.slider("Steps per Path", 3, 20, 10)

    # Run simulation button
    st.sidebar.markdown("---")
    run_button = st.sidebar.button("🚀 Run Simulation", type="primary", use_container_width=True)

    # Main content area
    with tab_sim:
        if run_button:
            if sim_mode == "Monte Carlo (Random)":
                run_monte_carlo_simulation(
                    n_simulations, n_operational, n_strategic, influence_density,
                    likelihood_range, severity_range, mitigation_coverage_range
                )
            else:
                run_mitigation_path_simulation_ui(
                    n_paths, n_steps, n_operational, n_strategic, influence_density,
                    likelihood_range, severity_range
                )
        else:
            # Show instructions
            st.info("👈 Configure parameters in the sidebar and click **Run Simulation** to start.")
            _render_about_expander()

    with tab_saved:
        _render_saved_results_tab()


def _render_about_expander():
    """Render the About / formula expander shown on the instructions screen."""
    with st.expander("📖 About the Exposure Model", expanded=True):
        st.markdown("""
        ### Exposure Calculation Formula

        The model calculates risk exposure through three factors:

        **1. Base Exposure** = `Likelihood × Severity` (scale 1-100)

        **2. Mitigation Factor** = `∏(1 - Effectiveness)` (multiplicative, diminishing returns)

        | Effectiveness | Reduction |
        |---------------|-----------|
        | Critical | 90% |
        | High | 70% |
        | Medium | 50% |
        | Low | 30% |

        **3. Influence Limitation** = `Avg(Upstream_Residual × Strength)`

        | Strength | Weight |
        |----------|--------|
        | Critical | 1.0 |
        | Strong | 0.75 |
        | Moderate | 0.50 |
        | Weak | 0.25 |

        **Final Formula:**
        ```
        Effective_Factor = Mit_Factor + (1 - Mit_Factor) × Influence_Limitation
        Final_Exposure = Base × Effective_Factor
        ```

        ### What This Simulator Tests

        - **Monte Carlo Mode**: Random scenarios to see distribution of outcomes
        - **Mitigation Path Mode**: How exposure decreases as mitigations are added
        - **Scope-Based Mode**: Real graph topology with real or randomised L×I values

        The visualization helps identify:
        - Sensitivity to different parameters
        - Effect of influence limitation on mitigation effectiveness
        - Optimal mitigation strategies
        """)


def run_monte_carlo_simulation(
    n_simulations, n_operational, n_strategic, influence_density,
    likelihood_range, severity_range, mitigation_coverage_range
):
    """Run and display Monte Carlo simulation results."""

    st.header("🎲 Monte Carlo Simulation Results")

    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(current, total):
        progress_bar.progress(current / total)
        status_text.text(f"Running simulation {current}/{total}...")

    # Run simulation
    start_time = datetime.now()

    df = run_monte_carlo(
        n_simulations, n_operational, n_strategic, influence_density,
        likelihood_range, severity_range, mitigation_coverage_range,
        progress_callback=update_progress
    )

    elapsed = (datetime.now() - start_time).total_seconds()
    progress_bar.progress(1.0)
    status_text.text(f"✅ Completed {n_simulations} simulations in {elapsed:.2f}s")

    # Summary statistics
    st.subheader("📊 Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Mean Residual Risk %", f"{df['residual_risk_pct'].mean():.1f}%")
        st.metric("Std Dev", f"{df['residual_risk_pct'].std():.1f}%")

    with col2:
        st.metric("Mean Risk Score", f"{df['weighted_risk_score'].mean():.1f}")
        st.metric("Std Dev", f"{df['weighted_risk_score'].std():.1f}")

    with col3:
        st.metric("Mean Max Exposure", f"{df['max_single_exposure'].mean():.1f}")
        st.metric("Std Dev", f"{df['max_single_exposure'].std():.1f}")

    with col4:
        st.metric("Mean Coverage", f"{df['mitigation_coverage'].mean()*100:.1f}%")
        st.metric("Simulations", n_simulations)

    _render_save_results_button(
        df=df,
        mode="Monte Carlo (Random)",
        scope_label="Full Graph",
        params={
            "n_simulations": n_simulations, "n_operational": n_operational,
            "n_strategic": n_strategic, "influence_density": influence_density,
            "likelihood_range": likelihood_range, "severity_range": severity_range,
            "mitigation_coverage_range": mitigation_coverage_range,
        },
        button_key="save_mc",
    )

    st.markdown("---")

    # Visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Distributions",
        "☁️ Scatter Clouds",
        "🔥 Heatmaps",
        "📋 Data"
    ])

    with tab1:
        render_distribution_plots(df)

    with tab2:
        render_scatter_plots(df)

    with tab3:
        render_heatmaps(df)

    with tab4:
        st.dataframe(df, use_container_width=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Results (CSV)",
            csv,
            "monte_carlo_results.csv",
            "text/csv"
        )


def render_distribution_plots(df: pd.DataFrame):
    """Render distribution plots for Monte Carlo results."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df, x="residual_risk_pct", nbins=50,
            title="Distribution of Residual Risk %",
            labels={"residual_risk_pct": "Residual Risk %"},
            color_discrete_sequence=["#3498db"]
        )
        fig.add_vline(x=df["residual_risk_pct"].mean(), line_dash="dash", 
                      line_color="red", annotation_text="Mean")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(
            df, x="weighted_risk_score", nbins=50,
            title="Distribution of Weighted Risk Score",
            labels={"weighted_risk_score": "Risk Score (0-100)"},
            color_discrete_sequence=["#e74c3c"]
        )
        fig.add_vline(x=df["weighted_risk_score"].mean(), line_dash="dash",
                      line_color="blue", annotation_text="Mean")
        st.plotly_chart(fig, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig = px.histogram(
            df, x="max_single_exposure", nbins=50,
            title="Distribution of Max Single Exposure",
            labels={"max_single_exposure": "Max Exposure"},
            color_discrete_sequence=["#f39c12"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        fig = px.histogram(
            df, x="mitigation_coverage", nbins=30,
            title="Distribution of Mitigation Coverage",
            labels={"mitigation_coverage": "Coverage (0-1)"},
            color_discrete_sequence=["#27ae60"]
        )
        st.plotly_chart(fig, use_container_width=True)


def render_scatter_plots(df: pd.DataFrame):
    """Render scatter cloud plots."""
    
    st.subheader("☁️ Scatter Cloud Analysis")
    
    # Main scatter: Coverage vs Residual Risk
    fig = px.scatter(
        df, x="mitigation_coverage", y="residual_risk_pct",
        color="avg_influence_strength",
        size="n_influences",
        hover_data=["n_mitigations", "max_single_exposure"],
        title="Mitigation Coverage vs Residual Risk (colored by Influence Strength)",
        labels={
            "mitigation_coverage": "Mitigation Coverage",
            "residual_risk_pct": "Residual Risk %",
            "avg_influence_strength": "Avg Influence Strength"
        },
        color_continuous_scale="RdYlGn_r"
    )
    fig.update_traces(marker=dict(opacity=0.6))
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Coverage vs Risk Score
        fig = px.scatter(
            df, x="mitigation_coverage", y="weighted_risk_score",
            color="n_influences",
            title="Coverage vs Weighted Risk Score",
            labels={
                "mitigation_coverage": "Mitigation Coverage",
                "weighted_risk_score": "Risk Score",
                "n_influences": "# Influences"
            },
            color_continuous_scale="Viridis"
        )
        fig.update_traces(marker=dict(opacity=0.5, size=5))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Base vs Final Exposure
        fig = px.scatter(
            df, x="total_base_exposure", y="total_final_exposure",
            color="mitigation_coverage",
            title="Base vs Final Exposure",
            labels={
                "total_base_exposure": "Total Base Exposure",
                "total_final_exposure": "Total Final Exposure",
                "mitigation_coverage": "Coverage"
            },
            color_continuous_scale="RdYlGn_r"
        )
        # Add diagonal line (no mitigation)
        max_val = max(df["total_base_exposure"].max(), df["total_final_exposure"].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines", line=dict(dash="dash", color="gray"),
            name="No Mitigation Line"
        ))
        fig.update_traces(marker=dict(opacity=0.5, size=5), selector=dict(mode="markers"))
        st.plotly_chart(fig, use_container_width=True)
    
    # 3D scatter
    st.subheader("🎯 3D View: Coverage × Influence × Residual Risk")
    
    fig = px.scatter_3d(
        df, x="mitigation_coverage", y="avg_influence_strength", z="residual_risk_pct",
        color="weighted_risk_score",
        size="max_single_exposure",
        opacity=0.6,
        title="3D Scatter: Key Factors",
        labels={
            "mitigation_coverage": "Coverage",
            "avg_influence_strength": "Influence Strength",
            "residual_risk_pct": "Residual Risk %"
        },
        color_continuous_scale="RdYlGn_r"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_heatmaps(df: pd.DataFrame):
    """Render heatmap visualizations."""
    
    st.subheader("🔥 Sensitivity Heatmaps")
    
    # Bin the data for heatmaps
    df["coverage_bin"] = pd.cut(df["mitigation_coverage"], bins=10, labels=False)
    df["influence_bin"] = pd.cut(df["avg_influence_strength"], bins=10, labels=False)
    
    # Pivot for heatmap
    heatmap_data = df.groupby(["coverage_bin", "influence_bin"])["residual_risk_pct"].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="influence_bin", columns="coverage_bin", values="residual_risk_pct")
    
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Mitigation Coverage (bins)", y="Influence Strength (bins)", color="Residual Risk %"),
        title="Residual Risk % by Coverage and Influence Strength",
        color_continuous_scale="RdYlGn_r",
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Second heatmap: Risk Score
    heatmap_data2 = df.groupby(["coverage_bin", "influence_bin"])["weighted_risk_score"].mean().reset_index()
    heatmap_pivot2 = heatmap_data2.pivot(index="influence_bin", columns="coverage_bin", values="weighted_risk_score")
    
    fig2 = px.imshow(
        heatmap_pivot2,
        labels=dict(x="Mitigation Coverage (bins)", y="Influence Strength (bins)", color="Risk Score"),
        title="Weighted Risk Score by Coverage and Influence Strength",
        color_continuous_scale="RdYlGn_r",
        aspect="auto"
    )
    st.plotly_chart(fig2, use_container_width=True)


def run_mitigation_path_simulation_ui(
    n_paths, n_steps, n_operational, n_strategic, influence_density,
    likelihood_range, severity_range
):
    """Run and display mitigation path simulation results."""
    
    st.header("🛤️ Mitigation Path Simulation Results")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current, total):
        progress_bar.progress(current / total)
        status_text.text(f"Generating path {current}/{total}...")
    
    # Run simulation
    start_time = datetime.now()
    
    df = run_mitigation_path_simulation(
        n_paths, n_steps, n_operational, n_strategic, influence_density,
        likelihood_range, severity_range,
        progress_callback=update_progress
    )
    
    elapsed = (datetime.now() - start_time).total_seconds()
    progress_bar.progress(1.0)
    status_text.text(f"✅ Completed {n_paths} paths × {n_steps+1} steps in {elapsed:.2f}s")

    # Summary by step
    st.subheader("📊 Average Metrics by Mitigation Step")

    step_summary = df.groupby("step").agg({
        "mitigation_coverage": "mean",
        "residual_risk_pct": ["mean", "std", "min", "max"],
        "weighted_risk_score": ["mean", "std"],
        "max_single_exposure": ["mean", "std"]
    }).round(2)

    st.dataframe(step_summary, use_container_width=True)

    _render_save_results_button(
        df=df,
        mode="Mitigation Path",
        scope_label="Full Graph",
        params={
            "n_paths": n_paths, "n_steps": n_steps,
            "n_operational": n_operational, "n_strategic": n_strategic,
            "influence_density": influence_density,
            "likelihood_range": likelihood_range, "severity_range": severity_range,
        },
        button_key="save_path",
    )

    st.markdown("---")

    # Visualizations
    tab1, tab2, tab3 = st.tabs([
        "📈 Path Evolution",
        "☁️ Cloud View",
        "📋 Data"
    ])

    with tab1:
        render_path_evolution_plots(df)

    with tab2:
        render_path_cloud_plots(df)

    with tab3:
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Results (CSV)",
            csv,
            "mitigation_path_results.csv",
            "text/csv"
        )


def render_path_evolution_plots(df: pd.DataFrame):
    """Render path evolution plots."""
    
    # Average path with confidence band
    step_stats = df.groupby("step").agg({
        "residual_risk_pct": ["mean", "std", "min", "max"],
        "mitigation_coverage": "mean"
    }).reset_index()
    step_stats.columns = ["step", "mean", "std", "min", "max", "coverage"]
    
    fig = go.Figure()
    
    # Confidence band (±1 std)
    fig.add_trace(go.Scatter(
        x=list(step_stats["step"]) + list(step_stats["step"][::-1]),
        y=list(step_stats["mean"] + step_stats["std"]) + list((step_stats["mean"] - step_stats["std"])[::-1]),
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.2)",
        line=dict(color="rgba(255,255,255,0)"),
        name="±1 Std Dev"
    ))
    
    # Min-max band
    fig.add_trace(go.Scatter(
        x=list(step_stats["step"]) + list(step_stats["step"][::-1]),
        y=list(step_stats["max"]) + list(step_stats["min"][::-1]),
        fill="toself",
        fillcolor="rgba(52, 152, 219, 0.1)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Min-Max Range"
    ))
    
    # Mean line
    fig.add_trace(go.Scatter(
        x=step_stats["step"],
        y=step_stats["mean"],
        mode="lines+markers",
        line=dict(color="#3498db", width=3),
        name="Mean Residual Risk %"
    ))
    
    fig.update_layout(
        title="Residual Risk % Evolution Along Mitigation Path",
        xaxis_title="Mitigation Step",
        yaxis_title="Residual Risk %",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Individual paths (sample)
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample 20 random paths
        sample_paths = df["path_id"].drop_duplicates().sample(min(20, df["path_id"].nunique()))
        df_sample = df[df["path_id"].isin(sample_paths)]
        
        fig = px.line(
            df_sample, x="step", y="residual_risk_pct",
            color="path_id",
            title="Sample Individual Paths (Residual Risk %)",
            labels={"step": "Step", "residual_risk_pct": "Residual Risk %"}
        )
        fig.update_traces(opacity=0.5)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            df_sample, x="step", y="weighted_risk_score",
            color="path_id",
            title="Sample Individual Paths (Risk Score)",
            labels={"step": "Step", "weighted_risk_score": "Risk Score"}
        )
        fig.update_traces(opacity=0.5)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Coverage vs Residual
    st.subheader("📉 Coverage Effect on Exposure")
    
    fig = px.scatter(
        df, x="mitigation_coverage", y="residual_risk_pct",
        color="step",
        title="Mitigation Coverage vs Residual Risk (by Step)",
        labels={
            "mitigation_coverage": "Coverage",
            "residual_risk_pct": "Residual Risk %",
            "step": "Step"
        },
        color_continuous_scale="Viridis"
    )
    fig.update_traces(marker=dict(opacity=0.4, size=5))
    st.plotly_chart(fig, use_container_width=True)


def render_path_cloud_plots(df: pd.DataFrame):
    """Render cloud plots for path simulation."""
    
    st.subheader("☁️ Point Cloud: All Simulation Points")
    
    fig = px.scatter(
        df, x="mitigation_coverage", y="residual_risk_pct",
        color="step",
        hover_data=["path_id", "n_mitigations", "max_single_exposure"],
        title="All Points: Coverage vs Residual Risk",
        labels={
            "mitigation_coverage": "Mitigation Coverage",
            "residual_risk_pct": "Residual Risk %",
            "step": "Step"
        },
        color_continuous_scale="Plasma"
    )
    fig.update_traces(marker=dict(opacity=0.3, size=4))
    st.plotly_chart(fig, use_container_width=True)
    
    # Density contour
    fig = px.density_contour(
        df, x="mitigation_coverage", y="residual_risk_pct",
        title="Density Contour: Coverage vs Residual Risk",
        labels={
            "mitigation_coverage": "Mitigation Coverage",
            "residual_risk_pct": "Residual Risk %"
        }
    )
    fig.update_traces(contours_coloring="fill", contours_showlabels=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Box plots by step
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(
            df, x="step", y="residual_risk_pct",
            title="Residual Risk % Distribution by Step",
            labels={"step": "Step", "residual_risk_pct": "Residual Risk %"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.box(
            df, x="step", y="weighted_risk_score",
            title="Risk Score Distribution by Step",
            labels={"step": "Step", "weighted_risk_score": "Risk Score"}
        )
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# SCOPE-BASED (REAL DATA) SIMULATION  — F31a
# =============================================================================

def _load_scope_data(
    manager,
    scope_ids: Optional[List[str]],
    include_inactive: bool = False,
) -> Tuple[List[SimulatedRisk], List[SimulatedInfluence], List[SimulatedMitigation]]:
    """Load real DB data and convert to simulation structs.

    Applies in-memory scope filtering using the same pattern as
    exposure_calculator.py.  Returns (risks, influences, mitigations).

    When include_inactive is True, lifecycle-inactive risks (accepted/watching/
    suppressed/closed) are included to model worst-case canvas exposure (F31c).
    """
    risks_raw = manager.get_all_risks(exclude_inactive=not include_inactive)
    influences_raw = manager.get_all_influences()  # pure INFLUENCES edges
    mitigates_raw = manager.get_all_mitigates_relationships()

    # ── Scope filtering ──────────────────────────────────────────────────────
    if scope_ids is not None:
        scope_set = set(scope_ids)
        risks_raw = [r for r in risks_raw if r["id"] in scope_set]

    risk_ids = {r["id"] for r in risks_raw}

    influences_raw = [
        i for i in influences_raw
        if i.get("source_id") in risk_ids and i.get("target_id") in risk_ids
    ]
    mitigates_raw = [mr for mr in mitigates_raw if mr.get("risk_id") in risk_ids]

    # ── Convert to simulation structs ────────────────────────────────────────
    # DB field: probability (not likelihood); level: "Business" | "Operational"
    real_risks = [
        SimulatedRisk(
            id=r["id"],
            name=r["name"],
            level="Strategic" if r.get("level") == "Business" else "Operational",
            likelihood=float(r.get("probability") or 5.0),
            severity=float(r.get("severity") or r.get("impact") or 5.0),  # impact fallback for legacy data
        )
        for r in risks_raw
    ]

    real_influences = [
        SimulatedInfluence(
            source_id=i["source_id"],
            target_id=i["target_id"],
            strength=i.get("strength", "Moderate"),
        )
        for i in influences_raw
    ]

    # effectiveness lives on the MITIGATES relationship
    real_mitigations = [
        SimulatedMitigation(
            id=mr["mitigation_id"],
            target_risk_id=mr["risk_id"],
            effectiveness=mr.get("effectiveness") or "Medium",
        )
        for mr in mitigates_raw
    ]

    return real_risks, real_influences, real_mitigations


def run_scope_based_monte_carlo(
    real_risks: List[SimulatedRisk],
    real_influences: List[SimulatedInfluence],
    real_mitigations: List[SimulatedMitigation],
    n_simulations: int,
    coverage_variance: float,
    randomize_params: bool,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float],
    progress_callback=None,
) -> pd.DataFrame:
    """Monte Carlo over a fixed real topology.

    Each run varies mitigation coverage by ±coverage_variance around the
    real coverage ratio.  When randomize_params is True, likelihood and
    severity are also sampled randomly per run; otherwise real values are used.

    Returns a DataFrame with the same schema as run_monte_carlo(), plus a
    'param_mode' column.
    """
    if not real_risks:
        return pd.DataFrame()

    n_risks = len(real_risks)
    real_coverage = (
        len({m.target_risk_id for m in real_mitigations}) / n_risks
        if n_risks > 0 else 0.0
    )

    results = []

    for i in range(n_simulations):
        # ── Build risks for this run ─────────────────────────────────────────
        if randomize_params:
            run_risks = [
                SimulatedRisk(
                    id=r.id, name=r.name, level=r.level,
                    likelihood=random.uniform(*likelihood_range),
                    severity=random.uniform(*severity_range),
                )
                for r in real_risks
            ]
        else:
            run_risks = list(real_risks)

        # ── Vary mitigation coverage ─────────────────────────────────────────
        lo = max(0.0, real_coverage - coverage_variance)
        hi = min(1.0, real_coverage + coverage_variance)
        target_coverage = random.uniform(lo, hi)

        # Sample mitigations to include based on target coverage
        risk_ids_in_scope = [r.id for r in run_risks]
        mitigated_risks_target = max(1, round(target_coverage * n_risks))

        # Shuffle risk order; assign real mitigations where available
        shuffled_ids = risk_ids_in_scope[:]
        random.shuffle(shuffled_ids)
        selected_risk_ids = set(shuffled_ids[:mitigated_risks_target])

        run_mitigations = [
            m for m in real_mitigations if m.target_risk_id in selected_risk_ids
        ]
        # If a selected risk has no real mitigation, add a synthetic one
        covered_ids = {m.target_risk_id for m in run_mitigations}
        for rid in selected_risk_ids - covered_ids:
            run_mitigations.append(SimulatedMitigation(
                id=f"SYN_{rid}",
                target_risk_id=rid,
                effectiveness=random.choice(EFFECTIVENESS_LEVELS),
            ))

        scenario = SimulationScenario(
            risks=run_risks,
            influences=list(real_influences),
            mitigations=run_mitigations,
        )
        calculate_scenario_exposures(scenario)

        total_base = sum(r.base_exposure for r in run_risks)
        total_final = sum(scenario.risk_exposures.values())
        n_mitigated = len({m.target_risk_id for m in run_mitigations})
        avg_strength = (
            np.mean([INFLUENCE_STRENGTH_SCORES.get(inf.strength, 0.5) for inf in real_influences])
            if real_influences else 0.0
        )

        results.append({
            "simulation_id": i + 1,
            "n_risks": n_risks,
            "n_influences": len(real_influences),
            "avg_influence_strength": avg_strength,
            "n_mitigations": len(run_mitigations),
            "n_risks_mitigated": n_mitigated,
            "mitigation_coverage": n_mitigated / n_risks if n_risks else 0,
            "total_base_exposure": total_base,
            "total_final_exposure": total_final,
            "residual_risk_pct": scenario.global_residual_pct,
            "weighted_risk_score": scenario.global_risk_score,
            "max_single_exposure": scenario.max_exposure,
            "avg_likelihood": np.mean([r.likelihood for r in run_risks]),
            "avg_severity": np.mean([r.severity for r in run_risks]),
            "param_mode": "Random L×I" if randomize_params else "Real L×I",
        })

        if progress_callback and (i + 1) % 50 == 0:
            progress_callback(i + 1, n_simulations)

    return pd.DataFrame(results)


def _compute_sb_and_store(
    manager,
    scope_ids: Optional[List[str]],
    scope_label: str,
    n_simulations: int,
    coverage_variance: float,
    randomize_params: bool,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float],
    include_inactive: bool = False,
) -> None:
    """Run the scope-based Monte Carlo and store the result in session state.

    Separating compute from render ensures the 💾 Save Results button works on
    the rerun triggered by clicking it (run_button is False on that rerun, so the
    old monolithic function was never called and the button click was lost).
    """
    # Clear any previous result so the render section won't show stale data
    # if something goes wrong mid-compute.
    st.session_state["last_sb_result"] = None

    with st.spinner("Loading data from DB…"):
        real_risks, real_influences, real_mitigations = _load_scope_data(
            manager, scope_ids, include_inactive=include_inactive
        )

    if not real_risks:
        st.warning("No risks found for the active scope. Check your DB connection and scope settings.")
        return

    # Compute latent count once during compute so it's stored with the result.
    latent_count = 0
    if include_inactive:
        normal_risks, _, _ = _load_scope_data(manager, scope_ids, include_inactive=False)
        latent_count = len(real_risks) - len(normal_risks)

    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(current, total):
        progress_bar.progress(current / total)
        status_text.text(f"Running simulation {current}/{total}…")

    start_time = datetime.now()
    df = run_scope_based_monte_carlo(
        real_risks, real_influences, real_mitigations,
        n_simulations, coverage_variance, randomize_params,
        likelihood_range, severity_range,
        progress_callback=update_progress,
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    progress_bar.progress(1.0)
    status_text.text(f"✅ Completed {n_simulations} simulations in {elapsed:.2f}s")

    if df.empty:
        st.error("Simulation returned no results.")
        return

    # Store the full result for persistent rendering across reruns.
    st.session_state["last_sb_result"] = {
        "df": df,
        "scope_label": scope_label,
        "include_inactive": include_inactive,
        "latent_count": latent_count,
        "n_risks": len(real_risks),
        "n_influences": len(real_influences),
        "n_mitigations": len(real_mitigations),
        "n_simulations": n_simulations,
        "coverage_variance": coverage_variance,
        "randomize_params": randomize_params,
        "likelihood_range": likelihood_range,
        "severity_range": severity_range,
        "mode": "Scope-Based (Worst-Case)" if include_inactive else "Scope-Based (Real Data)",
        "timestamp": datetime.now(),
    }


def _render_sb_results(stored: dict) -> None:
    """Render scope-based simulation results from a stored result dict.

    Called every rerun when last_sb_result is set — including the rerun
    triggered by clicking 💾 Save Results — which is what makes the save work.
    """
    df = stored["df"]
    scope_label = stored["scope_label"]
    include_inactive = stored["include_inactive"]
    latent_count = stored["latent_count"]
    n_simulations = stored["n_simulations"]
    coverage_variance = stored["coverage_variance"]
    randomize_params = stored["randomize_params"]
    likelihood_range = stored["likelihood_range"]
    severity_range = stored["severity_range"]
    mode = stored["mode"]
    ts = stored["timestamp"].strftime("%H:%M:%S")

    st.header("🗺️ Scope-Based Simulation Results")
    st.caption(
        f"Scope: **{scope_label}** | "
        f"Mode: **{'Random L×I' if randomize_params else 'Real L×I'}** | "
        f"Run at {ts}"
    )

    # F31c — worst-case canvas banner
    if include_inactive and latent_count > 0:
        st.warning(
            f"🧟 **Worst-Case Canvas**: {latent_count} lifecycle-inactive risk"
            f"{'s' if latent_count != 1 else ''} re-activated "
            f"(accepted / watching / suppressed / closed)."
        )

    st.info(
        f"**{stored['n_risks']} risks** | **{stored['n_influences']} influences** | "
        f"**{stored['n_mitigations']} mitigation assignments** | "
        f"**{n_simulations} simulations**"
    )

    # Summary statistics
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean Residual Risk %", f"{df['residual_risk_pct'].mean():.1f}%")
        st.metric("Std Dev", f"{df['residual_risk_pct'].std():.1f}%")
    with col2:
        st.metric("Mean Risk Score", f"{df['weighted_risk_score'].mean():.1f}")
        st.metric("Std Dev", f"{df['weighted_risk_score'].std():.1f}")
    with col3:
        st.metric("Mean Max Exposure", f"{df['max_single_exposure'].mean():.1f}")
        st.metric("Std Dev", f"{df['max_single_exposure'].std():.1f}")
    with col4:
        st.metric("Mean Coverage", f"{df['mitigation_coverage'].mean()*100:.1f}%")
        st.metric("Risks in Scope", stored["n_risks"])

    # Save + export row
    col_save, col_dl, col_spacer = st.columns([2, 2, 5])
    with col_save:
        _render_save_results_button(
            df=df,
            mode=mode,
            scope_label=scope_label,
            params={
                "n_simulations": n_simulations,
                "coverage_variance": coverage_variance,
                "param_mode": "Random L×I" if randomize_params else "Real L×I",
                "likelihood_range": likelihood_range if randomize_params else "real",
                "severity_range": severity_range if randomize_params else "real",
                "scope_label": scope_label,
                "worst_case_canvas": include_inactive,
            },
            button_key="save_sb",
        )
    with col_dl:
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export CSV",
            csv,
            f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            key="dl_sb_quick",
        )

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 Distributions", "☁️ Scatter Clouds", "📋 Data"])

    with tab1:
        render_distribution_plots(df)

    with tab2:
        fig = px.scatter(
            df, x="mitigation_coverage", y="residual_risk_pct",
            color="avg_influence_strength",
            size="n_influences" if df["n_influences"].max() > 0 else None,
            hover_data=["n_mitigations", "max_single_exposure"],
            title="Mitigation Coverage vs Residual Risk",
            labels={
                "mitigation_coverage": "Mitigation Coverage",
                "residual_risk_pct": "Residual Risk %",
                "avg_influence_strength": "Avg Influence Strength",
            },
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_traces(marker=dict(opacity=0.6))
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(
                df, x="total_base_exposure", y="total_final_exposure",
                color="mitigation_coverage",
                title="Base vs Final Exposure",
                labels={
                    "total_base_exposure": "Total Base Exposure",
                    "total_final_exposure": "Total Final Exposure",
                    "mitigation_coverage": "Coverage",
                },
                color_continuous_scale="RdYlGn_r",
            )
            max_val = max(df["total_base_exposure"].max(), df["total_final_exposure"].max())
            fig.add_trace(go.Scatter(
                x=[0, max_val], y=[0, max_val],
                mode="lines", line=dict(dash="dash", color="gray"),
                name="No Mitigation",
            ))
            fig.update_traces(marker=dict(opacity=0.5, size=5), selector=dict(mode="markers"))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.histogram(
                df, x="weighted_risk_score", nbins=40,
                title="Risk Score Distribution",
                labels={"weighted_risk_score": "Risk Score"},
                color_discrete_sequence=["#e74c3c"],
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Results (CSV)",
            csv,
            "scope_based_results.csv",
            "text/csv",
            key="dl_sb_data_tab",
        )


# =============================================================================
# RESULTS STORAGE — F31b
# =============================================================================

def _render_save_results_button(
    df: pd.DataFrame,
    mode: str,
    scope_label: str,
    params: dict,
    button_key: str,
) -> None:
    """Render a 💾 Save Results button and append to saved_simulations on click."""
    if st.button("💾 Save Results", key=button_key):
        record = SimulationRecord(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            mode=mode,
            scope_label=scope_label,
            params=params,
            key_metrics={
                "mean_residual_risk_pct": float(df["residual_risk_pct"].mean()),
                "std_residual_risk_pct": float(df["residual_risk_pct"].std()),
                "mean_risk_score": float(df["weighted_risk_score"].mean()),
                "mean_max_exposure": float(df["max_single_exposure"].mean()),
                "mean_coverage": float(df["mitigation_coverage"].mean()),
                "n_simulations": len(df),
            },
            df=df.copy(),
        )
        if st.session_state.saved_simulations is None:
            st.session_state.saved_simulations = []
        st.session_state.saved_simulations.append(record)
        st.success(f"✅ Saved run #{len(st.session_state.saved_simulations)}")


def _render_saved_results_tab() -> None:
    """Render the 📊 Saved Results comparison tab."""
    saved: List[SimulationRecord] = st.session_state.get("saved_simulations") or []

    if not saved:
        st.info("No saved simulations yet. Run a simulation and click **💾 Save Results**.")
        return

    st.subheader(f"📊 {len(saved)} Saved Run{'s' if len(saved) != 1 else ''}")

    # ── Comparison table ─────────────────────────────────────────────────────
    rows = []
    for i, rec in enumerate(saved):
        m = rec.key_metrics
        row: Dict[str, Any] = {
            "#": i + 1,
            "Timestamp": rec.timestamp.strftime("%H:%M:%S"),
            "Mode": rec.mode,
            "Scope": rec.scope_label,
            "Mean Residual %": round(m["mean_residual_risk_pct"], 1),
            "± Std": round(m["std_residual_risk_pct"], 1),
            "Mean Risk Score": round(m["mean_risk_score"], 1),
            "Mean Max Exposure": round(m["mean_max_exposure"], 1),
            "Coverage %": round(m["mean_coverage"] * 100, 1),
            "N Sims": m["n_simulations"],
        }
        if i > 0:
            base = saved[0].key_metrics
            row["Δ Residual %"] = round(m["mean_residual_risk_pct"] - base["mean_residual_risk_pct"], 1)
            row["Δ Risk Score"] = round(m["mean_risk_score"] - base["mean_risk_score"], 1)
        else:
            row["Δ Residual %"] = "—"
            row["Δ Risk Score"] = "—"
        rows.append(row)

    summary_df = pd.DataFrame(rows)

    def _colour_delta(val):
        if isinstance(val, str):
            return ""
        if val > 0:
            return "color: #e74c3c"   # red = worse
        if val < 0:
            return "color: #27ae60"   # green = better
        return ""

    styled = summary_df.style.applymap(
        _colour_delta, subset=["Δ Residual %", "Δ Risk Score"]
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Per-run expanders ─────────────────────────────────────────────────────
    for i, rec in enumerate(saved):
        with st.expander(f"Run #{i+1} — {rec.mode} — {rec.timestamp.strftime('%H:%M:%S')}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Parameters**")
                st.json(rec.params)
            with col2:
                st.markdown("**Key Metrics**")
                st.json(rec.key_metrics)
            st.dataframe(rec.df.head(50), use_container_width=True)

    st.markdown("---")

    # ── Export all runs to Excel ──────────────────────────────────────────────
    col_exp, col_clr = st.columns([3, 1])

    with col_exp:
        if st.button("📥 Export All Runs (Excel)", key="export_excel"):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                for i, rec in enumerate(saved):
                    mode_short = rec.mode.split(" ")[0]  # "Monte", "Mitigation", "Scope-Based"
                    ts = rec.timestamp.strftime("%H%M%S")
                    sheet_name = f"Run{i+1}_{mode_short}_{ts}"[:31]  # Excel 31-char limit
                    rec.df.to_excel(writer, sheet_name=sheet_name, index=False)
            buf.seek(0)
            st.download_button(
                "⬇️ Download Excel",
                data=buf,
                file_name=f"rim_simulations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_excel",
            )

    with col_clr:
        confirm_clear = st.checkbox("Confirm clear", key="confirm_clear_sims")
        if st.button("🗑️ Clear All", key="clear_all_sims", disabled=not confirm_clear):
            st.session_state.saved_simulations = []
            st.rerun()


# =============================================================================
# TRI α CALIBRATION MODE — F31d
# =============================================================================

# Target quadrant profiles for recommended α selection
_TAC_PROFILES: Dict[str, Dict[str, float]] = {
    "Balanced": {
        "critical_pct": 25.0, "frequency_pct": 25.0,
        "severity_pct": 25.0, "marginal_pct": 25.0,
    },
    "Tail-Heavy (Critical dominant)": {
        "critical_pct": 40.0, "frequency_pct": 20.0,
        "severity_pct": 25.0, "marginal_pct": 15.0,
    },
    "Frequency-Heavy": {
        "critical_pct": 20.0, "frequency_pct": 45.0,
        "severity_pct": 15.0, "marginal_pct": 20.0,
    },
    "Severity-Heavy": {
        "critical_pct": 20.0, "frequency_pct": 10.0,
        "severity_pct": 50.0, "marginal_pct": 20.0,
    },
}


def _run_alpha_sweep(
    real_risks: List[SimulatedRisk],
    real_influences: List[SimulatedInfluence],
    real_mitigations: List[SimulatedMitigation],
    alpha_values: List[float],
    runs_per_alpha: int,
    randomize_params: bool,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float],
    progress_callback=None,
) -> pd.DataFrame:
    """For each α value, run Monte Carlo and compute TRI + quadrant statistics.

    Returns a DataFrame with one row per α:
      alpha | mean_tri | std_tri | p95_tri | critical_pct | frequency_pct |
      severity_pct | marginal_pct
    """
    if not real_risks:
        return pd.DataFrame()

    rows = []
    total_steps = len(alpha_values) * runs_per_alpha
    step = 0

    for alpha in alpha_values:
        tri_values: List[float] = []
        quadrant_counts: Dict[str, int] = {
            "critical": 0, "frequency": 0, "severity": 0, "marginal": 0
        }
        total_risk_runs = 0

        for run_i in range(runs_per_alpha):
            if randomize_params:
                run_risks = [
                    SimulatedRisk(
                        id=r.id, name=r.name, level=r.level,
                        likelihood=random.uniform(*likelihood_range),
                        severity=random.uniform(*severity_range),
                    )
                    for r in real_risks
                ]
            else:
                run_risks = list(real_risks)

            for r in run_risks:
                tri = r.likelihood * (r.severity ** alpha)
                tri_values.append(tri)
                q = _compute_risk_quadrant(r.likelihood, r.severity)
                quadrant_counts[q] += 1
                total_risk_runs += 1

            step += 1
            if progress_callback and step % max(1, total_steps // 100) == 0:
                progress_callback(step, total_steps)

        n = len(tri_values)
        q_total = total_risk_runs or 1
        rows.append({
            "alpha": round(float(alpha), 4),
            "mean_tri": float(np.mean(tri_values)),
            "std_tri": float(np.std(tri_values)),
            "p95_tri": float(np.percentile(tri_values, 95)),
            "critical_pct": round(quadrant_counts["critical"] / q_total * 100, 1),
            "frequency_pct": round(quadrant_counts["frequency"] / q_total * 100, 1),
            "severity_pct": round(quadrant_counts["severity"] / q_total * 100, 1),
            "marginal_pct": round(quadrant_counts["marginal"] / q_total * 100, 1),
        })

    return pd.DataFrame(rows)


def _find_recommended_alpha(calib_df: pd.DataFrame, target_profile: str) -> float:
    """Return the α value whose quadrant distribution best matches the target profile."""
    target = _TAC_PROFILES[target_profile]
    best_alpha = float(calib_df["alpha"].iloc[0])
    best_dist = float("inf")
    for _, row in calib_df.iterrows():
        dist = sum(
            (row[k] - target[k]) ** 2
            for k in ("critical_pct", "frequency_pct", "severity_pct", "marginal_pct")
        ) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_alpha = float(row["alpha"])
    return best_alpha


def _render_tri_alpha_about_expander() -> None:
    """Instructions shown when TRI α Calibration mode is selected but not run."""
    with st.expander("📖 About TRI α Calibration", expanded=True):
        st.markdown(f"""
### What is TRI α?

The **Tail Risk Indicator (TRI)** is a secondary metric that emphasises catastrophic,
low-frequency risks:

> **TRI = Likelihood × Severity^α**

The exponent **α** controls how strongly severity is amplified:
- **α = 1.0** — TRI equals base exposure (L × S), no amplification.
- **α = 1.5** — current schema default; moderate tail emphasis.
- **α = 2.0+** — strong tail emphasis; high-severity risks dominate the portfolio.

### What does this mode do?

This mode sweeps α from your chosen minimum to maximum, runs **N Monte Carlo
iterations per α value** using real graph data, and records:
- Mean / Std / P95 TRI across all risks × runs.
- Quadrant distribution shift (Critical / Frequency / Severity / Marginal %).

The output helps you select a domain-appropriate α. Compare the quadrant
distribution to your domain expectation, then update `tri_alpha` in
`schemas/[domain]/schema.yaml` to persist the calibrated value.

### Current default
`TRI_ALPHA = {TRI_ALPHA}` (hardcoded in `services/exposure_calculator.py`)
        """)


def _compute_tac_and_store(
    manager,
    scope_ids: Optional[List[str]],
    scope_label: str,
    alpha_min: float,
    alpha_max: float,
    alpha_step: float,
    runs_per_alpha: int,
    randomize_params: bool,
    likelihood_range: Tuple[float, float],
    severity_range: Tuple[float, float],
    include_inactive: bool = False,
) -> None:
    """Run the TRI α sweep and store the result in session state (F31d compute half).

    Separating compute from render ensures the 💾 Save Calibration Results button
    works on the rerun triggered by clicking it.
    """
    st.session_state["last_tac_result"] = None  # clear stale result

    if alpha_min >= alpha_max:
        st.error("α Min must be less than α Max.")
        return

    with st.spinner("Loading data from DB…"):
        real_risks, real_influences, real_mitigations = _load_scope_data(
            manager, scope_ids, include_inactive=include_inactive
        )

    if not real_risks:
        st.warning("No risks found for the active scope. Check your DB connection and scope settings.")
        return

    latent_count = 0
    if include_inactive:
        normal_risks, _, _ = _load_scope_data(manager, scope_ids, include_inactive=False)
        latent_count = len(real_risks) - len(normal_risks)

    alpha_values = list(np.arange(alpha_min, alpha_max + alpha_step / 2, alpha_step))
    n_alpha = len(alpha_values)
    total_runs = n_alpha * runs_per_alpha

    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(current, total):
        progress_bar.progress(current / total)
        status_text.text(f"Computing… {current:,}/{total:,} risk-runs")

    start_time = datetime.now()
    calib_df = _run_alpha_sweep(
        real_risks, real_influences, real_mitigations,
        alpha_values, runs_per_alpha, randomize_params,
        likelihood_range, severity_range,
        progress_callback=update_progress,
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    progress_bar.progress(1.0)
    status_text.text(f"✅ Calibration complete in {elapsed:.2f}s")

    if calib_df.empty:
        st.error("Calibration returned no results.")
        return

    st.session_state["last_tac_result"] = {
        "calib_df": calib_df,
        "scope_label": scope_label,
        "include_inactive": include_inactive,
        "latent_count": latent_count,
        "n_risks": len(real_risks),
        "alpha_min": alpha_min,
        "alpha_max": alpha_max,
        "alpha_step": alpha_step,
        "alpha_values": alpha_values,
        "n_alpha": n_alpha,
        "runs_per_alpha": runs_per_alpha,
        "total_runs": total_runs,
        "randomize_params": randomize_params,
        "likelihood_range": likelihood_range,
        "severity_range": severity_range,
        "timestamp": datetime.now(),
    }


def _render_tac_results(stored: dict) -> None:
    """Render TRI α calibration results from a stored result dict (F31d render half).

    Called every rerun when last_tac_result is set — including the rerun
    triggered by clicking 💾 Save Calibration Results.
    """
    calib_df = stored["calib_df"]
    scope_label = stored["scope_label"]
    include_inactive = stored["include_inactive"]
    latent_count = stored["latent_count"]
    alpha_min = stored["alpha_min"]
    alpha_max = stored["alpha_max"]
    alpha_step = stored["alpha_step"]
    n_alpha = stored["n_alpha"]
    runs_per_alpha = stored["runs_per_alpha"]
    total_runs = stored["total_runs"]
    randomize_params = stored["randomize_params"]
    likelihood_range = stored["likelihood_range"]
    severity_range = stored["severity_range"]
    ts = stored["timestamp"].strftime("%H:%M:%S")

    st.header("📐 TRI α Calibration Results")
    st.caption(
        f"Scope: **{scope_label}** | "
        f"α: {alpha_min} → {alpha_max} (step {alpha_step}) | "
        f"{runs_per_alpha} runs/α | "
        f"Mode: **{'Random L×I' if randomize_params else 'Real L×I'}** | "
        f"Run at {ts}"
    )

    if include_inactive and latent_count > 0:
        st.warning(
            f"🧟 **Worst-Case Canvas**: {latent_count} lifecycle-inactive risk"
            f"{'s' if latent_count != 1 else ''} re-activated."
        )

    st.info(
        f"**{stored['n_risks']} risks** | "
        f"**{n_alpha} α values** × **{runs_per_alpha} runs** = **{total_runs:,} total runs**"
    )

    # ── Target profile selector (interactive — reactive to selectbox changes) ─
    st.markdown("---")
    col_profile, col_spacer = st.columns([2, 3])
    with col_profile:
        target_profile = st.selectbox(
            "Target quadrant profile",
            list(_TAC_PROFILES.keys()),
            index=0,
            help=(
                "Select the quadrant distribution that best reflects your domain's risk profile. "
                "The recommended α minimises the distance to this target."
            ),
            key="tac_target_profile",
        )

    recommended_alpha = _find_recommended_alpha(calib_df, target_profile)

    st.success(
        f"📌 **Recommended α = {recommended_alpha}** for profile *{target_profile}*  "
        f"(current schema default: α = {TRI_ALPHA})"
    )
    if recommended_alpha != TRI_ALPHA:
        st.caption(
            "To apply: update `tri_alpha` under `exposure_model` in "
            "`schemas/[domain]/schema.yaml` and reload the schema."
        )

    # ── Output tabs ───────────────────────────────────────────────────────────
    tab_chart, tab_report, tab_raw = st.tabs(
        ["📈 Calibration Chart", "📋 Calibration Report", "📋 Raw Data"]
    )

    with tab_chart:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=calib_df["alpha"],
            y=calib_df["mean_tri"] + calib_df["std_tri"],
            mode="lines", line=dict(width=0), showlegend=False,
            name="+1σ",
        ))
        fig.add_trace(go.Scatter(
            x=calib_df["alpha"],
            y=calib_df["mean_tri"] - calib_df["std_tri"],
            mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor="rgba(52,152,219,0.15)",
            showlegend=True, name="±1σ band",
        ))
        fig.add_trace(go.Scatter(
            x=calib_df["alpha"],
            y=calib_df["mean_tri"],
            mode="lines+markers", line=dict(color="#3498db", width=2),
            name="Mean TRI",
        ))
        fig.add_trace(go.Scatter(
            x=calib_df["alpha"],
            y=calib_df["p95_tri"],
            mode="lines", line=dict(color="#e74c3c", width=1.5, dash="dash"),
            name="P95 TRI",
        ))
        fig.add_vline(
            x=recommended_alpha, line_dash="dot", line_color="#27ae60",
            annotation_text=f"Recommended α={recommended_alpha}",
            annotation_position="top right",
        )
        fig.add_vline(
            x=TRI_ALPHA, line_dash="dot", line_color="#95a5a6",
            annotation_text=f"Current α={TRI_ALPHA}",
            annotation_position="top left",
        )
        fig.update_layout(
            title="TRI vs α — Mean, ±1σ Band, and P95",
            xaxis_title="α (TRI exponent)",
            yaxis_title="TRI value",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        _bar_colors = {
            "critical_pct": "#c0392b",
            "frequency_pct": "#e67e22",
            "severity_pct": "#8e44ad",
            "marginal_pct": "#95a5a6",
        }
        _bar_labels = {
            "critical_pct": "Critical",
            "frequency_pct": "Frequency",
            "severity_pct": "Severity",
            "marginal_pct": "Marginal",
        }
        for col, color in _bar_colors.items():
            fig2.add_trace(go.Bar(
                x=calib_df["alpha"],
                y=calib_df[col],
                name=_bar_labels[col],
                marker_color=color,
            ))
        fig2.add_vline(x=recommended_alpha, line_dash="dot", line_color="#27ae60")
        fig2.update_layout(
            barmode="stack",
            title="Quadrant Distribution vs α",
            xaxis_title="α (TRI exponent)",
            yaxis_title="% of risk-runs",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab_report:
        target = _TAC_PROFILES[target_profile]
        display_df = calib_df.copy()
        display_df.columns = [
            "α", "Mean TRI", "Std TRI", "P95 TRI",
            "Critical %", "Frequency %", "Severity %", "Marginal %",
        ]

        def _highlight_recommended(row):
            return [
                "background-color: #d5f5e3; font-weight: bold"
                if row["α"] == recommended_alpha else ""
                for _ in row
            ]

        styled = display_df.style.apply(_highlight_recommended, axis=1).format({
            "α": "{:.2f}",
            "Mean TRI": "{:.2f}",
            "Std TRI": "{:.2f}",
            "P95 TRI": "{:.2f}",
            "Critical %": "{:.1f}",
            "Frequency %": "{:.1f}",
            "Severity %": "{:.1f}",
            "Marginal %": "{:.1f}",
        })
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.caption(
            f"Target profile **{target_profile}**: "
            f"Critical {target['critical_pct']:.0f}% | "
            f"Frequency {target['frequency_pct']:.0f}% | "
            f"Severity {target['severity_pct']:.0f}% | "
            f"Marginal {target['marginal_pct']:.0f}%"
        )

        # Save button — rendered every rerun, so the click is always processed.
        col_save_tac, col_dl_tac, _ = st.columns([2, 2, 5])
        with col_save_tac:
            if st.button("💾 Save Calibration Results", key="save_tac"):
                record = SimulationRecord(
                    id=str(uuid.uuid4())[:8],
                    timestamp=datetime.now(),
                    mode="TRI α Calibration",
                    scope_label=scope_label,
                    params={
                        "alpha_min": alpha_min,
                        "alpha_max": alpha_max,
                        "alpha_step": alpha_step,
                        "runs_per_alpha": runs_per_alpha,
                        "param_mode": "Random L×I" if randomize_params else "Real L×I",
                        "target_profile": target_profile,
                        "recommended_alpha": recommended_alpha,
                        "worst_case_canvas": include_inactive,
                    },
                    key_metrics={
                        "recommended_alpha": recommended_alpha,
                        "current_default_alpha": TRI_ALPHA,
                        "n_alpha_values": n_alpha,
                        "n_risks": stored["n_risks"],
                        "total_runs": total_runs,
                        # Stubs for _render_saved_results_tab compatibility
                        "mean_residual_risk_pct": 0.0,
                        "std_residual_risk_pct": 0.0,
                        "mean_risk_score": 0.0,
                        "mean_max_exposure": 0.0,
                        "mean_coverage": 0.0,
                        "n_simulations": total_runs,
                    },
                    df=calib_df.copy(),
                )
                if st.session_state.saved_simulations is None:
                    st.session_state.saved_simulations = []
                st.session_state.saved_simulations.append(record)
                st.success(f"✅ Saved calibration run #{len(st.session_state.saved_simulations)}")
        with col_dl_tac:
            csv = calib_df.to_csv(index=False)
            st.download_button(
                "📥 Export CSV",
                csv,
                f"tac_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                key="dl_tac_report_quick",
            )

    with tab_raw:
        st.dataframe(calib_df, use_container_width=True)
        csv = calib_df.to_csv(index=False)
        st.download_button(
            "📥 Download Calibration Report (CSV)",
            csv,
            f"tri_alpha_calibration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            key="dl_tac_csv",
        )


if __name__ == "__main__":
    main()
