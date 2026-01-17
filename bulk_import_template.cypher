// =============================================================================
// BULK IMPORT TEMPLATE - Risk Influence Map
// =============================================================================
// 
// This template is designed for importing larger risk portfolios.
// 
// INSTRUCTIONS:
// 1. Fill in the data sections below with your risk data
// 2. Execute in Neo4j Browser or via cypher-shell
// 3. Run verification queries at the end to confirm import
//
// TIPS FOR LARGE IMPORTS:
// - Execute each section separately if you encounter memory issues
// - Use UNWIND for batch operations (more efficient than individual CREATE)
// - Consider splitting into multiple files if > 500 nodes
//
// =============================================================================

// =============================================================================
// 0. OPTIONAL: PURGE EXISTING DATA
// =============================================================================
// WARNING: Uncomment the line below ONLY if you want to delete ALL existing data
// MATCH (n) DETACH DELETE n;

// =============================================================================
// 1. CREATE CONSTRAINTS AND INDEXES (Run once, improves performance)
// =============================================================================

// Unique constraints
CREATE CONSTRAINT risk_id IF NOT EXISTS FOR (r:Risk) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT tpo_id IF NOT EXISTS FOR (t:TPO) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT tpo_ref IF NOT EXISTS FOR (t:TPO) REQUIRE t.reference IS UNIQUE;

// Indexes for faster lookups
CREATE INDEX risk_level IF NOT EXISTS FOR (r:Risk) ON (r.level);
CREATE INDEX risk_status IF NOT EXISTS FOR (r:Risk) ON (r.status);
CREATE INDEX tpo_cluster IF NOT EXISTS FOR (t:TPO) ON (t.cluster);

// =============================================================================
// 2. BULK IMPORT: STRATEGIC RISKS
// =============================================================================
// 
// Copy and adapt the data rows below. Each row represents one Strategic Risk.
// Required fields: id, name, level (must be 'Strategic')
// Optional fields: description, status, categories, owner, probability, impact,
//                  activation_condition, activation_decision_date
//

UNWIND [
  // === COPY THIS BLOCK FOR EACH STRATEGIC RISK ===
  {
    id: 'RS-001',
    name: 'Strategic Risk Name Here',
    description: 'Detailed description of the risk',
    level: 'Strategic',
    status: 'Active',  // Active | Contingent | Archived
    categories: ['Programme', 'Produit'],  // Programme | Produit | Industriel | Supply Chain
    owner: 'Risk Owner Name',
    probability: 5.0,  // 0.0 to 10.0
    impact: 7.0,       // 0.0 to 10.0
    activation_condition: null,      // Only for Contingent risks
    activation_decision_date: null   // Only for Contingent risks (format: 'YYYY-MM-DD')
  },
  {
    id: 'RS-002',
    name: 'Another Strategic Risk',
    description: 'Description here',
    level: 'Strategic',
    status: 'Contingent',
    categories: ['Programme'],
    owner: 'Owner Name',
    probability: 6.0,
    impact: 8.0,
    activation_condition: 'If decision X is taken in Q3 2026',
    activation_decision_date: '2026-09-30'
  }
  // === ADD MORE STRATEGIC RISKS ABOVE THIS LINE ===
] AS row

