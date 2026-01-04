#!/bin/bash

# Risk Influence Map - Startup Script (Linux/Mac)
# This script starts the Neo4j database and launches the Streamlit application

echo "🎯 Starting Risk Influence Map..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Start Neo4j with docker-compose
echo "📦 Starting Neo4j database..."
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
else
    echo "⚠️  docker-compose.yml not found, starting Neo4j manually..."
    docker run -d \
        --name neo4j-rim \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/risk2024secure \
        -v neo4j_rim_data:/data \
        neo4j:latest
fi

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
sleep 10

# Check if Neo4j is accessible
if curl -s http://localhost:7474 > /dev/null; then
    echo "✅ Neo4j is running at http://localhost:7474"
else
    echo "❌ Neo4j failed to start properly"
    exit 1
fi

echo ""
echo "📊 Neo4j Browser: http://localhost:7474"
echo "   Username: neo4j"
echo "   Password: risk2024secure"
echo ""

# Check if Python virtual environment exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found"
    echo "💡 Tip: Create one with 'python -m venv venv'"
fi

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Launch Streamlit application
echo ""
echo "🚀 Launching Risk Influence Map application..."
echo ""
streamlit run app.py

# Cleanup function (called when script exits)
cleanup() {
    echo ""
    echo "👋 Shutting down..."
    # Uncomment to stop Neo4j when exiting:
    # docker-compose down
}

trap cleanup EXIT
