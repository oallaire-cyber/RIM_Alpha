// =============================================================================
// Orbital Dynamics Technologies - Risk Influence Map Demo Dataset
// Space Industry Use Case: LEO Constellation & GEO Relay Programs
// Execute in Neo4j Browser or via cypher-shell
// =============================================================================

// 1. PURGE (optional, uncomment if you need to start fresh)
MATCH (n) DETACH DELETE n;

// =============================================================================
// 2. COMPANY-LEVEL BUSINESS RISKS (5)
// Corporate risks affecting ODT as a whole
// =============================================================================

CREATE (rc01:Risk {
  id: 'RC-01',
  name: 'Failure to achieve EBITDA positive by 2028',
  description: 'Risk that ODT does not reach positive EBITDA within the investor-committed timeline, triggering covenant breach and potential forced restructuring',
  level: 'Business',
  scope: 'Company',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Corporate', 'Financial'],
  owner: 'CEO',
  probability: 6.0,
  impact: 10.0,
  exposure: 60.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (rc02:Risk {
  id: 'RC-02',
  name: 'Cash runway exhaustion before revenue ramp',
  description: 'Risk of depleting available cash reserves before recurring revenue from constellation services reaches sustainability threshold',
  level: 'Business',
  scope: 'Company',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Corporate', 'Financial'],
  owner: 'CFO',
  probability: 5.0,
  impact: 10.0,
  exposure: 50.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (rc03:Risk {
  id: 'RC-03',
  name: 'Loss of investor confidence',
  description: 'Risk that key investors lose confidence in ODT execution capability, blocking Series C funding or triggering down-round valuation',
  level: 'Business',
  scope: 'Company',
  status: 'Active',
  origin: 'New',
  categories: ['Corporate', 'Financial'],
  owner: 'CEO',
  probability: 4.0,
  impact: 9.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (rc04:Risk {
  id: 'RC-04',
  name: 'Multi-jurisdiction regulatory non-compliance',
  description: 'Risk of simultaneous regulatory failures across FCC, ITU, ESA and national authorities blocking global service deployment',
  level: 'Business',
  scope: 'Company',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Corporate', 'Regulatory'],
  owner: 'VP Compliance & Quality',
  probability: 4.0,
  impact: 8.0,
  exposure: 32.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rc05:Risk {
  id: 'RC-05',
  name: 'Reputational damage from on-orbit incident',
  description: 'Risk that a satellite collision, debris generation event, or service outage causes lasting reputational harm affecting customer acquisition and investor relations',
  level: 'Business',
  scope: 'Company',
  status: 'Active',
  origin: 'New',
  categories: ['Corporate', 'Product'],
  owner: 'CEO',
  probability: 3.0,
  impact: 9.0,
  exposure: 27.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 3. HORIZON-LEO PROGRAM BUSINESS RISKS (7)
// Operational constellation program - Phase 2 complete, Phase 3 underway
// =============================================================================

CREATE (rh01:Risk {
  id: 'RH-01',
  name: 'Phase 3 launch schedule delay',
  description: 'Risk of delay in Phase 3 deployment (24 satellites) due to launch vehicle availability, integration issues, or regulatory holdups',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Industrial'],
  owner: 'VP Launch Operations',
  probability: 7.0,
  impact: 8.0,
  exposure: 56.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (rh02:Risk {
  id: 'RH-02',
  name: 'On-orbit satellite performance degradation',
  description: 'Risk of premature degradation of Phase 1/2 satellites reducing constellation capacity before Phase 3 compensates',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Product'],
  owner: 'VP Engineering',
  probability: 5.0,
  impact: 7.0,
  exposure: 35.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (rh03:Risk {
  id: 'RH-03',
  name: 'Corporate segment revenue target miss',
  description: 'Risk of missing corporate connectivity revenue targets due to slower-than-expected enterprise customer acquisition',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Commercial'],
  owner: 'VP Sales',
  probability: 6.0,
  impact: 7.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (rh04:Risk {
  id: 'RH-04',
  name: 'Loss of competitive positioning vs mega-constellations',
  description: 'Risk that Starlink, Kuiper, or OneWeb achieve price/performance levels that commoditise ODT offering before differentiation is established',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Commercial'],
  owner: 'CTO',
  probability: 6.0,
  impact: 8.0,
  exposure: 48.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (rh05:Risk {
  id: 'RH-05',
  name: 'Government & Defense contract pipeline failure',
  description: 'Risk of failing to secure targeted DoD and allied government contracts due to security certification gaps or competitor incumbency',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Commercial'],
  owner: 'VP Sales',
  probability: 5.0,
  impact: 8.0,
  exposure: 40.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (rh06:Risk {
  id: 'RH-06',
  name: 'Ground segment capacity bottleneck',
  description: 'Risk that ground station throughput becomes the limiting factor for constellation service quality as satellite count scales',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Contingent',
  origin: 'New',
  categories: ['Programme', 'Product'],
  owner: 'VP Ground & Ops',
  activation_condition: 'If Phase 3 satellites exceed 40 active beams per satellite in high-demand zones',
  activation_decision_date: '2026-06-30',
  probability: 5.0,
  impact: 6.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rh07:Risk {
  id: 'RH-07',
  name: 'ITU frequency coordination failure',
  description: 'Risk of losing priority filing or failing coordination with incumbent operators, restricting available spectrum in key markets',
  level: 'Business',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Regulatory'],
  owner: 'VP Compliance & Quality',
  probability: 4.0,
  impact: 8.0,
  exposure: 32.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 4. AURORA-GEO PROGRAM BUSINESS RISKS (5)
// Early development GEO relay satellite program - PDR stage
// =============================================================================

CREATE (ra01:Risk {
  id: 'RA-01',
  name: 'PDR technical readiness delay',
  description: 'Risk of Preliminary Design Review schedule slip due to incomplete system-level trade studies or immature subsystem definitions',
  level: 'Business',
  scope: 'AURORA-GEO',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Product'],
  owner: 'AURORA Program Director',
  probability: 6.0,
  impact: 7.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (ra02:Risk {
  id: 'RA-02',
  name: 'Development budget overrun',
  description: 'Risk of exceeding allocated Phase A/B development budget due to technology maturation challenges or scope creep',
  level: 'Business',
  scope: 'AURORA-GEO',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Financial'],
  owner: 'CFO',
  probability: 7.0,
  impact: 6.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (ra03:Risk {
  id: 'RA-03',
  name: 'Optical inter-satellite link technology maturation failure',
  description: 'Risk that free-space optical communication technology does not achieve required BER and pointing accuracy within timeline',
  level: 'Business',
  scope: 'AURORA-GEO',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Product'],
  owner: 'CTO',
  probability: 5.0,
  impact: 9.0,
  exposure: 45.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (ra04:Risk {
  id: 'RA-04',
  name: 'Strategic partner withdrawal',
  description: 'Risk that key technology or co-investment partner withdraws from AURORA program due to strategic realignment or M&A activity',
  level: 'Business',
  scope: 'AURORA-GEO',
  status: 'Contingent',
  origin: 'New',
  categories: ['Programme', 'Supply Chain'],
  owner: 'AURORA Program Director',
  activation_condition: 'If partner M&A activity is confirmed or strategic review initiated',
  activation_decision_date: '2026-12-31',
  probability: 4.0,
  impact: 9.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ra05:Risk {
  id: 'RA-05',
  name: 'ITAR export control blocking key partnerships',
  description: 'Risk that US export control restrictions prevent critical technology sharing with non-US partners essential for AURORA development',
  level: 'Business',
  scope: 'AURORA-GEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Regulatory'],
  owner: 'VP Compliance & Quality',
  probability: 5.0,
  impact: 7.0,
  exposure: 35.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 5. OPERATIONAL RISKS - ENGINEERING (3)
// =============================================================================

CREATE (roe01:Risk {
  id: 'ROE-01',
  name: 'Payload reconfiguration software critical defect',
  description: 'Undetected software defect in payload reconfiguration engine causing beam misallocation or service interruption across active satellites',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Product', 'Engineering'],
  owner: 'Lead Software Architect',
  probability: 4.0,
  impact: 9.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (roe02:Risk {
  id: 'ROE-02',
  name: 'Thermal design margin exceedance on Phase 3 batch',
  description: 'Risk that thermal analysis margins are insufficient for Phase 3 orbital configuration, leading to premature component degradation',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Product', 'Engineering'],
  owner: 'Thermal Subsystem Lead',
  probability: 5.0,
  impact: 7.0,
  exposure: 35.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (roe03:Risk {
  id: 'ROE-03',
  name: 'Optical terminal pointing accuracy failure',
  description: 'Risk that AURORA inter-satellite optical link terminal cannot maintain required pointing accuracy in GEO thermal environment',
  level: 'Operational',
  scope: 'AURORA-GEO',
  status: 'Active',
  origin: 'New',
  categories: ['Product', 'Engineering'],
  owner: 'AURORA Chief Engineer',
  probability: 5.0,
  impact: 8.0,
  exposure: 40.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

// =============================================================================
// 6. OPERATIONAL RISKS - MANUFACTURING & SUPPLY CHAIN (4)
// =============================================================================

CREATE (rom01:Risk {
  id: 'ROM-01',
  name: 'RF component sole-source supplier failure',
  description: 'Failure or force majeure event at Teledyne, sole source for Ku/Ka-band transponder modules, halting satellite production',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Supply Chain', 'Industrial'],
  owner: 'VP Manufacturing & Supply Chain',
  probability: 4.0,
  impact: 9.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (rom02:Risk {
  id: 'ROM-02',
  name: 'Battery supplier critical delivery delay',
  description: 'Risk that Saft Batteries fails to deliver qualified space-grade lithium-ion cells within 12-month lead time window',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Supply Chain'],
  owner: 'VP Manufacturing & Supply Chain',
  probability: 5.0,
  impact: 7.0,
  exposure: 35.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (rom03:Risk {
  id: 'ROM-03',
  name: 'Composite structure quality deviation',
  description: 'Progressive quality drift in composite satellite bus structures from tier-1 subcontractor, risking structural integrity',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Industrial', 'Supply Chain'],
  owner: 'Quality Manager',
  probability: 4.0,
  impact: 7.0,
  exposure: 28.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rom04:Risk {
  id: 'ROM-04',
  name: 'Clean room contamination event',
  description: 'Particulate or chemical contamination event in satellite AIT clean room forcing production halt and decontamination',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Industrial'],
  owner: 'Plant Director',
  probability: 3.0,
  impact: 7.0,
  exposure: 21.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 7. OPERATIONAL RISKS - LAUNCH OPERATIONS (2)
// =============================================================================

CREATE (rol01:Risk {
  id: 'ROL-01',
  name: 'Launch vehicle availability gap',
  description: 'Risk of SpaceX or Rocket Lab manifest congestion creating 6+ month gap in available launch slots for Phase 3 deployment',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Supply Chain'],
  owner: 'VP Launch Operations',
  probability: 6.0,
  impact: 8.0,
  exposure: 48.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (rol02:Risk {
  id: 'ROL-02',
  name: 'Orbital debris collision during deployment',
  description: 'Risk of collision with tracked or untracked debris during constellation deployment manoeuvres in congested LEO regime',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Product'],
  owner: 'VP Launch Operations',
  probability: 2.0,
  impact: 10.0,
  exposure: 20.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 8. OPERATIONAL RISKS - COMMERCIAL (2)
// =============================================================================

CREATE (roc01:Risk {
  id: 'ROC-01',
  name: 'Key enterprise customer churn',
  description: 'Risk of losing top-5 enterprise customers to competitor offering due to pricing pressure or SLA underperformance',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Commercial'],
  owner: 'VP Sales',
  probability: 5.0,
  impact: 6.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (roc02:Risk {
  id: 'ROC-02',
  name: 'Channel partner underperformance',
  description: 'Risk that contracted satellite integrators and managed service providers fail to deliver committed customer acquisition volumes',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Commercial'],
  owner: 'VP Sales',
  probability: 6.0,
  impact: 5.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

// =============================================================================
// 9. OPERATIONAL RISKS - FINANCE & HR & LEGAL (5)
// =============================================================================

CREATE (rof01:Risk {
  id: 'ROF-01',
  name: 'Foreign exchange exposure on international contracts',
  description: 'Risk of significant FX losses on EUR/GBP/SGD-denominated contracts without adequate hedging, eroding margins',
  level: 'Operational',
  scope: 'Company',
  status: 'Active',
  origin: 'New',
  categories: ['Financial'],
  owner: 'CFO',
  probability: 6.0,
  impact: 5.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rof02:Risk {
  id: 'ROF-02',
  name: 'On-orbit asset insurance coverage gap',
  description: 'Risk that underwriters reduce coverage limits or increase premiums making satellite constellation insurance economically unviable',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Financial'],
  owner: 'CFO',
  probability: 4.0,
  impact: 7.0,
  exposure: 28.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (roh01:Risk {
  id: 'ROH-01',
  name: 'Key engineering talent attrition',
  description: 'Risk of losing critical satellite design and payload software engineers to competitor new space companies',
  level: 'Operational',
  scope: 'Company',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'HR'],
  owner: 'HR Director',
  probability: 7.0,
  impact: 7.0,
  exposure: 49.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (roh02:Risk {
  id: 'ROH-02',
  name: 'ITAR-cleared personnel shortage',
  description: 'Risk that insufficient ITAR-cleared engineers are available for Government & Defense program work, blocking contract execution',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['HR', 'Regulatory'],
  owner: 'HR Director',
  probability: 6.0,
  impact: 6.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (ror01:Risk {
  id: 'ROR-01',
  name: 'FCC spectrum license conditions breach',
  description: 'Risk of unintentional breach of FCC license conditions triggering investigation, fine, or license suspension',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Regulatory'],
  owner: 'VP Compliance & Quality',
  probability: 3.0,
  impact: 9.0,
  exposure: 27.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 10. OPERATIONAL RISKS - IT & DIGITAL (1)
// =============================================================================

CREATE (roi01:Risk {
  id: 'ROI-01',
  name: 'NOC system extended outage',
  description: 'Major failure of Network Operations Center systems causing loss of constellation monitoring and customer service management',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'IT'],
  owner: 'IT Director',
  probability: 3.0,
  impact: 8.0,
  exposure: 24.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 11. SECURITY OPERATIONAL RISKS (14)
// =============================================================================

CREATE (sec01:Risk {
  id: 'SEC-01',
  name: 'APT attack on satellite command and control system',
  description: 'Advanced persistent threat actor gains access to TT&C (telemetry, tracking and command) systems enabling unauthorized satellite commands',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'Product'],
  owner: 'CISO',
  probability: 4.0,
  impact: 10.0,
  exposure: 40.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (sec02:Risk {
  id: 'SEC-02',
  name: 'Supply chain compromise - malicious firmware insertion',
  description: 'State-sponsored actor inserts malicious firmware or hardware backdoor into satellite components during manufacturing supply chain',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'Supply Chain'],
  owner: 'CISO',
  probability: 3.0,
  impact: 10.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec03:Risk {
  id: 'SEC-03',
  name: 'Insider threat - privileged TT&C access abuse',
  description: 'Malicious or compromised insider with privileged access to satellite command systems executes unauthorized operations',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security'],
  owner: 'CISO',
  probability: 3.0,
  impact: 9.0,
  exposure: 27.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec04:Risk {
  id: 'SEC-04',
  name: 'Ransomware attack on ground segment infrastructure',
  description: 'Ransomware deployment across ground station control systems and NOC, causing complete loss of constellation management capability',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Security', 'IT'],
  owner: 'CISO',
  probability: 5.0,
  impact: 9.0,
  exposure: 45.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (sec05:Risk {
  id: 'SEC-05',
  name: 'RF signal jamming and spoofing attack',
  description: 'Deliberate jamming or spoofing of customer communication links degrading service quality in targeted geographic regions',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'Product'],
  owner: 'CISO',
  probability: 5.0,
  impact: 7.0,
  exposure: 35.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec06:Risk {
  id: 'SEC-06',
  name: 'Engineering data exfiltration by state-sponsored actor',
  description: 'Competitor- or state-sponsored actor exfiltrates proprietary payload design, beam-forming algorithms, or reconfiguration IP from PLM/engineering systems',
  level: 'Operational',
  scope: 'Company',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Security', 'Product'],
  owner: 'CISO',
  probability: 5.0,
  impact: 9.0,
  exposure: 45.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

CREATE (sec07:Risk {
  id: 'SEC-07',
  name: 'Physical security breach at ground station',
  description: 'Unauthorized physical access to ground station facility enabling equipment tampering, data theft, or sabotage',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security'],
  owner: 'CISO',
  probability: 2.0,
  impact: 8.0,
  exposure: 16.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (sec08:Risk {
  id: 'SEC-08',
  name: 'Cloud provider compromise affecting NOC services',
  description: 'Compromise of third-party cloud infrastructure hosting NOC orchestration and customer management platforms',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'IT'],
  owner: 'CISO',
  probability: 3.0,
  impact: 7.0,
  exposure: 21.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec09:Risk {
  id: 'SEC-09',
  name: 'Social engineering targeting launch operations staff',
  description: 'Targeted phishing or social engineering campaign against launch operations team to obtain credentials or operational intelligence',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'HR'],
  owner: 'CISO',
  probability: 6.0,
  impact: 6.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec10:Risk {
  id: 'SEC-10',
  name: 'DDoS on customer portal and API gateway',
  description: 'Distributed denial-of-service attack overwhelming customer-facing portal, provisioning APIs, and billing systems',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'Commercial'],
  owner: 'CISO',
  probability: 6.0,
  impact: 5.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec11:Risk {
  id: 'SEC-11',
  name: 'Satellite telemetry interception and analysis',
  description: 'Adversary intercepts and analyses unencrypted or weakly encrypted satellite telemetry to derive operational intelligence',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security'],
  owner: 'CISO',
  probability: 5.0,
  impact: 6.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec12:Risk {
  id: 'SEC-12',
  name: 'Unauthorized firmware modification via maintenance backdoor',
  description: 'Exploitation of maintenance or debug interfaces left active in flight software to inject unauthorized firmware updates',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security', 'Product'],
  owner: 'CISO',
  probability: 3.0,
  impact: 10.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec13:Risk {
  id: 'SEC-13',
  name: 'Cryptographic key compromise for satellite command auth',
  description: 'Compromise of cryptographic keys used for satellite command authentication, enabling unauthorized command injection',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'New',
  categories: ['Security'],
  owner: 'CISO',
  probability: 2.0,
  impact: 10.0,
  exposure: 20.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 60})
});

CREATE (sec14:Risk {
  id: 'SEC-14',
  name: 'IT-to-OT lateral movement into ground segment',
  description: 'Attacker pivots from corporate IT network into operational technology network controlling ground station equipment',
  level: 'Operational',
  scope: 'HORIZON-LEO',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Security', 'IT'],
  owner: 'CISO',
  probability: 4.0,
  impact: 9.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 30})
});

// =============================================================================
// 12. TOP PROGRAM OBJECTIVES (TPOs) - 6
// =============================================================================

CREATE (tpo01:TPO {
  id: 'TPO-01',
  reference: 'TPO-01',
  name: 'Achieve EBITDA positive by Q4 2028',
  cluster: 'Financial Performance',
  description: 'Reach positive EBITDA with 48+ operational satellites and $120M+ ARR by end of 2028',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo02:TPO {
  id: 'TPO-02',
  reference: 'TPO-02',
  name: 'Complete Phase 3 deployment by Q2 2027',
  cluster: 'Programme Delivery',
  description: 'Successfully deploy all 24 Phase 3 satellites to operational orbit with service activation',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo03:TPO {
  id: 'TPO-03',
  reference: 'TPO-03',
  name: 'Secure FCC full operational license by Q3 2026',
  cluster: 'Regulatory',
  description: 'Obtain full FCC operational license for HORIZON-LEO constellation including all frequency allocations',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo04:TPO {
  id: 'TPO-04',
  reference: 'TPO-04',
  name: 'Win first $10M+ Government contract by Q4 2026',
  cluster: 'Commercial',
  description: 'Secure at least one multi-year government or defense contract exceeding $10M ARR',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo05:TPO {
  id: 'TPO-05',
  reference: 'TPO-05',
  name: 'AURORA-GEO pass PDR gate by Q1 2027',
  cluster: 'Programme Delivery',
  description: 'Successfully pass Preliminary Design Review for AURORA-GEO relay satellite with all subsystem definitions at TRL 4+',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo06:TPO {
  id: 'TPO-06',
  reference: 'TPO-06',
  name: 'Maintain zero debris generation incidents',
  cluster: 'Safety & Compliance',
  description: 'Achieve and maintain zero debris generation events across entire constellation lifecycle, meeting IADC guidelines',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 13. MITIGATIONS - DEDICATED (12)
// =============================================================================

CREATE (m01:Mitigation {
  id: 'MIT-01',
  name: 'Multi-launcher diversification strategy',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Contracted launch slots with SpaceX, Rocket Lab, and Arianespace providing 3 independent launch paths for Phase 3',
  owner: 'VP Launch Operations',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m02:Mitigation {
  id: 'MIT-02',
  name: 'RF component dual-sourcing qualification',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Qualification of Airbus DS as second source for Ku/Ka transponder modules with framework contract negotiation',
  owner: 'VP Manufacturing & Supply Chain',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m03:Mitigation {
  id: 'MIT-03',
  name: 'Satellite engineering talent retention program',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Equity incentive program, technical career ladder, and competitive retention packages for top 50 critical engineers',
  owner: 'HR Director',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m04:Mitigation {
  id: 'MIT-04',
  name: 'Ground segment Zero Trust architecture',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Redesign of ground segment network following Zero Trust principles with micro-segmentation between IT and OT domains',
  owner: 'CISO',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m05:Mitigation {
  id: 'MIT-05',
  name: 'Satellite command authentication hardening',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Implementation of post-quantum cryptographic command authentication with hardware security module key management',
  owner: 'CISO',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m06:Mitigation {
  id: 'MIT-06',
  name: 'Enterprise customer success program',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Dedicated customer success managers for top-20 enterprise accounts with quarterly business reviews and SLA monitoring',
  owner: 'VP Sales',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m07:Mitigation {
  id: 'MIT-07',
  name: 'Autonomous collision avoidance system',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'AI-driven autonomous collision avoidance using 18th Space Defense Squadron conjunction data with sub-1km threshold manoeuvres',
  owner: 'VP Launch Operations',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m08:Mitigation {
  id: 'MIT-08',
  name: 'Payload software independent V&V program',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Independent verification and validation of payload reconfiguration software by third-party per ECSS-E-ST-40C',
  owner: 'Lead Software Architect',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m09:Mitigation {
  id: 'MIT-09',
  name: 'AURORA optical link risk reduction campaign',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Pre-PDR breadboard testing and thermal vacuum simulation of optical terminal pointing mechanism',
  owner: 'AURORA Chief Engineer',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m10:Mitigation {
  id: 'MIT-10',
  name: 'Supply chain hardware integrity verification',
  type: 'Dedicated',
  status: 'Proposed',
  description: 'X-ray inspection and firmware hash verification protocol for all mission-critical components received from tier-1 suppliers',
  owner: 'CISO',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m11:Mitigation {
  id: 'MIT-11',
  name: 'Anti-jamming adaptive beam-forming',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Software-defined anti-jamming capability using adaptive null-steering on phased array to mitigate targeted RF interference',
  owner: 'VP Engineering',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m12:Mitigation {
  id: 'MIT-12',
  name: 'Ransomware-specific incident response plan',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Dedicated ransomware playbook with offline backups, network isolation procedures, and pre-negotiated incident response retainer',
  owner: 'CISO',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 14. MITIGATIONS - INHERITED (4)
// =============================================================================

CREATE (m13:Mitigation {
  id: 'MIT-13',
  name: 'Corporate SOC 24/7 monitoring',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Shared Security Operations Center providing 24/7 threat detection, SIEM correlation, and incident response with SLA <15min',
  owner: 'CISO',
  source_entity: 'Corporate IT Security Division',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m14:Mitigation {
  id: 'MIT-14',
  name: 'Corporate financial planning and analysis process',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Monthly rolling forecast, variance analysis, and cash flow monitoring with board-level escalation on >5% deviation',
  owner: 'CFO',
  source_entity: 'Corporate Finance',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m15:Mitigation {
  id: 'MIT-15',
  name: 'Corporate IT disaster recovery',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Multi-region disaster recovery infrastructure with RTO 4h / RPO 1h for critical business systems',
  owner: 'IT Director',
  source_entity: 'Corporate IT Division',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m16:Mitigation {
  id: 'MIT-16',
  name: 'Corporate security awareness training',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Mandatory quarterly security awareness training and monthly phishing simulation campaigns for all employees',
  owner: 'CISO',
  source_entity: 'Corporate HR & Security',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 15. MITIGATIONS - BASELINE (5)
// =============================================================================

CREATE (m17:Mitigation {
  id: 'MIT-17',
  name: 'ECSS Space Product Assurance framework',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Compliance with ECSS-Q-ST-20C (quality assurance) and ECSS-Q-ST-80C (software product assurance) for all flight hardware and software',
  owner: 'VP Compliance & Quality',
  source_entity: 'ECSS Standards',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m18:Mitigation {
  id: 'MIT-18',
  name: 'NIST Cybersecurity Framework implementation',
  type: 'Baseline',
  status: 'Implemented',
  description: 'Full implementation of NIST CSF 2.0 across all IT and OT systems with annual maturity assessment',
  owner: 'CISO',
  source_entity: 'NIST CSF 2.0',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m19:Mitigation {
  id: 'MIT-19',
  name: 'FCC regulatory compliance program',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Systematic compliance tracking for all FCC license conditions with automated reporting and exception management',
  owner: 'VP Compliance & Quality',
  source_entity: 'FCC 47 CFR Parts 25 & 97',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m20:Mitigation {
  id: 'MIT-20',
  name: 'ITAR compliance management system',
  type: 'Baseline',
  status: 'Implemented',
  description: 'Comprehensive ITAR compliance program including technology control plans, deemed export procedures, and annual audit',
  owner: 'VP Compliance & Quality',
  source_entity: 'ITAR 22 CFR Parts 120-130',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m21:Mitigation {
  id: 'MIT-21',
  name: 'ISO 27001 ISMS certification',
  type: 'Baseline',
  status: 'Implemented',
  description: 'Certified Information Security Management System covering all ODT operations with annual surveillance audits',
  owner: 'CISO',
  source_entity: 'ISO/IEC 27001:2022',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 16. INFLUENCE LINKS - LEVEL 1 (Operational → Business)
// =============================================================================

// Engineering operational risks → Business risks
MATCH (source:Risk {id: 'ROE-01'}), (target:Risk {id: 'RH-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-01',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'Payload software defect directly degrades satellite performance',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROE-02'}), (target:Risk {id: 'RH-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-02',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'Thermal margin exceedance accelerates satellite degradation',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROE-03'}), (target:Risk {id: 'RA-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-03',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'Pointing accuracy failure is the core technical risk for optical ISL maturation',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Manufacturing & Supply Chain → Business
MATCH (source:Risk {id: 'ROM-01'}), (target:Risk {id: 'RH-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-04',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'RF component supplier failure halts satellite production, directly delaying Phase 3 launches',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROM-02'}), (target:Risk {id: 'RH-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-05',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'Battery delivery delay blocks satellite integration, impacting launch schedule',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROM-03'}), (target:Risk {id: 'RH-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-06',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Moderate',
  description: 'Structure quality deviation may cause premature satellite degradation',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Launch Operations → Business
MATCH (source:Risk {id: 'ROL-01'}), (target:Risk {id: 'RH-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-07',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'Launch vehicle unavailability directly blocks Phase 3 deployment schedule',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROL-02'}), (target:Risk {id: 'RC-05'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-08',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'Debris collision would generate severe reputational damage',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Commercial → Business
MATCH (source:Risk {id: 'ROC-01'}), (target:Risk {id: 'RH-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-09',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'Enterprise customer churn directly reduces corporate segment revenue',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROC-02'}), (target:Risk {id: 'RH-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-10',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'Channel underperformance reduces customer acquisition pipeline',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// HR → Business
MATCH (source:Risk {id: 'ROH-01'}), (target:Risk {id: 'RH-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-11',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'Talent loss erodes competitive technological differentiation',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROH-02'}), (target:Risk {id: 'RH-05'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-12',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'ITAR personnel shortage blocks government contract execution capability',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Regulatory → Business
MATCH (source:Risk {id: 'ROR-01'}), (target:Risk {id: 'RC-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-13',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'FCC breach directly contributes to multi-jurisdiction compliance failure',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// IT → Business
MATCH (source:Risk {id: 'ROI-01'}), (target:Risk {id: 'RH-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-14',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'NOC outage degrades ability to monitor and manage constellation performance',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Security → Business (key security escalation paths)
MATCH (source:Risk {id: 'SEC-01'}), (target:Risk {id: 'RC-05'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-15',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'APT compromising satellite command would be catastrophic reputational event',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-04'}), (target:Risk {id: 'RH-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-16',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'Ransomware on ground segment causes loss of constellation management',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-06'}), (target:Risk {id: 'RH-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-17',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Critical',
  description: 'IP exfiltration eliminates competitive technological advantage',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-05'}), (target:Risk {id: 'RH-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-18',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Strong',
  description: 'RF jamming degrades service quality causing customer revenue impact',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-10'}), (target:Risk {id: 'RH-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-19',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Moderate',
  description: 'DDoS on portal disrupts customer onboarding and billing',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Finance → Business
MATCH (source:Risk {id: 'ROF-01'}), (target:Risk {id: 'RC-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-20',
  influence_type: 'Level1_Op_to_Bus',
  strength: 'Moderate',
  description: 'FX losses erode margins impacting EBITDA target',
  confidence: 0.75,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 17. INFLUENCE LINKS - LEVEL 2 (Business → Business)
// =============================================================================

// HORIZON-LEO Business → Company
MATCH (source:Risk {id: 'RH-01'}), (target:Risk {id: 'RC-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-21',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Critical',
  description: 'Phase 3 delay pushes revenue ramp, directly threatening EBITDA timeline',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RH-03'}), (target:Risk {id: 'RC-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-22',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Critical',
  description: 'Revenue miss directly impacts EBITDA achievement',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RH-03'}), (target:Risk {id: 'RC-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-23',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Strong',
  description: 'Revenue shortfall accelerates cash burn rate',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RH-04'}), (target:Risk {id: 'RH-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-24',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Strong',
  description: 'Lost competitive positioning reduces customer win rates',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RC-02'}), (target:Risk {id: 'RC-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-25',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Critical',
  description: 'Cash runway exhaustion directly triggers investor confidence loss',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RC-04'}), (target:Risk {id: 'RH-07'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-26',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Strong',
  description: 'Multi-jurisdiction issues compound ITU coordination challenges',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RH-07'}), (target:Risk {id: 'RH-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-27',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Strong',
  description: 'Spectrum limitations reduce service capability vs competitors',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RC-05'}), (target:Risk {id: 'RC-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-28',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Critical',
  description: 'Reputational damage directly erodes investor confidence',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// AURORA → Company
MATCH (source:Risk {id: 'RA-02'}), (target:Risk {id: 'RC-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-29',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Moderate',
  description: 'AURORA budget overrun consumes cash reserves allocated for HORIZON operations',
  confidence: 0.75,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RA-03'}), (target:Risk {id: 'RA-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-30',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Critical',
  description: 'Optical technology maturation failure blocks PDR readiness',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RA-05'}), (target:Risk {id: 'RA-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-31',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Strong',
  description: 'ITAR restrictions may force partner to withdraw from program',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RH-05'}), (target:Risk {id: 'RC-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-32',
  influence_type: 'Level2_Bus_to_Bus',
  strength: 'Strong',
  description: 'Government contract failure removes high-ARPU revenue stream from EBITDA path',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 18. INFLUENCE LINKS - LEVEL 3 (Operational → Operational)
// =============================================================================

// Security chain reactions
MATCH (source:Risk {id: 'SEC-09'}), (target:Risk {id: 'SEC-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-33',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'Social engineering provides initial access vector for ransomware deployment',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-09'}), (target:Risk {id: 'SEC-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-34',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Social engineering credentials enable initial foothold for APT campaign',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-14'}), (target:Risk {id: 'SEC-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-35',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Critical',
  description: 'IT-to-OT lateral movement enables access to satellite command systems',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-14'}), (target:Risk {id: 'SEC-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-36',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'IT-to-OT pivot extends ransomware blast radius to ground segment',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-13'}), (target:Risk {id: 'SEC-12'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-37',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Critical',
  description: 'Compromised command keys enable unauthorized firmware modification',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-03'}), (target:Risk {id: 'SEC-13'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-38',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'Insider with privileged access can extract cryptographic keys',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-02'}), (target:Risk {id: 'SEC-12'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-39',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'Supply chain malicious firmware is unauthorized modification by nature',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-08'}), (target:Risk {id: 'ROI-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-40',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'Cloud provider compromise causes NOC service outage',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// Non-security operational chains
MATCH (source:Risk {id: 'ROH-01'}), (target:Risk {id: 'ROE-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-41',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Talent loss increases risk of undetected software defects',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'ROM-01'}), (target:Risk {id: 'ROM-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-42',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Supplier failure forces use of less qualified backup sources, increasing quality risk',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-07'}), (target:Risk {id: 'SEC-14'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-43',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Physical breach at ground station can provide network access point for IT-to-OT pivot',
  confidence: 0.65,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'SEC-11'}), (target:Risk {id: 'SEC-05'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-44',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Telemetry intelligence informs targeted jamming/spoofing attacks',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 19. TPO IMPACT LINKS (Business Risk → TPO)
// =============================================================================

// TPO-01: EBITDA positive by Q4 2028
MATCH (r:Risk {id: 'RC-01'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-01',
  impact_level: 'Critical',
  description: 'Direct impact: this is the risk of not achieving the TPO',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RC-02'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-02',
  impact_level: 'Critical',
  description: 'Cash exhaustion prevents reaching EBITDA positive date',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RH-03'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-03',
  impact_level: 'High',
  description: 'Revenue miss shifts EBITDA timeline',
  created_at: datetime()
}]->(t);

// TPO-02: Phase 3 deployment by Q2 2027
MATCH (r:Risk {id: 'RH-01'}), (t:TPO {id: 'TPO-02'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-04',
  impact_level: 'Critical',
  description: 'Direct impact: schedule delay threatens deployment objective',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RH-02'}), (t:TPO {id: 'TPO-02'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-05',
  impact_level: 'Medium',
  description: 'Degradation may require replacement satellites in Phase 3',
  created_at: datetime()
}]->(t);

// TPO-03: FCC license by Q3 2026
MATCH (r:Risk {id: 'RC-04'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-06',
  impact_level: 'Critical',
  description: 'Regulatory non-compliance directly blocks FCC license',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RH-07'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-07',
  impact_level: 'High',
  description: 'ITU coordination failures complicate FCC approval',
  created_at: datetime()
}]->(t);

// TPO-04: Government contract $10M+ by Q4 2026
MATCH (r:Risk {id: 'RH-05'}), (t:TPO {id: 'TPO-04'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-08',
  impact_level: 'Critical',
  description: 'Direct impact: government pipeline failure prevents contract win',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RC-05'}), (t:TPO {id: 'TPO-04'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-09',
  impact_level: 'High',
  description: 'Reputational damage undermines government trust and contract selection',
  created_at: datetime()
}]->(t);

// TPO-05: AURORA PDR by Q1 2027
MATCH (r:Risk {id: 'RA-01'}), (t:TPO {id: 'TPO-05'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-10',
  impact_level: 'Critical',
  description: 'Direct impact: PDR readiness delay threatens PDR gate objective',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RA-03'}), (t:TPO {id: 'TPO-05'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-11',
  impact_level: 'Critical',
  description: 'Optical ISL technology maturation is the PDR critical path item',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RA-05'}), (t:TPO {id: 'TPO-05'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-12',
  impact_level: 'Medium',
  description: 'ITAR issues may block partner contributions needed for PDR',
  created_at: datetime()
}]->(t);

// TPO-06: Zero debris incidents
MATCH (r:Risk {id: 'RC-05'}), (t:TPO {id: 'TPO-06'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-13',
  impact_level: 'High',
  description: 'Reputational events most likely to originate from debris incident',
  created_at: datetime()
}]->(t);

MATCH (r:Risk {id: 'RH-02'}), (t:TPO {id: 'TPO-06'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-14',
  impact_level: 'Medium',
  description: 'Degraded satellites may lose de-orbit capability',
  created_at: datetime()
}]->(t);

// =============================================================================
// 20. MITIGATES LINKS (Mitigation → Risk)
// =============================================================================

// MIT-01 (Multi-launcher) → Launch risks
MATCH (m:Mitigation {id: 'MIT-01'}), (r:Risk {id: 'ROL-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-01',
  effectiveness: 'High',
  description: 'Three independent launch providers reduce manifest congestion risk',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-01'}), (r:Risk {id: 'RH-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-02',
  effectiveness: 'Medium',
  description: 'Launch diversification provides schedule flexibility for Phase 3',
  created_at: datetime()
}]->(r);

// MIT-02 (RF dual-sourcing) → Supply chain risks
MATCH (m:Mitigation {id: 'MIT-02'}), (r:Risk {id: 'ROM-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-03',
  effectiveness: 'High',
  description: 'Second qualified source eliminates single-point supply failure',
  created_at: datetime()
}]->(r);

// MIT-03 (Talent retention) → HR risks
MATCH (m:Mitigation {id: 'MIT-03'}), (r:Risk {id: 'ROH-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-04',
  effectiveness: 'High',
  description: 'Retention program significantly reduces critical engineer turnover',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-03'}), (r:Risk {id: 'RH-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-05',
  effectiveness: 'Medium',
  description: 'Retaining talent preserves competitive innovation capability',
  created_at: datetime()
}]->(r);

// MIT-04 (Zero Trust) → Security risks
MATCH (m:Mitigation {id: 'MIT-04'}), (r:Risk {id: 'SEC-14'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-06',
  effectiveness: 'Critical',
  description: 'Zero Trust micro-segmentation prevents IT-to-OT lateral movement',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-04'}), (r:Risk {id: 'SEC-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-07',
  effectiveness: 'High',
  description: 'Network segmentation contains ransomware blast radius',
  created_at: datetime()
}]->(r);

// MIT-05 (Command auth hardening) → Security risks
MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'SEC-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-08',
  effectiveness: 'Critical',
  description: 'Post-quantum command authentication prevents unauthorized satellite commands',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'SEC-13'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-09',
  effectiveness: 'High',
  description: 'HSM-based key management reduces key compromise attack surface',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'SEC-12'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-10',
  effectiveness: 'High',
  description: 'Authenticated command chain prevents unauthorized firmware updates',
  created_at: datetime()
}]->(r);

// MIT-06 (Customer success) → Commercial risks
MATCH (m:Mitigation {id: 'MIT-06'}), (r:Risk {id: 'ROC-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-11',
  effectiveness: 'High',
  description: 'Customer success management reduces churn through proactive engagement',
  created_at: datetime()
}]->(r);

// MIT-07 (Collision avoidance) → Safety risks
MATCH (m:Mitigation {id: 'MIT-07'}), (r:Risk {id: 'ROL-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-12',
  effectiveness: 'Critical',
  description: 'Autonomous manoeuvre capability minimizes collision probability',
  created_at: datetime()
}]->(r);

// MIT-08 (Payload V&V) → Software risks
MATCH (m:Mitigation {id: 'MIT-08'}), (r:Risk {id: 'ROE-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-13',
  effectiveness: 'High',
  description: 'Independent V&V maximizes defect detection before deployment',
  created_at: datetime()
}]->(r);

// MIT-09 (Optical risk reduction) → AURORA risks
MATCH (m:Mitigation {id: 'MIT-09'}), (r:Risk {id: 'ROE-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-14',
  effectiveness: 'High',
  description: 'Pre-PDR breadboard testing reduces pointing accuracy uncertainty',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-09'}), (r:Risk {id: 'RA-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-15',
  effectiveness: 'High',
  description: 'Risk reduction campaign de-risks optical ISL technology maturation',
  created_at: datetime()
}]->(r);

// MIT-10 (Hardware integrity) → Supply chain security
MATCH (m:Mitigation {id: 'MIT-10'}), (r:Risk {id: 'SEC-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-16',
  effectiveness: 'High',
  description: 'X-ray and hash verification detect compromised components before integration',
  created_at: datetime()
}]->(r);

// MIT-11 (Anti-jamming) → RF security
MATCH (m:Mitigation {id: 'MIT-11'}), (r:Risk {id: 'SEC-05'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-17',
  effectiveness: 'High',
  description: 'Adaptive null-steering neutralizes targeted jamming sources',
  created_at: datetime()
}]->(r);

// MIT-12 (Ransomware IR) → Ransomware risk
MATCH (m:Mitigation {id: 'MIT-12'}), (r:Risk {id: 'SEC-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-18',
  effectiveness: 'High',
  description: 'Offline backups and playbook ensure rapid recovery from ransomware',
  created_at: datetime()
}]->(r);

// MIT-13 (SOC) → Multiple security risks
MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'SEC-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-19',
  effectiveness: 'High',
  description: '24/7 SOC monitoring enables early APT detection',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'SEC-14'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-20',
  effectiveness: 'Medium',
  description: 'SOC SIEM correlation detects lateral movement patterns',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'SEC-10'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-21',
  effectiveness: 'Medium',
  description: 'SOC can activate DDoS mitigation within SLA',
  created_at: datetime()
}]->(r);

// MIT-14 (FP&A) → Financial risks
MATCH (m:Mitigation {id: 'MIT-14'}), (r:Risk {id: 'RC-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-22',
  effectiveness: 'Medium',
  description: 'Cash flow monitoring enables early warning on runway exhaustion',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-14'}), (r:Risk {id: 'RA-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-23',
  effectiveness: 'Medium',
  description: 'Variance analysis catches AURORA budget overrun trends early',
  created_at: datetime()
}]->(r);

// MIT-15 (DR) → IT risks
MATCH (m:Mitigation {id: 'MIT-15'}), (r:Risk {id: 'ROI-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-24',
  effectiveness: 'Critical',
  description: 'DR infrastructure ensures NOC recovery within 4h RTO',
  created_at: datetime()
}]->(r);

// MIT-16 (Security awareness) → Social engineering
MATCH (m:Mitigation {id: 'MIT-16'}), (r:Risk {id: 'SEC-09'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-25',
  effectiveness: 'High',
  description: 'Phishing simulations and training reduce social engineering success rate',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-16'}), (r:Risk {id: 'SEC-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-26',
  effectiveness: 'Medium',
  description: 'Security culture awareness reduces insider threat opportunity',
  created_at: datetime()
}]->(r);

// MIT-17 (ECSS) → Quality risks
MATCH (m:Mitigation {id: 'MIT-17'}), (r:Risk {id: 'ROM-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-27',
  effectiveness: 'High',
  description: 'ECSS quality framework mandates rigorous process controls',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-17'}), (r:Risk {id: 'ROE-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-28',
  effectiveness: 'Medium',
  description: 'ECSS thermal analysis requirements ensure margin adequacy',
  created_at: datetime()
}]->(r);

// MIT-18 (NIST CSF) → Broad security
MATCH (m:Mitigation {id: 'MIT-18'}), (r:Risk {id: 'SEC-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-29',
  effectiveness: 'High',
  description: 'NIST CSF Protect function controls reduce data exfiltration risk',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-18'}), (r:Risk {id: 'SEC-08'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-30',
  effectiveness: 'Medium',
  description: 'NIST CSF supply chain risk management extends to cloud providers',
  created_at: datetime()
}]->(r);

// MIT-19 (FCC compliance) → Regulatory risks
MATCH (m:Mitigation {id: 'MIT-19'}), (r:Risk {id: 'ROR-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-31',
  effectiveness: 'Critical',
  description: 'Automated compliance tracking prevents unintentional license breaches',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-19'}), (r:Risk {id: 'RC-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-32',
  effectiveness: 'High',
  description: 'FCC compliance program is key pillar of multi-jurisdiction compliance',
  created_at: datetime()
}]->(r);

// MIT-20 (ITAR) → Export control risks
MATCH (m:Mitigation {id: 'MIT-20'}), (r:Risk {id: 'RA-05'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-33',
  effectiveness: 'High',
  description: 'ITAR compliance system enables structured technology sharing within legal boundaries',
  created_at: datetime()
}]->(r);

// MIT-21 (ISO 27001) → Security posture
MATCH (m:Mitigation {id: 'MIT-21'}), (r:Risk {id: 'SEC-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-34',
  effectiveness: 'Medium',
  description: 'ISMS controls provide defense-in-depth for IP protection',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-21'}), (r:Risk {id: 'SEC-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-35',
  effectiveness: 'High',
  description: 'ISO 27001 Annex A physical security controls protect ground stations',
  created_at: datetime()
}]->(r);

MATCH (m:Mitigation {id: 'MIT-21'}), (r:Risk {id: 'SEC-11'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-36',
  effectiveness: 'Medium',
  description: 'ISMS cryptographic controls address telemetry encryption requirements',
  created_at: datetime()
}]->(r);

// =============================================================================
// 21. VERIFICATION QUERIES
// =============================================================================

// Count risks by level and scope
MATCH (r:Risk)
RETURN r.level as Level, r.scope as Scope, count(r) as Count
ORDER BY Level, Scope;

// Count risks by category
MATCH (r:Risk)
UNWIND r.categories AS cat
RETURN cat as Category, count(r) as Count
ORDER BY Count DESC;

// Count risks by status
MATCH (r:Risk)
RETURN r.status as Status, count(r) as Count
ORDER BY Status;

// Count influences by type
MATCH ()-[i:INFLUENCES]->()
RETURN i.influence_type as Type, count(i) as Count
ORDER BY Type;

// Display contingent risks
MATCH (r:Risk {status: 'Contingent'})
RETURN r.id, r.name, r.scope, r.activation_condition, r.activation_decision_date;

// Count TPOs by cluster
MATCH (t:TPO)
RETURN t.cluster as Cluster, count(t) as Count
ORDER BY Cluster;

// Display TPOs and their impact count
MATCH (t:TPO)
OPTIONAL MATCH (r:Risk)-[i:IMPACTS_TPO]->(t)
RETURN t.reference as TPO, t.name as Name, t.cluster as Cluster, 
       count(i) as ImpactCount
ORDER BY t.reference;

// Count mitigations by type and status
MATCH (m:Mitigation)
RETURN m.type as Type, m.status as Status, count(m) as Count
ORDER BY Type, Status;

// Display most mitigated risks
MATCH (r:Risk)
OPTIONAL MATCH (m:Mitigation)-[rel:MITIGATES]->(r)
RETURN r.id as ID, r.name as Risk, r.level as Level, r.scope as Scope,
       count(rel) as MitigationCount
ORDER BY count(rel) DESC
LIMIT 15;

// Security risk analysis - attack chains
MATCH path = (r1:Risk)-[:INFLUENCES*1..3]->(r2:Risk)
WHERE r1.id STARTS WITH 'SEC' AND r2.level = 'Business'
RETURN r1.id as AttackOrigin, r1.name as AttackName,
       [n IN nodes(path) | n.id] as Chain,
       r2.id as BusinessImpact, r2.name as ImpactName
ORDER BY length(path) DESC;

// Global statistics
MATCH (r:Risk) WITH count(r) as risks
MATCH (t:TPO) WITH risks, count(t) as tpos
MATCH (m:Mitigation) WITH risks, tpos, count(m) as mitigations
MATCH ()-[i:INFLUENCES]->() WITH risks, tpos, mitigations, count(i) as influences
MATCH ()-[it:IMPACTS_TPO]->() WITH risks, tpos, mitigations, influences, count(it) as tpo_impacts
MATCH ()-[mt:MITIGATES]->() 
RETURN risks as Risks, tpos as TPOs, mitigations as Mitigations, 
       influences as Influences, tpo_impacts as TPOImpacts, count(mt) as MitigatesLinks;
