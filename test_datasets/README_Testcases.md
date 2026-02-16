# RIM Test Datasets

## Overview

These Excel files contain test data for validating and demonstrating the **Risk Influence Map (RIM)** exposure calculation model.

Each test case isolates a specific aspect of the calculation logic to make it easy to verify and visualize the behavior.

---

## Quick Reference: Exposure Calculation Formula

```
Base Exposure = Likelihood × Impact  (scale 1-10 each, max = 100)

Mitigation Factor = ∏(1 - Effectiveness_i)
  - Critical: 0.9 reduction → factor = 0.1
  - High:     0.7 reduction → factor = 0.3  
  - Medium:   0.5 reduction → factor = 0.5
  - Low:      0.3 reduction → factor = 0.7

Influence Limitation = Avg(Upstream_Residual_Norm × Strength)
  - Residual_Norm = Final_Exposure / Base_Exposure (of upstream risk)
  - Strength: Critical=1.0, Strong=0.75, Moderate=0.5, Weak=0.25

Effective Mitigation Factor = Mit_Factor + (1 - Mit_Factor) × Limitation

Final Exposure = Base_Exposure × Effective_Mitigation_Factor
```

---

## Test Cases

### TC01 - Baseline
**Purpose:** Establish baseline with simplest possible values.

| Risk | L | I | Base | Mitigations | Influences | Final |
|------|---|---|------|-------------|------------|-------|
| Business Risk 1 | 1 | 1 | 1 | None | None | 1 |
| Business Risk 2 | 1 | 1 | 1 | None | None | 1 |
| Operational Risk 1 | 1 | 1 | 1 | None | None | 1 |
| Operational Risk 2 | 1 | 1 | 1 | None | None | 1 |

**Expected:** All risks show Final Exposure = 1, Residual Risk % = 100%

---

### TC02 - Simple Chain
**Purpose:** Demonstrate linear influence propagation.

```
Operational Risk 1 ──[Critical]──► Operational Risk 2 ──[Critical]──► Business Risk 1
     (L=10, I=10)                      (L=5, I=5)                       (L=5, I=5)
     NO mitigation                   NO mitigation                    NO mitigation
```

**Expected:** 
- Op1: Base=100, Final=100 (no mitigation)
- Op2: Base=25, but influenced by fully exposed Op1
- Bus1: Base=25, cascading influence from chain

**Key Learning:** Unmitigated upstream risk propagates through the entire chain.

---

### TC03 - Mitigation Effect
**Purpose:** Demonstrate the multiplicative mitigation model.

All risks have Base Exposure = 100 (L=10, I=10).

| Risk | Mitigations | Factor Calculation | Final Exposure |
|------|-------------|-------------------|----------------|
| No Mitigation | None | 1.0 | 100 |
| Low Mitigation | 1× Low | 1 - 0.3 = 0.7 | 70 |
| Medium Mitigation | 1× Medium | 1 - 0.5 = 0.5 | 50 |
| High Mitigation | 1× High | 1 - 0.7 = 0.3 | 30 |
| Critical Mitigation | 1× Critical | 1 - 0.9 = 0.1 | 10 |
| Double Medium | 2× Medium | 0.5 × 0.5 = 0.25 | 25 |
| High + Medium | High + Medium | 0.3 × 0.5 = 0.15 | 15 |
| Triple Low | 3× Low | 0.7³ = 0.343 | 34.3 |

**Key Learning:** Multiple weak mitigations (3× Low = 34.3) are LESS effective than one strong mitigation (1× High = 30). Demonstrates diminishing returns.

---

### TC04 - Influence Limitation
**Purpose:** Show how upstream risk residual limits downstream mitigation effectiveness.

All targets have **Critical mitigation** (Factor = 0.1), but differ by their upstream influence:

```
Upstream Unmitigated (100/100 = 1.0 residual) ────[Critical]───► Downstream Target A
Upstream Well Mitigated (10/100 = 0.1 residual) ──[Critical]───► Downstream Target B
                                                     (no influence) Downstream No Influence
```

**Expected Results:**

