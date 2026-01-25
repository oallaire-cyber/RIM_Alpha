// =============================================================================
// Script de chargement des données de démo - Risk Influence Map Phase 1
// Avec support TPO (Top Program Objectives) et Mitigations
// À exécuter dans Neo4j Browser ou via cypher-shell
// =============================================================================

// 1. PURGE (optionnel, décommenter si besoin de repartir à zéro)
MATCH (n) DETACH DELETE n;

// =============================================================================
// 2. CRÉATION DES RISQUES STRATÉGIQUES (8)
// =============================================================================

CREATE (rs01:Risk {
  id: 'RS-01',
  name: 'Non-atteinte objectif profitabilité',
  description: 'Risque de ne pas atteindre le niveau de profitabilité fixé dans les délais impartis',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Programme'],
  owner: 'Directeur Programme',
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
  name: 'Retard mise en production série',
  description: 'Risque de retard dans le démarrage de la production en série prévue pour 2030',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Industriel'],
  owner: 'VP Industrialisation',
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
  name: 'Perte avance technologique compétitive',
  description: 'Risque de perdre l\'avance technologique face aux compétiteurs SMR',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Programme', 'Produit'],
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
  name: 'Non-conformité safety réglementaire',
  description: 'Risque de non-conformité aux standards de sûreté nucléaire',
  level: 'Strategic',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Produit'],
  owner: 'Responsable Safety',
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
  name: 'Tension approvisionnement combustible',
  description: 'Risque de tension géopolitique sur l\'approvisionnement en combustible type A',
  level: 'Strategic',
  status: 'Contingent',
  origin: 'Legacy',
  categories: ['Programme', 'Supply Chain'],
  owner: 'VP Supply Chain',
  activation_condition: 'Si choix combustible uranium enrichi type A lors de la décision Q3 2026',
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
  name: 'Compromission propriété intellectuelle',
  description: 'Risque de fuite ou vol de propriété intellectuelle critique via le backbone digital',
  level: 'Strategic',
  status: 'Contingent',
  origin: 'New',
  categories: ['Programme', 'Produit'],
  owner: 'CISO',
  activation_condition: 'Si architecture backbone digital ouverte vers écosystème externe',
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
  name: 'Insuffisance capacité production',
  description: 'Risque de capacité de production insuffisante pour atteindre le rate nominal',
  level: 'Strategic',
  status: 'Active',
  origin: 'New',
  categories: ['Industriel'],
  owner: 'Directeur Usine',
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
  name: 'Dépassement budget développement',
  description: 'Risque de dépassement significatif du budget alloué au développement',
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
// 3. CRÉATION DES RISQUES OPÉRATIONNELS (7)
// =============================================================================

CREATE (ro01:Risk {
  id: 'RO-01',
  name: 'Défaillance fournisseur pièce critique système de contrôle',
  description: 'Défaillance ou faillite du fournisseur unique de composants critiques du système de contrôle',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Supply Chain', 'Produit'],
  owner: 'Responsable Achats Critiques',
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
  name: 'Cyberattaque sur infrastructure PLM',
  description: 'Attaque ciblée sur le système PLM causant fuite de données ou indisponibilité',
  level: 'Operational',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Produit'],
  owner: 'RSSI',
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
  name: 'Dérive qualité process fabrication',
  description: 'Dégradation progressive de la qualité des process de fabrication',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Industriel'],
  owner: 'Responsable Qualité',
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
  name: 'Retard certification fournisseur critique',
  description: 'Retard dans l\'obtention des certifications requises pour un fournisseur stratégique',
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
  name: 'Fuite compétences clés équipe R&D',
  description: 'Départ d\'experts critiques de l\'équipe R&D vers la concurrence',
  level: 'Operational',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme', 'Produit'],
  owner: 'DRH',
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
  name: 'Bug critique logiciel embarqué safety',
  description: 'Défaut logiciel critique non détecté dans le système de contrôle-commande',
  level: 'Operational',
  status: 'Active',
  origin: 'New',
  categories: ['Produit'],
  owner: 'Lead Développeur Embarqué',
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
  name: 'Indisponibilité prolongée infrastructure digitale',
  description: 'Panne majeure ou crash de l\'infrastructure backbone digital',
  level: 'Operational',
  status: 'Active',
  origin: 'Legacy',
  categories: ['Programme'],
  owner: 'Directeur SI',
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
// 4. CRÉATION DES TOP PROGRAM OBJECTIVES (TPOs) - 3 exemples
// =============================================================================

CREATE (tpo01:TPO {
  id: 'TPO-01',
  reference: 'TPO-01',
  name: 'Atteindre la profitabilité à horizon 2032',
  cluster: 'Business Efficiency',
  description: 'Objectif de ROI positif et marge opérationnelle > 15% d\'ici fin 2032',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo02:TPO {
  id: 'TPO-02',
  reference: 'TPO-02',
  name: 'Certification safety ASN avant fin 2029',
  cluster: 'Safety',
  description: 'Obtenir l\'ensemble des certifications de sûreté nucléaire requises par l\'ASN pour autoriser la mise en service',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (tpo03:TPO {
  id: 'TPO-03',
  reference: 'TPO-03',
  name: 'Démarrage production série Q1 2030',
  cluster: 'Industrial Efficiency',
  description: 'Lancer la production en série du premier SMR avec une cadence initiale de 2 unités/an',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 5. CRÉATION DES MITIGATIONS
// =============================================================================

// --- MITIGATIONS DÉDIÉES (créées spécifiquement pour le programme) ---

CREATE (m01:Mitigation {
  id: 'MIT-01',
  name: 'Stratégie dual-sourcing composants critiques',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Qualification d\'un second fournisseur pour tous les composants critiques du système de contrôle avec contrats cadre signés',
  owner: 'Responsable Achats Critiques',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m02:Mitigation {
  id: 'MIT-02',
  name: 'Programme de rétention talents R&D',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Package de rétention incluant incentives long-terme, parcours de carrière technique et programme de mentoring pour les experts clés',
  owner: 'DRH',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m03:Mitigation {
  id: 'MIT-03',
  name: 'Système de revue qualité temps réel',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Déploiement de capteurs IoT et dashboard temps réel pour monitoring continu des paramètres qualité process',
  owner: 'Responsable Qualité',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m04:Mitigation {
  id: 'MIT-04',
  name: 'Architecture Zero Trust PLM',
  type: 'Dedicated',
  status: 'Proposed',
  description: 'Refonte de l\'architecture de sécurité du PLM selon le modèle Zero Trust avec micro-segmentation et authentification continue',
  owner: 'RSSI',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m05:Mitigation {
  id: 'MIT-05',
  name: 'Plan de contingence production',
  type: 'Dedicated',
  status: 'Implemented',
  description: 'Plan détaillé de montée en cadence alternative avec identification de sous-traitants qualifiés en backup',
  owner: 'VP Industrialisation',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m06:Mitigation {
  id: 'MIT-06',
  name: 'Revue de code safety indépendante',
  type: 'Dedicated',
  status: 'In Progress',
  description: 'Contrat avec organisme tiers indépendant pour revue systématique du code safety-critical selon DO-178C',
  owner: 'Lead Développeur Embarqué',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m07:Mitigation {
  id: 'MIT-07',
  name: 'Diversification sources combustible',
  type: 'Dedicated',
  status: 'Proposed',
  description: 'Négociation de contrats long-terme avec fournisseurs de combustible dans différentes zones géopolitiques',
  owner: 'VP Supply Chain',
  source_entity: '',
  created_at: datetime(),
  updated_at: datetime()
});

// --- MITIGATIONS HÉRITÉES (du groupe ou d'autres programmes) ---

CREATE (m08:Mitigation {
  id: 'MIT-08',
  name: 'Processus de gestion budgétaire Groupe',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Application du processus corporate de suivi budgétaire avec revues mensuelles et alertes automatiques sur déviations >5%',
  owner: 'CFO',
  source_entity: 'Direction Financière Groupe',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m09:Mitigation {
  id: 'MIT-09',
  name: 'SOC mutualisé Groupe',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Surveillance 24/7 par le Security Operations Center du groupe avec capacité de réponse incident <15min',
  owner: 'RSSI',
  source_entity: 'DSI Groupe',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m10:Mitigation {
  id: 'MIT-10',
  name: 'Plan de continuité IT Groupe',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Infrastructure de disaster recovery avec RTO 4h et RPO 1h pour les systèmes critiques',
  owner: 'Directeur SI',
  source_entity: 'DSI Groupe',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m11:Mitigation {
  id: 'MIT-11',
  name: 'Programme Innovation partagée',
  type: 'Inherited',
  status: 'Implemented',
  description: 'Accès aux brevets et innovations des autres divisions du groupe via le programme de partage de propriété intellectuelle',
  owner: 'CTO',
  source_entity: 'Direction R&D Groupe',
  created_at: datetime(),
  updated_at: datetime()
});

// --- MITIGATIONS BASELINE (standards, réglementations, best practices) ---

CREATE (m12:Mitigation {
  id: 'MIT-12',
  name: 'Certification ISO 19443 Nuclear Quality',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Certification du système qualité selon ISO 19443 spécifique à la supply chain nucléaire',
  owner: 'Responsable Qualité',
  source_entity: 'ISO 19443:2018',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m13:Mitigation {
  id: 'MIT-13',
  name: 'Conformité IEC 61513 Nuclear I&C',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Application systématique de la norme IEC 61513 pour les systèmes d\'instrumentation et contrôle nucléaires',
  owner: 'Lead Développeur Embarqué',
  source_entity: 'IEC 61513:2011',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m14:Mitigation {
  id: 'MIT-14',
  name: 'Framework cybersécurité NIS2',
  type: 'Baseline',
  status: 'Implemented',
  description: 'Mise en conformité avec la directive NIS2 pour les opérateurs de services essentiels du secteur énergie',
  owner: 'RSSI',
  source_entity: 'Directive UE 2022/2555 (NIS2)',
  created_at: datetime(),
  updated_at: datetime()
});

CREATE (m15:Mitigation {
  id: 'MIT-15',
  name: 'Référentiel ASN INB',
  type: 'Baseline',
  status: 'In Progress',
  description: 'Application du référentiel ASN pour les installations nucléaires de base avec jalons de conformité définis',
  owner: 'Responsable Safety',
  source_entity: 'Arrêté INB du 7 février 2012',
  created_at: datetime(),
  updated_at: datetime()
});

// =============================================================================
// 6. CRÉATION DES LIENS D'INFLUENCE - NIVEAU 1 (Op → Strat)
// =============================================================================

MATCH (source:Risk {id: 'RO-01'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-01',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Critical',
  description: 'La défaillance du fournisseur de pièces critiques bloque directement la production en série',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-02'}), (target:Risk {id: 'RS-06'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-02',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Strong',
  description: 'Une cyberattaque sur le PLM expose directement la propriété intellectuelle critique',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-03'}), (target:Risk {id: 'RS-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-03',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Critical',
  description: 'La dérive qualité compromet la conformité aux standards de sûreté nucléaire',
  confidence: 0.95,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-04'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-04',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Strong',
  description: 'Le retard de certification fournisseur retarde la qualification de la supply chain',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-05'}), (target:Risk {id: 'RS-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-05',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Strong',
  description: 'La perte de compétences clés ralentit le développement et l\'innovation',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-06'}), (target:Risk {id: 'RS-04'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-06',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Critical',
  description: 'Un bug critique dans le logiciel embarqué compromet directement la safety',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-07'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-07',
  influence_type: 'Level1_Op_to_Strat',
  strength: 'Moderate',
  description: 'L\'indisponibilité du backbone digital ralentit le développement produit',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 7. CRÉATION DES LIENS D'INFLUENCE - NIVEAU 2 (Strat → Strat)
// =============================================================================

MATCH (source:Risk {id: 'RS-02'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-08',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Critical',
  description: 'Le retard de production impacte directement le CA et donc la profitabilité',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-03'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-09',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'La perte d\'avance technologique réduit les marges et la part de marché',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-04'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-10',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Critical',
  description: 'La non-conformité safety bloque l\'autorisation de mise en production',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-05'}), (target:Risk {id: 'RS-02'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-11',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'La tension sur le combustible retarde le démarrage des premiers réacteurs',
  confidence: 0.8,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-06'}), (target:Risk {id: 'RS-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-12',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'La compromission IP fait perdre l\'avantage concurrentiel technologique',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-07'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-13',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Strong',
  description: 'L\'insuffisance de capacité limite les revenus potentiels',
  confidence: 0.85,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RS-08'}), (target:Risk {id: 'RS-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-14',
  influence_type: 'Level2_Strat_to_Strat',
  strength: 'Moderate',
  description: 'Le dépassement budget réduit directement la marge opérationnelle',
  confidence: 1.0,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 8. CRÉATION DES LIENS D'INFLUENCE - NIVEAU 3 (Op → Op)
// =============================================================================

MATCH (source:Risk {id: 'RO-01'}), (target:Risk {id: 'RO-03'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-15',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'La défaillance fournisseur force l\'utilisation de composants de secours moins fiables',
  confidence: 0.7,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-02'}), (target:Risk {id: 'RO-07'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-16',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Strong',
  description: 'La cyberattaque cause l\'indisponibilité de l\'infrastructure digitale',
  confidence: 0.9,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-05'}), (target:Risk {id: 'RO-06'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-17',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Moderate',
  description: 'La perte de compétences augmente le risque d\'introduction de bugs',
  confidence: 0.75,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

MATCH (source:Risk {id: 'RO-04'}), (target:Risk {id: 'RO-01'})
CREATE (source)-[:INFLUENCES {
  id: 'INF-18',
  influence_type: 'Level3_Op_to_Op',
  strength: 'Weak',
  description: 'Les retards de certification corrèlent généralement avec d\'autres défaillances fournisseurs',
  confidence: 0.6,
  created_at: datetime(),
  last_validated: datetime()
}]->(target);

// =============================================================================
// 9. CRÉATION DES LIENS TPO IMPACTS (Strategic Risk → TPO)
// =============================================================================

// RS-01 (Non-atteinte profitabilité) → TPO-01 (Profitabilité 2032)
MATCH (r:Risk {id: 'RS-01'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-01',
  impact_level: 'Critical',
  description: 'Impact direct : ce risque menace frontalement l\'objectif de profitabilité',
  created_at: datetime()
}]->(t);

// RS-02 (Retard production série) → TPO-01 (Profitabilité 2032)
MATCH (r:Risk {id: 'RS-02'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-02',
  impact_level: 'High',
  description: 'Le retard de production décale les revenus et impacte le ROI',
  created_at: datetime()
}]->(t);

// RS-02 (Retard production série) → TPO-03 (Démarrage production Q1 2030)
MATCH (r:Risk {id: 'RS-02'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-03',
  impact_level: 'Critical',
  description: 'Impact direct : ce risque menace l\'objectif de démarrage production série',
  created_at: datetime()
}]->(t);

// RS-04 (Non-conformité safety) → TPO-02 (Certification ASN 2029)
MATCH (r:Risk {id: 'RS-04'}), (t:TPO {id: 'TPO-02'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-04',
  impact_level: 'Critical',
  description: 'Impact direct : la non-conformité empêche l\'obtention de la certification ASN',
  created_at: datetime()
}]->(t);

// RS-04 (Non-conformité safety) → TPO-03 (Démarrage production Q1 2030)
MATCH (r:Risk {id: 'RS-04'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-05',
  impact_level: 'High',
  description: 'Sans certification safety, le démarrage de production est bloqué',
  created_at: datetime()
}]->(t);

// RS-07 (Insuffisance capacité) → TPO-03 (Démarrage production Q1 2030)
MATCH (r:Risk {id: 'RS-07'}), (t:TPO {id: 'TPO-03'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-06',
  impact_level: 'High',
  description: 'L\'insuffisance de capacité compromet l\'atteinte de la cadence cible',
  created_at: datetime()
}]->(t);

// RS-08 (Dépassement budget) → TPO-01 (Profitabilité 2032)
MATCH (r:Risk {id: 'RS-08'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-07',
  impact_level: 'High',
  description: 'Le dépassement budget dégrade directement la marge et le ROI',
  created_at: datetime()
}]->(t);

// RS-03 (Perte avance techno) → TPO-01 (Profitabilité 2032)
MATCH (r:Risk {id: 'RS-03'}), (t:TPO {id: 'TPO-01'})
CREATE (r)-[:IMPACTS_TPO {
  id: 'IMP-08',
  impact_level: 'Medium',
  description: 'La perte d\'avance technologique réduit le pricing power et les marges',
  created_at: datetime()
}]->(t);

// =============================================================================
// 10. CRÉATION DES LIENS MITIGATES (Mitigation → Risk)
// =============================================================================

// MIT-01 (Dual-sourcing) → RO-01 (Défaillance fournisseur)
MATCH (m:Mitigation {id: 'MIT-01'}), (r:Risk {id: 'RO-01'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-01',
  effectiveness: 'High',
  description: 'Le dual-sourcing permet de basculer vers le second fournisseur en cas de défaillance du principal',
  created_at: datetime()
}]->(r);

// MIT-01 (Dual-sourcing) → RS-02 (Retard production) - effet indirect
MATCH (m:Mitigation {id: 'MIT-01'}), (r:Risk {id: 'RS-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-02',
  effectiveness: 'Medium',
  description: 'La sécurisation de la supply chain réduit les risques de retard liés aux composants',
  created_at: datetime()
}]->(r);

// MIT-02 (Rétention talents) → RO-05 (Fuite compétences)
MATCH (m:Mitigation {id: 'MIT-02'}), (r:Risk {id: 'RO-05'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-03',
  effectiveness: 'High',
  description: 'Le programme de rétention réduit significativement le turnover des experts clés',
  created_at: datetime()
}]->(r);

// MIT-02 (Rétention talents) → RS-03 (Perte avance techno)
MATCH (m:Mitigation {id: 'MIT-02'}), (r:Risk {id: 'RS-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-04',
  effectiveness: 'Medium',
  description: 'La conservation des talents maintient la capacité d\'innovation',
  created_at: datetime()
}]->(r);

// MIT-03 (Revue qualité temps réel) → RO-03 (Dérive qualité)
MATCH (m:Mitigation {id: 'MIT-03'}), (r:Risk {id: 'RO-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-05',
  effectiveness: 'High',
  description: 'Le monitoring temps réel permet de détecter et corriger les dérives avant qu\'elles ne s\'aggravent',
  created_at: datetime()
}]->(r);

// MIT-04 (Zero Trust PLM) → RO-02 (Cyberattaque PLM)
MATCH (m:Mitigation {id: 'MIT-04'}), (r:Risk {id: 'RO-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-06',
  effectiveness: 'Critical',
  description: 'L\'architecture Zero Trust réduit drastiquement la surface d\'attaque et les possibilités de mouvement latéral',
  created_at: datetime()
}]->(r);

// MIT-04 (Zero Trust PLM) → RS-06 (Compromission IP)
MATCH (m:Mitigation {id: 'MIT-04'}), (r:Risk {id: 'RS-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-07',
  effectiveness: 'High',
  description: 'La sécurisation du PLM protège les données de propriété intellectuelle',
  created_at: datetime()
}]->(r);

// MIT-05 (Plan contingence production) → RS-07 (Insuffisance capacité)
MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'RS-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-08',
  effectiveness: 'Medium',
  description: 'Le plan de contingence permet de pallier partiellement les insuffisances de capacité interne',
  created_at: datetime()
}]->(r);

// MIT-05 (Plan contingence production) → RS-02 (Retard production)
MATCH (m:Mitigation {id: 'MIT-05'}), (r:Risk {id: 'RS-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-09',
  effectiveness: 'Medium',
  description: 'Les sous-traitants backup permettent de maintenir le planning en cas de problème',
  created_at: datetime()
}]->(r);

// MIT-06 (Revue code safety) → RO-06 (Bug critique)
MATCH (m:Mitigation {id: 'MIT-06'}), (r:Risk {id: 'RO-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-10',
  effectiveness: 'Critical',
  description: 'La revue indépendante maximise les chances de détection des bugs critiques avant déploiement',
  created_at: datetime()
}]->(r);

// MIT-06 (Revue code safety) → RS-04 (Non-conformité safety)
MATCH (m:Mitigation {id: 'MIT-06'}), (r:Risk {id: 'RS-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-11',
  effectiveness: 'High',
  description: 'La conformité DO-178C démontre la rigueur du processus de développement safety',
  created_at: datetime()
}]->(r);

// MIT-07 (Diversification combustible) → RS-05 (Tension combustible)
MATCH (m:Mitigation {id: 'MIT-07'}), (r:Risk {id: 'RS-05'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-12',
  effectiveness: 'High',
  description: 'La diversification géographique réduit l\'exposition aux tensions sur une zone spécifique',
  created_at: datetime()
}]->(r);

// MIT-08 (Processus budget Groupe) → RS-08 (Dépassement budget)
MATCH (m:Mitigation {id: 'MIT-08'}), (r:Risk {id: 'RS-08'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-13',
  effectiveness: 'Medium',
  description: 'Le suivi rigoureux permet de détecter les déviations tôt et de prendre des actions correctives',
  created_at: datetime()
}]->(r);

// MIT-09 (SOC Groupe) → RO-02 (Cyberattaque PLM)
MATCH (m:Mitigation {id: 'MIT-09'}), (r:Risk {id: 'RO-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-14',
  effectiveness: 'High',
  description: 'Le SOC 24/7 permet une détection et réponse rapide aux tentatives d\'intrusion',
  created_at: datetime()
}]->(r);

// MIT-09 (SOC Groupe) → RO-07 (Indisponibilité infra)
MATCH (m:Mitigation {id: 'MIT-09'}), (r:Risk {id: 'RO-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-15',
  effectiveness: 'Medium',
  description: 'La surveillance proactive permet d\'anticiper certaines pannes et incidents',
  created_at: datetime()
}]->(r);

// MIT-10 (PCA IT Groupe) → RO-07 (Indisponibilité infra)
MATCH (m:Mitigation {id: 'MIT-10'}), (r:Risk {id: 'RO-07'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-16',
  effectiveness: 'Critical',
  description: 'Le disaster recovery garantit une reprise rapide en cas de panne majeure',
  created_at: datetime()
}]->(r);

// MIT-11 (Innovation partagée) → RS-03 (Perte avance techno)
MATCH (m:Mitigation {id: 'MIT-11'}), (r:Risk {id: 'RS-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-17',
  effectiveness: 'Medium',
  description: 'L\'accès aux innovations du groupe permet d\'accélérer le développement',
  created_at: datetime()
}]->(r);

// MIT-12 (ISO 19443) → RO-03 (Dérive qualité)
MATCH (m:Mitigation {id: 'MIT-12'}), (r:Risk {id: 'RO-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-18',
  effectiveness: 'High',
  description: 'Le référentiel ISO 19443 impose des contrôles qualité rigoureux tout au long de la supply chain',
  created_at: datetime()
}]->(r);

// MIT-12 (ISO 19443) → RO-04 (Retard certification fournisseur)
MATCH (m:Mitigation {id: 'MIT-12'}), (r:Risk {id: 'RO-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-19',
  effectiveness: 'Medium',
  description: 'Le framework ISO structure le processus de qualification des fournisseurs',
  created_at: datetime()
}]->(r);

// MIT-13 (IEC 61513) → RO-06 (Bug critique)
MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'RO-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-20',
  effectiveness: 'High',
  description: 'La norme IEC 61513 définit des exigences strictes pour le développement de systèmes I&C nucléaires',
  created_at: datetime()
}]->(r);

// MIT-13 (IEC 61513) → RS-04 (Non-conformité safety)
MATCH (m:Mitigation {id: 'MIT-13'}), (r:Risk {id: 'RS-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-21',
  effectiveness: 'Critical',
  description: 'La conformité IEC 61513 est un prérequis pour la certification safety des systèmes I&C',
  created_at: datetime()
}]->(r);

// MIT-14 (NIS2) → RO-02 (Cyberattaque PLM)
MATCH (m:Mitigation {id: 'MIT-14'}), (r:Risk {id: 'RO-02'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-22',
  effectiveness: 'High',
  description: 'NIS2 impose des mesures de cybersécurité et de notification d\'incidents',
  created_at: datetime()
}]->(r);

// MIT-14 (NIS2) → RS-06 (Compromission IP)
MATCH (m:Mitigation {id: 'MIT-14'}), (r:Risk {id: 'RS-06'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-23',
  effectiveness: 'Medium',
  description: 'Les exigences NIS2 renforcent la posture de sécurité globale',
  created_at: datetime()
}]->(r);

// MIT-15 (Référentiel ASN) → RS-04 (Non-conformité safety)
MATCH (m:Mitigation {id: 'MIT-15'}), (r:Risk {id: 'RS-04'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-24',
  effectiveness: 'Critical',
  description: 'L\'application systématique du référentiel ASN garantit la conformité réglementaire',
  created_at: datetime()
}]->(r);

// MIT-15 (Référentiel ASN) → RO-03 (Dérive qualité)
MATCH (m:Mitigation {id: 'MIT-15'}), (r:Risk {id: 'RO-03'})
CREATE (m)-[:MITIGATES {
  id: 'MIG-25',
  effectiveness: 'High',
  description: 'Les exigences ASN imposent des standards qualité élevés sur les processus',
  created_at: datetime()
}]->(r);

// =============================================================================
// 11. VÉRIFICATION
// =============================================================================

// Compter les risques par niveau
MATCH (r:Risk)
RETURN r.level as Niveau, count(r) as Nombre
ORDER BY Niveau;

// Compter les risques par origine
MATCH (r:Risk)
RETURN r.origin as Origine, count(r) as Nombre
ORDER BY Origine;

// Compter les risques par statut
MATCH (r:Risk)
RETURN r.status as Statut, count(r) as Nombre
ORDER BY Statut;

// Compter les influences par type
MATCH ()-[i:INFLUENCES]->()
RETURN i.influence_type as Type, count(i) as Nombre
ORDER BY Type;

// Afficher les risques contingents
MATCH (r:Risk {status: 'Contingent'})
RETURN r.id, r.name, r.origin, r.activation_condition, r.activation_decision_date;

// Compter les TPOs par cluster
MATCH (t:TPO)
RETURN t.cluster as Cluster, count(t) as Nombre
ORDER BY Cluster;

// Afficher les TPOs et leurs impacts
MATCH (t:TPO)
OPTIONAL MATCH (r:Risk)-[i:IMPACTS_TPO]->(t)
RETURN t.reference as TPO, t.name as Nom, t.cluster as Cluster, 
       count(i) as NombreImpacts
ORDER BY t.reference;

// Compter les mitigations par type
MATCH (m:Mitigation)
RETURN m.type as Type, count(m) as Nombre
ORDER BY Type;

// Compter les mitigations par statut
MATCH (m:Mitigation)
RETURN m.status as Statut, count(m) as Nombre
ORDER BY Statut;

// Afficher les mitigations et le nombre de risques adressés
MATCH (m:Mitigation)
OPTIONAL MATCH (m)-[rel:MITIGATES]->(r:Risk)
RETURN m.id as ID, m.name as Mitigation, m.type as Type, m.status as Statut,
       count(rel) as RisquesAdresses
ORDER BY count(rel) DESC, m.type;

// Afficher les risques les plus mitigés
MATCH (r:Risk)
OPTIONAL MATCH (m:Mitigation)-[rel:MITIGATES]->(r)
RETURN r.id as ID, r.name as Risque, r.level as Niveau, r.origin as Origine,
       count(rel) as NombreMitigations
ORDER BY count(rel) DESC
LIMIT 10;

// Afficher les mitigations par efficacité
MATCH (m:Mitigation)-[rel:MITIGATES]->(r:Risk)
RETURN rel.effectiveness as Efficacite, count(rel) as Nombre
ORDER BY 
  CASE rel.effectiveness 
    WHEN 'Critical' THEN 1 
    WHEN 'High' THEN 2 
    WHEN 'Medium' THEN 3 
    WHEN 'Low' THEN 4 
  END;

// Afficher le détail des impacts TPO
MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
RETURN r.id as RisqueID, r.name as Risque, r.origin as Origine,
       t.reference as TPO, i.impact_level as NiveauImpact
ORDER BY t.reference, i.impact_level DESC;

// Statistiques globales
MATCH (r:Risk) WITH count(r) as risks
MATCH (t:TPO) WITH risks, count(t) as tpos
MATCH (m:Mitigation) WITH risks, tpos, count(m) as mitigations
MATCH ()-[i:INFLUENCES]->() WITH risks, tpos, mitigations, count(i) as influences
MATCH ()-[it:IMPACTS_TPO]->() WITH risks, tpos, mitigations, influences, count(it) as tpo_impacts
MATCH ()-[mt:MITIGATES]->() 
RETURN risks as Risques, tpos as TPOs, mitigations as Mitigations, 
       influences as Influences, tpo_impacts as ImpactsTPO, count(mt) as LiensMitigates;
