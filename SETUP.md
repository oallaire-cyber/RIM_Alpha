# Risk Influence Map - Setup Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Detailed Setup Instructions](#detailed-setup-instructions)
4. [Configuration Options](#configuration-options)
5. [Data Management](#data-management)
6. [Deployment Considerations](#deployment-considerations)
7. [Security Notes](#security-notes)

## System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 2 GB free space
- **Docker**: Version 20.10+ with Docker Compose
- **Python**: Version 3.9, 3.10, or 3.11
- **Browser**: Chrome 90+, Firefox 88+, or Safari 14+

### Recommended Setup

- **RAM**: 16 GB for handling large risk networks
- **CPU**: Multi-core processor for better Neo4j performance
- **SSD**: For faster Docker volume operations

### Network Requirements

- Ports 7474 (HTTP), 7687 (Bolt), and 8501 (Streamlit) must be available
- Internet connection for initial Docker image downloads

## Installation Methods

### Method 1: Quick Start (Recommended)

Best for: Demos, POC, local development

```bash
# Clone or download the repository
git clone https://github.com/your-org/RIM_Alpha.git
cd RIM_Alpha

# Run the startup script
# Windows:
start.bat

# Linux/Mac:
chmod +x start.sh
./start.sh
```

### Method 2: Manual Setup

Best for: Custom configurations, troubleshooting

See [Detailed Setup Instructions](#detailed-setup-instructions) below.

### Method 3: Docker-Only Deployment

Best for: Server deployments, containerized environments

See [Deployment Considerations](#deployment-considerations) below.

## Detailed Setup Instructions

### Step 1: Install Prerequisites

#### Install Docker

**Windows/Mac**:
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and launch Docker Desktop
3. Verify installation: `docker --version`

**Linux (Ubuntu/Debian)**:
```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io docker-compose

# Add user to docker group (optional, avoids sudo)
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

#### Install Python

**Windows**:
1. Download Python from https://www.python.org/downloads/
2. Run installer, **check "Add Python to PATH"**
3. Verify: `python --version`

**Mac** (using Homebrew):
```bash
brew install python@3.11
python3 --version
```

**Linux**:
```bash
sudo apt-get install python3.11 python3-pip python3-venv
python3 --version
```

### Step 2: Set Up the Project

#### Download Project Files

**Option A: Git Clone**
```bash
git clone https://github.com/your-org/RIM_Alpha.git
cd RIM_Alpha
```

**Option B: Direct Download**
1. Download ZIP from GitHub
2. Extract to desired location
3. Open terminal in extracted folder

#### Create Python Virtual Environment

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Streamlit (web interface)
- Neo4j driver (database connection)
- PyVis (graph visualization)
- Pandas (data manipulation)

### Step 3: Start Neo4j Database

#### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This creates:
- Neo4j container named `neo4j-rim`
- Persistent data volume `neo4j_data`
- Network bridge for communication

#### Manual Docker Command

```bash
docker run -d \
    --name neo4j-rim \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/risk2024secure \
    -v neo4j_rim_data:/data \
    neo4j:latest
```

#### Verify Neo4j is Running

1. Wait 10-15 seconds for startup
2. Access Neo4j Browser: http://localhost:7474
3. Login:
   - Username: `neo4j`
   - Password: `risk2024secure`
4. You should see the Neo4j interface

### Step 4: Load Demo Data (Optional)

1. Open Neo4j Browser (http://localhost:7474)
2. Open `demo_data.cypher` file
3. Copy all contents
4. Paste into Neo4j Browser query box
5. Click the play button (▶) or press Ctrl+Enter
6. Verify: `MATCH (n) RETURN count(n)` should return > 0

### Step 5: Launch RIM Application

```bash
streamlit run app.py
```

The application should automatically open in your browser at http://localhost:8501

## Configuration Options

### Environment Variables

Create a `.env` file in the project root:

```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=risk2024secure

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

Load with:
```bash
pip install python-dotenv
```

### Neo4j Configuration

Edit `docker-compose.yml` to customize Neo4j:

```yaml
environment:
  # Memory allocation
  - NEO4J_dbms_memory_heap_initial__size=512m
  - NEO4J_dbms_memory_heap_max__size=2G
  - NEO4J_dbms_memory_pagecache_size=512m
  
  # Enable plugins
  - NEO4J_PLUGINS=["apoc", "graph-data-science"]
  
  # Security (change these!)
  - NEO4J_AUTH=neo4j/your_secure_password
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
```

## Data Management

### Backup Neo4j Data

#### Method 1: Export to Cypher

1. Open Neo4j Browser
2. Run: `CALL apoc.export.cypher.all("backup.cypher", {})`
3. Find file in Neo4j container's import folder

#### Method 2: Docker Volume Backup

```bash
# Create backup directory
mkdir -p ./backups

# Copy data from Docker volume
docker run --rm \
  -v neo4j_data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu tar czf /backup/neo4j_backup_$(date +%Y%m%d).tar.gz /data
```

### Restore Neo4j Data

#### From Cypher File

1. Copy backup.cypher to project folder
2. Neo4j Browser: `CALL apoc.cypher.runFile("backup.cypher")`

#### From Docker Volume

```bash
# Stop Neo4j
docker-compose down

# Restore from backup
docker run --rm \
  -v neo4j_data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu bash -c "cd / && tar xzf /backup/neo4j_backup_YYYYMMDD.tar.gz"

# Restart Neo4j
docker-compose up -d
```

### Export to CSV

Use Neo4j Browser:

```cypher
// Export all risks
CALL apoc.export.csv.query(
  "MATCH (r:Risk) RETURN r.name, r.category, r.probability, r.impact, r.score, r.status",
  "risks_export.csv",
  {}
)

// Export all influences
CALL apoc.export.csv.query(
  "MATCH (r1:Risk)-[i:INFLUENCES]->(r2:Risk) 
   RETURN r1.name as source, r2.name as target, i.type, i.strength",
  "influences_export.csv",
  {}
)
```

## Deployment Considerations

### Production Deployment

**⚠️ Important**: This is a POC. For production use, implement:

1. **Security**:
   - Change default passwords
   - Enable HTTPS/SSL
   - Implement authentication
   - Network segmentation

2. **Scalability**:
   - Use Neo4j Enterprise for clustering
   - Increase memory allocations
   - Consider load balancing for Streamlit

3. **Reliability**:
   - Automated backups
   - Monitoring and alerting
   - High availability setup

### Server Deployment Example

**Docker Compose with Reverse Proxy**:

```yaml
version: '3.8'

services:
  neo4j:
    # ... (same as before)
    networks:
      - backend
    restart: always

  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
    depends_on:
      - neo4j
    networks:
      - backend
      - frontend
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - streamlit
    networks:
      - frontend
    restart: always

networks:
  backend:
  frontend:
```

### Cloud Deployment

**AWS**:
- EC2 instance with Docker
- RDS for Neo4j (if using Neo4j Aura)
- ELB for load balancing

**Azure**:
- Azure Container Instances
- Azure Cosmos DB (with Gremlin API as alternative)
- Application Gateway

**GCP**:
- Google Kubernetes Engine
- Cloud Run for Streamlit
- Neo4j Aura for database

## Security Notes

### Default Credentials

**⚠️ CHANGE IMMEDIATELY FOR PRODUCTION**:
- Neo4j password: `risk2024secure` → Use strong password
- Exposed ports: Lock down firewall rules

### Best Practices

1. **Authentication**:
   ```python
   # Add to app.py for basic auth
   import streamlit_authenticator as stauth
   ```

2. **Network Security**:
   - Use VPN for remote access
   - Restrict Neo4j ports to localhost
   - Use HTTPS for Streamlit

3. **Data Protection**:
   - Encrypt sensitive risk descriptions
   - Implement role-based access
   - Audit logs for changes

4. **Container Security**:
   - Use specific image versions (not `:latest`)
   - Scan images for vulnerabilities
   - Run containers as non-root user

### Environment-Specific Security

**Development**:
- Default passwords OK
- Open ports acceptable
- No encryption required

**Staging/Testing**:
- Unique passwords
- Limited port exposure
- Basic encryption

**Production**:
- Strong, unique passwords
- Firewall rules strictly enforced
- Full encryption (at rest and in transit)
- Regular security audits
- Compliance requirements met

## Troubleshooting Setup Issues

### Docker Issues

**Problem**: "Cannot connect to Docker daemon"
```bash
# Linux: Start Docker service
sudo systemctl start docker

# Windows/Mac: Launch Docker Desktop
```

**Problem**: Port already in use
```bash
# Find process using port
# Windows:
netstat -ano | findstr :7474
taskkill /PID <process_id> /F

# Linux/Mac:
lsof -i :7474
kill -9 <process_id>
```

### Python Issues

**Problem**: ModuleNotFoundError
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem**: Permission denied
```bash
# Linux/Mac: Use sudo or check permissions
sudo chmod +x start.sh
```

### Neo4j Issues

**Problem**: Neo4j fails to start
```bash
# Check logs
docker logs neo4j-rim

# Remove and recreate
docker-compose down -v
docker-compose up -d
```

**Problem**: Authentication failed
- Ensure password matches `NEO4J_AUTH` in docker-compose.yml
- Clear browser cache
- Try incognito/private window

## Next Steps

After successful setup:

1. Review [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
2. Load demo data to explore features
3. Create your first custom risks
4. Configure for your specific use case

## Support

For setup assistance:
- Check existing GitHub issues
- Review documentation
- Contact development team

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Maintained by**: RIM Development Team
