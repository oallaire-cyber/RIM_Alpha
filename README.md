# 🎯 Risk Influence Map - Phase 1

POC enrichi pour la gestion des risques avec architecture stratégique/opérationnelle et risques contingents.

## 🆕 Nouvelles fonctionnalités Phase 1

### Architecture à deux niveaux
- **Risques Stratégiques** : Orientés conséquences business, pilotés par la direction
- **Risques Opérationnels** : Orientés causes, pilotés par les fonctions métiers

### Trois types de liens d'influence
1. **Niveau 1 (Op → Strat)** : Comment les risques opérationnels impactent les stratégiques
2. **Niveau 2 (Strat → Strat)** : Effets de cascade entre risques stratégiques
3. **Niveau 3 (Op → Op)** : Propagation entre risques opérationnels

### Gestion des risques contingents
- Modélisation des risques futurs dépendants de décisions structurantes
- Timeline des décisions (ex: Q3 2026)
- Visualisation en pointillés dans le graphe
- Conditions d'activation traçables

### Multi-catégorisation
- **Programme** : Risques transverses
- **Produit** : Risques techniques du réacteur
- **Industriel** : Risques de production
- **Supply Chain** : Risques d'approvisionnement

Un risque peut appartenir à plusieurs catégories simultanément.

### Import/Export Excel
- Export complet des risques et influences
- Import pour alimentation initiale
- Format standardisé pour faciliter le partage

### Filtres avancés
- Filtrage par niveau (Stratégique/Opérationnel)
- Filtrage par catégories (multi-sélection)
- Filtrage par statut (Active/Contingent/Archived)
- Visualisation adaptée selon les filtres

## 📊 Modèle de données

### Nœud Risk
```
Properties:
- id: UUID unique
- name: Nom du risque
- level: "Strategic" | "Operational"
- categories: ["Programme", "Produit", "Industriel", "Supply Chain"]
- description: Description détaillée
- status: "Active" | "Contingent" | "Archived"
- activation_condition: Condition pour risques contingents
- activation_decision_date: Date de décision structurante
- owner: Responsable du risque
- probability: 0-10 (optionnel)
- impact: 0-10 (optionnel)
- exposure: probability × impact (calculé)
- current_score_type: "Qualitative_4x4" | "Quantitative" | "None"
```

### Relation INFLUENCES
```
Properties:
- id: UUID unique
- influence_type: "Level1_Op_to_Strat" | "Level2_Strat_to_Strat" | "Level3_Op_to_Op"
- strength: "Weak" | "Moderate" | "Strong" | "Critical"
- description: Explication du lien
- confidence: 0.0-1.0 (niveau de certitude)
```

## 🚀 Installation

### Prérequis
- Python 3.9+
- Docker (pour Neo4j)

### 1. Lancer Neo4j
```bash
docker run -d \
    --name neo4j-risk \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password123 \
    -v neo4j_data:/data \
    neo4j:latest
```

### 2. Installer les dépendances
```bash
pip install -r requirements_phase1.txt
```

### 3. Lancer l'application
```bash
streamlit run app_phase1.py
```

## 💡 Cas d'usage

### Exemple 1 : Risque contingent lié au choix du combustible
```
Nom: Tension approvisionnement combustible type A
Niveau: Strategic
Catégories: ["Programme", "Supply Chain"]
Statut: Contingent
Condition d'activation: "Si choix du combustible uranium enrichi type A"
Date de décision: 2026-09-30
```

### Exemple 2 : Chaîne d'influence Op → Strat
```
[Risque Op] Défaillance fournisseur pièce critique
    ↓ (INFLUENCES Level1, Critical)
[Risque Strat] Retard mise en production
    ↓ (INFLUENCES Level2, Strong)
[Risque Strat] Non-atteinte objectif profitabilité
```

## 📋 Format Excel pour Import

### Sheet "Risks"
| name | level | categories | description | status | owner | probability | impact |
|------|-------|------------|-------------|--------|-------|-------------|--------|
| Risque 1 | Strategic | ["Programme"] | Description | Active | John | 7.0 | 8.0 |

### Sheet "Influences"
| source_id | target_id | strength | description | confidence |
|-----------|-----------|----------|-------------|------------|
| uuid-1 | uuid-2 | Critical | Description | 0.9 |

## 🎨 Légende de visualisation

### Couleurs par niveau
- 🟣 **Violet** : Risques Stratégiques
- 🔵 **Bleu** : Risques Opérationnels

### Couleurs par exposition
- 🔴 **Rouge** : Critique (≥7)
- 🟠 **Orange** : Élevé (4-7)
- 🔵 **Bleu** : Modéré (2-4)
- 🟢 **Vert** : Faible (<2)

### Types de liens
- 🔴 **Rouge** : Op → Strat (Niveau 1)
- 🟣 **Violet** : Strat → Strat (Niveau 2)
- 🔵 **Bleu** : Op → Op (Niveau 3)

### Styles visuels
- **Pointillés** : Risques contingents
- **Solides** : Risques actifs
- **Largeur du lien** : Proportionnelle à la force (Weak → Critical)

## 🔜 Phases suivantes

### Phase 2 (1 mois)
- Dashboard exécutif avec KPIs
- Historisation des modifications
- Simulation "Si décision X, quels risques s'activent?"
- Scoring flexible (quali/quanti)

### Phase 3 (1-2 mois)
- KRIs et monitoring temps réel
- Analyse de scénarios
- Exports PowerPoint/PDF
- Formation et documentation

### Phase 4 (évolutif)
- Transition vers quantitatif (€, jours)
- Monte Carlo
- API pour alimentation auto
- Machine learning

## 📞 Support

Pour questions ou suggestions sur le POC Phase 1, contacter l'équipe programme.

---
*POC Phase 1 - Risk Influence Map pour programme SMR*
