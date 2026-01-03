# 🚀 Installation et démarrage - Risk Influence Map Phase 1

Guide d'installation rapide pour démarrer l'application Risk Influence Map.

## 📋 Prérequis

1. **Docker Desktop**
   - Windows/Mac : [Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux : [Installer Docker Engine](https://docs.docker.com/engine/install/)

2. **Python 3.9+**
   - Windows/Mac : [Télécharger Python](https://www.python.org/downloads/)
   - Linux : `sudo apt-get install python3 python3-pip`

3. **Git** (optionnel, pour cloner le repo)
   - [Télécharger Git](https://git-scm.com/downloads)

## 🛠️ Installation

### Méthode 1 : Démarrage automatique (recommandé)

#### Sur Windows :
```cmd
# 1. Ouvrir un terminal dans le dossier du projet
cd "D:\Users\oalla\OneDrive\Documents\Projects\RIM Alpha"

# 2. Installer les dépendances Python
pip install -r requirements_phase1.txt

# 3. Lancer l'application (démarre Neo4j automatiquement)
start.bat
```

#### Sur Linux/Mac :
```bash
# 1. Ouvrir un terminal dans le dossier du projet
cd ~/path/to/RIM_Alpha

# 2. Installer les dépendances Python
pip3 install -r requirements_phase1.txt

# 3. Rendre le script exécutable (une seule fois)
chmod +x start.sh

# 4. Lancer l'application
./start.sh
```

### Méthode 2 : Démarrage manuel (contrôle total)

#### 1. Démarrer Neo4j
```bash
# Avec Docker Compose
docker-compose up -d

# Vérifier que Neo4j est démarré
docker ps
```

#### 2. Attendre l'initialisation (10 secondes)
```bash
# Linux/Mac
sleep 10

# Windows
timeout /t 10
```

#### 3. Charger les données de démo (optionnel)
```bash
# Ouvrir Neo4j Browser
# http://localhost:7474
# Login: neo4j / risk2024secure

# Copier-coller le contenu de demo_data_loader.cypher
# Exécuter section par section
```

#### 4. Lancer Streamlit
```bash
# Linux/Mac
python3 -m streamlit run app_phase1.py

# Windows
python -m streamlit run app_phase1.py
```

## 🔗 Accès aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Application Streamlit** | http://localhost:8501 | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j / risk2024secure |

## 📊 Charger les données de démo

### Via Neo4j Browser (recommandé)

1. Ouvrir [http://localhost:7474](http://localhost:7474)
2. Se connecter : `neo4j` / `risk2024secure`
3. Ouvrir le fichier `demo_data_loader.cypher`
4. Copier-coller chaque section et exécuter

### Via cypher-shell

```bash
# Linux/Mac
docker exec -it neo4j-risk-map cypher-shell -u neo4j -p risk2024secure < demo_data_loader.cypher

# Windows (depuis WSL ou Git Bash)
cat demo_data_loader.cypher | docker exec -i neo4j-risk-map cypher-shell -u neo4j -p risk2024secure
```

## 🛑 Arrêter l'application

### Arrêter Streamlit
- **Windows** : Fermer la fenêtre ou appuyer sur `Ctrl+C`
- **Linux/Mac** : Appuyer sur `Ctrl+C`

### Arrêter Neo4j
```bash
docker-compose down
```

### Tout arrêter et nettoyer
```bash
# Arrêter et supprimer les conteneurs
docker-compose down

# Supprimer également les volumes (⚠️ efface les données)
docker-compose down -v
```

## 🔧 Dépannage

### Problème : "Docker n'est pas installé"
**Solution** : Installer Docker Desktop et le démarrer

### Problème : "Port 7474 ou 7687 déjà utilisé"
**Solution** :
```bash
# Voir quel processus utilise le port
# Linux/Mac
lsof -i :7474
lsof -i :7687

# Windows
netstat -ano | findstr :7474
netstat -ano | findstr :7687

# Arrêter l'ancien conteneur Neo4j
docker stop neo4j-risk-map
docker rm neo4j-risk-map
```

### Problème : "streamlit: command not found"
**Solution** :
```bash
# Réinstaller les dépendances
pip install -r requirements_phase1.txt

# Ou installer Streamlit directement
pip install streamlit
```

### Problème : Neo4j ne démarre pas
**Solution** :
```bash
# Voir les logs Docker
docker-compose logs neo4j

# Redémarrer proprement
docker-compose down
docker-compose up -d
```

### Problème : "Cannot connect to Neo4j"
**Solution** :
1. Vérifier que Neo4j est bien démarré : `docker ps`
2. Attendre 10-15 secondes après le démarrage
3. Vérifier les identifiants dans l'application : `neo4j` / `risk2024secure`

## 📁 Structure du projet

```
RIM_Alpha/
├── app_phase1.py              # Application Streamlit Phase 1
├── requirements_phase1.txt    # Dépendances Python
├── docker-compose.yml         # Configuration Docker Neo4j
├── demo_data_loader.cypher    # Données de démo
├── start.bat                  # Script de démarrage Windows
├── start.sh                   # Script de démarrage Linux/Mac
├── README_PHASE1.md           # Documentation Phase 1
└── INSTALLATION.md            # Ce fichier
```

## 💡 Conseils

### Développement
- Utilisez `start.bat` ou `start.sh` pour un démarrage rapide
- Les données Neo4j persistent dans un volume Docker
- Streamlit se recharge automatiquement quand vous modifiez le code

### Production
- Changez le mot de passe Neo4j dans `docker-compose.yml`
- Configurez des volumes externes pour les backups
- Utilisez un reverse proxy (nginx) pour l'accès web

### Performance
- Ajustez la mémoire Neo4j dans `docker-compose.yml` si besoin
- Pour un gros dataset (>1000 risques), augmentez `heap_max_size`

## 📞 Support

Pour toute question ou problème :
1. Consultez le fichier `RIM_Demo_Preparation_Guide.docx`
2. Vérifiez les logs : `docker-compose logs`
3. Contactez l'équipe du programme

---

**Bon démarrage avec Risk Influence Map ! 🎯**
