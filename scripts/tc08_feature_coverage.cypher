// =============================================================================
// TC08 - FEATURE COVERAGE DATASET
// Purpose: Manual test & fix campaign — covers features added in Iterations 3-5
//          (lifecycle, TRI, templates, TPO, quadrant, threshold alerts, simulation)
//
// Dataset summary:
//   Risks        : 7 (4 active, 2 lifecycle-inactive, 1 template)
//   Mitigations  : 3 (2 linked, 1 unlinked/proposed — tests coverage gap)
//   Influences   : 2 (OR1 →[Critical]→ OR2, OR2 →[Strong]→ BR1)
//   TPO          : 1 (linked to BR1)
//
// Known calculation results (verify against app after loading):
//   OR1  : Base=100, No mitigation          → Final = 100   | Quadrant: critical | TRI ≈ 316.2
//   OR2  : Base=36,  M1 High (0.7 red)      → mit_factor=0.3
//          Upstream OR1 [Critical, residual=1.0] → limitation=1.0
//          Effective_factor = 0.3 + 0.7×1.0 = 1.0 → Final = 36    | Quadrant: critical | TRI ≈ 135.8
//          (TC04 lesson: High mitigation nullified by unmitigated upstream)
//   BR1  : Base=48,  M2 Medium (0.5 red)    → mit_factor=0.5
//          Upstream OR2 [Strong=0.75, residual=36/36=1.0] → limitation=0.75
//          Effective_factor = 0.5 + 0.5×0.75 = 0.875 → Final = 42 | Quadrant: critical | TRI ≈ 135.8
//   BR2  : Base=12,  M3 exists but NOT LINKED to any risk
//          No active mitigation → Final = 12                | Quadrant: marginal  | TRI ≈ 13.5
//
// Mitigation Exposure deltas (key for test D3):
//   M2 (Medium, BR1) : removing → BR1 Final = 48  → Δ = +6.0 (largest delta)
//   M1 (High, OR2)   : removing → OR2 Final = 36  → Δ = 0.0  (upstream OR1 nullifies it)
//   M3               : no MITIGATES rel → Δ = 0.0
//
// Threshold alert (test C8, default threshold=50):
//   OR1 Final=100 > 50 → fires alert
//
// Execute in Neo4j Browser or cypher-shell
// Uncomment line below to purge before loading:
// MATCH (n) DETACH DELETE n;
// =============================================================================


// ===========================================================================
// TC08 — RISKS (Active)
// ===========================================================================

// BR1: Business Risk Alpha — L=6, S=8 — Critical quadrant — has Medium mitigation + upstream influence
MERGE (r_tc08_br1:Risk {id: 'tc08-0001-0000-0000-000000000001'})
ON CREATE SET
  r_tc08_br1.name        = '[TC08] Business Risk Alpha',
  r_tc08_br1.level       = 'Business',
  r_tc08_br1.categories  = ['Programme'],
  r_tc08_br1.status      = 'Active',
  r_tc08_br1.origin      = 'New',
  r_tc08_br1.probability = 6,
  r_tc08_br1.severity    = 8,
  r_tc08_br1.description = '[TC08] Business Risk Alpha — L=6, S=8, Base=48. Final=42 after Medium mitigation + Strong upstream influence. Critical quadrant. TRI≈135.8.',
  r_tc08_br1.created_at  = datetime(),
  r_tc08_br1.updated_at  = datetime();

// BR2: Business Risk Beta — L=3, S=4 — Marginal quadrant — no effective mitigation (M3 is unlinked)
MERGE (r_tc08_br2:Risk {id: 'tc08-0001-0000-0000-000000000002'})
ON CREATE SET
  r_tc08_br2.name        = '[TC08] Business Risk Beta',
  r_tc08_br2.level       = 'Business',
  r_tc08_br2.categories  = ['Product'],
  r_tc08_br2.status      = 'Active',
  r_tc08_br2.origin      = 'New',
  r_tc08_br2.probability = 3,
  r_tc08_br2.severity    = 4,
  r_tc08_br2.description = '[TC08] Business Risk Beta — L=3, S=4, Base=12. No MITIGATES link (M3 Proposed but unlinked). Final=12. Marginal quadrant.',
  r_tc08_br2.created_at  = datetime(),
  r_tc08_br2.updated_at  = datetime();

