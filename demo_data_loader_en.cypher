// =============================================================================
// Demo Data Loading Script - Risk Influence Map Phase 1
// With TPO (Top Program Objectives) and Mitigations support
// Execute in Neo4j Browser or via cypher-shell
// =============================================================================

// 1. PURGE (optional, uncomment if you need to start fresh)
MATCH (n) DETACH DELETE n;

// =============================================================================
// 2. CREATION OF STRATEGIC RISKS (8)
// =============================================================================

CREATE (rs01:Risk {
  id: 'RS-01',
  name: 'Failure to achieve profitability target',
  description: 'Risk of not achieving the required profitability level within the specified timeframe',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Programme'],
  owner: 'Program Director',
  probability: 6.0,
  impact: 9.0,
  exposure: 54.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs02:Risk {
  id: 'RS-02',
  name: 'Series production start delay',
  description: 'Risk of delay in starting series production scheduled for 2030',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Industrial'],
  owner: 'VP Industrialization',
  probability: 7.0,
  impact: 8.0,
  exposure: 56.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs03:Risk {
  id: 'RS-03',
  name: 'Loss of competitive technological advantage',
  description: 'Risk of losing technological lead against SMR competitors',
  level: 'Strategic',
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
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs04:Risk {
  id: 'RS-04',
  name: 'Regulatory safety non-compliance',
  description: 'Risk of non-compliance with nuclear safety standards',
  level: 'Strategic',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Product'],
  owner: 'Safety Manager',
  probability: 3.0,
  impact: 10.0,
  exposure: 30.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs05:Risk {
  id: 'RS-05',
  name: 'Fuel supply tension',
  description: 'Risk of geopolitical tension affecting Type A fuel supply',
  level: 'Strategic',
  status: 'Contingent',
  origin: 'Legacy',
  categories: ['Programme', 'Supply Chain'],
  owner: 'VP Supply Chain',
  activation_condition: 'If Type A enriched uranium fuel is selected in Q3 2026 decision',
  activation_decision_date: '2026-09-30',
  probability: 8.0,
  impact: 7.0,
  exposure: 56.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs06:Risk {
  id: 'RS-06',
  name: 'Intellectual property compromise',
  description: 'Risk of critical intellectual property leakage or theft via digital backbone',
  level: 'Strategic',
  status: 'Contingent',
  origin: 'New',
  categories: ['Programme', 'Product'],
  owner: 'CISO',
  activation_condition: 'If digital backbone architecture opens to external ecosystem',
  activation_decision_date: '2026-09-30',
  probability: 6.0,
  impact: 9.0,
  exposure: 54.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs07:Risk {
  id: 'RS-07',
  name: 'Insufficient production capacity',
  description: 'Risk of production capacity being insufficient to achieve nominal rate',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Industrial'],
  owner: 'Plant Director',
  probability: 6.0,
  impact: 7.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (rs08:Risk {
  id: 'RS-08',
  name: 'Development budget overrun',
  description: 'Risk of significant overrun of allocated development budget',
  level: 'Strategic',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme'],
  owner: 'CFO',
  probability: 7.0,
  impact: 6.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 3. CREATION OF OPERATIONAL RISKS (7)
// =============================================================================

CREATE (ro01:Risk {
  id: 'RO-01',
  name: 'Critical control system component supplier failure',
  description: 'Failure or bankruptcy of sole supplier of critical control system components',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Supply Chain', 'Product'],
  owner: 'Critical Procurement Manager',
  probability: 6.0,
  impact: 8.0,
  exposure: 48.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ro02:Risk {
  id: 'RO-02',
  name: 'Cyberattack on PLM infrastructure',
  description: 'Targeted attack on PLM system causing data leakage or unavailability',
  level: 'Operational',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Product'],
  owner: 'CISO',
  probability: 5.0,
  impact: 8.0,
  exposure: 40.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ro03:Risk {
  id: 'RO-03',
  name: 'Manufacturing process quality drift',
  description: 'Progressive degradation of manufacturing process quality',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Industrial'],
  owner: 'Quality Manager',
  probability: 5.0,
  impact: 7.0,
  exposure: 35.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ro04:Risk {
  id: 'RO-04',
  name: 'Critical supplier certification delay',
  description: 'Delay in obtaining required certifications for a strategic supplier',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Supply Chain'],
  owner: 'Supply Chain Manager',
  probability: 7.0,
  impact: 6.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ro05:Risk {
  id: 'RO-05',
  name: 'Key R&D team competency loss',
  description: 'Departure of critical R&D experts to competitors',
  level: 'Operational',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Product'],
  owner: 'HR Director',
  probability: 6.0,
  impact: 7.0,
  exposure: 42.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ro06:Risk {
  id: 'RO-06',
  name: 'Critical safety embedded software bug',
  description: 'Undetected critical software defect in control-command system',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Product'],
  owner: 'Lead Embedded Developer',
  probability: 4.0,
  impact: 9.0,
  exposure: 36.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

CREATE (ro07:Risk {
  id: 'RO-07',
  name: 'Extended digital infrastructure unavailability',
  description: 'Major failure or crash of digital backbone infrastructure',
  level: 'Operational',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme'],
  owner: 'IT Director',
  probability: 4.0,
  impact: 6.0,
  exposure: 24.0,
  current_score_type: 'Qualitative_4x4',
  created_at: datetime(),
  updated_at: datetime(),
  last_review_date: datetime(),
  next_review_date: datetime() + duration({days: 90})
});

// =============================================================================
// 4. CREATION OF TOP PROGRAM OBJECTIVES (TPOs) - 3 examples
// =============================================================================

CREATE (tpo01:TPO {
  id: 'TPO-01',
  reference: 'TPO-01',
  name: 'Achieve profitability by 2032',
  cluster: 'Business Efficiency',
  description: 'Positive ROI target and operating margin > 15% by end of 2032',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo02:TPO {
  id: 'TPO-02',
  reference: 'TPO-02',
  name: 'NRC safety certification before end of 2029',
  cluster: 'Safety',
  description: 'Obtain all nuclear safety certifications required by the NRC to authorize commissioning',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo03:TPO {
  id: 'TPO-03',
  reference: 'TPO-03',
  name: 'Series production start Q1 2030',
  cluster: 'Industrial Efficiency',
  description: 'Launch series production of the first SMR with an initial rate of 2 units/year',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 5. CREATION OF MITIGATIONS
// =============================================================================

// --- DEDICATED MITIGATIONS (created specifically for the program) ---

CREATE (m01:Mitigation {
  id: 'MIT-01',
  name: 'Critical components dual-sourcing strategy',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Qualification of a second supplier for all critical control system components with signed framework contracts',
  owner: 'Critical Procurement Manager',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m02:Mitigation {
  id: 'MIT-02',
  name: 'R&D talent retention program',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Retention package including long-term incentives, technical career paths and mentoring program for key experts',
  owner: 'HR Director',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m03:Mitigation {
  id: 'MIT-03',
  name: 'Real-time quality review system',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Deployment of IoT sensors and real-time dashboard for continuous monitoring of process quality parameters',
  owner: 'Quality Manager',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m04:Mitigation {
  id: 'MIT-04',
  name: 'PLM Zero Trust architecture',
  type: 'Dedicated',
  status: 'Proposed',
  description: 'Redesign of PLM security architecture following Zero Trust model with micro-segmentation and continuous authentication',
  owner: 'CISO',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m05:Mitigation {
  id: 'MIT-05',
  name: 'Production contingency plan',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Detailed alternative ramp-up plan with identification of qualified backup subcontractors',
  owner: 'VP Industrialization',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m06:Mitigation {
  id: 'MIT-06',
  name: 'Independent safety code review',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Contract with independent third party for systematic safety-critical code review per DO-178C',
  owner: 'Lead Embedded Developer',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m07:Mitigation {
  id: 'MIT-07',
  name: 'Fuel source diversification',
  type: 'Dedicated',
  status: 'Proposed',
  description: 'Negotiation of long-term contracts with fuel suppliers across different geopolitical zones',
  owner: 'VP Supply Chain',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

// --- INHERITED MITIGATIONS (from group or other programs) ---

CREATE (m08:Mitigation {
  id: 'MIT-08',
  name: 'Corporate budget management process',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Application of corporate budget tracking process with monthly reviews and automatic alerts on deviations >5%',
  owner: 'CFO',
  source_entity: 'Corporate Finance Division',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m09:Mitigation {
  id: 'MIT-09',
  name: 'Corporate shared SOC',
  type: 'Inherited',
  status: 'Implemented',
  description: '24/7 monitoring by corporate Security Operations Center with incident response capability <15min',
  owner: 'CISO',
  source_entity: 'Corporate IT Division',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m10:Mitigation {
  id: 'MIT-10',
  name: 'Corporate IT continuity plan',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Disaster recovery infrastructure with RTO 4h and RPO 1h for critical systems',
  owner: 'IT Director',
  source_entity: 'Corporate IT Division',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m11:Mitigation {
  id: 'MIT-11',
  name: 'Shared Innovation program',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Access to patents and innovations from other group divisions via intellectual property sharing program',
  owner: 'CTO',
  source_entity: 'Corporate R&D Division',
  created_at: datetime(),
  updated_at: datetime()
});

// --- BASELINE MITIGATIONS (standards, regulations, best practices) ---

CREATE (m12:Mitigation {
  id: 'MIT-12',
  name: 'ISO 19443 Nuclear Quality certification',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Quality system certification per ISO 19443 specific to nuclear supply chain',
  owner: 'Quality Manager',
  source_entity: 'ISO 19443:2018',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m13:Mitigation {
  id: 'MIT-13',
  name: 'IEC 61513 Nuclear I&C compliance',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Systematic application of IEC 61513 standard for nuclear instrumentation and control systems',
  owner: 'Lead Embedded Developer',
  source_entity: 'IEC 61513:2011',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m14:Mitigation {
  id: 'MIT-14',
  name: 'NIS2 cybersecurity framework',
  type: 'Baseline',
  status: 'Implemented',
  description: 'Compliance with NIS2 directive for essential service operators in energy sector',
  owner: 'CISO',
  source_entity: 'EU Directive 2022/2555 (NIS2)',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m15:Mitigation {
  id: 'MIT-15',
  name: 'NRC regulatory framework',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Application of NRC framework for nuclear facilities with defined compliance milestones',
  owner: 'Safety Manager',
  source_entity: '10 CFR Part 50/52',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 6. CREATION OF INFLUENCE LINKS - LEVEL 1 (Op → Strat)
// =============================================================================

MATCH (source:Risk {id: 'RO-01'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-01',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Critical',
  description: 'Critical component supplier failure directly blocks series production',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-02'}), (target:Risk {id: 'RS-06'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-02',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Strong',
  description: 'A cyberattack on PLM directly exposes critical intellectual property',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-03'}), (target:Risk {id: 'RS-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-03',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Critical',
  description: 'Quality drift compromises compliance with nuclear safety standards',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-04'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-04',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Strong',
  description: 'Supplier certification delay slows supply chain qualification',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-05'}), (target:Risk {id: 'RS-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-05',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Strong',
  description: 'Loss of key competencies slows development and innovation',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-06'}), (target:Risk {id: 'RS-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-06',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Critical',
  description: 'A critical bug in embedded software directly compromises safety',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-07'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-07',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Moderate',
  description: 'Digital backbone unavailability slows product development',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 7. CREATION OF INFLUENCE LINKS - LEVEL 2 (Strat → Strat)
// =============================================================================

MATCH (source:Risk {id: 'RS-02'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-08',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Critical',
  description: 'Production delay directly impacts revenue and therefore profitability',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-03'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-09',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'Loss of technological advantage reduces margins and market share',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-04'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-10',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Critical',
  description: 'Safety non-compliance blocks production authorization',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-05'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-11',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'Fuel supply tension delays first reactor startup',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-06'}), (target:Risk {id: 'RS-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-12',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'IP compromise causes loss of competitive technological advantage',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-07'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-13',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'Capacity insufficiency limits potential revenues',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-08'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-14',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Moderate',
  description: 'Budget overrun directly reduces operating margin',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 8. CREATION OF INFLUENCE LINKS - LEVEL 3 (Op → Op)
// =============================================================================

MATCH (source:Risk {id: 'RO-01'}), (target:Risk {id: 'RO-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-15',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Supplier failure forces use of less reliable backup components',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-02'}), (target:Risk {id: 'RO-07'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-16',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'Cyberattack causes digital infrastructure unavailability',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-05'}), (target:Risk {id: 'RO-06'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-17',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'Loss of competencies increases risk of bug introduction',
  confidence: 0.75,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-04'}), (target:Risk {id: 'RO-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-18',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Weak',
  description: 'Certification delays generally correlate with other supplier failures',
  confidence: 0.6,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 9. CREATION OF TPO IMPACT LINKS (Strategic Risk → TPO)
// =============================================================================

// RS-01 (Profitability failure) → TPO-01 (Profitability 2032)
MATCH (r:Risk {id: 'RS-01'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-01',
  impact_level: 'Critical',
  description: 'Direct impact: this risk directly threatens the profitability objective',
  created_at: datetime()
}]->(t);

// RS-02 (Production delay) → TPO-01 (Profitability 2032)
MATCH (r:Risk {id: 'RS-02'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-02',
  impact_level: 'High',
  description: 'Production delay shifts revenue and impacts ROI',
  created_at: datetime()
}]->(t);

// RS-02 (Production delay) → TPO-03 (Production start Q1 2030)
MATCH (r:Risk {id: 'RS-02'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-03',
  impact_level: 'Critical',
  description: 'Direct impact: this risk threatens the series production start objective',
  created_at: datetime()
}]->(t);

// RS-04 (Safety non-compliance) → TPO-02 (NRC Certification 2029)
MATCH (r:Risk {id: 'RS-04'}), (t:TPO {id: 'TPO-02'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-04',
  impact_level: 'Critical',
  description: 'Direct impact: non-compliance prevents obtaining NRC certification',
  created_at: datetime()
}]->(t);

// RS-04 (Safety non-compliance) → TPO-03 (Production start Q1 2030)
MATCH (r:Risk {id: 'RS-04'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-05',
  impact_level: 'High',
  description: 'Without safety certification, production start is blocked',
  created_at: datetime()
}]->(t);

// RS-07 (Capacity insufficiency) → TPO-03 (Production start Q1 2030)
MATCH (r:Risk {id: 'RS-07'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-06',
  impact_level: 'High',
  description: 'Capacity insufficiency compromises achieving target production rate',
  created_at: datetime()
}]->(t);

// RS-08 (Budget overrun) → TPO-01 (Profitability 2032)
MATCH (r:Risk {id: 'RS-08'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-07',
  impact_level: 'High',
  description: 'Budget overrun directly degrades margin and ROI',
  created_at: datetime()
}]->(t);

// RS-03 (Tech advantage loss) → TPO-01 (Profitability 2032)
MATCH (r:Risk {id: 'RS-03'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-08',
  impact_level: 'Medium',
  description: 'Loss of technological advantage reduces pricing power and margins',
  created_at: datetime()
}]->(t);

// =============================================================================
// 10. CREATION OF MITIGATES LINKS (Mitigation → Risk)
// =============================================================================

// MIT-01 (Dual-sourcing) → RO-01 (Supplier failure)
MATCH (m:Mitigation {id: 'MIT-01'}), (r:Risk {id: 'RO-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-01',
  effectiveness: 'High',
  description: 'Dual-sourcing allows switching to second supplier in case of primary supplier failure',
  created_at: datetime()
}]->(r);

// MIT-01 (Dual-sourcing) → RS-02 (Production delay) - indirect effect
MATCH (m:Mitigation {id: 'MIT-01'}), (r:Risk {id: 'RS-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-02',
  effectiveness: 'Medium',
  description: 'Securing supply chain reduces component-related delay risks',
  created_at: datetime()
}]->(r);

// MIT-02 (Talent retention) → RO-05 (Competency loss)
MATCH (m:Mitigation {id: 'MIT-02'}), (r:Risk {id: 'RO-05'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-03',
  effectiveness: 'High',
  description: 'Retention program significantly reduces key expert turnover',
  created_at: datetime()
}]->(r);

// MIT-02 (Talent retention) → RS-03 (Tech advantage loss)
MATCH (m:Mitigation {id: 'MIT-02'}), (r:Risk {id: 'RS-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-04',
  effectiveness: 'Medium',
  description: 'Talent retention maintains innovation capability',
  created_at: datetime()
}]->(r);

// MIT-03 (Real-time quality review) → RO-03 (Quality drift)
MATCH (m:Mitigation {id: 'MIT-03'}), (r:Risk {id: 'RO-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-05',
  effectiveness: 'High',
  description: 'Real-time monitoring enables detecting and correcting drifts before they worsen',
  created_at: datetime()
}]->(r);

// MIT-04 (Zero Trust PLM) → RO-02 (PLM cyberattack)
MATCH (m:Mitigation {id: 'MIT-04'}), (r:Risk {id: 'RO-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-06',
  effectiveness: 'Critical',
  description: 'Zero Trust architecture drastically reduces attack surface and lateral movement possibilities',
  created_at: datetime()
}]->(r);

// MIT-04 (Zero Trust PLM) → RS-06 (IP compromise)
MATCH (m:Mitigation {id: 'MIT-04'}), (r:Risk {id: 'RS-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-07',
  effectiveness: 'High',
  description: 'PLM security protects intellectual property data',
  created_at: datetime()
}]->(r);

// MIT-05 (Production contingency plan) → RS-07 (Capacity insufficiency)
MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'RS-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-08',
  effectiveness: 'Medium',
  description: 'Contingency plan allows partially compensating for internal capacity shortfalls',
  created_at: datetime()
}]->(r);

// MIT-05 (Production contingency plan) → RS-02 (Production delay)
MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'RS-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-09',
  effectiveness: 'Medium',
  description: 'Backup subcontractors help maintain schedule in case of problems',
  created_at: datetime()
}]->(r);

// MIT-06 (Safety code review) → RO-06 (Critical bug)
MATCH (m:Mitigation {id: 'MIT-06'}), (r:Risk {id: 'RO-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-10',
  effectiveness: 'Critical',
  description: 'Independent review maximizes chances of detecting critical bugs before deployment',
  created_at: datetime()
}]->(r);

// MIT-06 (Safety code review) → RS-04 (Safety non-compliance)
MATCH (m:Mitigation {id: 'MIT-06'}), (r:Risk {id: 'RS-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-11',
  effectiveness: 'High',
  description: 'DO-178C compliance demonstrates rigor of safety development process',
  created_at: datetime()
}]->(r);

// MIT-07 (Fuel diversification) → RS-05 (Fuel tension)
MATCH (m:Mitigation {id: 'MIT-07'}), (r:Risk {id: 'RS-05'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-12',
  effectiveness: 'High',
  description: 'Geographic diversification reduces exposure to tensions in any specific zone',
  created_at: datetime()
}]->(r);

// MIT-08 (Corporate budget process) → RS-08 (Budget overrun)
MATCH (m:Mitigation {id: 'MIT-08'}), (r:Risk {id: 'RS-08'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-13',
  effectiveness: 'Medium',
  description: 'Rigorous tracking enables early deviation detection and corrective action',
  created_at: datetime()
}]->(r);

// MIT-09 (Corporate SOC) → RO-02 (PLM cyberattack)
MATCH (m:Mitigation {id: 'MIT-09'}), (r:Risk {id: 'RO-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-14',
  effectiveness: 'High',
  description: '24/7 SOC enables rapid detection and response to intrusion attempts',
  created_at: datetime()
}]->(r);

// MIT-09 (Corporate SOC) → RO-07 (Infrastructure unavailability)
MATCH (m:Mitigation {id: 'MIT-09'}), (r:Risk {id: 'RO-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-15',
  effectiveness: 'Medium',
  description: 'Proactive monitoring allows anticipating certain failures and incidents',
  created_at: datetime()
}]->(r);

// MIT-10 (Corporate IT BCP) → RO-07 (Infrastructure unavailability)
MATCH (m:Mitigation {id: 'MIT-10'}), (r:Risk {id: 'RO-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-16',
  effectiveness: 'Critical',
  description: 'Disaster recovery guarantees rapid recovery in case of major failure',
  created_at: datetime()
}]->(r);

// MIT-11 (Shared innovation) → RS-03 (Tech advantage loss)
MATCH (m:Mitigation {id: 'MIT-11'}), (r:Risk {id: 'RS-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-17',
  effectiveness: 'Medium',
  description: 'Access to group innovations accelerates development',
  created_at: datetime()
}]->(r);

// MIT-12 (ISO 19443) → RO-03 (Quality drift)
MATCH (m:Mitigation {id: 'MIT-12'}), (r:Risk {id: 'RO-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-18',
  effectiveness: 'High',
  description: 'ISO 19443 framework mandates rigorous quality controls throughout supply chain',
  created_at: datetime()
}]->(r);

// MIT-12 (ISO 19443) → RO-04 (Supplier certification delay)
MATCH (m:Mitigation {id: 'MIT-12'}), (r:Risk {id: 'RO-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-19',
  effectiveness: 'Medium',
  description: 'ISO framework structures the supplier qualification process',
  created_at: datetime()
}]->(r);

// MIT-13 (IEC 61513) → RO-06 (Critical bug)
MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'RO-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-20',
  effectiveness: 'High',
  description: 'IEC 61513 standard defines strict requirements for nuclear I&C systems development',
  created_at: datetime()
}]->(r);

// MIT-13 (IEC 61513) → RS-04 (Safety non-compliance)
MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'RS-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-21',
  effectiveness: 'Critical',
  description: 'IEC 61513 compliance is a prerequisite for I&C systems safety certification',
  created_at: datetime()
}]->(r);

// MIT-14 (NIS2) → RO-02 (PLM cyberattack)
MATCH (m:Mitigation {id: 'MIT-14'}), (r:Risk {id: 'RO-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-22',
  effectiveness: 'High',
  description: 'NIS2 mandates cybersecurity measures and incident notification',
  created_at: datetime()
}]->(r);

// MIT-14 (NIS2) → RS-06 (IP compromise)
MATCH (m:Mitigation {id: 'MIT-14'}), (r:Risk {id: 'RS-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-23',
  effectiveness: 'Medium',
  description: 'NIS2 requirements strengthen overall security posture',
  created_at: datetime()
}]->(r);

// MIT-15 (NRC framework) → RS-04 (Safety non-compliance)
MATCH (m:Mitigation {id: 'MIT-15'}), (r:Risk {id: 'RS-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-24',
  effectiveness: 'Critical',
  description: 'Systematic application of NRC framework ensures regulatory compliance',
  created_at: datetime()
}]->(r);

// MIT-15 (NRC framework) → RO-03 (Quality drift)
MATCH (m:Mitigation {id: 'MIT-15'}), (r:Risk {id: 'RO-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-25',
  effectiveness: 'High',
  description: 'NRC requirements impose high quality standards on processes',
  created_at: datetime()
}]->(r);

// =============================================================================
// 11. VERIFICATION
// =============================================================================

// Count risks by level
MATCH (r:Risk)
RETURN r.level as Level, count(r) as Count
ORDER BY Level;

// Count risks by origin
MATCH (r:Risk)
RETURN r.origin as Origin, count(r) as Count
ORDER BY Origin;

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
RETURN r.id, r.name, r.origin, r.activation_condition, r.activation_decision_date;

// Count TPOs by cluster
MATCH (t:TPO)
RETURN t.cluster as Cluster, count(t) as Count
ORDER BY Cluster;

// Display TPOs and their impacts
MATCH (t:TPO)
OPTIONAL MATCH (r:Risk)-[i:IMPACTS_TPO]->(t)
RETURN t.reference as TPO, t.name as Name, t.cluster as Cluster, 
       count(i) as ImpactCount
ORDER BY t.reference;

// Count mitigations by type
MATCH (m:Mitigation)
RETURN m.type as Type, count(m) as Count
ORDER BY Type;

// Count mitigations by status
MATCH (m:Mitigation)
RETURN m.status as Status, count(m) as Count
ORDER BY Status;

// Display mitigations and number of risks addressed
MATCH (m:Mitigation)
OPTIONAL MATCH (m)-[rel:MITIGATES]->(r:Risk)
RETURN m.id as ID, m.name as Mitigation, m.type as Type, m.status as Status,
       count(rel) as RisksAddressed
ORDER BY count(rel) DESC, m.type;

// Display most mitigated risks
MATCH (r:Risk)
OPTIONAL MATCH (m:Mitigation)-[rel:MITIGATES]->(r)
RETURN r.id as ID, r.name as Risk, r.level as Level, r.origin as Origin,
       count(rel) as MitigationCount
ORDER BY count(rel) DESC
LIMIT 10;

// Display mitigations by effectiveness
MATCH (m:Mitigation)-[rel:MITIGATES]->(r:Risk)
RETURN rel.effectiveness as Effectiveness, count(rel) as Count
ORDER BY 
  CASE rel.effectiveness 
    WHEN 'Critical' THEN 1 
    WHEN 'High' THEN 2 
    WHEN 'Medium' THEN 3 
    WHEN 'Low' THEN 4 
  END;

// Display TPO impact details
MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
RETURN r.id as RiskID, r.name as Risk, r.origin as Origin,
       t.reference as TPO, i.impact_level as ImpactLevel
ORDER BY t.reference, i.impact_level DESC;

// Global statistics
MATCH (r:Risk) WITH count(r) as risks
MATCH (t:TPO) WITH risks, count(t) as tpos
MATCH (m:Mitigation) WITH risks, tpos, count(m) as mitigations
MATCH ()-[i:INFLUENCES]->() WITH risks, tpos, mitigations, count(i) as influences
MATCH ()-[it:IMPACTS_TPO]->() WITH risks, tpos, mitigations, influences, count(it) as tpo_impacts
MATCH ()-[mt:MITIGATES]->() 
RETURN risks as Risks, tpos as TPOs, mitigations as Mitigations, 
       influences as Influences, tpo_impacts as TPOImpacts, count(mt) as MitigatesLinks;
