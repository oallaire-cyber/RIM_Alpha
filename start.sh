#!/bin/bash

echo "========================================"
echo "Risk Influence Map - Démarrage"
echo "========================================"
echo ""

# Vérification de Docker
if ! command -v docker &> /dev/null; then
    echo "[ERREUR] Docker n'est pas installé"
    echo "Veuillez installer Docker depuis https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "[1/4] Vérification de Docker... OK"
echo ""

# Démarrage de Neo4j avec Docker Compose
echo "[2/4] Démarrage de Neo4j..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "[ERREUR] Impossible de démarrer Neo4j"
    exit 1
fi

echo "Neo4j démarre... Attente de 10 secondes pour initialisation..."
sleep 10

echo "[3/4] Neo4j démarré avec succès!"
echo ""
echo "Neo4j Browser accessible sur: http://localhost:7474"
echo "Identifiants par défaut: neo4j / risk2024secure"
echo ""

# Vérification de Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERREUR] Python n'est pas installé"
    echo "Veuillez installer Python depuis https://www.python.org/downloads/"
    exit 1
fi

# Déterminer la commande Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "[4/4] Lancement de l'application Streamlit..."
echo ""
echo "========================================"
echo "Application Risk Influence Map"
echo "========================================"
echo "L'application va s'ouvrir dans votre navigateur..."
echo "Pour arrêter l'application, appuyez sur Ctrl+C"
echo ""

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    echo ""
    read -p "Voulez-vous arrêter Neo4j ? (o/n): " STOP_NEO4J
    if [ "$STOP_NEO4J" = "o" ] || [ "$STOP_NEO4J" = "O" ]; then
        echo "Arrêt de Neo4j..."
        docker-compose down
        echo "Neo4j arrêté."
    fi
    exit 0
}

# Capture du signal Ctrl+C
trap cleanup SIGINT SIGTERM

# Lancement de Streamlit
streamlit run app_phase1.py

# Si Streamlit se termine normalement
cleanup
