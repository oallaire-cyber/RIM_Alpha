# 📍 Guide : Figer les nœuds du graphe

## 🎯 Fonctionnalité

La Risk Influence Map permet maintenant de **figer les nœuds** à des positions fixes après les avoir déplacés manuellement.

## 🔧 Comment utiliser

### Étape 1 : Organiser le graphe avec la physique active

1. Laissez la case **"🔄 Physique active"** cochée (par défaut)
2. Le graphe s'organise automatiquement avec un algorithme de force
3. Les nœuds bougent pour optimiser la lisibilité

### Étape 2 : Positionner manuellement les nœuds

Avec la physique active, vous pouvez :
- **Glisser-déposer** n'importe quel nœud
- Les autres nœuds s'ajustent automatiquement
- Organisez comme vous voulez

### Étape 3 : Figer les positions

1. **Décochez** la case "🔄 Physique active"
2. Le graphe se fige instantanément
3. Les nœuds restent exactement où vous les avez mis
4. Vous pouvez encore les déplacer individuellement

### Étape 4 : Réactiver la physique (optionnel)

Si vous voulez relancer l'organisation automatique :
- **Recochez** "🔄 Physique active"
- Le graphe se réorganise

## 💡 Cas d'usage

### Pour une démo

```
1. Cochez "Physique active"
2. Laissez le graphe se stabiliser (10-15 secondes)
3. Ajustez manuellement les nœuds importants
4. Décochez "Physique active"
5. Votre graphe est prêt pour la présentation !
```

### Pour un rapport figé

```
1. Organisez avec physique active
2. Décochez "Physique active"
3. Faites des captures d'écran
4. Le layout reste identique entre captures
```

### Pour comparer deux états

```
1. Créez un arrangement optimal
2. Décochez "Physique active"
3. Modifiez les filtres (ex: seulement Strategic)
4. Les nœuds restant gardent leur position
5. Facile de comparer !
```

## 🎨 Astuces

### Astuce 1 : Layout en couches

```
Avec physique désactivée, créez un layout en couches :

Niveau Strategic (en haut)
─────────────────────────────
    RS-01    RS-02    RS-03

           ↓    ↓    ↓

Niveau Operational (en bas)
─────────────────────────────
RO-01  RO-02  RO-03  RO-04
```

### Astuce 2 : Grouper par catégories

```
Organisez visuellement par catégories :

┌──────────────┐  ┌──────────────┐
│  Programme   │  │   Produit    │
│              │  │              │
│  RS-01       │  │  RS-03       │
│  RO-01       │  │  RO-05       │
└──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐
│ Industriel   │  │Supply Chain  │
│              │  │              │
│  RS-07       │  │  RS-05       │
│  RO-03       │  │  RO-01       │
└──────────────┘  └──────────────┘
```

### Astuce 3 : Chemin critique en ligne

```
Pour montrer un chemin d'influence :

RO-01 → RS-02 → RS-01

Alignez ces 3 nœuds horizontalement
Les autres en périphérie
```

## ⚙️ Paramètres techniques

### Physique active (par défaut)

```javascript
"physics": {
    "enabled": true,
    "solver": "forceAtlas2Based",
    // Les nœuds se repoussent et attirent
}
```

**Comportement :**
- Les nœuds bougent continuellement
- S'organisent pour minimiser les croisements
- Difficile à figer visuellement

### Physique désactivée

```javascript
"physics": {
    "enabled": false
    // Les nœuds ne bougent plus automatiquement
}
```

**Comportement :**
- Les nœuds restent où vous les mettez
- Parfait pour présentation
- Vous gardez le contrôle total

## 🚫 Limitations connues

### ⚠️ Positions non sauvegardées

**Important :** Les positions des nœuds ne sont **PAS sauvegardées** dans Neo4j.

Si vous actualisez la page :
- Les positions sont perdues
- Le graphe se réorganise automatiquement

**Solution future (Phase 2-3) :**
- Bouton "Sauvegarder layout"
- Stockage des coordonnées (x, y) dans Neo4j
- Restauration automatique au chargement

### ⚠️ Changement de filtres

Si vous changez les filtres :
- Les nœuds qui disparaissent perdent leur position
- Les nouveaux nœuds apparaissent aléatoirement

**Astuce :** Organisez d'abord avec tous les filtres, puis filtrez.

## 🎯 Workflow recommandé pour démo

```bash
# 1. Préparer le graphe
☑ Charger toutes les données de démo
☑ Activer tous les filtres (tout afficher)
☑ Cocher "Physique active"
☑ Attendre stabilisation (15 secondes)

# 2. Organiser manuellement
☑ Identifier les nœuds clés (RS-01, RS-02, etc.)
☑ Les positionner stratégiquement
☑ Grouper visuellement par catégorie ou niveau

# 3. Figer
☑ Décocher "Physique active"
☑ Vérifier que tout est bien placé
☑ Ajuster si nécessaire

# 4. Démo
☑ Utiliser les filtres pour montrer différentes vues
☑ Les nœuds gardent leur position relative
☑ Navigation fluide
```

## 📊 Comparaison

| Critère | Physique ON | Physique OFF |
|---------|-------------|--------------|
| Organisation auto | ✅ Oui | ❌ Non |
| Positions fixes | ❌ Non | ✅ Oui |
| Contrôle manuel | ⚠️ Limité | ✅ Total |
| Pour exploration | ✅ Idéal | ❌ Difficile |
| Pour présentation | ❌ Instable | ✅ Parfait |
| Modifications | ✅ S'adapte | ⚠️ Manuel |

## 🎓 En résumé

**Utilisez la physique :**
- Pour explorer les données
- Pour découvrir les structures
- Quand vous ajoutez/supprimez des nœuds fréquemment

**Désactivez la physique :**
- Pour les démos
- Pour les captures d'écran
- Pour créer des layouts personnalisés
- Pour communiquer au board

---

**🎯 Bonne organisation de votre Risk Influence Map !**
