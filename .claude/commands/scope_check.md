Review the code in $ARGUMENTS (file path or pasted code) and verify scope completeness compliance against RIM's golden rule: when a scope is active, it IS the entire graph.

Check each of the following:

1. Does every query/function accept and propagate `scope_node_ids` or `scope_context`?
2. Do statistics compute only scoped nodes (no global leakage)?
3. Do dropdowns and node selectors filter to scoped nodes only?
4. Does exposure propagation stop at the scope boundary?
5. Are there any hardcoded global queries that ignore scope parameters?

Report each finding as:
- [CRITICAL BUG] — silent data corruption, wrong results delivered to user
- [WARNING] — partial scope awareness, likely incorrect in edge cases
- [OK] — compliant

For each CRITICAL BUG or WARNING: show the exact line, explain the failure mode, and provide the corrected code.
