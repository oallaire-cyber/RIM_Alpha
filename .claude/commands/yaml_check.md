Review the schema YAML change in $ARGUMENTS and validate it against RIM's schema-driven architecture rules.

Check the following:

1. **New ContextNode types** — do they define all required fields?
   Required: `shape`, `color`, `zone` (must be `upper` or `lower`), `properties` list with at least a `name: string` entry.
   Valid shapes: `box`, `ellipse`, `circle`, `diamond`, `star`, `triangleDown`
   Valid property types: `string`, `float`, `int`, `bool`, `enum`

2. **New relationship types** — do they declare all required fields?
   Required: `semantic` (must be `influence`, `context`, or `cluster`), `valid_from` (list of node type IDs), `valid_to` (list of node type IDs)
   Warning if `semantic: influence` — this means the relationship participates in exposure propagation. Confirm this is intentional.

3. **Computational boundary** — does the change attempt to add a `computational: true` flag or otherwise make a ContextNode participate in exposure math? This is not yet supported. Flag it and explain the constraint.

4. **App code impact** — would this schema change require any modification to application Python code? It should never need to. If it would, flag it as [ARCHITECTURE VIOLATION].

5. **Scope definitions** — if new scopes are added, do they reference node UUIDs that exist in the demo dataset, or are they placeholders?

6. **Test coverage** — are there existing tests in `tests/` that should be updated to cover this schema change (e.g., `test_risk_subtypes.py`, `test_scopes.py`)?

Report each finding as [ERROR] / [WARNING] / [OK].
