# v2.31.0 Manual Test Campaign
> Pre-Iteration 6 Bug Fix Release
> Date: 2026-04-01
> Tester: _______________
> Legend: ✅ Pass · ❌ Fail · ⚠️ Partial · 🔁 Blocked

---

## Prerequisites

- [ ] Neo4j is running and the demo dataset has been **reset** using `scripts/demo_data_loader_en.cypher`
- [ ] Streamlit app is running (`streamlit run app.py`)
- [ ] You are on branch `fix/test_fix`
- [ ] Connected to Neo4j (green indicator in sidebar)

> **Important**: The demo data reset is required for TC-TPO tests. The old dataset had `:TPO` nodes
> that the new code cannot find. After reset all TPO nodes will be `:ContextNode {node_type: 'tpo'}`.

---

## TC-01 — Excel Export (BUG 1 + datetime timezone fix)

**What was broken:** Export crashed with `AttributeError: 'EntityTypeDefinition' has no attribute 'type_id'`,
silently returned `None`, which Streamlit reported as "Invalid binary data format: NoneType".
A second issue caused "Excel does not support datetimes with timezones" when Neo4j datetime values
(which carry UTC tzinfo) reached openpyxl.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 1.1 | Navigate to **Data Management** → **Import / Export** tab | Tab loads without error | |
| 1.2 | Click **📤 Export data** | Spinner appears briefly | |
| 1.3 | Click **⬇️ Download Excel file** | `.xlsx` file downloads | |
| 1.4 | Open the downloaded file in Excel / LibreOffice | File opens without corruption | |
| 1.5 | Check sheet tabs present | At minimum: **Risks**, **Mitigations**, **Influences**, **Mitigates**, **CN_tpo** | |
| 1.6 | Check **Risks** sheet — date columns (e.g. `created_at`) | Values are readable dates, not error text | |
| 1.7 | Check **CN_tpo** sheet | 6 rows (TPO-01 to TPO-06), columns: `node_type`, `id`, `reference`, `name`, `cluster` | |

**Pass criterion:** File downloads and opens; all sheets present; no crash message in UI.

---

## TC-02 — JSON Backup (BUG 1)

**What was broken:** Same `type_id` AttributeError caused backup to crash.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 2.1 | Data Management → Import / Export → scroll to **JSON Backup / Restore** | Section visible | |
| 2.2 | Click **💾 Create JSON Backup** | Spinner, then **⬇️ Download Backup** button appears | |
| 2.3 | Click **⬇️ Download Backup** | `.json` file downloads | |
| 2.4 | Open the JSON file in a text editor | Valid JSON with top-level keys: `schema_version`, `exported_at`, `risks`, `mitigations`, `influences`, `mitigates`, `context_nodes`, `context_edges` | |
| 2.5 | Check `context_nodes` key in JSON | Contains `"tpo": [...]` with 6 entries | |
| 2.6 | Check `context_edges` key in JSON | Contains `"impacts_tpo": [...]` with 14 entries | |

**Pass criterion:** File downloads; all top-level keys present; no crash message in UI.

---

## TC-03 — Configuration → Relationships tab (BUG 3)

**What was broken:** An editor for `impacts_tpo` impact levels appeared in the Relationships tab.
`impacts_tpo` is a context-edge, not a core relationship.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 3.1 | Navigate to **⚙️ Configuration** → **Schema** tab | Page loads | |
| 3.2 | Click the **🔗 Relationships** sub-tab | Relationships editor loads | |
| 3.3 | Observe the sections present | **Only**: "Influence Strengths" and "Mitigation Effectiveness Levels" | |
| 3.4 | Confirm **no "TPO Impact Levels"** section exists anywhere on the page | No such section visible | |

**Pass criterion:** Relationships tab shows exactly two sections; no TPO impact section.

---

## TC-04 — "Top Objective" naming (BUG 4)

**What was broken:** Various locations showed "Top Programme Objectives", "Top Program Objectives",
or "Target Performance Objective" instead of the standard "Top Objective / Top Objectives".

| # | Location | Expected Label | Result |
|---|----------|---------------|--------|
| 4.1 | Sidebar filter legend / node types | "Top Objectives" or "Top Objective" | |
| 4.2 | Data Management → Context Nodes tab label for the tpo type | "Top Objective" (not "Target Performance Objective") | |
| 4.3 | Data Management → Context Edges tab label for the impacts_tpo type | "Impacts Top Objective" (not "Impacts TPO") | |
| 4.4 | Configuration → **🏆 TPO Config** sub-tab heading or description | Contains "Top Objective" in description | |
| 4.5 | Graph canvas tooltip / node label for a TPO node | Shows "Top Objective" as type label | |

**Pass criterion:** No occurrence of "Programme Objective", "Program Objective", or "Target Performance Objective" visible anywhere in the UI.

---

