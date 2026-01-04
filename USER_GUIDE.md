# Risk Influence Map - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Managing Risks](#managing-risks)
5. [Managing Influences](#managing-influences)
6. [Visualization](#visualization)
7. [Analytics](#analytics)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Introduction

The Risk Influence Map (RIM) is a dynamic risk management tool that helps you visualize and analyze risks and their interdependencies. Unlike traditional risk registers, RIM uses graph database technology to model complex relationships between risks, enabling cascade impact analysis and strategic decision-making.

### Key Concepts

**Risk**: A potential event or condition that could impact your objectives. Each risk has:
- Name (unique identifier)
- Category (type of risk)
- Probability (1-10 scale)
- Impact (1-10 scale)
- Score (automatically calculated as Probability × Impact)
- Status (Active, Monitored, Mitigated, Closed)
- Description

**Influence**: A directional relationship between two risks showing how one risk affects another. Types include:
- **AMPLIFIES**: One risk increases the probability or impact of another
- **TRIGGERS**: One risk directly causes another to occur
- **MITIGATES**: One risk reduces the probability or impact of another
- **CORRELATES**: Two risks tend to occur together

## Getting Started

### First Time Setup

1. **Start the Application**
   - Windows: Double-click `start.bat`
   - Linux/Mac: Run `./start.sh`
   
2. **Access Neo4j Browser** (optional for data loading)
   - Navigate to `http://localhost:7474`
   - Login with username: `neo4j`, password: `risk2024secure`
   
3. **Load Demo Data** (optional)
   - Copy the contents of `demo_data.cypher`
   - Paste into Neo4j Browser and execute

4. **Access RIM Application**
   - The application automatically opens at `http://localhost:8501`
   - If not, manually navigate to this address

### Navigation

The application has five main sections accessible from the sidebar:

- **Dashboard**: Overview and quick statistics
- **Visualization**: Interactive graph view
- **Risks**: Create, view, edit, and delete risks
- **Influences**: Manage relationships between risks
- **Analytics**: Statistics and insights

## Dashboard Overview

The dashboard provides a high-level view of your risk landscape:

### Key Metrics

- **Total Risks**: Number of risks in the system
- **Total Influences**: Number of relationships between risks
- **Average Score**: Mean risk score across all risks

### Quick Visualization

The dashboard includes a preview of the risk network graph.

## Managing Risks

### Viewing Risks

1. Navigate to the **Risks** tab
2. Select **View Risks** sub-tab
3. All risks are displayed in a table format with sortable columns

### Creating a New Risk

1. Navigate to **Risks** → **Add Risk**
2. Fill in the required fields:
   - **Risk Name**: Unique identifier (e.g., "Data Breach", "Supply Chain Disruption")
   - **Category**: Select from the dropdown
   - **Probability**: Use slider (1-10, where 10 = most likely)
   - **Impact**: Use slider (1-10, where 10 = most severe)
   - **Status**: Select current status
   - **Description**: Provide detailed context
3. Click **Create Risk**

**Tips**:
- Use clear, specific names that distinguish risks from each other
- Be consistent with probability and impact scales
- Include context in descriptions for future reference

### Editing a Risk

1. Navigate to **Risks** → **Edit/Delete Risk**
2. Select the risk to edit from the dropdown
3. Modify any fields
4. Click **Update Risk**

**Note**: The risk score is automatically recalculated based on probability × impact.

### Deleting a Risk

1. Navigate to **Risks** → **Edit/Delete Risk**
2. Select the risk to delete
3. Click the **Delete Risk** button in the right column
4. The risk and all its relationships will be permanently removed

**Warning**: This action cannot be undone. All influences to and from this risk will also be deleted.

## Managing Influences

### Viewing Influences

1. Navigate to the **Influences** tab
2. Select **View Influences** sub-tab
3. All relationships are displayed showing source, target, type, and strength

### Creating an Influence

1. Navigate to **Influences** → **Add Influence**
2. Select:
   - **Source Risk**: The risk that influences another
   - **Target Risk**: The risk being influenced
   - **Influence Type**: How the source affects the target
   - **Strength**: Intensity of the influence (1-10)
   - **Description**: Explain the relationship
3. Click **Create Influence**

**Examples**:

**TRIGGERS Relationship**:
- Source: "Phishing Attack"
- Target: "Credential Compromise"
- Type: TRIGGERS
- Strength: 9
- Description: "Successful phishing directly leads to credential theft"

**AMPLIFIES Relationship**:
- Source: "System Downtime"
- Target: "Reputation Damage"
- Type: AMPLIFIES
- Strength: 7
- Description: "Extended outages increase negative public perception"

**MITIGATES Relationship**:
- Source: "Security Training"
- Target: "Phishing Attack"
- Type: MITIGATES
- Strength: 6
- Description: "Regular training reduces susceptibility to phishing"

**CORRELATES Relationship**:
- Source: "Economic Downturn"
- Target: "Budget Cuts"
- Type: CORRELATES
- Strength: 8
- Description: "These risks tend to occur together"

### Deleting an Influence

1. Navigate to **Influences** → **Delete Influence**
2. Select the relationship to remove
3. Click **Delete Influence**

## Visualization

The visualization tab provides an interactive graph view of your risk network.

### Understanding the Graph

**Nodes (Circles)**:
- Size: Proportional to risk score (larger = higher risk)
- Color: Either by category or score (toggle in options)
- Label: Risk name

**Edges (Arrows)**:
- Direction: Shows which risk influences which
- Width: Proportional to influence strength
- Color: Indicates influence type
  - Red: AMPLIFIES
  - Orange: TRIGGERS
  - Green: MITIGATES
  - Blue: CORRELATES

### Interaction

- **Pan**: Click and drag the background
- **Zoom**: Use mouse wheel
- **Select Node**: Click on any risk
- **Move Node**: Drag individual risks to rearrange
- **Hover**: View details in tooltip

### Visualization Options

**Color By Category**: Shows risk types at a glance
- Cyber (Red)
- Operational (Teal)
- Strategic (Blue)
- Financial (Light Orange)
- Compliance (Light Green)
- Reputation (Yellow)
- HR (Purple)
- Environmental (Light Blue)

**Color By Score**: Shows risk severity
- Red: High risk (score ≥ 70)
- Orange: Medium risk (40-69)
- Green: Low risk (< 40)

### Reading the Graph

**Identifying High-Impact Risks**:
- Look for large nodes (high score)
- Look for nodes with many outgoing arrows (influences many others)
- Look for nodes with many incoming arrows (influenced by many others)

**Understanding Risk Chains**:
- Follow arrows to see cascade effects
- Example: Phishing → Credential Compromise → Lateral Movement → Data Breach

**Spotting Vulnerabilities**:
- Dense clusters may indicate concentrated risk areas
- Long chains show potential for cascading failures

## Analytics

The Analytics tab provides statistical insights and rankings.

### Top Influencing Risks

Shows risks that have the most outgoing influences, helping identify:
- Trigger points for cascading failures
- Risks that amplify other risks
- Strategic intervention points

### Most Influenced Risks

Shows risks with the most incoming influences, indicating:
- Vulnerability to other risks
- Potential impact points
- Risks requiring robust mitigation

### Risk Distribution

Bar chart showing the number of risks in each category, useful for:
- Understanding risk portfolio balance
- Identifying concentration areas
- Resource allocation decisions

## Best Practices

### Risk Naming

✅ **Good**: "Ransomware Attack on Production Systems"
❌ **Bad**: "Cyber Risk #1"

✅ **Good**: "Key Supplier Bankruptcy"
❌ **Bad**: "Supplier Issue"

### Probability and Impact Scoring

Use a consistent scale across all risks:

**Probability (Likelihood)**:
- 1-2: Very unlikely (< 5% chance)
- 3-4: Unlikely (5-25% chance)
- 5-6: Possible (25-50% chance)
- 7-8: Likely (50-75% chance)
- 9-10: Very likely (> 75% chance)

**Impact (Severity)**:
- 1-2: Negligible (minimal impact)
- 3-4: Minor (limited impact, quick recovery)
- 5-6: Moderate (significant but manageable)
- 7-8: Major (severe impact, extended recovery)
- 9-10: Critical (catastrophic, threatens viability)

### Modeling Influences

**Be Specific**: Explain how and why risks influence each other

**Use Appropriate Types**:
- TRIGGERS: Direct causation (A always/often causes B)
- AMPLIFIES: Increases probability or impact (A makes B worse)
- MITIGATES: Decreases probability or impact (A reduces B)
- CORRELATES: Associated but not causal (A and B occur together)

**Set Realistic Strengths**:
- 1-3: Weak influence
- 4-6: Moderate influence
- 7-9: Strong influence
- 10: Extremely strong, near-certain influence

### Regular Maintenance

- **Review Monthly**: Update risk status and scores
- **Archive Closed Risks**: Keep the graph relevant
- **Document Changes**: Use descriptions to track evolution
- **Validate Influences**: Remove outdated relationships

### Strategic Use Cases

**Scenario Planning**:
Model different strategic decisions as risks and their influences to compare outcomes.

**Investment Prioritization**:
Identify high-leverage mitigation points by analyzing influence patterns.

**Communication**:
Use visualizations in presentations to stakeholders for clearer risk communication.

## Troubleshooting

### Neo4j Connection Issues

**Problem**: "Cannot connect to Neo4j database"

**Solutions**:
1. Ensure Docker is running
2. Check Neo4j is started: `docker ps`
3. Restart Neo4j: `docker-compose restart`
4. Verify connection at `http://localhost:7474`

### Application Won't Start

**Problem**: Streamlit fails to launch

**Solutions**:
1. Check Python is installed: `python --version`
2. Verify dependencies: `pip install -r requirements.txt`
3. Check port 8501 is available
4. Review terminal output for error messages

### Graph Not Displaying

**Problem**: Visualization shows blank or errors

**Solutions**:
1. Ensure you have created risks first
2. Refresh the page
3. Check browser console for JavaScript errors
4. Try a different browser

### Performance Issues

**Problem**: Application is slow

**Solutions**:
1. Limit the number of risks displayed (< 100 recommended for visualization)
2. Increase Neo4j memory in `docker-compose.yml`
3. Close other resource-intensive applications
4. Consider archiving old/closed risks

### Data Loss Concerns

**Problem**: Worried about losing data

**Solutions**:
1. Neo4j data is persisted in Docker volumes
2. Export data regularly using Neo4j Browser
3. Backup Docker volumes: `docker cp neo4j-rim:/data ./backup`
4. Document important risks in external systems

### Getting Help

If you encounter issues not covered here:

1. Check the project README.md
2. Review SETUP.md for installation details
3. Open an issue on the GitHub repository
4. Contact the development team

---

## Appendix: Keyboard Shortcuts

When in Neo4j Browser:
- `Ctrl + Enter`: Execute query
- `Ctrl + Up/Down`: Navigate command history

When in Streamlit:
- `R`: Rerun application
- `C`: Clear cache
- `?`: Show keyboard shortcuts

---

**Version**: 1.0  
**Last Updated**: January 2025  
**For**: Risk Influence Map POC
