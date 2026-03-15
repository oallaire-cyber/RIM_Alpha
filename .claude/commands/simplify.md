Review the code in $ARGUMENTS and identify complexity that can be reduced. Apply the RIM principle: make every change as simple as possible, impact minimal code.

Check for:

1. **Functions doing more than one thing** — should be split or delegated
2. **Unnecessary abstraction or indirection** — layers that add complexity without value
3. **Redundant code** — logic that duplicates something already in `utils/`, `config/schema_loader.py`, or `utils/state_manager.py`
4. **Hardcoded values** that should come from the schema YAML (IDs, labels, colors, thresholds)
5. **ContextNode architecture violations** — type-specific `if/else` blocks for non-computational node types that should be schema-driven
6. **Overly defensive code** — excessive null checks or try/except blocks masking root issues

For each finding:
- Show the current code
- Explain why it's unnecessarily complex
- Propose the simpler version
- Flag if the simplification requires cross-stream work (if so, note it but don't implement it)

Do not suggest simplifications that would change observable behavior or break existing tests.
