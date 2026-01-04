"""
Risk Influence Map - Phase 1
Streamlit application for risk management with strategic/operational approach
"""

import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import pandas as pd
import tempfile
import os
from datetime import datetime, timedelta
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Risk Influence Map - Phase 1",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .contingent-badge {
        background-color: #f39c12;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .strategic-badge {
        background-color: #9b59b6;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .operational-badge {
        background-color: #3498db;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# NEO4J MANAGEMENT CLASS
# ============================================================================

class RiskGraphManager:
    """Neo4j database manager for risks"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = None
        self.uri = uri
        self.user = user
        self.password = password
    
    def connect(self) -> bool:
        """Establishes connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            st.error(f"Connection error: {e}")
            return False
    
    def close(self):
        """Closes the connection"""
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: dict = None):
        """Executes a Cypher query"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)
    
    # --- RISK MANAGEMENT (NODES) ---
    
    def create_risk(self, name: str, level: str, categories: list, description: str,
                    status: str, activation_condition: str = None, 
                    activation_decision_date: str = None, owner: str = "",
                    probability: float = None, impact: float = None) -> bool:
        """Creates a new risk node with Phase 1 model"""
        query = """
        CREATE (r:Risk {
            id: randomUUID(),
            name: $name,
            description: $description,
            level: $level,
            status: $status,
            activation_condition: $activation_condition,
            activation_decision_date: $activation_decision_date,
            categories: $categories,
            owner: $owner,
            current_score_type: $current_score_type,
            probability: $probability,
            impact: $impact,
            exposure: $exposure,
            created_at: datetime(),
            updated_at: datetime(),
            last_review_date: $last_review_date,
            next_review_date: $next_review_date
        })
        RETURN r.id as id
        """
        
        # Exposure calculation
        if probability and impact:
            exposure = probability * impact
            current_score_type = "Qualitative_4x4"
        else:
            exposure = None
            current_score_type = "None"
        
        # Review dates
        last_review_date = datetime.now().isoformat()
        next_review_date = (datetime.now() + timedelta(days=90)).isoformat()
        
        try:
            result = self.execute_query(query, {
                "name": name,
                "level": level,
                "categories": categories,
                "description": description,
                "status": status,
                "activation_condition": activation_condition,
                "activation_decision_date": activation_decision_date,
                "owner": owner,
                "current_score_type": current_score_type,
                "probability": probability,
                "impact": impact,
                "exposure": exposure,
                "last_review_date": last_review_date,
                "next_review_date": next_review_date
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"Creation error: {e}")
            return False
    
    def get_all_risks(self, level_filter=None, category_filter=None, status_filter=None) -> list:
        """Retrieves all risks with optional filters"""
        conditions = []
        params = {}
        
        if level_filter:
            conditions.append("r.level = $level")
            params["level"] = level_filter
        
        if category_filter:
            conditions.append("$category IN r.categories")
            params["category"] = category_filter
        
        if status_filter:
            conditions.append("r.status = $status")
            params["status"] = status_filter
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
        MATCH (r:Risk)
        {where_clause}
        RETURN r.id as id, r.name as name, r.level as level,
               r.categories as categories, r.description as description,
               r.status as status, r.activation_condition as activation_condition,
               r.activation_decision_date as activation_decision_date,
               r.owner as owner, r.probability as probability,
               r.impact as impact, r.exposure as exposure,
               r.current_score_type as current_score_type
        ORDER BY r.exposure DESC
        """
        return self.execute_query(query, params)
    
    def get_risk_by_id(self, risk_id: str) -> dict:
        """Retrieves a risk by its ID"""
        query = """
        MATCH (r:Risk {id: $id})
        RETURN r.id as id, r.name as name, r.level as level,
               r.categories as categories, r.description as description,
               r.status as status, r.activation_condition as activation_condition,
               r.activation_decision_date as activation_decision_date,
               r.owner as owner, r.probability as probability,
               r.impact as impact, r.exposure as exposure
        """
        result = self.execute_query(query, {"id": risk_id})
        return dict(result[0]) if result else None
    
    def update_risk(self, risk_id: str, name: str, level: str, categories: list,
                    description: str, status: str, activation_condition: str,
                    activation_decision_date: str, owner: str,
                    probability: float, impact: float) -> bool:
        """Updates an existing risk"""
        exposure = (probability * impact) if (probability and impact) else None
        
        query = """
        MATCH (r:Risk {id: $id})
        SET r.name = $name,
            r.level = $level,
            r.categories = $categories,
            r.description = $description,
            r.status = $status,
            r.activation_condition = $activation_condition,
            r.activation_decision_date = $activation_decision_date,
            r.owner = $owner,
            r.probability = $probability,
            r.impact = $impact,
            r.exposure = $exposure,
            r.updated_at = datetime()
        RETURN r.id
        """
        try:
            result = self.execute_query(query, {
                "id": risk_id,
                "name": name,
                "level": level,
                "categories": categories,
                "description": description,
                "status": status,
                "activation_condition": activation_condition,
                "activation_decision_date": activation_decision_date,
                "owner": owner,
                "probability": probability,
                "impact": impact,
                "exposure": exposure
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"Update error: {e}")
            return False
    
    def delete_risk(self, risk_id: str) -> bool:
        """Deletes a risk and all its relationships"""
        query = """
        MATCH (r:Risk {id: $id})
        DETACH DELETE r
        """
        try:
            self.execute_query(query, {"id": risk_id})
            return True
        except Exception as e:
            st.error(f"Deletion error: {e}")
            return False
    
    # --- INFLUENCE MANAGEMENT (LINKS) ---
    
    def create_influence(self, source_id: str, target_id: str,
                         influence_type: str, strength: str,
                         description: str = "", confidence: float = 0.8) -> bool:
        """Creates an influence relationship between two risks"""
        query = """
        MATCH (source:Risk {id: $source_id})
        MATCH (target:Risk {id: $target_id})
        
        // Determine type based on levels
        WITH source, target,
             CASE 
                WHEN source.level = 'Operational' AND target.level = 'Strategic' THEN 'Level1_Op_to_Strat'
                WHEN source.level = 'Strategic' AND target.level = 'Strategic' THEN 'Level2_Strat_to_Strat'
                WHEN source.level = 'Operational' AND target.level = 'Operational' THEN 'Level3_Op_to_Op'
                ELSE 'Unknown'
             END as determined_type
        
        CREATE (source)-[i:INFLUENCES {
            id: randomUUID(),
            influence_type: determined_type,
            strength: $strength,
            description: $description,
            confidence: $confidence,
            created_at: datetime(),
            last_validated: datetime()
        }]->(target)
        RETURN i.id as id
        """
        try:
            result = self.execute_query(query, {
                "source_id": source_id,
                "target_id": target_id,
                "strength": strength,
                "description": description,
                "confidence": confidence
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"Link creation error: {e}")
            return False
    
    def get_all_influences(self) -> list:
        """Retrieves all influence relationships"""
        query = """
        MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
        RETURN i.id as id, source.id as source_id, source.name as source_name,
               source.level as source_level, target.id as target_id,
               target.name as target_name, target.level as target_level,
               i.influence_type as influence_type, i.strength as strength,
               i.description as description, i.confidence as confidence
        ORDER BY i.strength DESC
        """
        return self.execute_query(query)
    
    def update_influence(self, influence_id: str, strength: str,
                         description: str, confidence: float) -> bool:
        """Updates an influence relationship"""
        query = """
        MATCH ()-[i:INFLUENCES {id: $id}]->()
        SET i.strength = $strength,
            i.description = $description,
            i.confidence = $confidence,
            i.last_validated = datetime()
        RETURN i.id
        """
        try:
            result = self.execute_query(query, {
                "id": influence_id,
                "strength": strength,
                "description": description,
                "confidence": confidence
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"Update error: {e}")
            return False
    
    def delete_influence(self, influence_id: str) -> bool:
        """Deletes an influence relationship"""
        query = """
        MATCH ()-[i:INFLUENCES {id: $id}]->()
        DELETE i
        """
        try:
            self.execute_query(query, {"id": influence_id})
            return True
        except Exception as e:
            st.error(f"Deletion error: {e}")
            return False
    
    # --- STATISTICS AND GRAPH ---
    
    def get_statistics(self) -> dict:
        """Retrieves graph statistics"""
        stats = {
            "total_risks": 0,
            "strategic_risks": 0,
            "operational_risks": 0,
            "contingent_risks": 0,
            "total_influences": 0,
            "avg_exposure": 0,
            "categories": {},
            "by_level": {}
        }
        
        # Total risks
        result = self.execute_query("MATCH (r:Risk) RETURN count(r) as count")
        stats["total_risks"] = result[0]["count"] if result else 0
        
        # Strategic risks
        result = self.execute_query("MATCH (r:Risk {level: 'Strategic'}) RETURN count(r) as count")
        stats["strategic_risks"] = result[0]["count"] if result else 0
        
        # Operational risks
        result = self.execute_query("MATCH (r:Risk {level: 'Operational'}) RETURN count(r) as count")
        stats["operational_risks"] = result[0]["count"] if result else 0
        
        # Contingent risks
        result = self.execute_query("MATCH (r:Risk {status: 'Contingent'}) RETURN count(r) as count")
        stats["contingent_risks"] = result[0]["count"] if result else 0
        
        # Influences
        result = self.execute_query("MATCH ()-[i:INFLUENCES]->() RETURN count(i) as count")
        stats["total_influences"] = result[0]["count"] if result else 0
        
        # Average exposure
        result = self.execute_query("""
            MATCH (r:Risk) 
            WHERE r.exposure IS NOT NULL 
            RETURN avg(r.exposure) as avg
        """)
        stats["avg_exposure"] = round(result[0]["avg"] or 0, 2)
        
        # By category
        result = self.execute_query("""
            MATCH (r:Risk)
            UNWIND r.categories as category
            RETURN category, count(r) as count
            ORDER BY count DESC
        """)
        stats["categories"] = {r["category"]: r["count"] for r in result}
        
        return stats
    
    def get_graph_data(self, filters: dict = None) -> tuple:
        """Retrieves data for graph visualization"""
        # Build filter conditions
        conditions = []
        params = {}
        
        if filters:
            # Filter by level (Strategic/Operational)
            level_list = filters.get("level")
            if level_list and len(level_list) > 0:
                conditions.append("r.level IN $levels")
                params["levels"] = level_list
            
            # Filter by categories (multi-select)
            category_list = filters.get("categories")
            if category_list and len(category_list) > 0:
                # Use ANY to check if at least one filter category is in r.categories
                conditions.append("ANY(cat IN r.categories WHERE cat IN $categories)")
                params["categories"] = category_list
            
            # Filter by status (Active/Contingent/Archived)
            status_list = filters.get("status")
            if status_list and len(status_list) > 0:
                conditions.append("r.status IN $statuses")
                params["statuses"] = status_list
        
        # Build WHERE clause
        where_clause = "WHERE " + " AND ".join(conditions) if len(conditions) > 0 else ""
        
        nodes_query = f"""
            MATCH (r:Risk)
            {where_clause}
            RETURN r.id as id, r.name as name, r.level as level,
                   r.categories as categories, r.status as status,
                   r.exposure as exposure, r.owner as owner
        """
        nodes = self.execute_query(nodes_query, params)
        
        # Retrieve only links between filtered nodes
        if nodes and len(nodes) > 0:
            node_ids = [n["id"] for n in nodes]
            edges_query = """
                MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
                WHERE source.id IN $node_ids AND target.id IN $node_ids
                RETURN source.id as source, target.id as target,
                       i.influence_type as influence_type, i.strength as strength
            """
            edges = self.execute_query(edges_query, {"node_ids": node_ids})
        else:
            edges = []
        
        return nodes if nodes else [], edges if edges else []
    
    def export_to_excel(self, filepath: str):
        """Exports risks and influences to Excel"""
        risks = self.get_all_risks()
        influences = self.get_all_influences()
        
        df_risks = pd.DataFrame([dict(r) for r in risks])
        df_influences = pd.DataFrame([dict(i) for i in influences])
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if not df_risks.empty:
                df_risks.to_excel(writer, sheet_name='Risks', index=False)
            if not df_influences.empty:
                df_influences.to_excel(writer, sheet_name='Influences', index=False)
    
    def import_from_excel(self, filepath: str) -> dict:
        """Imports risks and influences from Excel"""
        result = {"risks_created": 0, "influences_created": 0, "errors": []}
        
        try:
            # Import risks
            df_risks = pd.read_excel(filepath, sheet_name='Risks')
            for _, row in df_risks.iterrows():
                try:
                    categories = eval(row['categories']) if isinstance(row['categories'], str) else row['categories']
                    if self.create_risk(
                        name=row['name'],
                        level=row['level'],
                        categories=categories,
                        description=row.get('description', ''),
                        status=row['status'],
                        activation_condition=row.get('activation_condition'),
                        activation_decision_date=row.get('activation_decision_date'),
                        owner=row.get('owner', ''),
                        probability=row.get('probability'),
                        impact=row.get('impact')
                    ):
                        result["risks_created"] += 1
                except Exception as e:
                    result["errors"].append(f"Risk error '{row['name']}': {str(e)}")
            
            # Import influences
            try:
                df_influences = pd.read_excel(filepath, sheet_name='Influences')
                for _, row in df_influences.iterrows():
                    try:
                        if self.create_influence(
                            source_id=row['source_id'],
                            target_id=row['target_id'],
                            influence_type=row['influence_type'],
                            strength=row['strength'],
                            description=row.get('description', ''),
                            confidence=row.get('confidence', 0.8)
                        ):
                            result["influences_created"] += 1
                    except Exception as e:
                        result["errors"].append(f"Influence error: {str(e)}")
            except:
                pass  # No Influences sheet
        except Exception as e:
            result["errors"].append(f"Global error: {str(e)}")
        
        return result


class LayoutManager:
    """Manager for saving/restoring node positions"""
    
    def __init__(self, layout_file: str = "graph_layouts.json"):
        self.layout_file = layout_file
        self.layouts = self._load_layouts()
    
    def _load_layouts(self):
        """Loads layouts from JSON file"""
        if Path(self.layout_file).exists():
            try:
                with open(self.layout_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_layouts(self):
        """Saves layouts to JSON file"""
        with open(self.layout_file, 'w', encoding='utf-8') as f:
            json.dump(self.layouts, f, indent=2, ensure_ascii=False)
    
    def save_layout(self, name: str, positions: dict):
        """Saves a layout"""
        self.layouts[name] = {
            "positions": positions,
            "saved_at": datetime.now().isoformat(),
            "node_count": len(positions)
        }
        self._save_layouts()
    
    def load_layout(self, name: str):
        """Loads a layout by name"""
        layout = self.layouts.get(name)
        return layout["positions"] if layout else None
    
    def list_layouts(self):
        """Lists all saved layouts with their metadata"""
        return {
            name: {
                "saved_at": data["saved_at"],
                "node_count": data["node_count"]
            }
            for name, data in self.layouts.items()
        }
    
    def delete_layout(self, name: str):
        """Deletes a layout"""
        if name in self.layouts:
            del self.layouts[name]
            self._save_layouts()
            return True
        return False


def generate_layered_layout(nodes: list) -> dict:
    """Generates a layered layout (Strategic at top, Operational at bottom)"""
    strategic = [n for n in nodes if n.get("level") == "Strategic"]
    operational = [n for n in nodes if n.get("level") == "Operational"]
    
    positions = {}
    
    # Strategic at top
    y_strategic = 150
    x_spacing = 800 / max(len(strategic), 1)
    for i, node in enumerate(strategic):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": y_strategic
        }
    
    # Operational at bottom
    y_operational = 550
    x_spacing = 800 / max(len(operational), 1)
    for i, node in enumerate(operational):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": y_operational
        }
    
    return positions


def generate_category_layout(nodes: list) -> dict:
    """Generates a layout grouped by categories in 2x2 grid"""
    categories = ["Programme", "Produit", "Industriel", "Supply Chain"]
    positions = {}
    
    # 2x2 grid
    grid_positions = [
        (200, 200),   # Programme (top left)
        (600, 200),   # Produit (top right)
        (200, 500),   # Industriel (bottom left)
        (600, 500)    # Supply Chain (bottom right)
    ]
    
    for cat_idx, category in enumerate(categories):
        cat_nodes = [n for n in nodes if category in n.get("categories", [])]
        base_x, base_y = grid_positions[cat_idx]
        
        for i, node in enumerate(cat_nodes):
            offset_x = (i % 3) * 100 - 100
            offset_y = (i // 3) * 80
            positions[node["id"]] = {
                "x": base_x + offset_x,
                "y": base_y + offset_y
            }
    
    return positions


# ============================================================================
# INTERFACE FUNCTIONS
# ============================================================================

def get_color_by_level(level: str) -> str:
    """Returns a color based on level"""
    return "#9b59b6" if level == "Strategic" else "#3498db"

def get_color_by_exposure(exposure: float) -> str:
    """Returns a color based on exposure level"""
    if exposure is None:
        return "#95a5a6"
    if exposure >= 7:
        return "#e74c3c"
    elif exposure >= 4:
        return "#f39c12"
    elif exposure >= 2:
        return "#3498db"
    else:
        return "#27ae60"

def render_graph(nodes: list, edges: list, color_by: str = "level", physics_enabled: bool = True, positions: dict = None):
    """Generates and displays the interactive graph with PyVis (with optional positions)"""
    if not nodes:
        st.info("No risks to display. Create your first risk!")
        return
    
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=True
    )
    
    # Configuration with physics option
    net.set_options(f"""
    {{
        "nodes": {{
            "font": {{"size": 14, "face": "Arial"}},
            "borderWidth": 2,
            "shadow": true
        }},
        "edges": {{
            "arrows": {{"to": {{"enabled": true, "scaleFactor": 1.0}}}},
            "smooth": {{"type": "curvedCW", "roundness": 0.2}},
            "shadow": true
        }},
        "physics": {{
            "enabled": {str(physics_enabled).lower()},
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {{
                "gravitationalConstant": -150,
                "centralGravity": 0.01,
                "springLength": 300,
                "springConstant": 0.05
            }},
            "stabilization": {{
                "iterations": 150,
                "fit": true
            }}
        }},
        "interaction": {{
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "dragNodes": true,
            "dragView": true,
            "zoomView": true
        }}
    }}
    """)
    
    for node in nodes:
        exposure = node["exposure"] or 0
        level = node["level"]
        status = node["status"]
        
        if color_by == "level":
            color = get_color_by_level(level)
        else:
            color = get_color_by_exposure(exposure)
        
        size = 3 + (exposure * 0.67) if exposure else 5
        
        # Style for contingent
        if status == "Contingent":
            shape = "box"
            border_style = "dashes"
        else:
            shape = "dot"
            border_style = None
        
        categories_str = ", ".join(node["categories"]) if node["categories"] else "N/A"
        
        # Format exposure correctly
        exposure_str = f"{exposure:.2f}" if exposure else "N/A"
        
        title = f"""
        <b>{node['name']}</b><br>
        <b>Level:</b> {level}<br>
        <b>Status:</b> {status}<br>
        <b>Categories:</b> {categories_str}<br>
        <b>Exposure:</b> {exposure_str}<br>
        <b>Owner:</b> {node.get('owner', 'N/A')}
        """
        
        # Node configuration
        node_config = {
            "label": node["name"],
            "title": title,
            "color": color,
            "size": size,
            "shape": shape,
            "borderWidthSelected": 4
        }
        
        # If positions are provided, apply them and fix the node
        if positions and node["id"] in positions:
            pos = positions[node["id"]]
            node_config["x"] = pos["x"]
            node_config["y"] = pos["y"]
            node_config["fixed"] = {"x": True, "y": True}
            node_config["physics"] = False
        
        net.add_node(node["id"], **node_config)
    
    for edge in edges:
        strength = edge["strength"]
        influence_type = edge["influence_type"]
        
        # Color based on influence type
        if "Level1" in influence_type:
            color = "#e74c3c"  # Red for Op→Strat
            width = 2
        elif "Level2" in influence_type:
            color = "#9b59b6"  # Purple for Strat→Strat
            width = 2.5
        else:  # Level3
            color = "#3498db"  # Blue for Op→Op
            width = 1.5
        
        # Adjust based on strength
        if strength == "Critical":
            width *= 2
        elif strength == "Strong":
            width *= 1.5
        elif strength == "Moderate":
            width *= 1.2
        
        net.add_edge(
            edge["source"],
            edge["target"],
            title=f"{influence_type} ({strength})",
            width=width,
            color=color
        )
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
    tmp_path = tmp_file.name
    tmp_file.close()
    
    net.save_graph(tmp_path)
    
    with open(tmp_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    try:
        os.unlink(tmp_path)
    except PermissionError:
        pass
    
    st.components.v1.html(html_content, height=720, scrolling=False)


def init_session_state():
    """Initializes session state"""
    if "manager" not in st.session_state:
        st.session_state.manager = None
    if "connected" not in st.session_state:
        st.session_state.connected = False


def connection_sidebar():
    """Displays the connection sidebar"""
    st.sidebar.markdown("## 🔌 Neo4j Connection")
    
    with st.sidebar.expander("Connection Settings", expanded=not st.session_state.connected):
        uri = st.text_input("URI", value="bolt://localhost:7687", key="neo4j_uri")
        user = st.text_input("User", value="neo4j", key="neo4j_user")
        password = st.text_input("Password", type="password", key="neo4j_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", type="primary", use_container_width=True):
                manager = RiskGraphManager(uri, user, password)
                if manager.connect():
                    st.session_state.manager = manager
                    st.session_state.connected = True
                    st.success("Connected!")
                    st.rerun()
        
        with col2:
            if st.button("Disconnect", use_container_width=True, disabled=not st.session_state.connected):
                if st.session_state.manager:
                    st.session_state.manager.close()
                st.session_state.manager = None
                st.session_state.connected = False
                st.rerun()
    
    if st.session_state.connected:
        st.sidebar.success("✅ Connected to Neo4j")
    else:
        st.sidebar.warning("⚠️ Not connected")
    
    if st.session_state.connected:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 Legend")
        st.sidebar.markdown("""
        **Levels:**
        - 🟣 Strategic
        - 🔵 Operational
        - ⬜ Contingent (dashed)
        
        **Influence Links:**
        - 🔴 Op → Strat (Level 1)
        - 🟣 Strat → Strat (Level 2)
        - 🔵 Op → Op (Level 3)
        """)


def main():
    """Main application function"""
    init_session_state()
    
    st.markdown('<p class="main-header">🎯 Risk Influence Map - Phase 1</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Dynamic mapping system for strategic and operational risks</p>', unsafe_allow_html=True)
    
    connection_sidebar()
    
    if not st.session_state.connected:
        st.info("👈 Please connect to Neo4j via the sidebar to get started.")
        
        with st.expander("📖 Phase 1 Instructions", expanded=True):
            st.markdown("""
            ### Phase 1 Features
            
            ✨ **Two-level Architecture**
            - **Strategic** risks (business consequence-oriented)
            - **Operational** risks (cause-oriented)
            
            🔗 **Three Types of Influence Links**
            - Level 1: Operational → Strategic
            - Level 2: Strategic → Strategic
            - Level 3: Operational → Operational
            
            ⚠️ **Contingent Risk Management**
            - Future risks linked to structural decisions
            - Decision timeline
            - Dashed visualization
            
            🏷️ **Multi-categorization**
            - Programme, Product, Industrial, Supply Chain
            - Multi-criteria filters
            
            📊 **Excel Import/Export**
            - Simplified initial data loading
            - Save and share
            """)
        return
    
    manager = st.session_state.manager
    
    # Statistics at top
    stats = manager.get_statistics()
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🎯 Total Risks", stats["total_risks"])
    with col2:
        st.metric("🟣 Strategic", stats["strategic_risks"])
    with col3:
        st.metric("🔵 Operational", stats["operational_risks"])
    with col4:
        st.metric("⚠️ Contingent", stats["contingent_risks"])
    with col5:
        st.metric("🔗 Influences", stats["total_influences"])
    
    st.markdown("---")
    
    # Main tabs
    tab_viz, tab_risks, tab_influences, tab_import = st.tabs([
        "📊 Visualization",
        "🎯 Risks",
        "🔗 Influences",
        "📥 Import/Export"
    ])
    
    # === VISUALIZATION TAB ===
    with tab_viz:
        col_filters, col_display = st.columns([1, 3])
        
        with col_filters:
            st.markdown("### Filters")
            
            level_filter = st.multiselect(
                "Level",
                ["Strategic", "Operational"],
                default=["Strategic", "Operational"]
            )
            
            all_categories = ["Programme", "Produit", "Industriel", "Supply Chain"]
            category_filter = st.multiselect(
                "Categories",
                all_categories,
                default=all_categories
            )
            
            status_filter = st.multiselect(
                "Status",
                ["Active", "Contingent", "Archived"],
                default=["Active", "Contingent"]
            )
            
            color_by = st.radio(
                "Color by:",
                ["level", "exposure"],
                format_func=lambda x: "Level" if x == "level" else "Exposure"
            )
            
            st.markdown("---")
            
            physics_enabled = st.checkbox(
                "🔄 Physics enabled",
                value=True,
                help="Uncheck to freeze nodes after positioning them"
            )
            
            st.info("💡 Tip: Uncheck 'Physics enabled' then drag nodes where you want. They will stay fixed!")
            
            st.markdown("---")
            st.markdown("### 💾 Layout Management")
            
            # Initialize layout manager
            if "layout_manager" not in st.session_state:
                st.session_state.layout_manager = LayoutManager()
            
            layout_mgr = st.session_state.layout_manager
            
            # Save section
            with st.expander("💾 Save current layout"):
                layout_name = st.text_input(
                    "Layout name",
                    value=f"layout_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    key="save_layout_name"
                )
                
                col_save_1, col_save_2 = st.columns(2)
                
                with col_save_1:
                    if st.button("💾 Save (manual)", key="save_manual", use_container_width=True):
                        st.warning("⚠️ Feature under development.\n\nFor Phase 1, use the predefined layouts below.")
                
                with col_save_2:
                    if st.button("🎨 Layered layout", key="save_layered", use_container_width=True):
                        nodes, _ = manager.get_graph_data(None)
                        positions = generate_layered_layout(nodes)
                        layout_mgr.save_layout(layout_name, positions)
                        st.success(f"✅ Layout '{layout_name}' saved!")
                        st.rerun()
            
            # Load section
            with st.expander("📂 Load a layout"):
                saved_layouts = layout_mgr.list_layouts()
                
                if saved_layouts:
                    layout_options = list(saved_layouts.keys())
                    selected_layout = st.selectbox(
                        "Choose a layout",
                        options=layout_options,
                        format_func=lambda x: f"{x} ({saved_layouts[x]['node_count']} nodes)",
                        key="select_layout"
                    )
                    
                    col_load_1, col_load_2 = st.columns(2)
                    
                    with col_load_1:
                        if st.button("📂 Load", key="load_layout", use_container_width=True):
                            st.session_state.selected_layout_name = selected_layout
                            st.success(f"✅ Layout '{selected_layout}' loaded!")
                            st.rerun()
                    
                    with col_load_2:
                        if st.button("🗑️ Delete", key="delete_layout", use_container_width=True):
                            layout_mgr.delete_layout(selected_layout)
                            if "selected_layout_name" in st.session_state:
                                del st.session_state.selected_layout_name
                            st.success(f"✅ Layout '{selected_layout}' deleted!")
                            st.rerun()
                else:
                    st.info("No saved layouts. Create one above!")
            
            # Predefined layouts section
            with st.expander("🎨 Predefined layouts"):
                col_preset_1, col_preset_2 = st.columns(2)
                
                with col_preset_1:
                    if st.button("📊 Layered", key="preset_layered", use_container_width=True, help="Strategic at top, Operational at bottom"):
                        nodes, _ = manager.get_graph_data(None)
                        positions = generate_layered_layout(nodes)
                        auto_name = f"layered_{datetime.now().strftime('%Y%m%d_%H%M')}"
                        layout_mgr.save_layout(auto_name, positions)
                        st.session_state.selected_layout_name = auto_name
                        st.success("✅ Layered layout applied!")
                        st.rerun()
                
                with col_preset_2:
                    if st.button("🗂️ By categories", key="preset_categories", use_container_width=True, help="Grouping by categories in grid"):
                        nodes, _ = manager.get_graph_data(None)
                        positions = generate_category_layout(nodes)
                        auto_name = f"categories_{datetime.now().strftime('%Y%m%d_%H%M')}"
                        layout_mgr.save_layout(auto_name, positions)
                        st.session_state.selected_layout_name = auto_name
                        st.success("✅ Category layout applied!")
                        st.rerun()
                
                if st.button("🔄 Reset (auto)", key="reset_layout", use_container_width=True, help="Return to automatic organization"):
                    if "selected_layout_name" in st.session_state:
                        del st.session_state.selected_layout_name
                    st.success("✅ Layout reset!")
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        with col_display:
            # Build filter dictionary (don't include None values)
            filters = {}
            if level_filter:
                filters["level"] = level_filter
            if category_filter:
                filters["categories"] = category_filter
            if status_filter:
                filters["status"] = status_filter
            
            nodes, edges = manager.get_graph_data(filters if filters else None)
            
            # Load positions if a layout is selected
            positions = None
            if "selected_layout_name" in st.session_state:
                layout_name = st.session_state.selected_layout_name
                positions = st.session_state.layout_manager.load_layout(layout_name)
                if positions:
                    st.info(f"📍 Active layout: **{layout_name}**")
            
            render_graph(nodes, edges, color_by, physics_enabled, positions)
    
    # === RISKS TAB ===
    with tab_risks:
        col_form, col_list = st.columns([1, 1])
        
        with col_form:
            st.markdown("### ➕ Create a Risk")
            
            with st.form("create_risk_form", clear_on_submit=True):
                name = st.text_input("Risk name *", placeholder="E.g.: Fuel delivery delay")
                
                level = st.selectbox("Level *", ["Strategic", "Operational"])
                
                categories = st.multiselect(
                    "Categories *",
                    ["Programme", "Produit", "Industriel", "Supply Chain"],
                    default=["Programme"]
                )
                
                description = st.text_area("Description", placeholder="Detailed risk description...")
                
                status = st.selectbox("Status", ["Active", "Contingent", "Archived"])
                
                activation_condition = None
                activation_decision_date = None
                
                if status == "Contingent":
                    activation_condition = st.text_area(
                        "Activation condition",
                        placeholder="E.g.: If fuel choice X, then..."
                    )
                    activation_decision_date = st.date_input("Decision date").isoformat()
                
                owner = st.text_input("Owner", placeholder="Risk owner")
                
                col_p, col_i = st.columns(2)
                with col_p:
                    probability = st.slider("Probability (optional)", 0.0, 10.0, 5.0, 0.5)
                with col_i:
                    impact = st.slider("Impact (optional)", 0.0, 10.0, 5.0, 0.5)
                
                if probability > 0 and impact > 0:
                    st.info(f"**Calculated exposure:** {probability * impact:.1f}")
                
                submitted = st.form_submit_button("Create risk", type="primary", use_container_width=True)
                
                if submitted:
                    if name and categories:
                        if manager.create_risk(
                            name, level, categories, description, status,
                            activation_condition, activation_decision_date, owner,
                            probability if probability > 0 else None,
                            impact if impact > 0 else None
                        ):
                            st.success(f"Risk '{name}' created successfully!")
                            st.rerun()
                    else:
                        st.error("Name and at least one category are required")
        
        with col_list:
            st.markdown("### 📋 Existing Risks")
            
            risks = manager.get_all_risks()
            
            if risks:
                for risk in risks:
                    level_badge = "strategic-badge" if risk['level'] == "Strategic" else "operational-badge"
                    contingent_badge = " <span class='contingent-badge'>CONTINGENT</span>" if risk['status'] == "Contingent" else ""
                    
                    title = f"{risk['name']}{contingent_badge}"
                    
                    with st.expander(f"{'🟣' if risk['level'] == 'Strategic' else '🔵'} {risk['name']}", expanded=False):
                        st.markdown(f"**Level:** {risk['level']}")
                        st.markdown(f"**Categories:** {', '.join(risk['categories'])}")
                        st.markdown(f"**Status:** {risk['status']}")
                        
                        if risk['status'] == "Contingent":
                            st.markdown(f"**Condition:** {risk.get('activation_condition', 'N/A')}")
                            st.markdown(f"**Decision:** {risk.get('activation_decision_date', 'N/A')}")
                        
                        if risk.get('exposure'):
                            st.markdown(f"**Exposure:** {risk['exposure']:.2f}")
                        
                        st.markdown(f"**Owner:** {risk.get('owner', 'Not defined')}")
                        
                        if risk.get('description'):
                            st.markdown(f"**Description:** {risk['description']}")
                        
                        col_edit, col_del = st.columns(2)
                        
                        with col_del:
                            if st.button("🗑️ Delete", key=f"del_{risk['id']}", use_container_width=True):
                                if manager.delete_risk(risk['id']):
                                    st.success("Risk deleted")
                                    st.rerun()
            else:
                st.info("No risks created.")
    
    # === INFLUENCES TAB ===
    with tab_influences:
        col_form, col_list = st.columns([1, 1])
        
        risks = manager.get_all_risks()
        risk_options = {f"{r['name']} [{r['level']}]": r['id'] for r in risks}
        
        with col_form:
            st.markdown("### ➕ Create an Influence")
            
            if len(risks) < 2:
                st.warning("You need at least 2 risks to create an influence.")
            else:
                with st.form("create_influence_form", clear_on_submit=True):
                    source_name = st.selectbox("Source risk", list(risk_options.keys()))
                    target_name = st.selectbox("Target risk",
                        [n for n in risk_options.keys() if n != source_name])
                    
                    st.info("ℹ️ The influence type (Level 1/2/3) is determined automatically based on source/target levels")
                    
                    strength = st.selectbox("Influence strength", [
                        "Weak", "Moderate", "Strong", "Critical"
                    ])
                    
                    confidence = st.slider("Confidence level", 0.0, 1.0, 0.8, 0.1)
                    
                    description = st.text_area("Description",
                        placeholder="Describe how this risk influences the other...")
                    
                    submitted = st.form_submit_button("Create influence", type="primary", use_container_width=True)
                    
                    if submitted:
                        source_id = risk_options[source_name]
                        target_id = risk_options[target_name]
                        
                        if manager.create_influence(source_id, target_id, "", strength, description, confidence):
                            st.success("Influence created!")
                            st.rerun()
        
        with col_list:
            st.markdown("### 📋 Existing Influences")
            
            influences = manager.get_all_influences()
            
            if influences:
                for inf in influences:
                    type_emoji = "🔴" if "Level1" in inf['influence_type'] else ("🟣" if "Level2" in inf['influence_type'] else "🔵")
                    
                    with st.expander(f"{type_emoji} {inf['source_name']} → {inf['target_name']}"):
                        st.markdown(f"**Type:** {inf['influence_type']}")
                        st.markdown(f"**Strength:** {inf['strength']}")
                        st.markdown(f"**Confidence:** {inf['confidence']:.0%}")
                        
                        if inf.get('description'):
                            st.markdown(f"**Description:** {inf['description']}")
                        
                        if st.button("🗑️ Delete", key=f"del_inf_{inf['id']}", use_container_width=True):
                            if manager.delete_influence(inf['id']):
                                st.success("Influence deleted")
                                st.rerun()
            else:
                st.info("No influences created.")
    
    # === IMPORT/EXPORT TAB ===
    with tab_import:
        st.markdown("### 📥 Excel Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export to Excel")
            if st.button("📤 Export data", use_container_width=True):
                filepath = "/tmp/rim_export.xlsx"
                manager.export_to_excel(filepath)
                
                with open(filepath, 'rb') as f:
                    st.download_button(
                        "⬇️ Download Excel file",
                        f.read(),
                        file_name=f"RIM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        with col2:
            st.markdown("#### Import from Excel")
            uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
            
            if uploaded_file is not None:
                if st.button("📥 Import data", use_container_width=True):
                    filepath = f"/tmp/{uploaded_file.name}"
                    with open(filepath, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    result = manager.import_from_excel(filepath)
                    
                    if result["errors"]:
                        st.warning(f"Import completed with errors")
                        for error in result["errors"]:
                            st.error(error)
                    else:
                        st.success(f"Import successful!")
                    
                    st.info(f"Risks created: {result['risks_created']}, Influences created: {result['influences_created']}")
                    
                    if result["risks_created"] > 0 or result["influences_created"] > 0:
                        st.rerun()


if __name__ == "__main__":
    main()
