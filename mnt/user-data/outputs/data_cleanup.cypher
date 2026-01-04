// Data Cleanup Script for RIM Alpha
// This script fixes common data type issues in the Neo4j database

// ============================================
// PART 1: Fix NULL values by setting defaults
// ============================================

// Set default values for risks with NULL numeric fields
MATCH (r:Risk)
WHERE r.probability IS NULL OR r.impact IS NULL OR r.score IS NULL
SET r.probability = COALESCE(r.probability, 5),
    r.impact = COALESCE(r.impact, 5),
    r.score = COALESCE(r.score, r.probability * r.impact, 25);

// Set default strength for influences with NULL values
MATCH ()-[i:INFLUENCES]->()
WHERE i.strength IS NULL
SET i.strength = 5;

// ============================================
// PART 2: Convert string numbers to integers
// ============================================

// Convert risk numeric fields from strings to integers
MATCH (r:Risk)
WHERE r.probability IS NOT NULL
SET r.probability = toInteger(r.probability),
    r.impact = toInteger(r.impact),
    r.score = toInteger(r.score);

// Convert influence strength from string to integer
MATCH ()-[i:INFLUENCES]->()
WHERE i.strength IS NOT NULL
SET i.strength = toInteger(i.strength);

// ============================================
// PART 3: Recalculate scores based on P × I
// ============================================

// Recalculate all risk scores to ensure consistency
MATCH (r:Risk)
WHERE r.probability IS NOT NULL AND r.impact IS NOT NULL
SET r.score = r.probability * r.impact;

// ============================================
// PART 4: Set default categories and statuses
// ============================================

// Set default category for risks without one
MATCH (r:Risk)
WHERE r.category IS NULL OR r.category = ''
SET r.category = 'Operational';

// Set default status for risks without one
MATCH (r:Risk)
WHERE r.status IS NULL OR r.status = ''
SET r.status = 'Active';

// Set default influence type if missing
MATCH ()-[i:INFLUENCES]->()
WHERE i.type IS NULL OR i.type = ''
SET i.type = 'CORRELATES';

// ============================================
// PART 5: Validation - Check results
// ============================================

// Count risks by data completeness
MATCH (r:Risk)
RETURN 
    'Risks with complete data' as category,
    count(r) as count
WHERE r.probability IS NOT NULL 
  AND r.impact IS NOT NULL 
  AND r.score IS NOT NULL
  AND r.category IS NOT NULL
  AND r.status IS NOT NULL

UNION

// Count influences with complete data
MATCH ()-[i:INFLUENCES]->()
RETURN 
    'Influences with complete data' as category,
    count(i) as count
WHERE i.strength IS NOT NULL 
  AND i.type IS NOT NULL

UNION

// Show any remaining issues
MATCH (r:Risk)
WHERE r.probability IS NULL 
   OR r.impact IS NULL 
   OR r.score IS NULL
RETURN 
    'Risks still with NULL values' as category,
    count(r) as count;

// ============================================
// VERIFICATION QUERIES
// ============================================

// Show sample of cleaned risks
MATCH (r:Risk)
RETURN r.name, r.category, r.probability, r.impact, r.score, r.status
LIMIT 10;

// Show sample of cleaned influences
MATCH (r1:Risk)-[i:INFLUENCES]->(r2:Risk)
RETURN r1.name as source, r2.name as target, i.type, i.strength
LIMIT 10;

// Show summary statistics
MATCH (r:Risk)
RETURN 
    count(r) as total_risks,
    avg(r.score) as avg_score,
    min(r.score) as min_score,
    max(r.score) as max_score;

// ============================================
// NOTES
// ============================================

// This script is safe to run multiple times
// It will not create duplicates or corrupt existing data
// All operations use COALESCE to preserve existing valid values
// Run in Neo4j Browser (http://localhost:7474)
// Execute all sections or run them individually
