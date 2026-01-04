"""
Risk Influence Map (RIM) - Main Application
A Streamlit application for dynamic risk mapping and influence visualization using Neo4j
"""

import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
from typing import List, Dict, Tuple, Optional
import os
import tempfile

# Page configuration
st.set_page_config(
    page_title="Risk Influence Map",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
RISK_CATEGORIES = [
    "Cyber", "Operational", "Strategic", "Financial", 
    "Compliance", "Reputation", "HR", "Environmental"
]

RISK_STATUS = ["Active", "Monitored", "Mitigated", "Closed"]

INFLUENCE_TYPES = ["AMPLIFIES", "TRIGGERS", "MITIGATES", "CORRELATES"]

CATEGORY_COLORS = {
    "Cyber": "#FF6B6B",
    "Operational": "#4ECDC4",
    "Strategic": "#45B7D1",
    "Financial": "#FFA07A",
    "Compliance": "#98D8C8",
    "Reputation": "#F7DC6F",
    "HR": "#BB8FCE",
    "Environmental": "#85C1E2"
}

# Neo4j Connection Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "risk2024secure")


def safe_int(value, default=0):
    """
    Safely convert a value to integer, handling None, strings, and invalid values.
    
    Args:
        value: Value to convert (can be None, int, str, etc.)
        default: Default value if conversion fails
        
    Returns:
        int: Converted integer or default value
    """
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """
    Safely convert a value to float, handling None, strings, and invalid values.
    
    Args:
        value: Value to convert (can be None, float, str, etc.)
        default: Default value if conversion fails
        
    Returns:
        float: Converted float or default value
    """
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class Neo4jConnection:
    """Handle Neo4j database connections"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connection
            self.driver.verify_connectivity()
        except Exception as e:
            st.error(f"❌ Failed to connect to Neo4j: {str(e)}")
            st.info("Please ensure Neo4j is running and credentials are correct.")
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None):
        """Execute a Cypher query and return results"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            st.error(f"Query execution error: {str(e)}")
            return []


def safe_int(value, default: int = 0) -> int:
    """
    Safely convert a value to integer, handling None, strings, and invalid types.
    
    Args:
        value: Value to convert (can be int, str, None, etc.)
        default: Default value if conversion fails
    
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# Initialize connection
@st.cache_resource
def get_neo4j_connection():
    """Get cached Neo4j connection"""
    return Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)


def get_all_risks(conn: Neo4jConnection) -> List[Dict]:
    """Retrieve all risks from database"""
    query = """
    MATCH (r:Risk)
    RETURN r.name as name, r.category as category, 
           r.probability as probability, r.impact as impact,
           r.score as score, r.status as status, 
           r.description as description
    ORDER BY r.score DESC
    """
    return conn.execute_query(query)


def get_all_influences(conn: Neo4jConnection) -> List[Dict]:
    """Retrieve all influences from database"""
    query = """
    MATCH (r1:Risk)-[i:INFLUENCES]->(r2:Risk)
    RETURN r1.name as source, r2.name as target, 
           type(i) as relationship_type,
           i.type as influence_type, i.strength as strength, 
           i.description as description
    """
    return conn.execute_query(query)


def create_risk(conn: Neo4jConnection, name: str, category: str, 
                probability: int, impact: int, status: str, 
                description: str) -> bool:
    """Create a new risk in the database"""
    score = probability * impact
    query = """
    CREATE (r:Risk {
        name: $name,
        category: $category,
        probability: $probability,
        impact: $impact,
        score: $score,
        status: $status,
        description: $description
    })
    """
    parameters = {
        "name": name,
        "category": category,
        "probability": probability,
        "impact": impact,
        "score": score,
        "status": status,
        "description": description
    }
    
    result = conn.execute_query(query, parameters)
    return result is not None


def update_risk(conn: Neo4jConnection, original_name: str, name: str, 
                category: str, probability: int, impact: int, 
                status: str, description: str) -> bool:
    """Update an existing risk"""
    score = probability * impact
    query = """
    MATCH (r:Risk {name: $original_name})
    SET r.name = $name,
        r.category = $category,
        r.probability = $probability,
        r.impact = $impact,
        r.score = $score,
        r.status = $status,
        r.description = $description
    """
    parameters = {
        "original_name": original_name,
        "name": name,
        "category": category,
        "probability": probability,
        "impact": impact,
        "score": score,
        "status": status,
        "description": description
    }
    
    result = conn.execute_query(query, parameters)
    return result is not None


def delete_risk(conn: Neo4jConnection, name: str) -> bool:
    """Delete a risk and all its relationships"""
    query = """
    MATCH (r:Risk {name: $name})
    DETACH DELETE r
    """
    result = conn.execute_query(query, {"name": name})
    return result is not None


def create_influence(conn: Neo4jConnection, source: str, target: str, 
                     influence_type: str, strength: int, 
                     description: str) -> bool:
    """Create an influence relationship between two risks"""
    query = f"""
    MATCH (r1:Risk {{name: $source}})
    MATCH (r2:Risk {{name: $target}})
    CREATE (r1)-[i:INFLUENCES {{
        type: $influence_type,
        strength: $strength,
        description: $description
    }}]->(r2)
    """
    parameters = {
        "source": source,
        "target": target,
        "influence_type": influence_type,
        "strength": strength,
        "description": description
    }
    
    result = conn.execute_query(query, parameters)
    return result is not None


def delete_influence(conn: Neo4jConnection, source: str, target: str) -> bool:
    """Delete an influence relationship"""
    query = """
    MATCH (r1:Risk {name: $source})-[i:INFLUENCES]->(r2:Risk {name: $target})
    DELETE i
    """
    result = conn.execute_query(query, {"source": source, "target": target})
    return result is not None


def get_risk_statistics(conn: Neo4jConnection) -> Dict:
    """Get statistics about the risk network"""
    stats = {}
    
    # Total risks
    query_risks = "MATCH (r:Risk) RETURN count(r) as count"
    result = conn.execute_query(query_risks)
    stats['total_risks'] = result[0]['count'] if result else 0
    
    # Total influences
    query_influences = "MATCH ()-[i:INFLUENCES]->() RETURN count(i) as count"
    result = conn.execute_query(query_influences)
    stats['total_influences'] = result[0]['count'] if result else 0
    
    # Average risk score (only for non-null scores)
    query_avg = """
    MATCH (r:Risk)
    WHERE r.score IS NOT NULL
    RETURN avg(r.score) as avg_score
    """
    result = conn.execute_query(query_avg)
    avg_score = result[0]['avg_score'] if result and result[0]['avg_score'] is not None else 0
    stats['avg_score'] = round(avg_score, 2)
    
    # Risk distribution by category
    query_category = """
    MATCH (r:Risk)
    RETURN r.category as category, count(r) as count
    ORDER BY count DESC
    """
    stats['category_distribution'] = conn.execute_query(query_category)
    
    return stats


def visualize_risk_network(conn: Neo4jConnection, color_by: str = "category"):
    """Create an interactive network visualization"""
    # Get all risks and influences
    risks = get_all_risks(conn)
    influences = get_all_influences(conn)
    
    if not risks:
        st.warning("No risks found in the database. Please add some risks first.")
        return
    
    # Create network
    net = Network(height="600px", width="100%", bgcolor="#222222", 
                  font_color="white", directed=True)
    
    # Configure physics
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 200,
                "springConstant": 0.04
            }
        },
        "edges": {
            "smooth": {
                "type": "continuous"
            },
            "arrows": {
                "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                }
            }
        }
    }
    """)
    
    # Add nodes
    for risk in risks:
        name = risk['name']
        category = risk.get('category', 'Unknown')
        score = safe_int(risk.get('score'), 0)
        probability = safe_int(risk.get('probability'), 0)
        impact = safe_int(risk.get('impact'), 0)
        status = risk.get('status', 'Active')
        
        # Determine color
        if color_by == "category":
            color = CATEGORY_COLORS.get(category, "#95a5a6")
        else:  # color by score
            if score >= 70:
                color = "#e74c3c"  # High risk - Red
            elif score >= 40:
                color = "#f39c12"  # Medium risk - Orange
            else:
                color = "#27ae60"  # Low risk - Green
        
        # Size proportional to score (min 10, max 50)
        size = max(10, min(50, score // 2))
        
        # Create hover title
        title = f"""
        <b>{name}</b><br>
        Category: {category}<br>
        Score: {score} (P:{probability} × I:{impact})<br>
        Status: {status}
        """
        
        net.add_node(name, label=name, color=color, size=size, title=title)
    
    # Add edges
    for influence in influences:
        source = influence['source']
        target = influence['target']
        influence_type = influence.get('influence_type', 'INFLUENCES')
        
        # Safely convert strength to int
        strength = safe_int(influence.get('strength'), 5)
        
        # Edge width proportional to strength
        width = max(1, strength / 2)
        
        # Color by influence type
        edge_colors = {
            "AMPLIFIES": "#e74c3c",
            "TRIGGERS": "#e67e22",
            "MITIGATES": "#27ae60",
            "CORRELATES": "#3498db"
        }
        color = edge_colors.get(influence_type, "#95a5a6")
        
        title = f"{influence_type} (Strength: {strength})"
        
        net.add_edge(source, target, width=width, color=color, title=title)
    
    # Generate and display
    # Use temporary file for cross-platform compatibility
    temp_file = os.path.join(tempfile.gettempdir(), "risk_network.html")
    net.save_graph(temp_file)
    
    with open(temp_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    components.html(html_content, height=650)


def render_dashboard():
    """Render the main dashboard with statistics"""
    st.title("🎯 Risk Influence Map")
    st.markdown("Dynamic risk visualization and influence mapping")
    
    conn = get_neo4j_connection()
    
    if not conn.driver:
        st.error("Cannot connect to Neo4j database. Please check your configuration.")
        return
    
    # Get statistics
    stats = get_risk_statistics(conn)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Risks", stats['total_risks'])
    
    with col2:
        st.metric("🔗 Total Influences", stats['total_influences'])
    
    with col3:
        st.metric("📈 Average Score", stats['avg_score'])
    
    st.markdown("---")


def render_visualization_tab():
    """Render the visualization tab"""
    st.header("📊 Risk Network Visualization")
    
    conn = get_neo4j_connection()
    
    if not conn.driver:
        return
    
    # Visualization options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        color_option = st.radio(
            "Color nodes by:",
            ["category", "score"],
            horizontal=True
        )
    
    with col2:
        if st.button("🔄 Refresh Visualization"):
            st.rerun()
    
    # Display network
    visualize_risk_network(conn, color_by=color_option)
    
    # Legend
    with st.expander("📖 Legend"):
        st.markdown("""
        **Node Size**: Proportional to risk score
        
        **Node Colors** (when colored by category):
        """)
        for category, color in CATEGORY_COLORS.items():
            st.markdown(f'<span style="color:{color}">■</span> {category}', 
                       unsafe_allow_html=True)
        
        st.markdown("""
        **Node Colors** (when colored by score):
        - 🔴 Red: High risk (≥70)
        - 🟠 Orange: Medium risk (40-69)
        - 🟢 Green: Low risk (<40)
        
        **Edge Colors**:
        - 🔴 Red: AMPLIFIES
        - 🟠 Orange: TRIGGERS
        - 🟢 Green: MITIGATES
        - 🔵 Blue: CORRELATES
        
        **Edge Width**: Proportional to influence strength
        """)


def render_risks_tab():
    """Render the risks management tab"""
    st.header("🎯 Risk Management")
    
    conn = get_neo4j_connection()
    
    if not conn.driver:
        return
    
    # Create tabs for CRUD operations
    tab1, tab2, tab3 = st.tabs(["View Risks", "Add Risk", "Edit/Delete Risk"])
    
    with tab1:
        st.subheader("All Risks")
        risks = get_all_risks(conn)
        
        if risks:
            df = pd.DataFrame(risks)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No risks found. Create your first risk in the 'Add Risk' tab.")
    
    with tab2:
        st.subheader("Create New Risk")
        
        with st.form("create_risk_form"):
            name = st.text_input("Risk Name*", placeholder="e.g., Data Breach")
            category = st.selectbox("Category*", RISK_CATEGORIES)
            
            col1, col2 = st.columns(2)
            with col1:
                probability = st.slider("Probability", 1, 10, 5)
            with col2:
                impact = st.slider("Impact", 1, 10, 5)
            
            status = st.selectbox("Status", RISK_STATUS)
            description = st.text_area("Description", 
                                      placeholder="Describe the risk in detail...")
            
            submitted = st.form_submit_button("✅ Create Risk")
            
            if submitted:
                if not name:
                    st.error("Risk name is required")
                else:
                    success = create_risk(conn, name, category, probability, 
                                        impact, status, description)
                    if success:
                        st.success(f"✅ Risk '{name}' created successfully!")
                        st.balloons()
                    else:
                        st.error("Failed to create risk. It may already exist.")
    
    with tab3:
        st.subheader("Edit or Delete Risk")
        
        risks = get_all_risks(conn)
        if not risks:
            st.info("No risks available to edit.")
            return
        
        risk_names = [r['name'] for r in risks]
        selected_risk_name = st.selectbox("Select Risk", risk_names)
        
        # Get selected risk details
        selected_risk = next((r for r in risks if r['name'] == selected_risk_name), None)
        
        if selected_risk:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                with st.form("edit_risk_form"):
                    st.markdown("**Edit Risk Details**")
                    
                    new_name = st.text_input("Risk Name", value=selected_risk['name'])
                    category = st.selectbox("Category", RISK_CATEGORIES, 
                                          index=RISK_CATEGORIES.index(selected_risk.get('category', RISK_CATEGORIES[0])))
                    
                    col_p, col_i = st.columns(2)
                    with col_p:
                        probability = st.slider("Probability", 1, 10, 
                                              safe_int(selected_risk.get('probability'), 5))
                    with col_i:
                        impact = st.slider("Impact", 1, 10, 
                                         safe_int(selected_risk.get('impact'), 5))
                    
                    status = st.selectbox("Status", RISK_STATUS,
                                        index=RISK_STATUS.index(selected_risk.get('status', RISK_STATUS[0])))
                    description = st.text_area("Description", 
                                              value=selected_risk.get('description', ''))
                    
                    submitted = st.form_submit_button("💾 Update Risk")
                    
                    if submitted:
                        success = update_risk(conn, selected_risk_name, new_name, 
                                            category, probability, impact, 
                                            status, description)
                        if success:
                            st.success(f"✅ Risk updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update risk.")
            
            with col2:
                st.markdown("**Delete Risk**")
                if st.button("🗑️ Delete Risk", type="secondary"):
                    success = delete_risk(conn, selected_risk_name)
                    if success:
                        st.success(f"✅ Risk '{selected_risk_name}' deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete risk.")


def render_influences_tab():
    """Render the influences management tab"""
    st.header("🔗 Influence Management")
    
    conn = get_neo4j_connection()
    
    if not conn.driver:
        return
    
    tab1, tab2, tab3 = st.tabs(["View Influences", "Add Influence", "Delete Influence"])
    
    with tab1:
        st.subheader("All Influences")
        influences = get_all_influences(conn)
        
        if influences:
            df = pd.DataFrame(influences)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No influences found. Create your first influence in the 'Add Influence' tab.")
    
    with tab2:
        st.subheader("Create New Influence")
        
        risks = get_all_risks(conn)
        if len(risks) < 2:
            st.warning("You need at least 2 risks to create an influence.")
            return
        
        risk_names = [r['name'] for r in risks]
        
        with st.form("create_influence_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                source = st.selectbox("Source Risk*", risk_names, key="source")
            with col2:
                target = st.selectbox("Target Risk*", risk_names, key="target")
            
            influence_type = st.selectbox("Influence Type*", INFLUENCE_TYPES)
            strength = st.slider("Strength", 1, 10, 5)
            description = st.text_area("Description", 
                                      placeholder="Explain how the source influences the target...")
            
            submitted = st.form_submit_button("✅ Create Influence")
            
            if submitted:
                if source == target:
                    st.error("Source and target must be different risks")
                else:
                    success = create_influence(conn, source, target, 
                                             influence_type, strength, description)
                    if success:
                        st.success(f"✅ Influence created: {source} → {target}")
                        st.balloons()
                    else:
                        st.error("Failed to create influence.")
    
    with tab3:
        st.subheader("Delete Influence")
        
        influences = get_all_influences(conn)
        if not influences:
            st.info("No influences available to delete.")
            return
        
        # Create display strings for influences
        influence_options = [
            f"{inf['source']} → {inf['target']} ({inf.get('influence_type', 'INFLUENCES')})"
            for inf in influences
        ]
        
        selected = st.selectbox("Select Influence to Delete", influence_options)
        
        if st.button("🗑️ Delete Influence", type="secondary"):
            # Parse the selected influence
            parts = selected.split(" → ")
            source = parts[0]
            target = parts[1].split(" (")[0]
            
            success = delete_influence(conn, source, target)
            if success:
                st.success("✅ Influence deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete influence.")


def render_analytics_tab():
    """Render the analytics tab"""
    st.header("📊 Risk Analytics")
    
    conn = get_neo4j_connection()
    
    if not conn.driver:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Influencing Risks")
        query = """
        MATCH (r:Risk)-[i:INFLUENCES]->()
        RETURN r.name as Risk, count(i) as Outgoing_Influences
        ORDER BY Outgoing_Influences DESC
        LIMIT 5
        """
        results = conn.execute_query(query)
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, hide_index=True)
        else:
            st.info("No data available")
    
    with col2:
        st.subheader("Most Influenced Risks")
        query = """
        MATCH ()-[i:INFLUENCES]->(r:Risk)
        RETURN r.name as Risk, count(i) as Incoming_Influences
        ORDER BY Incoming_Influences DESC
        LIMIT 5
        """
        results = conn.execute_query(query)
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, hide_index=True)
        else:
            st.info("No data available")
    
    st.markdown("---")
    
    # Risk distribution by category
    st.subheader("Risk Distribution by Category")
    stats = get_risk_statistics(conn)
    if stats.get('category_distribution'):
        df = pd.DataFrame(stats['category_distribution'])
        st.bar_chart(df.set_index('category'))
    else:
        st.info("No data available")


def main():
    """Main application entry point"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1e3a8a/ffffff?text=RIM+POC", 
                 use_container_width=True)
        st.markdown("### Navigation")
        
        page = st.radio(
            "Select View:",
            ["Dashboard", "Visualization", "Risks", "Influences", "Analytics"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        **Risk Influence Map** is a proof-of-concept for dynamic risk 
        management using graph database technology.
        """)
        
        st.markdown("---")
        st.markdown("### Connection Status")
        conn = get_neo4j_connection()
        if conn.driver:
            st.success("✅ Neo4j Connected")
        else:
            st.error("❌ Neo4j Disconnected")
    
    # Main content
    if page == "Dashboard":
        render_dashboard()
        render_visualization_tab()
    elif page == "Visualization":
        render_visualization_tab()
    elif page == "Risks":
        render_risks_tab()
    elif page == "Influences":
        render_influences_tab()
    elif page == "Analytics":
        render_analytics_tab()


if __name__ == "__main__":
    main()
