// =============================================================================
// Script de chargement des données de démo - Risk Influence Map Phase 1
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
  name: 'Bug critique logiciel embarqué',
  description: 'Découverte tardive d\'un bug majeur dans le logiciel de contrôle embarqué',
  level: 'Operational',
  status: 'Active',
  categories: ['Produit'],
  owner: 'Lead Software Engineer',
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
// 4. CRÉATION DES LIENS D'INFLUENCE - NIVEAU 1 (Op → Strat)
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
// 5. CRÉATION DES LIENS D'INFLUENCE - NIVEAU 2 (Strat → Strat)
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
// 6. CRÉATION DES LIENS D'INFLUENCE - NIVEAU 3 (Op → Op)
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
// 7. VÉRIFICATION
// =============================================================================

// Compter les risques par niveau
MATCH (r:Risk)
RETURN r.level as Niveau, count(r) as Nombre
ORDER BY Niveau;

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
RETURN r.id, r.name, r.activation_condition, r.activation_decision_date;