## TC-05 — Context node tab isolation (BUG 5 — part A)

**What was broken:** All ContextNode types share the Neo4j label `ContextNode`. `get_all_entities`
queried all of them without filtering by `node_type`, so every tab showed every context node.

**Setup:** Ensure at least one Top Objective exists (should be present after demo data reset).
If you have other context node types in the schema (e.g. scenarios), create one of those too.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 5.1 | Data Management → Context Nodes → **Top Objective** tab | Shows only Top Objective nodes (TPO-01 through TPO-06) | |
| 5.2 | If a second context node type exists, click its tab | Shows only nodes of that type — no TPO nodes visible | |
| 5.3 | Return to Top Objective tab | Still shows only TPO nodes | |

**Pass criterion:** Each tab is isolated; switching tabs does not show cross-type contamination.

---

## TC-06 — New context node appears in correct tab and on canvas (BUG 5 — part B)

**What was broken:** `create_entity` did not write `node_type` to the Neo4j node, so newly
created context nodes were invisible to the canvas query and also appeared in all tabs.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 6.1 | Data Management → Context Nodes → Top Objective tab → **Create** | Form opens | |
| 6.2 | Fill: Reference = `TPO-TEST`, Name = `Test Objective`, Cluster = `Safety & Compliance` | — | |
| 6.3 | Click **Create** | Success message; new row appears in the Top Objective tab | |
| 6.4 | Navigate to **Home** / Dashboard → Graph canvas | Graph renders | |
| 6.5 | Locate the new Top Objective node on the canvas | `TPO-TEST` node visible as gold hexagon | |
| 6.6 | Return to Data Management → if other context type tabs exist, open them | `TPO-TEST` does **not** appear in other type tabs | |
| 6.7 | Delete `TPO-TEST` to clean up (optional) | Node removed | |

**Pass criterion:** Newly created node appears on canvas and only in its own tab.

---

## TC-07 — Top Objectives on graph canvas (BUG 5 — part C, legacy skip-guard)

**What was broken:** `get_graph_data` had `if entity_id == "tpo": continue` left over from the
old hardcoded TPO path. TPO nodes never reached the canvas node list even when correctly stored.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 7.1 | Navigate to **Home** → Visualization tab | Graph canvas renders | |
| 7.2 | Observe node types on canvas | Gold hexagon nodes (Top Objectives) visible | |
| 7.3 | Count gold hexagon nodes | 6 (TPO-01 through TPO-06) | |
| 7.4 | Hover over a gold hexagon node | Tooltip shows node name and type "Top Objective" / "tpo" | |
| 7.5 | In sidebar filters, if "Show Top Objectives" toggle exists, turn it **off** | TPO nodes disappear from canvas | |
| 7.6 | Turn it back **on** | TPO nodes reappear | |

**Pass criterion:** Top Objectives visible on canvas; toggle works if present.

---

## TC-08 — IMPACTS_TPO edges on canvas (BUG 5 — part D, legacy edge skip-guard)

**What was broken:** `if rel_id == "impacts_tpo": continue` prevented these edges from being
added to the generic edge loop.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 8.1 | Home → Visualization → ensure Top Objectives are visible | Gold hexagons visible | |
| 8.2 | Observe edges connecting Risk nodes to Top Objective nodes | Dotted / vee-arrow lines visible between risks and TPOs | |
| 8.3 | Click on a Business Risk node that should impact a TPO (e.g. RC-01) | Node property panel opens | |
| 8.4 | Note which TPO it connects to from panel or canvas | RC-01 → TPO-01 (EBITDA objective) | |

**Pass criterion:** IMPACTS_TPO edges visible on canvas connecting risk nodes to Top Objective nodes.

---

## TC-09 — Scope persistence after "Add to scope" on new risk (BUG 6)

**What was broken:** `add_node_to_scope` used a stale module-level schema singleton. When saved
back to disk, it could overwrite newer scope data with old content, causing the scope selector
to find no matching scopes on the next rerun and silently deselect.

**Setup:** Have at least one named scope active (e.g. `odt_demo`).

| # | Step | Expected | Result |
|---|------|----------|--------|
| 9.1 | Sidebar → **📐 Analysis Scopes** → select `odt_demo` scope | Graph filters to scoped nodes | |
| 9.2 | Data Management → Risks → **Create Risk** | Form opens | |
| 9.3 | Fill: Name = `Scope Test Risk`, Level = `Business`, Likelihood = 3, Severity = 3 | — | |
| 9.4 | Tick **"Add to scope"** → select `odt_demo` | Checkbox / multiselect shows scope selected | |
| 9.5 | Click **Create** | Success; risk appears in list | |
| 9.6 | Observe sidebar scope selector | `odt_demo` still selected (not reset) | |
| 9.7 | Navigate to **Home** | `odt_demo` scope still active in sidebar | |
| 9.8 | Do a **full browser reload** (F5 / Cmd+R) | After reconnect: `odt_demo` scope is still present in schema and can be selected | |
| 9.9 | Select `odt_demo` scope after reload | `Scope Test Risk` appears in the scoped graph | |
| 9.10 | Clean up: delete `Scope Test Risk` | Risk removed | |

