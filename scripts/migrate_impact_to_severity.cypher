// U13 Migration: rename Risk.impact → Risk.severity
// Run this script once against your Neo4j instance after deploying v2.25.0.
//
// It is safe to run multiple times (idempotent):
//   - Only acts on nodes that still carry the old property.
//   - Nodes already migrated (r.impact IS NULL) are not touched.
//
// Usage (Neo4j Browser or cypher-shell):
//   :source migrate_impact_to_severity.cypher

MATCH (r:Risk)
WHERE r.impact IS NOT NULL
SET r.severity = r.impact
REMOVE r.impact
RETURN count(r) AS migrated_nodes;
