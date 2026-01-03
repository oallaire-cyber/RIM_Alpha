// ============================================
// Risk Influence Map - Données de démonstration
// Scénario: Chaîne d'attaque cyber et impacts business
// ============================================

// Suppression des données existantes (optionnel)
// MATCH (n) DETACH DELETE n;

// ============================================
// CRÉATION DES RISQUES
// ============================================

// --- Risques Cyber (vecteurs d'attaque) ---
CREATE (phishing:Risk {
    id: randomUUID(),
    name: "Phishing ciblé (Spear Phishing)",
    category: "Cyber",
    description: "Attaque par email ciblant des employés clés avec des messages personnalisés",
    probability: 8.0,
    impact: 6.0,
    score: 48.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (vuln_0day:Risk {
    id: randomUUID(),
    name: "Exploitation vulnérabilité 0-day",
    category: "Cyber",
    description: "Exploitation d'une vulnérabilité non corrigée dans un composant critique",
    probability: 4.0,
    impact: 9.0,
    score: 36.0,
    status: "Surveillé",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (credential_theft:Risk {
    id: randomUUID(),
    name: "Vol de credentials",
    category: "Cyber",
    description: "Compromission des identifiants d'un utilisateur à privilèges",
    probability: 6.0,
    impact: 8.0,
    score: 48.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (lateral_movement:Risk {
    id: randomUUID(),
    name: "Mouvement latéral",
    category: "Cyber",
    description: "Propagation de l'attaquant dans le réseau interne",
    probability: 5.0,
    impact: 8.0,
    score: 40.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (ransomware:Risk {
    id: randomUUID(),
    name: "Déploiement ransomware",
    category: "Cyber",
    description: "Chiffrement des données et systèmes critiques",
    probability: 4.0,
    impact: 10.0,
    score: 40.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (data_exfil:Risk {
    id: randomUUID(),
    name: "Exfiltration de données",
    category: "Cyber",
    description: "Vol de données sensibles (clients, propriété intellectuelle)",
    probability: 5.0,
    impact: 9.0,
    score: 45.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

// --- Risques Opérationnels ---
CREATE (service_interruption:Risk {
    id: randomUUID(),
    name: "Interruption de service",
    category: "Opérationnel",
    description: "Arrêt des systèmes de production et services clients",
    probability: 4.0,
    impact: 9.0,
    score: 36.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (supply_chain:Risk {
    id: randomUUID(),
    name: "Perturbation chaîne logistique",
    category: "Opérationnel",
    description: "Impact sur les fournisseurs et partenaires connectés",
    probability: 3.0,
    impact: 7.0,
    score: 21.0,
    status: "Surveillé",
    created_at: datetime(),
    updated_at: datetime()
})

// --- Risques Financiers ---
CREATE (financial_loss:Risk {
    id: randomUUID(),
    name: "Pertes financières directes",
    category: "Financier",
    description: "Coûts de remédiation, rançon potentielle, perte de CA",
    probability: 5.0,
    impact: 8.0,
    score: 40.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (stock_impact:Risk {
    id: randomUUID(),
    name: "Impact cours de bourse",
    category: "Financier",
    description: "Dévaluation suite à l'annonce publique de l'incident",
    probability: 6.0,
    impact: 7.0,
    score: 42.0,
    status: "Surveillé",
    created_at: datetime(),
    updated_at: datetime()
})

// --- Risques Conformité ---
CREATE (rgpd_breach:Risk {
    id: randomUUID(),
    name: "Violation RGPD",
    category: "Conformité",
    description: "Non-conformité suite à une fuite de données personnelles",
    probability: 5.0,
    impact: 8.0,
    score: 40.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (regulatory_sanction:Risk {
    id: randomUUID(),
    name: "Sanctions réglementaires",
    category: "Conformité",
    description: "Amendes CNIL, ANSSI, ou autres autorités",
    probability: 4.0,
    impact: 7.0,
    score: 28.0,
    status: "Surveillé",
    created_at: datetime(),
    updated_at: datetime()
})

// --- Risques Réputation ---
CREATE (reputation_damage:Risk {
    id: randomUUID(),
    name: "Atteinte à la réputation",
    category: "Réputation",
    description: "Perte de confiance des clients et partenaires",
    probability: 6.0,
    impact: 8.0,
    score: 48.0,
    status: "Actif",
    created_at: datetime(),
    updated_at: datetime()
})

CREATE (media_exposure:Risk {
    id: randomUUID(),
    name: "Exposition médiatique négative",
    category: "Réputation",
    description: "Couverture presse défavorable de l'incident",
    probability: 7.0,
    impact: 6.0,
    score: 42.0,
    status: "Surveillé",
    created_at: datetime(),
    updated_at: datetime()
})

// ============================================
// CRÉATION DES INFLUENCES
// ============================================

// Récupération des nœuds pour créer les relations
MATCH (phishing:Risk {name: "Phishing ciblé (Spear Phishing)"})
MATCH (credential_theft:Risk {name: "Vol de credentials"})
MATCH (lateral_movement:Risk {name: "Mouvement latéral"})
MATCH (ransomware:Risk {name: "Déploiement ransomware"})
MATCH (data_exfil:Risk {name: "Exfiltration de données"})
MATCH (vuln_0day:Risk {name: "Exploitation vulnérabilité 0-day"})
MATCH (service_interruption:Risk {name: "Interruption de service"})
MATCH (supply_chain:Risk {name: "Perturbation chaîne logistique"})
MATCH (financial_loss:Risk {name: "Pertes financières directes"})
MATCH (stock_impact:Risk {name: "Impact cours de bourse"})
MATCH (rgpd_breach:Risk {name: "Violation RGPD"})
MATCH (regulatory_sanction:Risk {name: "Sanctions réglementaires"})
MATCH (reputation_damage:Risk {name: "Atteinte à la réputation"})
MATCH (media_exposure:Risk {name: "Exposition médiatique négative"})

// --- Chaîne d'attaque ---
CREATE (phishing)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 8.0,
    description: "Le phishing réussi permet le vol de credentials",
    created_at: datetime()
}]->(credential_theft)

CREATE (vuln_0day)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 9.0,
    description: "L'exploitation 0-day donne un accès initial",
    created_at: datetime()
}]->(lateral_movement)

CREATE (credential_theft)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 7.0,
    description: "Les credentials volés permettent le mouvement latéral",
    created_at: datetime()
}]->(lateral_movement)

CREATE (lateral_movement)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 8.0,
    description: "Le mouvement latéral prépare le déploiement du ransomware",
    created_at: datetime()
}]->(ransomware)

CREATE (lateral_movement)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 7.0,
    description: "L'accès étendu permet l'exfiltration de données",
    created_at: datetime()
}]->(data_exfil)

// --- Impacts opérationnels ---
CREATE (ransomware)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 9.0,
    description: "Le chiffrement cause l'interruption des services",
    created_at: datetime()
}]->(service_interruption)

CREATE (service_interruption)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 6.0,
    description: "L'interruption se propage aux partenaires",
    created_at: datetime()
}]->(supply_chain)

// --- Impacts financiers ---
CREATE (ransomware)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 8.0,
    description: "Ransomware = coûts de remédiation + potentielle rançon",
    created_at: datetime()
}]->(financial_loss)

CREATE (service_interruption)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 7.0,
    description: "L'arrêt de production génère des pertes de CA",
    created_at: datetime()
}]->(financial_loss)

