# Data Management Guide

This guide explains how to import, export, and back up your RIM graph data —
including all schema-driven **Context Nodes** and **Context Edges**.

---

## 1. Excel Export

Go to **💾 Data Management → 📥 Import / Export → Export to Excel**.

The exported `.xlsx` file contains:

| Sheet | Contents |
|---|---|
| `Risks` | All Risk nodes |
| `Influences` | Risk → Risk semantic influence relationships |
| `TPOs` | Top Programme Objectives |
| `TPO_Impacts` | Risk → TPO impact relationships |
| `Mitigations` | All Mitigation nodes |
| `Mitigates` | Mitigation → Risk relationships |
| `CN_{type_id}` | One sheet per Context Node type defined in `schema.yaml` |
| `CE_{rel_type_id}` | One sheet per Context Edge type defined in `schema.yaml` |

**Using the export as a template:** Export first even on an empty graph; this
produces correctly-structured empty sheets with the right column headers. Fill
in the data and re-import.

---

## 2. Excel Import

Go to **💾 Data Management → 📥 Import / Export → Import from Excel**.

### Required columns per sheet type

**Core sheets** — same as the export structure described above. Required columns
for each type are validated at import time.

**Context Node sheets (`CN_{type_id}`)**
- `name` (required)
- Any property columns declared in `schema.yaml` under `context_nodes.{type_id}.properties`
- Additional columns are filtered out (see [Handling Import Warnings](#3-handling-import-warnings))

**Context Edge sheets (`CE_{rel_type_id}`)**
- `source_name` (required) — name of the source node
- `target_name` (required) — name of the target node
- Any property columns declared under `relationship_types.{rel_type_id}.properties`

> [!NOTE]
> **Link resolution**: `source_name` and `target_name` are resolved against
> the names of all nodes that already exist in the graph at import time
> (including any nodes created in the same import run). The order of sheets
> in the file does not matter — context edges are always processed last.

---

## 3. Handling Import Warnings

### What `[SCHEMA]` log lines mean

After an import, any skipped or degraded data appears in the **Schema
Warnings** section of the import summary. Lines prefixed with `[SCHEMA]`
always indicate a **mismatch between the Excel file and `schema.yaml`** — and
they include a ready-to-paste YAML snippet to fix it.

### Case 1: Unknown Context Node type

```
[SCHEMA] Sheet 'CN_supplier' skipped — type 'supplier' not found in schema.yaml.
To enable this import, add the following to schema.yaml under 'context_nodes':

    supplier:
      shape: "box"
      color: "#AAAAAA"
      zone: "lower"   # or "upper"
      properties:
        - { name: "name", type: "string" }   # detected columns: name, capacity, region
        - { name: "capacity", type: "string" }
        - { name: "region", type: "string" }

Then re-import the file.
```

**Steps to resolve:**

1. Open `schema.yaml` in your editor
2. Find the `context_nodes:` section
3. Paste the YAML snippet from the warning (review `shape`, `color`, `zone` and
   property `type` values before saving — the scaffold defaults everything to
   `string`)
4. Re-export (the `CN_supplier` sheet will now appear with the correct columns)
5. Re-import

### Case 2: Extra columns on a known type

```
[SCHEMA] Sheet 'CN_scenario': unrecognized columns ['new_field', 'budget'] ignored.
These are not declared in schema.yaml under context_nodes.scenario.properties.
To persist them, add entries like:
    - { name: "new_field", type: "string" }
    - { name: "budget", type: "float" }
to the 'context_nodes.scenario.properties' list.
```

**Steps to resolve:**

1. Open `schema.yaml`
2. Navigate to `context_nodes.scenario.properties`
3. Add the property entries from the warning (adjust `type` as needed)
4. Re-import — the columns will now be stored

### Case 3: Unknown Context Edge type

```
[SCHEMA] Sheet 'CE_depends_on' skipped — relationship type 'depends_on' not found in schema.yaml.
To enable this import, add the following to schema.yaml under 'relationship_types':

    depends_on:
      semantic: "context"          # or "influence" / "cluster"
      valid_from: ["<source_node_type>"]
      valid_to:   ["<target_node_type>"]
      properties: []

Then re-import the file.
```

**Steps to resolve:** same pattern — paste into `relationship_types:` in
`schema.yaml`, fill in `valid_from` / `valid_to` with the actual node type IDs,
then re-import.

### Schema YAML Quick Reference

| Field | Accepted values |
|---|---|
| `type` (property) | `string`, `float`, `int`, `bool`, `enum` |
| `zone` | `upper`, `lower` |
| `semantic` (relationship) | `context`, `influence`, `cluster` |
| `shape` | `box`, `ellipse`, `circle`, `diamond`, `star`, `triangleDown` |

---

## 4. JSON Backup / Restore

Go to **💾 Data Management → 📥 Import / Export → 🗄️ JSON Backup / Restore**.

### When to use JSON backup vs. Excel

| | Excel | JSON |
|---|---|---|
| Best for | Bulk data entry, migration from other tools | Full point-in-time backup, disaster recovery |
| Schema versioned | No | Yes (`schema_version` field) |
| Includes all types | Yes (schema-driven) | Yes |
| Human-readable | Yes (table format) | Yes (nested JSON) |

### Backup format

```json
{
  "schema_version": "2.18.0",
  "exported_at": "2026-03-08T18:16:00+00:00",
  "risks": [],
  "tpos": [],
  "mitigations": [],
  "influences": [],
  "tpo_impacts": [],
  "mitigates": [],
  "context_nodes": { "<type_id>": [] },
  "context_edges": { "<rel_type_id>": [] }
}
```

### Restore behaviour

- Records are inserted in topological order (nodes before edges)
- Each node is **upserted by name** — if a node with the same name already
  exists, it is skipped (existing data is never overwritten or deleted)
- If a context type in the backup is not found in the current `schema.yaml`,
  those records are skipped with a `[SCHEMA]` error in the summary
