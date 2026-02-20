# RIM Demo Dataset — Deployment Guide

## Overview

This guide covers the deployment of **DEMO_Complete**, a unified dataset that combines all 7 Test Cases (TC01–TC07) into a single Neo4j database instance, with pre-configured schema scopes for targeted demos.

---

## Deliverables

| File | Purpose |
|---|---|
| `demo_tc_dataset.cypher` | Cypher script — loads all 37 risks, 25 mitigations, 18 influences, TPOs into Neo4j |
| `DEMO_Complete.xlsx` | Excel import file — same data, for use via the app's Import/Export tab |
| `demo_schema_complete.yaml` | Updated `schema.yaml` with 7 pre-configured scopes (one per TC) |

---

## Architecture Decision: Cypher vs Excel

**Use the Cypher script** (`demo_tc_dataset.cypher`) for the demo setup. It has two key advantages over the Excel import:

1. **Deterministic UUIDs** — All node IDs are fixed (UUID v5, namespace-derived). This means the schema scopes in `demo_schema_complete.yaml` reference the correct IDs immediately, with no post-import step needed.
2. **Idempotent** — Uses `MERGE` instead of `CREATE`, so it can be re-run safely without creating duplicates (ideal for the Reset button).

Use the **Excel file** (`DEMO_Complete.xlsx`) only if you want to demonstrate the Import/Export feature itself during a demo.

---

## Deployment Procedure

### Step 1 — Replace the Default Schema

Copy the complete demo schema into the `schemas/default/` folder:

```bash
# Backup the existing schema
cp schemas/default/schema.yaml schemas/default/schema.yaml.bak

# Replace with the demo schema
cp demo_schema_complete.yaml schemas/default/schema.yaml
```

The new schema is identical to the original except it **adds 7 analysis scopes** (TC01–TC07) at the bottom. All existing functionality is preserved.

### Step 2 — Copy the Cypher Script

Place the Cypher loader next to the existing `demo_data_loader_en.cypher`:

```bash
cp demo_tc_dataset.cypher /path/to/app/demo_tc_dataset.cypher
```

### Step 3 — Load the Data into Neo4j

**Option A — Neo4j Browser** (interactive):
1. Open Neo4j Browser at `http://localhost:7474`
2. Open `demo_tc_dataset.cypher` and paste or drag it into the query editor
3. Execute (Ctrl+Enter / Cmd+Enter)
4. Verify: `MATCH (n) RETURN labels(n), count(*) ORDER BY labels(n)`

**Option B — cypher-shell** (CLI):
```bash
cypher-shell -u neo4j -p <password> -f demo_tc_dataset.cypher
```

**Option C — Docker** (if using the app's docker-compose):
```bash
docker exec -i rim_neo4j cypher-shell -u neo4j -p rimpassword \
  < demo_tc_dataset.cypher
```

### Step 4 — Verify in the RIM Application

1. Start the Streamlit app: `streamlit run app.py`
2. Connect to Neo4j on the sidebar
3. Verify data in **Risks** tab: you should see 37 risks prefixed `[TC01]`–`[TC07]`
4. Open **Visualization** tab → sidebar → **Scopes** section: all 7 TC scopes should be listed
5. Select **TC02 - Simple Chain** scope → verify only 3 nodes visible (Op1 → Op2 → Bus1)
6. Run **Exposure Calculation** and verify expected values from README_Testcases.md

---

## Schema Scopes Reference

Each scope filters the graph to exactly the risks from one Test Case. All connected mitigations and TPOs are automatically included (via `include_connected_edges: true`).

| Scope ID | TC | Risks | Color |
|---|---|---|---|
| `tc01_baseline` | TC01 - Baseline | 4 | Light Blue |
| `tc02_simple_chain` | TC02 - Simple Chain | 3 | Light Green |
| `tc03_mitigation_effect` | TC03 - Mitigation Effect | 8 | Light Yellow |
| `tc04_influence_limitation` | TC04 - Influence Limitation | 5 | Light Red |
| `tc05_convergence` | TC05 - Convergence | 5 | Light Purple |
| `tc06_full_chain` | TC06 - Full Chain | 7 | Light Teal |
| `tc07_influence_strengths` | TC07 - Influence Strengths | 5 | Amber |

To show the **full combined demo** (all 37 risks + all connections), select all 7 scopes simultaneously — the app takes their union.

---

## Demo Flow Suggestions

### Quick Function Demo (single concept, ~5 min)
1. Load dataset (already done)
2. In sidebar, select one scope (e.g., TC04 for "Influence Limitation")
3. Run Exposure Calculation
4. Point out: Target A has Critical mitigation but 100% exposure — explain limitation concept

### Progressive Demo (30 min)
Follow TC01→TC07 in order, activating each scope in turn:
- TC01: Establish baseline (all equal, no interaction)
- TC02: Add influence propagation
- TC03: Show mitigation math
- TC04: Key insight — mitigation can be neutralized by upstream
- TC05: Convergence averaging
- TC06: Real-world full chain with a gap
- TC07: Influence strength as coupling factor

### Full Dataset Overview
Deactivate all scopes → show the complete 37-node graph with all interactions visible.

---

## Reset Procedure (manual)

To restore the demo to a clean state:

```cypher
// In Neo4j Browser:
MATCH (n) WHERE n.name STARTS WITH '[TC0' DETACH DELETE n;
```

Then re-run `demo_tc_dataset.cypher`.

> **Note:** The app's Configuration page will include a **Reset Demo Data** button (see separate Claude Code prompt) that automates this procedure.

---

## Data Design Notes

### Naming Convention
All TC entities use the prefix `[TCxx]` — e.g., `[TC02] Operational Risk 1`. This allows:
- Easy identification in lists and queries
- No collision between entities with the same name in different TCs
- Clear association to the test case documentation

### UUID Stability
All UUIDs are computed as UUID v5 from a fixed namespace + entity name. This means:
- Re-running the Cypher script always produces the same IDs (idempotent via MERGE)
- Schema scopes can reference IDs without an update step
- The reset button can safely re-create exact same IDs

### Coexistence with SNR Data
The TC entities are completely isolated from the main SNR demo data by their `[TCxx]` name prefix and distinct UUIDs. Both datasets can coexist in the same database. Use separate scopes or the existing SNR scopes to switch context.
