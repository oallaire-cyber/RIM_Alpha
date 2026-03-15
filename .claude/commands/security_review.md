Review the code in $ARGUMENTS for security issues relevant to a Streamlit + Neo4j application.

Check for:

1. **Cypher injection** — unsanitized user input interpolated directly into Cypher queries. All dynamic values must use parameterized queries (`{param}` syntax with a params dict).

2. **Credentials exposure** — Neo4j URI, username, or password appearing in code, session state keys, or log output. Credentials must come from environment variables or the connection form only.

3. **Neo4j connection handling** — connection leaks (no close/cleanup), singleton integrity violations in `utils/db_manager.py`, or multiple parallel connections being opened unintentionally.

4. **Streamlit session state pollution** — state keys that could leak data between user sessions, or sensitive data (node IDs, exposure values) stored in state without scoping.

5. **File handling risks** — Excel/JSON import paths: unsanitized filenames, no file size limits, no validation of file content before processing, or temp files not cleaned up.

6. **Schema YAML loading** — YAML loaded with `yaml.load()` instead of `yaml.safe_load()` (arbitrary code execution risk).

Report each finding as [HIGH] / [MEDIUM] / [LOW] with:
- Exact file and line
- The attack vector or failure mode
- The fix required