**Pass criterion:** Scope stays selected across reruns; scope still exists in YAML after reload; new risk is included when scope reactivated.

---

## TC-10 — Scope "Remove node" persistence

**What was broken:** `remove_node_from_scope` had a broken `load_schema()` import and missing
`schema_name` argument — removals were silently not persisted.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 10.1 | Activate `odt_demo` scope; note a risk in it (e.g. RC-01) | RC-01 visible in scoped canvas | |
| 10.2 | Data Management → Risks → find RC-01 → **Edit** | Edit form opens | |
| 10.3 | If "Remove from scope" option exists, remove RC-01 from `odt_demo` | Success message | |
| 10.4 | Reselect `odt_demo` scope | RC-01 no longer visible in scoped graph | |
| 10.5 | Full browser reload → reconnect → reselect `odt_demo` | RC-01 still absent from scope | |
| 10.6 | Restore RC-01 to scope | Risk reappears | |

**Pass criterion:** Removal persists across rerun and browser reload.

> ⚠️ If the remove-from-scope UI is not exposed on the edit form, mark as N/A and note it as a
> UX gap for F39.

---

## TC-11 — Excel Import round-trip

**What was broken (indirectly):** Export was crashing, so import from a fresh export was
never testable. Now that export works, verify the full round-trip.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 11.1 | Export to Excel (TC-01 already done — reuse that file) | `.xlsx` available | |
| 11.2 | Data Management → Import / Export → **Import from Excel** | File uploader visible | |
| 11.3 | Upload the exported file | File accepted | |
| 11.4 | Click **📥 Import data** | Import summary shows; "N created, M skipped" (all existing = skipped) | |
| 11.5 | Observe warnings | No `[SCHEMA]` warnings for known types (Risks, Mitigations, CN_tpo, etc.) | |
| 11.6 | Confirm no errors in the error panel | Error panel empty or absent | |

**Pass criterion:** Import completes; all existing records show as skipped (not duplicated); no unexpected schema warnings.

---

## TC-12 — JSON Backup restore round-trip

| # | Step | Expected | Result |
|---|------|----------|--------|
| 12.1 | Use backup from TC-02 | `.json` file available | |
| 12.2 | Data Management → Import / Export → **Restore from Backup** → upload JSON | Confirm warning displayed | |
| 12.3 | Click **♻️ Restore from Backup** | Summary shows; records created = 0 (all exist), skipped = total count | |
| 12.4 | No errors | Error panel empty | |

**Pass criterion:** Restore completes; all records skipped (upsert-by-name, all already exist).

---

## TC-13 — SNR demo dataset (bonus — if time permits)

Verify the SNR demo file also works correctly with the ContextNode fix.

| # | Step | Expected | Result |
|---|------|----------|--------|
| 13.1 | Clear Neo4j; load `scripts/SNR_demo_data_loader_en.cypher` | No Cypher errors | |
| 13.2 | Connect app to freshly loaded SNR database | Connection successful | |
| 13.3 | Data Management → Context Nodes → Top Objective tab | 3 TPO nodes visible (TPO-01, 02, 03) | |
| 13.4 | Graph canvas → Top Objective nodes visible | 3 gold hexagons visible | |
| 13.5 | Export to Excel | File downloads; CN_tpo sheet has 3 rows | |

**Pass criterion:** SNR dataset works identically to ODT dataset for TPO handling.

---

## Regression Checks

Quick smoke tests to confirm existing functionality was not broken by the fixes.

| # | Area | Step | Expected | Result |
|---|------|------|----------|--------|
| R1 | Exposure calculation | Home → Calculate Exposure | Completes; exposure scores shown on canvas | |
| R2 | Influence analysis | Home → Analysis panel → Influence | Top propagators list appears | |
| R3 | Mitigation coverage | Home → Analysis panel → Mitigation | Coverage stats appear | |
| R4 | Scope-based simulation | Simulation page → Scope-Based → run | Results generated without error | |
| R5 | Configuration save | Config → make minor change → Save | Saved successfully; no YAML corruption | |
| R6 | Risk lifecycle | Data Management → Risks → edit a risk status | Status updates; lifecycle state reflected on canvas | |

---

## Issues Log

| TC | Severity | Description | Screenshot | Status |
|----|----------|-------------|------------|--------|
| | | | | |

---

## Sign-off

- [ ] All TC-01 through TC-12 pass (or documented exception)
- [ ] All R1 through R6 pass
- [ ] No new regressions observed
- [ ] Ready to merge `fix/test_fix` → main

**Signed:** _______________ **Date:** _______________