CREATE (reputation_damage)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 6.0,
    description: "La perte de confiance impacte le cours de bourse",
    created_at: datetime()
}]->(stock_impact)

// --- Impacts conformité ---
CREATE (data_exfil)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 8.0,
    description: "L'exfiltration de données personnelles = violation RGPD",
    created_at: datetime()
}]->(rgpd_breach)

CREATE (rgpd_breach)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 7.0,
    description: "La violation RGPD entraîne des sanctions",
    created_at: datetime()
}]->(regulatory_sanction)

CREATE (regulatory_sanction)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 5.0,
    description: "Les sanctions alourdissent les pertes financières",
    created_at: datetime()
}]->(financial_loss)

// --- Impacts réputation ---
CREATE (data_exfil)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 8.0,
    description: "La fuite de données détruit la confiance clients",
    created_at: datetime()
}]->(reputation_damage)

CREATE (service_interruption)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 6.0,
    description: "L'indisponibilité prolongée nuit à l'image",
    created_at: datetime()
}]->(reputation_damage)

CREATE (reputation_damage)-[:INFLUENCES {
    id: randomUUID(),
    type: "Déclenche",
    strength: 7.0,
    description: "L'atteinte réputation attire l'attention médiatique",
    created_at: datetime()
}]->(media_exposure)

CREATE (media_exposure)-[:INFLUENCES {
    id: randomUUID(),
    type: "Amplifie",
    strength: 6.0,
    description: "La couverture médiatique amplifie les dégâts réputationnels",
    created_at: datetime()
}]->(reputation_damage)

// --- Boucles de rétroaction ---
CREATE (financial_loss)-[:INFLUENCES {
    id: randomUUID(),
    type: "Corrèle",
    strength: 5.0,
    description: "Les pertes financières limitent la capacité de remédiation",
    created_at: datetime()
}]->(service_interruption)

// ============================================
// Vérification
// ============================================
// MATCH (r:Risk) RETURN count(r) as nb_risques;
// MATCH ()-[i:INFLUENCES]->() RETURN count(i) as nb_influences;
