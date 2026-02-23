### 🛡️ Mitigation Model

Mitigations represent controls, actions, or safeguards
that reduce risk exposure. One mitigation can address
multiple risks, and one risk can have multiple mitigations.

---

**Mitigation Types:**

| Type | Description | Visual |
|------|-------------|--------|
| Dedicated | Program-specific controls | Teal, solid border |
| Inherited | From corporate or other programs | Blue, dotted border |
| Baseline | Standards, regulations, best practices | Purple, thick border |

---

**Status Levels:**
- ✅ **Implemented** — Active protection
- 🔄 **In Progress** — Being deployed
- 📋 **Proposed** — Planned, not yet started
- ⏸️ **Deferred** — On hold

---

**Effectiveness Levels:**

| Level | Reduction | When to use |
|-------|-----------|-------------|
| Critical | 90% | Eliminates root cause |
| High | 70% | Significantly reduces probability or impact |
| Medium | 50% | Moderate reduction |
| Low | 30% | Minor reduction |

---

**Mitigation Analysis** *(scope-aware)*:
- **Coverage Overview**: Risks with/without mitigations
- **Treatment Explorer**: Detailed per-risk mitigation status
- **High-Priority Unmitigated**: Flags risks that are unmitigated
  AND are top propagators, convergence points, or bottlenecks

**Strategic Advice:**
- Mitigate upstream risks first (influence limitation principle)
- Prioritize high-exposure, high-influence risks
- Review coverage gaps regularly in the Analysis tab
