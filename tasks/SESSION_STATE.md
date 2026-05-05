# RIM Session State
> **Purpose**: Enables seamless handoff between conversations without information loss.
> Update this file at the END of every session or before a major context switch.
> Claude Code reads this at the START of every new session.

---

## Current Version
`v2.32.0` — Pre-Iteration 6 Bug Fix Release. Branch: `fix/test_fix`.

## Last Updated
2026-05-05 — TC-11 ROOT CAUSE FIXED. Manual re-import test verified: 0 created across all entity types.
Phase A coherence cleanup (A1, A3, A5) + context node/edge round-trip hardening committed alongside.
445 tests passing. Ready for commit + merge to main.

---

## ✅ TC-11 RESOLVED

**Root cause**: Excel + JSON export used `manager.get_semantic_influences()` which **concatenates kernel
INFLUENCES (Risk→Risk) PLUS kernel MITIGATES (Mitigation→Risk, normalized to `source_id`/`target_id`)**
into a single Influences sheet. The same MITIGATES rows were also written to the dedicated Mitigates
sheet — so every export emitted MITIGATES twice. App-layer + DB-layer dedup were correct for clean
Risk→Risk pairs, but the contaminated Influences sheet caused 67 mitigates rows to fail the importer's
`MATCH (source:Risk)` check (silently counted as skips while the same data was re-created via the
Mitigates sheet path), and the 64 Risk→Risk influences were treated as duplicates of edges that didn't
exist on the right node pair under the contaminated shape.

**Fix**: switched export to `manager.get_all_influences()` (Risk→Risk only). Mitigates remain captured
via the dedicated Mitigates sheet/key fed by `get_all_mitigates_relationships()`. JSON restore-dedup
set in `backup_service.py:175` switched to match. Exposure engine and analysis paths still use
`get_semantic_influences()` (correct for math).

**Verification (manual, by user, 2026-05-05)**:
```
Import Summary
Created:  Risks: 0, TPOs: 0, Influences: 0, TPO Impacts: 0, Mitigations: 0, Mitigates: 0
Skipped:  Risks: 89, TPOs: 0, Influences: 64, TPO Impacts: 0, Mitigations: 49, Mitigates: 67,
          Context Nodes: 9, Context Edges: 18
```

---

## 🧹 Phase A Cleanup (also in v2.32.0)

| Step | File | Change |
|------|------|--------|
| **A1** | `schemas/default/schema.yaml` | Trimmed legacy `entities.tpo` block to just `clusters:` registry — dropped duplicate `neo4j_label` / `attributes` / `custom_attributes` (live attribute definitions are in `context_nodes.tpo`). |
| **A3** | `services/import_service.py` | Removed dead `_import_tpos` (called non-existent `manager.create_tpo`) and `_import_tpo_impacts` (called non-existent `manager.create_tpo_impact`). Removed call sites in `import_from_excel`. Dropped `TPO_CLUSTERS` / `IMPACT_LEVELS` from `config.settings` import list. |
| **A5** | `ui/layouts.py` | 5 occurrences of `node_type == "TPO"` → `"tpo"`. The graph-data builder writes `node_type = entity_id` (lowercase) for context nodes; uppercase comparisons matched zero. |

## 🛡️ Context Node / Edge Round-Trip Hardening

After the TC-11 fix, re-imports surfaced `[SCHEMA]` warnings on `CN_tpo` and `CE_impacts_tpo` sheets:

- **Real data columns added to schema**:
  - `context_nodes.tpo.properties` += `reference`, `description`
  - `context_edges.impacts_tpo.properties` += `impact_level`, `description`
- **Export-only metadata silenced**: `services/import_service.py` introduces module-level constant
  `EXPORT_RESERVED_COLUMNS = {"_element_id", "_source", "_target", "created_at", "updated_at"}` and
  subtracts it from the unknown-columns warning set in both `_import_context_nodes` and
  `_import_context_edges`. These columns exist for round-trip readability/debugging but are
  Neo4j-internal, edge-derived, or auto-set — re-importing them would clobber correct values.

---

## ⏭️ Deferred follow-ups (tracked as [F-CN-IMPORT] in ROADMAPv4 Stream B backlog)

- **A2** — Remove the empty `relationships.impacts_tpo: { impact_levels: [] }` stub from `schema.yaml`.
  Cascades into `pages/1_⚙️_Configuration.py:2062` (`random.choice(impact_levels)` in the sample-data
  generator), which is itself already broken (emits legacy `:TPO {reference}` cypher and
  `IMPACTS_TPO {impact_level}` edges that no live query reads).
