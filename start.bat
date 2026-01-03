@echo off
echo ========================================
echo Risk Influence Map - Demarrage
echo ========================================
echo.

REM Verification de Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Docker Desktop depuis https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [1/4] Verification de Docker... OK
echo.

REM Demarrage de Neo4j avec Docker Compose
echo [2/4] Demarrage de Neo4j...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERREUR] Impossible de demarrer Neo4j
    pause
    exit /b 1
)

echo Neo4j demarre... Attente de 10 secondes pour initialisation...
timeout /t 10 /nobreak >nul

echo [3/4] Neo4j demarre avec succes!
echo.
echo Neo4j Browser accessible sur: http://localhost:7474
echo Identifiants par defaut: neo4j / risk2024secure
echo.

REM Verification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [4/4] Lancement de l'application Streamlit...
echo.
echo ========================================
echo Application Risk Influence Map
echo ========================================
echo L'application va s'ouvrir dans votre navigateur...
echo Pour arreter l'application, fermez cette fenetre ou appuyez sur Ctrl+C
echo.

REM Lancement de Streamlit
streamlit run app_phase1.py

REM Si l'utilisateur ferme Streamlit, proposer d'arreter Neo4j
echo.
echo.
set /p STOP_NEO4J="Voulez-vous arreter Neo4j ? (o/n): "
if /i "%STOP_NEO4J%"=="o" (
    echo Arret de Neo4j...
    docker-compose down
    echo Neo4j arrete.
)

pause