// OR1: Op Risk Upstream — L=10, S=10 — Critical quadrant — unmitigated source
MERGE (r_tc08_or1:Risk {id: 'tc08-0001-0000-0000-000000000003'})
ON CREATE SET
  r_tc08_or1.name        = '[TC08] Op Risk Upstream',
  r_tc08_or1.level       = 'Operational',
  r_tc08_or1.categories  = ['Industrial'],
  r_tc08_or1.status      = 'Active',
  r_tc08_or1.origin      = 'New',
  r_tc08_or1.probability = 10,
  r_tc08_or1.severity    = 10,
  r_tc08_or1.description = '[TC08] Op Risk Upstream — L=10, S=10, Base=100. NO mitigation. Residual=1.0. Propagates Critical influence to OR2. Critical quadrant. TRI≈316.2.',
  r_tc08_or1.created_at  = datetime(),
  r_tc08_or1.updated_at  = datetime();

// OR2: Op Risk Downstream — L=6, S=6 — Critical quadrant — has High mitigation but nullified by OR1
MERGE (r_tc08_or2:Risk {id: 'tc08-0001-0000-0000-000000000004'})
ON CREATE SET
  r_tc08_or2.name        = '[TC08] Op Risk Downstream',
  r_tc08_or2.level       = 'Operational',
  r_tc08_or2.categories  = ['Industrial'],
  r_tc08_or2.status      = 'Active',
  r_tc08_or2.origin      = 'New',
  r_tc08_or2.probability = 6,
  r_tc08_or2.severity    = 6,
  r_tc08_or2.description = '[TC08] Op Risk Downstream — L=6, S=6, Base=36. High mitigation (M1) applied but fully nullified by unmitigated upstream OR1. Final=36. Same lesson as TC04. Critical quadrant.',
  r_tc08_or2.created_at  = datetime(),
  r_tc08_or2.updated_at  = datetime();


// ===========================================================================
// TC08 — RISKS (Lifecycle Inactive — excluded from normal exposure calculation)
// ===========================================================================

// OR3: Op Risk Accepted — lifecycle status = Accepted
MERGE (r_tc08_or3:Risk {id: 'tc08-0001-0000-0000-000000000005'})
ON CREATE SET
  r_tc08_or3.name        = '[TC08] Op Risk Accepted',
  r_tc08_or3.level       = 'Operational',
  r_tc08_or3.categories  = ['Supply Chain'],
  r_tc08_or3.status      = 'Accepted',
  r_tc08_or3.origin      = 'New',
  r_tc08_or3.probability = 5,
  r_tc08_or3.severity    = 5,
  r_tc08_or3.description = '[TC08] Op Risk Accepted — status=Accepted (lifecycle inactive). Excluded from exposure calculation by default. Appears under lifecycle inactive list. Worst-case canvas re-activates it.',
  r_tc08_or3.acceptance_date  = date(),
  r_tc08_or3.acceptance_owner = 'Test Reviewer',
  r_tc08_or3.created_at  = datetime(),
  r_tc08_or3.updated_at  = datetime();

// OR4: Op Risk Suppressed — lifecycle status = Suppressed
MERGE (r_tc08_or4:Risk {id: 'tc08-0001-0000-0000-000000000006'})
ON CREATE SET
  r_tc08_or4.name        = '[TC08] Op Risk Suppressed',
  r_tc08_or4.level       = 'Operational',
  r_tc08_or4.categories  = ['Supply Chain'],
  r_tc08_or4.status      = 'Suppressed',
  r_tc08_or4.origin      = 'New',
  r_tc08_or4.probability = 4,
  r_tc08_or4.severity    = 3,
  r_tc08_or4.description = '[TC08] Op Risk Suppressed — status=Suppressed (lifecycle inactive). Excluded from exposure calculation by default. Tests lifecycle opacity encoding on canvas.',
  r_tc08_or4.created_at  = datetime(),
  r_tc08_or4.updated_at  = datetime();