- **A4** — Cluster enum on `context_nodes.tpo.properties.cluster`. Requires extending `AttributeConfig`
  / `_parse_context_node` to read a `values:` list. Defer until a second context-node type needs the
  same treatment.
- **Sample-data generator rewrite** — `pages/1_⚙️_Configuration.py:2055-2069` generates cypher targeting
  the legacy `:TPO` label and `IMPACTS_TPO {impact_level}` shape; rewrite against
  `:ContextNode {node_type:'tpo'}` and the live `context_edges.impacts_tpo` properties.
- **Excel/JSON column contract** — review what gets emitted on context node + edge sheets (CN_*, CE_*).
  Ideally export should not emit `_element_id`/`_source`/`_target`/`created_at`/`updated_at` at all,
  or label them as such; current importer-side silent-ignore is a workaround.
- **Demo cypher idempotency** — `scripts/demo_data_loader_en.cypher` uses bare `CREATE` for all 169
  statements; convert to `MERGE` so the script becomes idempotent against existing DB state.

---

## ✅ Recently Completed (last 2 sessions)

### Session N+16 (this session — v2.32.0 TC-11 root-cause fix + cleanup)
- Diagnosed TC-11 export contamination via `get_semantic_influences()`.
- Phase A coherence audit + cleanup (A1, A3, A5; A2/A4 deferred to backlog).
- Phase A6 export switch — Excel + JSON.
- Context node / edge round-trip hardening (schema additions + `EXPORT_RESERVED_COLUMNS`).
- ROADMAPv4 v2.32.0 release table extended; new backlog item `[F-CN-IMPORT]` filed.
- CHANGELOG v2.32.0 updated with full root-cause analysis.
- 445 tests passing.

### Session N+15 (v2.32.0 TC-11 dedup investigation Round 3)
- Round 3 ID-from-Excel preference logic added to `_import_influences` / `_import_mitigates`.
  Did not resolve TC-11 — root cause was upstream of dedup (export emitted contaminated sheet).

### Session N+14 (v2.32.0 Manual Test Campaign Fixes)
- BUG-1 → BUG-10 (impact→severity arg, edit form crashes, JSON restore, mitigation/influence/context
  node dedup, TPO mapping migration, demo cypher migration).

### Session N+13 (v2.31.0 Pre-Iteration 6 Bug Fixes)
- 7-bug fix release. See CHANGELOG.

---

## 🧠 Key decisions made this session

- **`get_semantic_influences()` is for math, not export.** It exists so the exposure engine can treat
  INFLUENCES and MITIGATES uniformly as influence-semantic edges; the export path needs the kernel
  separation that the dedicated Mitigates sheet already provides. Future kernel relationships with
  `semantic: influence` should follow the same rule — exposure-engine pulls semantic, file-format
  paths pull kernel-specific.
- **JSON dedup mirrors Excel**, per user direction. The BUG-4 dedup work in `backup_service.py` was
  the right direction; A6 keeps the dedup set's shape matching the export shape so the dedup actually
  fires on the right pairs.
- **Demo cypher CREATE→MERGE deferred** per user direction. No current dupes confirmed by
  `MATCH (r:Risk) WITH r.name … count > 1` query, so non-blocking. Idempotency hardening is a
  separate small task.

---

## ⚠️ Known issues / tech debt

- **Configuration.py:2062 sample-data generator broken** — emits legacy `:TPO` cypher; tracked under
  [F-CN-IMPORT] in ROADMAPv4 Stream B backlog.
- **Existing `:TPO` nodes in any live DB** still need the v2.31.0 patch:
  ```cypher
  MATCH (t:TPO) SET t:ContextNode, t.node_type = 'tpo' REMOVE t:TPO
  ```
- **`pydantic` and `openpyxl`** must be installed via venv — always `.\venv\Scripts\python.exe -m pytest tests/` (445 pass).

---

## 📋 Open questions pending user decision

_None._

---

## 🔁 Resumption prompt (copy-paste to start next session)
```
Resume RIM development. Read tasks/SESSION_STATE.md first.
v2.32.0 COMPLETE on branch fix/test_fix. TC-11 fixed and verified manually (0 created on re-import).
445 tests passing. Awaiting user-driven commit + merge to main.

After merge: Iteration 6 begins (Financial Layer & LEC: U16, F34, F9). SPICE synchronisation
briefing required first (ROADMAPv4.md is the sync document).

ROADMAPv4.md is the authoritative roadmap. New backlog item [F-CN-IMPORT] in Stream B captures
the context-node round-trip follow-ups (sample-data generator rewrite, schema enum support, etc.).
```
