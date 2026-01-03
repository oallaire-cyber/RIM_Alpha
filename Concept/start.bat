@echo off
REM ============================================
REM  Risk Influence Map - Script de démarrage
REM ============================================

echo.
echo  🎯 Risk Influence Map - Demarrage
echo  ================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    
    echo [INFO] Activation de l'environnement...
    call venv\Scripts\activate.bat
    
    echo [INFO] Installation des dependances...
    pip install -r requirements.txt
) else (
    echo [INFO] Activation de l'environnement existant...
    call venv\Scripts\activate.bat
)

echo.
echo [INFO] Verification de Neo4j...
docker ps | findstr "neo4j-risk-map" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Neo4j n'est pas demarre.
    echo [INFO] Demarrage de Neo4j via Docker Compose...
    docker-compose up -d
    echo [INFO] Attente du demarrage de Neo4j (30 secondes)...
    timeout /t 30 /nobreak >nul
)

echo.
echo [INFO] Lancement de l'application Streamlit...
echo [INFO] L'application s'ouvrira dans votre navigateur.
echo [INFO] Pour arreter: Ctrl+C
echo.

streamlit run app.py --server.headless true

pause
