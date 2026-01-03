# 🎯 Risk Influence Map

Application Streamlit pour la cartographie dynamique des risques et de leurs influences mutuelles, utilisant Neo4j comme base de données graphe.

## 🎯 Objectif

Disposer d'une vue dynamique des risques permettant de :
- **Visualiser** le graphe des risques et leurs interdépendances
- **Modéliser** les influences entre risques (amplification, déclenchement, atténuation, corrélation)
- **Gérer** le cycle de vie complet des risques (CRUD)
- **Analyser** l'impact en cascade des risques

## 📋 Prérequis

- **Python 3.9+** (déjà installé sur la plupart des systèmes)
- **Docker** pour Neo4j (ou Neo4j Desktop)
- Aucun droit administrateur requis
- Aucun serveur web tiers nécessaire

## 🚀 Installation rapide

### 1. Lancer Neo4j avec Docker

```bash
docker run -d \
    --name neo4j-risk-map \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/risk2024secure \
    -v neo4j_risk_data:/data \
    neo4j:latest
```

### 2. Installer les dépendances Python

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur sur `http://localhost:8501`

## 📊 Fonctionnalités

### Gestion des Risques (Nœuds)

| Attribut | Description |
|----------|-------------|
| **Nom** | Identifiant du risque |
| **Catégorie** | Cyber, Opérationnel, Stratégique, Financier, Conformité, Réputation, RH, Environnemental |
| **Probabilité** | Échelle 1-10 |
| **Impact** | Échelle 1-10 |
| **Score** | Calculé automatiquement (Probabilité × Impact) |
| **Statut** | Actif, Surveillé, Mitigé, Fermé |
| **Description** | Texte libre |

### Gestion des Influences (Relations)

| Attribut | Description |
|----------|-------------|
| **Source** | Risque origine |
| **Cible** | Risque impacté |
| **Type** | Amplifie, Déclenche, Atténue, Corrèle |
| **Force** | Échelle 1-10 |
| **Description** | Explication de l'influence |

### Visualisation

- **Graphe interactif** avec PyVis
- **Couleurs dynamiques** selon le score ou la catégorie
- **Taille des nœuds** proportionnelle au score de risque
- **Épaisseur des liens** proportionnelle à la force d'influence
- **Navigation** : zoom, déplacement, sélection
- **Info-bulles** au survol

### Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Risk Influence Map                                      │
├─────────────────────────────────────────────────────────────┤
│  📊 Risques: 12  │  🔗 Influences: 18  │  📈 Score: 5.2     │
├─────────────────────────────────────────────────────────────┤
│  [Visualisation] [Risques] [Influences] [Données]           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │              [Graphe Interactif]                    │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Connexion Neo4j

Par défaut :
- **URI** : `bolt://localhost:7687`
- **Utilisateur** : `neo4j`
- **Mot de passe** : celui défini dans `NEO4J_AUTH`

### Variables d'environnement (optionnel)

```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=votre_mot_de_passe
```

## 📁 Structure du projet

```
risk_influence_map/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
└── README.md          # Documentation
```

## 🔍 Requêtes Cypher utiles

### Risques les plus influents
```cypher
MATCH (r:Risk)-[i:INFLUENCES]->()
RETURN r.name, count(i) as influences_sortantes
ORDER BY influences_sortantes DESC
LIMIT 5
```

### Risques les plus impactés
```cypher
MATCH ()-[i:INFLUENCES]->(r:Risk)
RETURN r.name, count(i) as influences_entrantes
ORDER BY influences_entrantes DESC
LIMIT 5
```

### Chaînes d'influence
```cypher
MATCH path = (a:Risk)-[:INFLUENCES*1..3]->(b:Risk)
WHERE a <> b
RETURN path
LIMIT 20
```

### Score d'influence cumulé
```cypher
MATCH (r:Risk)
OPTIONAL MATCH (r)-[out:INFLUENCES]->()
OPTIONAL MATCH ()-[in:INFLUENCES]->(r)
RETURN r.name, 
       r.score as score_propre,
       sum(out.strength) as influence_emise,
       sum(in.strength) as influence_recue
ORDER BY r.score DESC
```

## 🛡️ Cas d'usage Cybersécurité

### Exemple de modélisation

```
[Phishing réussi] --Déclenche--> [Compromission credentials]
         |                              |
         |                              v
         +-------Amplifie------> [Mouvement latéral]
                                        |
                                        v
                                 [Exfiltration données]
                                        |
                                        v
                                 [Impact réputation]
```

### Catégories recommandées pour la cyber

- **Cyber** : Risques techniques (malware, vulnérabilités, etc.)
- **Opérationnel** : Continuité d'activité, processus
- **Conformité** : RGPD, NIS2, certifications
- **Réputation** : Image, confiance clients
- **Financier** : Pertes directes, amendes

## 🔄 Évolutions possibles

- [ ] Import/Export CSV des risques
- [ ] Simulation de propagation d'impact
- [ ] Historique des modifications
- [ ] Calcul automatique du risque résiduel
- [ ] Intégration avec des référentiels (EBIOS RM, ISO 27005)
- [ ] API REST pour intégration SIEM/SOAR
- [ ] Multi-utilisateurs avec authentification

## 📝 Licence

POC interne - Usage libre pour développement et tests.

---

*Développé pour l'analyse dynamique des risques cyber et business*
