@echo off
REM Risk Influence Map - Startup Script (Windows)
REM This script starts the Neo4j database and launches the Streamlit application

echo.
echo ============================================
echo   Risk Influence Map - Starting...
echo ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Start Neo4j with docker-compose
echo [INFO] Starting Neo4j database...
if exist docker-compose.yml (
    docker-compose up -d
) else (
    echo [WARN] docker-compose.yml not found, starting Neo4j manually...
    docker run -d --name neo4j-rim -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/risk2024secure -v neo4j_rim_data:/data neo4j:latest
)

REM Wait for Neo4j to be ready
echo [INFO] Waiting for Neo4j to be ready...
timeout /t 10 /nobreak >nul

REM Check if Neo4j is accessible
curl -s http://localhost:7474 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Neo4j is running
) else (
    echo [ERROR] Neo4j failed to start properly
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Neo4j Browser: http://localhost:7474
echo   Username: neo4j
echo   Password: risk2024secure
echo ============================================
echo.

REM Check if Python virtual environment exists
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Virtual environment not found
    echo [TIP] Create one with: python -m venv venv
)

REM Check if dependencies are installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing Python dependencies...
    pip install -r requirements.txt
)

REM Launch Streamlit application
echo.
echo ============================================
echo   Launching Risk Influence Map...
echo ============================================
echo.
streamlit run app.py

REM Cleanup (optional - uncomment to stop Neo4j when closing)
REM docker-compose down

pause