| Target | Influenced By | Limitation | Effective Factor | Final |
|--------|---------------|------------|------------------|-------|
| No Influence | None | 0.0 | 0.1 | 10 |
| Target B | Well Mitigated | 0.1 | 0.1 + 0.9×0.1 = 0.19 | 19 |
| Target A | Unmitigated | 1.0 | 0.1 + 0.9×1.0 = 1.0 | **100** |

**Key Learning:** Target A has Critical mitigation but NO effective reduction because the unmitigated upstream risk fully limits its effectiveness! This is the most important concept in the model.

---

### TC05 - Convergence Point
**Purpose:** Show how multiple upstream influences combine (via averaging).

```
Source A (Unmitigated, residual=1.0) ───┐
Source B (Medium, residual=0.5)     ────┼──[All Critical]──► Convergence Point
Source C (Critical, residual=0.1)   ────┤                   (Critical mitigation)
Source D (Critical, residual=0.1)   ────┘
```

**Calculation:**
- Limitation = (1.0 + 0.5 + 0.1 + 0.1) / 4 = 0.425
- Effective Factor = 0.1 + 0.9 × 0.425 = 0.4825
- Final Exposure = 100 × 0.4825 ≈ **48.25**

**Key Learning:** ONE unmitigated source significantly degrades protection, even when 3 out of 4 sources are well-mitigated.

---

### TC06 - Full Chain
**Purpose:** Complete demonstration with two parallel chains converging.

```
CHAIN 1 (Well-mitigated):              CHAIN 2 (Gap at source):

Chain1 Source [Critical] ──┐           Chain2 Source [NONE!] ──┐
         │ Strong          │                    │ Strong       │
         ▼                 │                    ▼              │
Chain1 Middle [High] ──────┤           Chain2 Middle [High] ───┤
         │ Strong          │                    │ Strong       │
         ▼                 │                    ▼              │
Chain1 Target [Medium] ────┼─► Moderate  Chain2 Target [Medium]─┘
                           │                    │ Moderate
                           └────────────► Final Convergence [High]
```

**Expected:**
- Chain 1: Low residual propagates through the well-mitigated chain
- Chain 2: Despite High+Medium mitigations on middle/target, the unmitigated source limits effectiveness throughout
- Final: Degraded by Chain 2's high residual

**Key Learning:** This demonstrates the CRITICAL importance of mitigating root causes!

---

### TC07 - Influence Strengths
**Purpose:** Show how influence strength acts as a "coupling factor."

Same unmitigated source (residual=1.0) influences 4 targets with different strengths:

| Target | Strength | Limitation | Effective Factor | Final |
|--------|----------|------------|------------------|-------|
| Weak Influence | 0.25 | 0.25 | 0.1 + 0.225 = 0.325 | 32.5 |
| Moderate Influence | 0.50 | 0.50 | 0.1 + 0.45 = 0.55 | 55 |
| Strong Influence | 0.75 | 0.75 | 0.1 + 0.675 = 0.775 | 77.5 |
| Critical Influence | 1.00 | 1.00 | 0.1 + 0.9 = 1.0 | 100 |

**Key Learning:** Weak influence partially insulates the target from upstream issues. Use Weak when the connection is possible but not certain; use Critical when it's direct causation.

---

## How to Use

1. **Start the RIM application**
2. **Clear existing data** (if needed) in the database
3. **Go to Import/Export tab**
4. **Upload one TC*.xlsx file**
5. **View the visualization** - observe node sizes (exposure), colors (levels)
6. **Check exposure calculations** - verify against expected values above
7. **Experiment** - add/remove mitigations or influences and observe changes

---

## Validation Checklist

For each test case, verify:

- [ ] Base Exposure = L × I
- [ ] Mitigation Factor matches multiplicative formula
- [ ] Influence Limitation reflects upstream residuals
- [ ] Effective Factor = Mit_Factor + (1 - Mit_Factor) × Limitation
- [ ] Final Exposure = Base × Effective_Factor
- [ ] Global metrics (Residual %, Weighted Score) are reasonable

---

## Notes

- All test cases use the **default schema** (Business/Operational levels)
- Influence strengths: Weak=0.25, Moderate=0.5, Strong=0.75, Critical=1.0
- Effectiveness: Low=0.3, Medium=0.5, High=0.7, Critical=0.9
- Risks are processed in topological order (sources before targets)
