# 💾 Guide : Sauvegarde des layouts de graphe

## 🎯 Fonctionnalité

La Risk Influence Map permet maintenant de **sauvegarder et restaurer** les positions des nœuds dans le graphe. Finies les organisations perdues à chaque actualisation !

## 📋 Table des matières

1. [Layouts prédéfinis](#layouts-prédéfinis)
2. [Sauvegarder un layout](#sauvegarder-un-layout)
3. [Charger un layout](#charger-un-layout)
4. [Gérer les layouts](#gérer-les-layouts)
5. [Cas d'usage](#cas-dusage)
6. [Limitations](#limitations)

---

## 🎨 Layouts prédéfinis

### Layout "En couches"

Organisation hiérarchique à deux niveaux :

```
┌────────────────────────────────────────┐
│  Niveau Strategic (en haut)            │
│  RS-01    RS-02    RS-03    RS-04 ...  │
└────────────────────────────────────────┘
                 ↓ ↓ ↓
┌────────────────────────────────────────┐
│  Niveau Operational (en bas)           │
│  RO-01    RO-02    RO-03    RO-04 ...  │
└────────────────────────────────────────┘
```

**Utilisation :**
1. Cliquez sur **"📊 En couches"** dans la section "Layouts prédéfinis"
2. Le layout est automatiquement sauvegardé et appliqué
3. Parfait pour montrer la hiérarchie stratégique/opérationnelle

**Avantages :**
- ✅ Clarté visuelle immédiate
- ✅ Idéal pour les présentations
- ✅ Montre bien les liens de causalité (Op → Strat)

---

### Layout "Par catégories"

Organisation en grille 2x2 par catégorie :

```
┌──────────────────┐  ┌──────────────────┐
│   Programme      │  │    Produit       │
│                  │  │                  │
│  RS-01  RO-01    │  │  RS-03  RO-05    │
│  RS-08           │  │  RO-06           │
└──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐
│   Industriel     │  │  Supply Chain    │
│                  │  │                  │
│  RS-07  RO-03    │  │  RS-05  RO-01    │
│                  │  │  RO-04           │
└──────────────────┘  └──────────────────┘
```

**Utilisation :**
1. Cliquez sur **"🗂️ Par catégories"** dans la section "Layouts prédéfinis"
2. Les risques sont automatiquement groupés par catégorie
3. Parfait pour les revues par verticale métier

**Avantages :**
- ✅ Visualisation par domaine métier
- ✅ Facilite les revues avec les responsables de chaque verticale
- ✅ Identifie rapidement les zones à risque concentré

---

## 💾 Sauvegarder un layout

### Méthode 1 : Sauvegarder un layout prédéfini

**Le plus simple pour commencer :**

1. Allez dans l'onglet **Visualisation**
2. Ouvrez la section **"🎨 Layouts prédéfinis"**
3. Cliquez sur **"📊 En couches"** ou **"🗂️ Par catégories"**
4. Le layout est automatiquement sauvegardé avec un nom horodaté

**Nom auto-généré :**
- Format : `couches_20250103_1430` ou `categories_20250103_1430`
- Horodaté pour éviter les conflits

---

### Méthode 2 : Sauvegarder après ajustements manuels (Phase 2)

**⚠️ En cours de développement pour Phase 2**

Cette fonctionnalité permettra de :
1. Organiser le graphe manuellement avec la souris
2. Cliquer sur "💾 Sauvegarder (manuel)"
3. Donner un nom personnalisé
4. Conserver le layout exactement comme vous l'avez créé

**Workaround Phase 1 :**
1. Utilisez un layout prédéfini comme base
2. Physique OFF pour ajustements manuels
3. Notez mentalement l'organisation
4. Recréez au besoin pour la prochaine session

---

## 📂 Charger un layout

### Étape 1 : Ouvrir la section de chargement

1. Onglet **Visualisation**
2. Panneau de gauche (Filtres)
3. Section **"💾 Gestion des layouts"**
4. Ouvrir **"📂 Charger un layout"**

### Étape 2 : Choisir un layout

```
┌────────────────────────────────────┐
│ Choisir un layout                  │
│ ▼ couches_20250103_1430 (15 nœuds)│
│   categories_20250103_1025 (15)    │
│   demo_final (15)                  │
└────────────────────────────────────┘
```

Le nombre de nœuds vous aide à identifier le bon layout.

### Étape 3 : Charger

Cliquez sur **"📂 Charger"** :
- ✅ Le layout est appliqué instantanément
- ✅ Les nœuds se positionnent aux coordonnées sauvegardées
- ✅ La physique est automatiquement désactivée
- ✅ Message de confirmation affiché

### Indicateur de layout actif

Quand un layout est chargé, vous verrez en haut du graphe :

```
📍 Layout actif : couches_20250103_1430
```

---

## 🗑️ Gérer les layouts

### Supprimer un layout

1. Ouvrir **"📂 Charger un layout"**
2. Sélectionner le layout à supprimer
3. Cliquer sur **"🗑️ Supprimer"**
4. Confirmation : "✅ Layout 'xxx' supprimé !"

### Lister tous les layouts

Tous les layouts sauvegardés apparaissent dans le menu déroulant :

```
couches_20250103_1430 (15 nœuds)
  └─ Sauvegardé le: 2025-01-03 14:30
  
categories_20250103_1025 (15 nœuds)
  └─ Sauvegardé le: 2025-01-03 10:25
```

### Réinitialiser (retour à l'auto)

Pour revenir à l'organisation automatique :

1. Section **"🎨 Layouts prédéfinis"**
2. Cliquer sur **"🔄 Réinitialiser (auto)"**
3. Le graphe s'organise automatiquement avec la physique

---

## 💡 Cas d'usage

### Cas 1 : Préparer une démo

**Objectif :** Avoir un graphe parfait pour présenter

```bash
# J-1 : Préparation
1. Charger les données de démo
2. Appliquer "Layout en couches"
3. Vérifier la lisibilité
4. Sauvegarder avec le nom "demo_20250104"

# Jour J : Démo
1. Ouvrir l'application
2. Charger le layout "demo_20250104"
3. Graphe instantanément parfait !
4. Présentation fluide
```

**Résultat :** Zéro stress, layout toujours identique

---

### Cas 2 : Revue mensuelle par verticale

**Objectif :** Faciliter les revues risques avec chaque verticale

```bash
# Préparation mensuelle
1. Appliquer "Layout par catégories"
2. Sauvegarder comme "revue_mensuelle_jan2025"

# Réunion Programme
1. Charger "revue_mensuelle_jan2025"
2. Filtrer : Catégories = Programme uniquement
3. Les risques Programme sont au même endroit
4. Discussion focalisée

# Réunion Supply Chain
1. Même layout
2. Filtrer : Catégories = Supply Chain
3. Continuité visuelle entre réunions
```

**Résultat :** Efficacité maximale, pas de réorganisation mentale

---

### Cas 3 : Comparer deux périodes

**Objectif :** Voir l'évolution des risques

```bash
# Janvier 2025
1. Layout "couches_jan2025"
2. Snapshot des risques

# Mars 2025
1. Recharger "couches_jan2025"
2. Nouveaux risques apparaissent
3. Mais les anciens sont au même endroit
4. Comparaison facile
```

**Résultat :** Visualisation claire de l'évolution

---

### Cas 4 : Communication COMEX

**Objectif :** Graphe professionnel pour le board

```bash
# Préparation COMEX
1. Appliquer "Layout en couches"
2. Ajuster manuellement les nœuds clés
   - RS-01 bien visible en haut à gauche
   - Risques contingents groupés à droite
3. Sauvegarder "comex_q1_2025"
4. Faire captures d'écran

# 3 mois plus tard : COMEX Q2
1. Recharger "comex_q1_2025"
2. Continuité visuelle avec Q1
3. Board comprend instantanément
```

**Résultat :** Communication professionnelle et cohérente

---

## 📊 Workflow recommandé

### Pour une utilisation quotidienne

```
1. Démarrage
   └─ Charger votre layout favori
   
2. Travail
   └─ Ajouter/modifier risques normalement
   
3. Fin de journée
   └─ Layout reste valide pour demain
```

### Pour une présentation

```
1. J-2 : Préparer
   ├─ Créer layout prédéfini
   └─ Sauvegarder avec nom explicite
   
2. J-1 : Vérifier
   ├─ Charger le layout
   └─ Tester les filtres
   
3. Jour J : Présenter
   ├─ Charger le layout
   └─ Graphe parfait instantanément
```

---

## 🚫 Limitations (Phase 1)

### ⚠️ Pas de sauvegarde manuelle (encore)

**Limitation :**
- Impossible de sauvegarder un layout après l'avoir positionné manuellement
- Seuls les layouts prédéfinis sont disponibles

**Workaround :**
- Utilisez les layouts prédéfinis comme base
- Ajustez manuellement à chaque session si besoin

**Solution Phase 2 :**
- Bouton "Capturer positions actuelles"
- Sauvegarde des positions manuelles

---

### ⚠️ Stockage local uniquement

**Limitation :**
- Layouts sauvegardés dans `graph_layouts.json` (même dossier que l'app)
- Pas synchronisés entre machines

**Workaround :**
- Copier le fichier `graph_layouts.json` sur d'autres machines
- Ou recréer les layouts prédéfinis (rapide)

**Solution Phase 3 :**
- Stockage dans Neo4j
- Synchronisation automatique
- Partage entre utilisateurs

---

### ⚠️ Changement de données

**Limitation :**
- Si vous ajoutez/supprimez des risques, le layout peut devenir désorganisé
- Les nouveaux nœuds apparaissent à des positions aléatoires

**Workaround :**
- Recréer le layout prédéfini après modifications importantes
- Les noms auto-horodatés évitent les conflits

**Solution Phase 2 :**
- Layout "intelligent" qui positionne les nouveaux nœuds logiquement
- Basé sur les catégories/niveau des nouveaux risques

---

## 📁 Fichiers

### graph_layouts.json

Tous les layouts sont sauvegardés dans ce fichier JSON :

```json
{
  "couches_20250103_1430": {
    "positions": {
      "RS-01": {"x": 100, "y": 150},
      "RS-02": {"x": 300, "y": 150},
      "RO-01": {"x": 200, "y": 550}
    },
    "saved_at": "2025-01-03T14:30:00",
    "node_count": 15
  }
}
```

**Emplacement :**
- Même dossier que `app.py`
- Créé automatiquement au premier enregistrement

**Backup :**
- Copiez ce fichier pour sauvegarder vos layouts
- Restaurez-le pour récupérer vos layouts sur une autre machine

---

## 🎓 Résumé

| Action | Bouton | Résultat |
|--------|--------|----------|
| Créer layout couches | 📊 En couches | Stratégique/Opérationnel |
| Créer layout catégories | 🗂️ Par catégories | Grille 2x2 |
| Charger un layout | 📂 Charger | Positions restaurées |
| Supprimer un layout | 🗑️ Supprimer | Layout effacé |
| Retour auto | 🔄 Réinitialiser | Organisation automatique |

---

## 🚀 Prochaines améliorations (Phases 2-3)

### Phase 2
- ✅ Sauvegarde manuelle des positions
- ✅ Export/import de layouts en JSON
- ✅ Layouts "intelligents" pour nouveaux nœuds

### Phase 3
- ✅ Stockage dans Neo4j
- ✅ Partage entre utilisateurs
- ✅ Layouts par défaut organisationnels
- ✅ Historique des layouts

---

**🎯 Profitez de vos layouts sauvegardés !**
