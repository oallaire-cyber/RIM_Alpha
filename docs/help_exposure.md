### ⚡ Exposure Calculation

Quantifies risk severity by combining base scores,
mitigation effectiveness, and upstream influence limitation.

---

**1️⃣ Base Exposure**
```
Base = Likelihood × Impact
```
*Scale: 1-10 each → Base ranges 1 to 100*

---

**2️⃣ Mitigation Factor** *(diminishing returns)*
```
Factor = ∏(1 - Effectiveness)
```

| Effectiveness | Reduction | Description |
|---------------|-----------|-------------|
| Critical | 90% | Near-complete elimination |
| High | 70% | Strong protection |
| Medium | 50% | Moderate reduction |
| Low | 30% | Minimal impact |

*Example: High + Medium = 0.3 × 0.5 = 0.15 → 85% total reduction*

---

**3️⃣ Influence Limitation**

Upstream risks **limit** downstream mitigation effectiveness:
```
Limitation = Avg(Upstream_Residual × Strength)
```

*"Fixing symptoms without addressing root causes has limited effect"*

| Strength | Weight | Interpretation |
|----------|--------|----------------|
| Critical | 1.0 | Direct, inevitable |
| Strong | 0.75 | High probability |
| Moderate | 0.50 | Likely contributes |
| Weak | 0.25 | Minor contribution |

---

**4️⃣ Final Exposure**
```
Final = Base × Effective_Mitigation_Factor
```

---

**📊 Global Metrics**

| Metric | Purpose |
|--------|---------|
| Residual Risk % | How much risk remains after mitigations |
| Weighted Risk Score | Impact²-weighted executive metric (0-100) |
| Max Single Exposure | Worst-case individual risk alert |

> **Scope-aware:** When a scope is active, exposure only
> considers in-scope risks and their connected mitigations.
> Toggle "Show connected neighbors" to include adjacent risks.