CREATE (r:Risk {
  id: row.id,
  name: row.name,
  description: COALESCE(row.description, ''),
  level: row.level,
  status: COALESCE(row.status, 'Active'),
  categories: COALESCE(row.categories, ['Programme']),
  owner: COALESCE(row.owner, ''),
  probability: row.probability,
  impact: row.impact,
  exposure: CASE WHEN row.probability IS NOT NULL AND row.impact IS NOT NULL 
                 THEN row.probability * row.impact 
                 ELSE null END,
  current_score_type: CASE WHEN row.probability IS NOT NULL AND row.impact IS NOT NULL 
                           THEN 'Qualitative_4x4' 
                           ELSE 'None' END,
  activation_condition: row.activation_condition,
  activation_decision_date: row.activation_decision_date,
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 3. BULK IMPORT: OPERATIONAL RISKS
// =============================================================================

UNWIND [
  // === COPY THIS BLOCK FOR EACH OPERATIONAL RISK ===
  {
    id: 'RO-001',
    name: 'Operational Risk Name Here',
    description: 'Detailed description of the operational risk',
    level: 'Operational',
    status: 'Active',
    categories: ['Supply Chain', 'Industriel'],
    owner: 'Risk Owner Name',
    probability: 5.0,
    impact: 6.0
  },
  {
    id: 'RO-002',
    name: 'Another Operational Risk',
    description: 'Description here',
    level: 'Operational',
    status: 'Active',
    categories: ['Produit'],
    owner: 'Owner Name',
    probability: 4.0,
    impact: 7.0
  }
  // === ADD MORE OPERATIONAL RISKS ABOVE THIS LINE ===
] AS row

CREATE (r:Risk {
  id: row.id,
  name: row.name,
  description: COALESCE(row.description, ''),
  level: row.level,
  status: COALESCE(row.status, 'Active'),
  categories: COALESCE(row.categories, ['Programme']),
  owner: COALESCE(row.owner, ''),
  probability: row.probability,
  impact: row.impact,
  exposure: CASE WHEN row.probability IS NOT NULL AND row.impact IS NOT NULL 
                 THEN row.probability * row.impact 
                 ELSE null END,
  current_score_type: CASE WHEN row.probability IS NOT NULL AND row.impact IS NOT NULL 
                           THEN 'Qualitative_4x4' 
                           ELSE 'None' END,
  activation_condition: null,
  activation_decision_date: null,
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 4. BULK IMPORT: TOP PROGRAM OBJECTIVES (TPOs)
// =============================================================================
//
// Clusters available:
//   - Product Efficiency
//   - Business Efficiency
//   - Industrial Efficiency
//   - Sustainability
//   - Safety
//

UNWIND [
  // === COPY THIS BLOCK FOR EACH TPO ===
  {
    id: 'TPO-01',
    reference: 'TPO-01',
    name: 'TPO Name Here',
    cluster: 'Business Efficiency',
    description: 'Detailed description of the objective'
  },
  {
    id: 'TPO-02',
    reference: 'TPO-02',
    name: 'Another TPO',
    cluster: 'Safety',
    description: 'Description here'
  }
  // === ADD MORE TPOs ABOVE THIS LINE ===
] AS row

CREATE (t:TPO {
  id: row.id,
  reference: row.reference,
  name: row.name,
  cluster: row.cluster,
  description: COALESCE(row.description, ''),
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 5. BULK IMPORT: RISK INFLUENCES (Risk → Risk)
// =============================================================================
//
// Influence types are AUTO-DETERMINED based on source/target levels:
//   - Operational → Strategic = Level1_Op_to_Strat
//   - Strategic → Strategic   = Level2_Strat_to_Strat
//   - Operational → Operational = Level3_Op_to_Op
//
// Strength values: Weak | Moderate | Strong | Critical
// Confidence: 0.0 to 1.0
//

UNWIND [
  // === COPY THIS BLOCK FOR EACH INFLUENCE ===
  {
    id: 'INF-001',
    source_id: 'RO-001',    // Source risk ID
    target_id: 'RS-001',    // Target risk ID
    strength: 'Strong',      // Weak | Moderate | Strong | Critical
    confidence: 0.85,        // 0.0 to 1.0
    description: 'Description of how source influences target'
  },
  {
    id: 'INF-002',
    source_id: 'RS-001',
    target_id: 'RS-002',
    strength: 'Critical',
    confidence: 0.95,
    description: 'Description here'
  }
  // === ADD MORE INFLUENCES ABOVE THIS LINE ===
] AS row

MATCH (source:Risk {id: row.source_id})
MATCH (target:Risk {id: row.target_id})
WITH source, target, row,
     CASE 
        WHEN source.level = 'Operational' AND target.level = 'Strategic' THEN 'Level1_Op_to_Strat'
        WHEN source.level = 'Strategic' AND target.level = 'Strategic' THEN 'Level2_Strat_to_Strat'
        WHEN source.level = 'Operational' AND target.level = 'Operational' THEN 'Level3_Op_to_Op'
        ELSE 'Unknown'
     END as influence_type
CREATE (source)-[:INFLUENCES {
  id: row.id,
  influence_type: influence_type,
  strength: row.strength,
  description: COALESCE(row.description, ''),
  confidence: COALESCE(row.confidence, 0.8),
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 6. BULK IMPORT: TPO IMPACTS (Strategic Risk → TPO)
// =============================================================================
//
// NOTE: Only Strategic risks can impact TPOs
// Impact levels: Low | Medium | High | Critical
//

UNWIND [
  // === COPY THIS BLOCK FOR EACH TPO IMPACT ===
  {
    id: 'IMP-001',
    risk_id: 'RS-001',      // Must be a Strategic risk
    tpo_id: 'TPO-01',       // Target TPO ID
    impact_level: 'High',   // Low | Medium | High | Critical
    description: 'Description of how risk impacts the TPO'
  },
  {
    id: 'IMP-002',
    risk_id: 'RS-002',
    tpo_id: 'TPO-01',
    impact_level: 'Critical',
    description: 'Description here'
  }
  // === ADD MORE TPO IMPACTS ABOVE THIS LINE ===
] AS row

MATCH (r:Risk {id: row.risk_id, level: 'Strategic'})
MATCH (t:TPO {id: row.tpo_id})
CREATE (r)-[:IMPACTS_TPO {
  id: row.id,
  impact_level: row.impact_level,
  description: COALESCE(row.description, ''),
  created_at: datetime()
}]->(t);

// =============================================================================
// 7. VERIFICATION QUERIES
// =============================================================================
// Run these after import to verify data integrity

// --- Count summary ---
MATCH (r:Risk)
WITH r.level as Level, count(r) as Count
RETURN 'Risks by Level' as Category, Level as Type, Count
UNION ALL
MATCH (r:Risk)
WITH r.status as Status, count(r) as Count
RETURN 'Risks by Status' as Category, Status as Type, Count
UNION ALL
MATCH (t:TPO)
WITH t.cluster as Cluster, count(t) as Count
RETURN 'TPOs by Cluster' as Category, Cluster as Type, Count
UNION ALL
MATCH ()-[i:INFLUENCES]->()
WITH i.influence_type as InfluenceType, count(i) as Count
RETURN 'Influences by Type' as Category, InfluenceType as Type, Count
UNION ALL
MATCH ()-[i:IMPACTS_TPO]->()
WITH i.impact_level as ImpactLevel, count(i) as Count
RETURN 'TPO Impacts by Level' as Category, ImpactLevel as Type, Count;

// --- Total counts ---
MATCH (r:Risk) WITH count(r) as risks
MATCH (t:TPO) WITH risks, count(t) as tpos
MATCH ()-[i:INFLUENCES]->() WITH risks, tpos, count(i) as influences
MATCH ()-[imp:IMPACTS_TPO]->() WITH risks, tpos, influences, count(imp) as impacts
RETURN risks as TotalRisks, tpos as TotalTPOs, influences as TotalInfluences, impacts as TotalTPOImpacts;

// --- Check for orphan risks (no connections) ---
MATCH (r:Risk)
WHERE NOT (r)-[:INFLUENCES]-() AND NOT (r)<-[:INFLUENCES]-() AND NOT (r)-[:IMPACTS_TPO]->()
RETURN r.id as OrphanRiskID, r.name as Name, r.level as Level;

// --- Check for orphan TPOs (no impacts) ---
MATCH (t:TPO)
WHERE NOT ()-[:IMPACTS_TPO]->(t)
RETURN t.reference as OrphanTPO, t.name as Name, t.cluster as Cluster;

// --- View influence network summary ---
MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
RETURN source.id as SourceID, source.level as SourceLevel, 
       i.influence_type as Type, i.strength as Strength,
       target.id as TargetID, target.level as TargetLevel
ORDER BY i.influence_type, i.strength DESC;

// --- View TPO impact summary ---
MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
RETURN r.id as RiskID, r.name as RiskName, 
       i.impact_level as ImpactLevel,
       t.reference as TPO, t.name as TPOName, t.cluster as Cluster
ORDER BY t.reference, i.impact_level DESC;

// =============================================================================
// 8. USEFUL MAINTENANCE QUERIES
// =============================================================================

// --- Update all review dates (batch) ---
// MATCH (r:Risk)
// SET r.last_review_date = datetime(),
//     r.next_review_date = datetime() + duration({days: 90});

// --- Find high-exposure risks without influences ---
// MATCH (r:Risk)
// WHERE r.exposure > 40 AND NOT (r)-[:INFLUENCES]->() AND NOT (r)<-[:INFLUENCES]-()
// RETURN r.id, r.name, r.exposure
// ORDER BY r.exposure DESC;

// --- Find strategic risks not linked to any TPO ---
// MATCH (r:Risk {level: 'Strategic'})
// WHERE NOT (r)-[:IMPACTS_TPO]->()
// RETURN r.id, r.name, r.exposure
// ORDER BY r.exposure DESC;

// --- Delete specific risk and its relationships ---
// MATCH (r:Risk {id: 'RS-XXX'})
// DETACH DELETE r;

// --- Delete specific TPO and its relationships ---
// MATCH (t:TPO {id: 'TPO-XX'})
// DETACH DELETE t;

// =============================================================================
// END OF TEMPLATE
// =============================================================================
