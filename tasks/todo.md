# Task: Pre-Iteration 6 Manual Test & Fix Campaign
**Session**: 2026-03-23
**Target**: Complete manual test execution against v2.30.0 before Iteration 6 begins

## Deliverables (done)
- [x] Define user roles (R1–R4)
- [x] Create `scripts/tc08_feature_coverage.cypher` (TC08 dataset)
- [x] Add `tc08_feature_coverage` scope to `schemas/default/schema.yaml`
- [x] Create `tasks/MANUAL_TEST_SCRIPT.md` (34 tests, exact expected results)

## Test Execution (user action required)
- [ ] A1–A4: Setup & Configuration tests
- [ ] B1–B8: Data Management tests
- [ ] C1–C12: Dashboard & Visualization tests (includes TC01/TC03/TC04/TC05/TC07 math + TC08 TRI)
- [ ] D1–D4: Analysis Tools tests
- [ ] E1–E6: Simulation tests

## After each failed test
- [ ] Log bug to `tasks/lessons.md`
- [ ] Fix bug in relevant file
- [ ] Re-run `pytest` → confirm 445 still pass
- [ ] Re-run the specific test that was failing

## Session sign-off
- [ ] All tests pass (or documented skip)
- [ ] 445 pytest tests still green
- [ ] `tasks/SESSION_STATE.md` updated for next session