// ===========================================================================
// TC08 — RISK TEMPLATE (is_template=true — excluded from canvas and computation)
// ===========================================================================

MERGE (r_tc08_tpl:Risk {id: 'tc08-0001-0000-0000-000000000007'})
ON CREATE SET
  r_tc08_tpl.name        = '[TC08] Business Risk Template',
  r_tc08_tpl.level       = 'Business',
  r_tc08_tpl.categories  = ['Programme'],
  r_tc08_tpl.status      = 'Active',
  r_tc08_tpl.origin      = 'New',
  r_tc08_tpl.is_template = true,
  r_tc08_tpl.probability = 5,
  r_tc08_tpl.severity    = 5,
  r_tc08_tpl.description = '[TC08] Risk Template — is_template=true. Excluded from canvas, exposure, and simulation. Visible only in the Risk Templates library. Use test B7 to instantiate it.',
  r_tc08_tpl.created_at  = datetime(),
  r_tc08_tpl.updated_at  = datetime();


// ===========================================================================
// TC08 — MITIGATIONS
// ===========================================================================

// M1: High effectiveness — linked to OR2 via MITIGATES (but nullified by upstream OR1)
MERGE (m_tc08_m1:Mitigation {id: 'tc08-0002-0000-0000-000000000001'})
ON CREATE SET
  m_tc08_m1.name        = '[TC08] Control High',
  m_tc08_m1.type        = 'Dedicated',
  m_tc08_m1.status      = 'Implemented',
  m_tc08_m1.description = '[TC08] High-effectiveness control on OR2. Reduction=0.7, factor=0.3. BUT upstream OR1 (unmitigated) nullifies it — Mitigation Exposure delta = 0.',
  m_tc08_m1.created_at  = datetime(),
  m_tc08_m1.updated_at  = datetime();

// M2: Medium effectiveness — linked to BR1 via MITIGATES (provides effective reduction)
MERGE (m_tc08_m2:Mitigation {id: 'tc08-0002-0000-0000-000000000002'})
ON CREATE SET
  m_tc08_m2.name        = '[TC08] Control Medium',
  m_tc08_m2.type        = 'Inherited',
  m_tc08_m2.status      = 'Implemented',
  m_tc08_m2.description = '[TC08] Medium-effectiveness control on BR1. Reduction=0.5, factor=0.5. Provides real protection: Mitigation Exposure delta = +6.0 (BR1 goes from 42 to 48 if removed).',
  m_tc08_m2.created_at  = datetime(),
  m_tc08_m2.updated_at  = datetime();

// M3: Proposed, NOT LINKED to any risk — tests coverage gap and unlinked mitigation
MERGE (m_tc08_m3:Mitigation {id: 'tc08-0002-0000-0000-000000000003'})
ON CREATE SET
  m_tc08_m3.name        = '[TC08] Control Proposed',
  m_tc08_m3.type        = 'Dedicated',
  m_tc08_m3.status      = 'Proposed',
  m_tc08_m3.description = '[TC08] Proposed control — NOT linked to any risk via MITIGATES. Tests coverage gap: BR2 (Final=12) has no active mitigation. Mitigation Exposure shows no delta for M3.',
  m_tc08_m3.created_at  = datetime(),
  m_tc08_m3.updated_at  = datetime();


// ===========================================================================
// TC08 — TPO (Target Performance Objective)
// ===========================================================================

MERGE (t_tc08_tpo1:TPO {id: 'tc08-0003-0000-0000-000000000001'})
ON CREATE SET
  t_tc08_tpo1.reference   = '[TC08] TPO-1',
  t_tc08_tpo1.name        = '[TC08] Programme Cost Objective',
  t_tc08_tpo1.cluster     = 'Business Efficiency',
  t_tc08_tpo1.description = '[TC08] Programme cost objective impacted by BR1. Tests TPO display, IMPACTS_TPO relationship, and node property panel.',
  t_tc08_tpo1.created_at  = datetime(),
  t_tc08_tpo1.updated_at  = datetime();


