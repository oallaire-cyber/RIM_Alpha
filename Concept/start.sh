#!/bin/bash
# ============================================
#  Risk Influence Map - Script de démarrage
# ============================================

echo ""
echo "🎯 Risk Influence Map - Démarrage"
echo "================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "[INFO] Création de l'environnement virtuel..."
    python3 -m venv venv
    
    echo "[INFO] Activation de l'environnement..."
    source venv/bin/activate
    
    echo "[INFO] Installation des dépendances..."
    pip install -r requirements.txt
else
    echo "[INFO] Activation de l'environnement existant..."
    source venv/bin/activate
fi

echo ""
echo "[INFO] Vérification de Neo4j..."
if ! docker ps | grep -q "neo4j-risk-map"; then
    echo "[WARN] Neo4j n'est pas démarré."
    echo "[INFO] Démarrage de Neo4j via Docker Compose..."
    docker-compose up -d
    echo "[INFO] Attente du démarrage de Neo4j (30 secondes)..."
    sleep 30
fi

echo ""
echo "[INFO] Lancement de l'application Streamlit..."
echo "[INFO] L'application s'ouvrira dans votre navigateur."
echo "[INFO] Pour arrêter: Ctrl+C"
echo ""

streamlit run app.py --server.headless true
