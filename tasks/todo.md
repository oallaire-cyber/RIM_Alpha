# Task: v2.28.0 F6 Mitigation Exposure View
**Stream**: A
**Started**: 2026-03-21
**Target version**: v2.28.0

## Plan
- [x] Add `MITIGATION_EXPOSURE_DEFAULTS` + `init_mitigation_exposure_state()` to `utils/state_manager.py`
- [x] Create `pages/4_📊_Mitigation_Exposure.py` — counterfactual per-mitigation impact page
- [x] Create `docs/help_mitigation_exposure.md`
- [x] Update `docs/help_overview.md`, `docs/welcome.md`
- [x] Update `docs/USER_GUIDE.md` — add Mitigation Exposure View section
- [x] Update `docs/ARCHITECTURE.md` — page diagram + state defaults table
- [x] Update `CHANGELOG.md` — v2.28.0 entry
- [x] Update `ROADMAPv3.md` — F6 marked complete
- [x] Run full test suite → 445 passing
- [x] Update SESSION_STATE.md + todo.md

## Git Commit
```
feat(v2.28.0): F6 Mitigation Exposure View

New page: pages/4_📊_Mitigation_Exposure.py
- Counterfactual per-mitigation impact: for each active mitigation,
  recomputes portfolio exposure with that mitigation disabled to derive
  the marginal EL Delta and TRI Delta attributable to it.
- Scope-aware (respects active FilterManager scope), lifecycle-filtered
  (inactive risks excluded by default), level filter (All/Business/Operational).
- 4-column summary header: Active Mitigations, Portfolio EL, EL Reduction,
  Portfolio TRI.
- Per-mitigation table: Name | Type | Status | Level | Risks Covered |
  EL Delta ↑ | TRI Delta ↑ | % Portfolio EL — sorted by EL delta descending.
- Inline help expander loads docs/help_mitigation_exposure.md.

State manager (utils/state_manager.py):
- MITIGATION_EXPOSURE_DEFAULTS dict (mitexp_* keys).
- init_mitigation_exposure_state() registered in init_all().

Docs: help_mitigation_exposure.md (new); help_overview.md, welcome.md,
USER_GUIDE.md, ARCHITECTURE.md updated. CHANGELOG v2.28.0. ROADMAPv3 F6 done.

445 tests passing.
```