// ===========================================================================
// TC08 — RELATIONSHIPS: INFLUENCES
// ===========================================================================

// OR1 → OR2 : Critical (Op-to-Op) — unmitigated source propagates full residual
MATCH (s:Risk {id: 'tc08-0001-0000-0000-000000000003'}),
      (t:Risk {id: 'tc08-0001-0000-0000-000000000004'})
MERGE (s)-[rel:INFLUENCES {id: 'tc08-inf-0000-0000-000000000001'}]->(t)
ON CREATE SET
  rel.strength    = 'Critical',
  rel.description = '[TC08] OR1 → OR2: Critical influence. Unmitigated source (residual=1.0) fully nullifies OR2\'s High mitigation.',
  rel.confidence  = 0.8,
  rel.created_at  = datetime();

// OR2 → BR1 : Strong (Op-to-Bus) — residual=1.0 from OR2 (mitigation nullified) limits BR1
MATCH (s:Risk {id: 'tc08-0001-0000-0000-000000000004'}),
      (t:Risk {id: 'tc08-0001-0000-0000-000000000001'})
MERGE (s)-[rel:INFLUENCES {id: 'tc08-inf-0000-0000-000000000002'}]->(t)
ON CREATE SET
  rel.strength    = 'Strong',
  rel.description = '[TC08] OR2 → BR1: Strong influence. OR2 residual=1.0 (mitigation nullified), so limitation = 0.75×1.0 = 0.75 on BR1.',
  rel.confidence  = 0.8,
  rel.created_at  = datetime();


// ===========================================================================
// TC08 — RELATIONSHIPS: MITIGATES
// ===========================================================================

// M1 → OR2 : High effectiveness (but nullified by upstream OR1 — Mitigation Exposure delta = 0)
MATCH (m:Mitigation {id: 'tc08-0002-0000-0000-000000000001'}),
      (r:Risk       {id: 'tc08-0001-0000-0000-000000000004'})
MERGE (m)-[rel:MITIGATES {id: 'tc08-mit-0000-0000-000000000001'}]->(r)
ON CREATE SET
  rel.effectiveness = 'High',
  rel.description   = '[TC08] High control on OR2. Factor=0.3, but nullified by upstream OR1. Removing this mitigation has ZERO impact on Final Exposure.',
  rel.created_at    = datetime();

// M2 → BR1 : Medium effectiveness (provides real residual reduction — Mitigation Exposure delta = 6)
MATCH (m:Mitigation {id: 'tc08-0002-0000-0000-000000000002'}),
      (r:Risk       {id: 'tc08-0001-0000-0000-000000000001'})
MERGE (m)-[rel:MITIGATES {id: 'tc08-mit-0000-0000-000000000002'}]->(r)
ON CREATE SET
  rel.effectiveness = 'Medium',
  rel.description   = '[TC08] Medium control on BR1. Factor=0.5. Provides genuine protection: BR1 Final goes from 48→42. Mitigation Exposure delta=6.',
  rel.created_at    = datetime();

// NOTE: M3 ([TC08] Control Proposed) has NO MITIGATES relationship.
// This is intentional — tests the coverage gap for BR2.


// ===========================================================================
// TC08 — RELATIONSHIPS: IMPACTS_TPO
// ===========================================================================

// BR1 → TPO-1 (programme cost objective impacted by Business Risk Alpha)
MATCH (r:Risk {id: 'tc08-0001-0000-0000-000000000001'}),
      (t:TPO  {id: 'tc08-0003-0000-0000-000000000001'})
MERGE (r)-[rel:IMPACTS_TPO {id: 'tc08-tpo-0000-0000-000000000001'}]->(t)
ON CREATE SET
  rel.created_at = datetime();

// ===========================================================================
// END TC08
// ===========================================================================
