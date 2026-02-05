# 🎚️ Monte Carlo Calibration Simulator

A standalone Streamlit application for validating and calibrating the RIM exposure calculation model through Monte Carlo simulations.

## 🏃 Quick Start

```bash
# From project root with venv activated
streamlit run calibration_simulator.py
```

Opens at: `http://localhost:8501`

---

## 📋 Purpose

The Calibration Simulator helps you:

1. **Validate Model Behavior** - Ensure exposure calculations produce expected distributions
2. **Sensitivity Analysis** - Understand how parameter changes affect outcomes
3. **Calibrate Parameters** - Fine-tune decay rates, thresholds, and multipliers
4. **Generate Evidence** - Export simulation data for documentation

---

## 🎮 Simulation Modes

### 🎲 Monte Carlo Simulation

Generates random risk scenarios to explore the exposure model's behavior across the parameter space.

**Parameters:**
| Parameter | Description | Default |
|-----------|-------------|---------|
| Number of Simulations | Scenarios to generate | 500 |
| Seed | Random seed for reproducibility | 42 |
| Propagation Decay | Influence decay rate | 0.85 |
| Convergence Multiplier | Amplification at convergence points | 0.20 |
| High Threshold Multiplier | High-exposure threshold factor | 1.20 |
| Apply Mitigation | Include randomly applied mitigations | Yes |

**Output Metrics:**
- `base_exposure` - Raw likelihood × impact score
- `mitigated_exposure` - After mitigation reduction
- `net_exposure` - Final exposure after all factors
- `mitigation_factor` - Combined mitigation effectiveness (0-1)

### 📊 Mitigation Path Analysis

Simulates progressive mitigation application to understand diminishing returns.

**Process:**
1. Start with a fixed base risk (likelihood=7, impact=8)
2. Apply one mitigation at a time
3. Track how net exposure decreases with each addition
4. Observe diminishing returns effect

---

## 📈 Visualizations

### Distribution Tab

| Chart | Purpose |
|-------|---------|
| **Net Exposure Distribution** | Histogram with kernel density - shows where most exposures fall |
| **Box Plots by Decay** | Compare distributions at different decay rates |

### Scatter Clouds Tab

| Chart | Purpose |
|-------|---------|
| **Base vs Net Exposure** | Identify non-linear mitigation effects |
| **Mitigation Factor vs Net** | Visualize mitigation impact curves |
| **Marginal Distributions** | Histograms along axes |

### Heatmap Tab

| Chart | Purpose |
|-------|---------|
| **Decay × Convergence Heatmap** | Mean exposure by parameter combination |
| **Risk Profile Heatmap** | Mean exposure by likelihood × impact |

### 3D Surface Tab

Interactive 3D visualization showing exposure as a function of two varying parameters.

---

## 📊 Statistics Panel

Each simulation run displays:

| Statistic | Description |
|-----------|-------------|
| Mean | Average exposure across all simulations |
| Median | 50th percentile exposure |
| Std Dev | Spread of exposures |
| Min/Max | Range bounds |
| 25th/75th Percentile | Interquartile range |
| % High Exposure | Percentage above threshold |

---

## 💾 Data Export

**Export to CSV** button downloads simulation results including:
- All input parameters
- Calculated metrics
- Timestamp for reproducibility

File format: `simulation_results_YYYYMMDD_HHMMSS.csv`

---

## 🎯 Common Use Cases

### 1. Validate Default Parameters

Run Monte Carlo with defaults to ensure:
- Mean exposure is reasonable (typically 20-40)
- Distribution is not skewed excessively
- High exposure percentage is around 5-15%

### 2. Tune Decay Rate

If influence propagation seems too strong/weak:
1. Run simulations at decay values 0.70, 0.85, 1.00
2. Compare distribution spreads on box plot
3. Choose value that gives desired propagation behavior

### 3. Calibrate Mitigation Impact

If mitigations feel too/not effective enough:
1. Use Mitigation Path Analysis
2. Observe diminishing returns curve shape
3. Adjust effectiveness multipliers as needed

### 4. Document Model Behavior

For audits or stakeholder presentations:
1. Run representative simulations
2. Export CSV data
3. Screenshot key visualizations
4. Include in methodology documentation

---

## 🔗 Related Documentation

| Document | Description |
|----------|-------------|
| [Methodology](docs/METHODOLOGY.md) | Exposure calculation formulas |
| [User Guide](docs/USER_GUIDE.md) | Main app features |
| [Architecture](docs/ARCHITECTURE.md) | Code structure |

---

## 📁 File Reference

| File | Lines | Description |
|------|-------|-------------|
| `calibration_simulator.py` | ~1,100 | Main Streamlit application |
| `services/exposure_calculator.py` | ~565 | Exposure calculation engine used by simulator |
