"""
Risk Influence Map - Phase 1
Application Streamlit pour la gestion des risques avec approche stratégique/opérationnelle
"""

import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import pandas as pd
import tempfile
import os
from datetime import datetime, timedelta
import json

# Configuration de la page
st.set_page_config(
    page_title="Risk Influence Map - Phase 1",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
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
# CLASSE DE GESTION NEO4J
# ============================================================================

class RiskGraphManager:
    """Gestionnaire de la base de données Neo4j pour les risques"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = None
        self.uri = uri
        self.user = user
        self.password = password
    
    def connect(self) -> bool:
        """Établit la connexion à Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            st.error(f"Erreur de connexion: {e}")
            return False
    
    def close(self):
        """Ferme la connexion"""
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: dict = None):
        """Exécute une requête Cypher"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return list(result)
    
    # --- GESTION DES RISQUES (NŒUDS) ---
    
    def create_risk(self, name: str, level: str, categories: list, description: str,
                    status: str, activation_condition: str = None, 
                    activation_decision_date: str = None, owner: str = "",
                    probability: float = None, impact: float = None) -> bool:
        """Crée un nouveau nœud de risque avec le modèle Phase 1"""
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
        
        # Calcul de l'exposition
        if probability and impact:
            exposure = probability * impact
            current_score_type = "Qualitative_4x4"
        else:
            exposure = None
            current_score_type = "None"
        
        # Dates de revue
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
            st.error(f"Erreur lors de la création: {e}")
            return False
    
    def get_all_risks(self, level_filter=None, category_filter=None, status_filter=None) -> list:
        """Récupère tous les risques avec filtres optionnels"""
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
        """Récupère un risque par son ID"""
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
        """Met à jour un risque existant"""
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
            st.error(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def delete_risk(self, risk_id: str) -> bool:
        """Supprime un risque et toutes ses relations"""
        query = """
        MATCH (r:Risk {id: $id})
        DETACH DELETE r
        """
        try:
            self.execute_query(query, {"id": risk_id})
            return True
        except Exception as e:
            st.error(f"Erreur lors de la suppression: {e}")
            return False
    
    # --- GESTION DES INFLUENCES (LIENS) ---
    
    def create_influence(self, source_id: str, target_id: str,
                         influence_type: str, strength: str,
                         description: str = "", confidence: float = 0.8) -> bool:
        """Crée une relation d'influence entre deux risques"""
        query = """
        MATCH (source:Risk {id: $source_id})
        MATCH (target:Risk {id: $target_id})
        
        // Détermine le type basé sur les niveaux
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
            st.error(f"Erreur lors de la création du lien: {e}")
            return False
    
    def get_all_influences(self) -> list:
        """Récupère toutes les relations d'influence"""
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
        """Met à jour une relation d'influence"""
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
            st.error(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def delete_influence(self, influence_id: str) -> bool:
        """Supprime une relation d'influence"""
        query = """
        MATCH ()-[i:INFLUENCES {id: $id}]->()
        DELETE i
        """
        try:
            self.execute_query(query, {"id": influence_id})
            return True
        except Exception as e:
            st.error(f"Erreur lors de la suppression: {e}")
            return False
    
    # --- STATISTIQUES ET GRAPHE ---
    
    def get_statistics(self) -> dict:
        """Récupère les statistiques du graphe"""
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
        
        # Risques totaux
        result = self.execute_query("MATCH (r:Risk) RETURN count(r) as count")
        stats["total_risks"] = result[0]["count"] if result else 0
        
        # Risques stratégiques
        result = self.execute_query("MATCH (r:Risk {level: 'Strategic'}) RETURN count(r) as count")
        stats["strategic_risks"] = result[0]["count"] if result else 0
        
        # Risques opérationnels
        result = self.execute_query("MATCH (r:Risk {level: 'Operational'}) RETURN count(r) as count")
        stats["operational_risks"] = result[0]["count"] if result else 0
        
        # Risques contingents
        result = self.execute_query("MATCH (r:Risk {status: 'Contingent'}) RETURN count(r) as count")
        stats["contingent_risks"] = result[0]["count"] if result else 0
        
        # Influences
        result = self.execute_query("MATCH ()-[i:INFLUENCES]->() RETURN count(i) as count")
        stats["total_influences"] = result[0]["count"] if result else 0
        
        # Exposition moyenne
        result = self.execute_query("""
            MATCH (r:Risk) 
            WHERE r.exposure IS NOT NULL 
            RETURN avg(r.exposure) as avg
        """)
        stats["avg_exposure"] = round(result[0]["avg"] or 0, 2)
        
        # Par catégorie
        result = self.execute_query("""
            MATCH (r:Risk)
            UNWIND r.categories as category
            RETURN category, count(r) as count
            ORDER BY count DESC
        """)
        stats["categories"] = {r["category"]: r["count"] for r in result}
        
        return stats
    
    def get_graph_data(self, filters: dict = None) -> tuple:
        """Récupère les données pour la visualisation du graphe"""
        # Construire les conditions de filtre
        conditions = []
        params = {}
        
        if filters:
            # Filtrer par niveau (Strategic/Operational)
            level_list = filters.get("level")
            if level_list and len(level_list) > 0:
                conditions.append("r.level IN $levels")
                params["levels"] = level_list
            
            # Filtrer par catégories (multi-sélection)
            category_list = filters.get("categories")
            if category_list and len(category_list) > 0:
                # Utiliser ANY pour vérifier si au moins une catégorie du filtre est dans r.categories
                conditions.append("ANY(cat IN r.categories WHERE cat IN $categories)")
                params["categories"] = category_list
            
            # Filtrer par statut (Active/Contingent/Archived)
            status_list = filters.get("status")
            if status_list and len(status_list) > 0:
                conditions.append("r.status IN $statuses")
                params["statuses"] = status_list
        
        # Construire la clause WHERE
        where_clause = "WHERE " + " AND ".join(conditions) if len(conditions) > 0 else ""
        
        nodes_query = f"""
            MATCH (r:Risk)
            {where_clause}
            RETURN r.id as id, r.name as name, r.level as level,
                   r.categories as categories, r.status as status,
                   r.exposure as exposure, r.owner as owner
        """
        nodes = self.execute_query(nodes_query, params)
        
        # Récupérer seulement les liens entre les nœuds filtrés
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
        """Exporte les risques et influences vers Excel"""
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
        """Importe les risques et influences depuis Excel"""
        result = {"risks_created": 0, "influences_created": 0, "errors": []}
        
        try:
            # Import des risques
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
                    result["errors"].append(f"Erreur risque '{row['name']}': {str(e)}")
            
            # Import des influences
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
                        result["errors"].append(f"Erreur influence: {str(e)}")
            except:
                pass  # Pas de sheet Influences
        except Exception as e:
            result["errors"].append(f"Erreur globale: {str(e)}")
        
        return result


# ============================================================================
# FONCTIONS D'INTERFACE
# ============================================================================

def get_color_by_level(level: str) -> str:
    """Retourne une couleur selon le niveau"""
    return "#9b59b6" if level == "Strategic" else "#3498db"

def get_color_by_exposure(exposure: float) -> str:
    """Retourne une couleur selon le niveau d'exposition"""
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

def render_graph(nodes: list, edges: list, color_by: str = "level", physics_enabled: bool = True):
    """Génère et affiche le graphe interactif avec PyVis"""
    if not nodes:
        st.info("Aucun risque à afficher. Créez votre premier risque !")
        return
    
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=True
    )
    
    # Configuration avec option de physique
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
        
        size = 10 + (exposure * 2) if exposure else 15
        
        # Style pour contingent
        if status == "Contingent":
            shape = "box"
            border_style = "dashes"
        else:
            shape = "dot"
            border_style = None
        
        categories_str = ", ".join(node["categories"]) if node["categories"] else "N/A"
        
        # Formater l'exposition correctement
        exposure_str = f"{exposure:.2f}" if exposure else "N/A"
        
        title = f"""
        <b>{node['name']}</b><br>
        <b>Niveau:</b> {level}<br>
        <b>Statut:</b> {status}<br>
        <b>Catégories:</b> {categories_str}<br>
        <b>Exposition:</b> {exposure_str}<br>
        <b>Owner:</b> {node.get('owner', 'N/A')}
        """
        
        net.add_node(
            node["id"],
            label=node["name"],
            title=title,
            color=color,
            size=size,
            shape=shape,
            borderWidthSelected=4
        )
    
    for edge in edges:
        strength = edge["strength"]
        influence_type = edge["influence_type"]
        
        # Couleur selon le type d'influence
        if "Level1" in influence_type:
            color = "#e74c3c"  # Rouge pour Op→Strat
            width = 2
        elif "Level2" in influence_type:
            color = "#9b59b6"  # Violet pour Strat→Strat
            width = 2.5
        else:  # Level3
            color = "#3498db"  # Bleu pour Op→Op
            width = 1.5
        
        # Ajuster selon strength
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
    """Initialise l'état de session"""
    if "manager" not in st.session_state:
        st.session_state.manager = None
    if "connected" not in st.session_state:
        st.session_state.connected = False


def connection_sidebar():
    """Affiche la barre latérale de connexion"""
    st.sidebar.markdown("## 🔌 Connexion Neo4j")
    
    with st.sidebar.expander("Paramètres de connexion", expanded=not st.session_state.connected):
        uri = st.text_input("URI", value="bolt://localhost:7687", key="neo4j_uri")
        user = st.text_input("Utilisateur", value="neo4j", key="neo4j_user")
        password = st.text_input("Mot de passe", type="password", key="neo4j_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connecter", type="primary", use_container_width=True):
                manager = RiskGraphManager(uri, user, password)
                if manager.connect():
                    st.session_state.manager = manager
                    st.session_state.connected = True
                    st.success("Connecté !")
                    st.rerun()
        
        with col2:
            if st.button("Déconnecter", use_container_width=True, disabled=not st.session_state.connected):
                if st.session_state.manager:
                    st.session_state.manager.close()
                st.session_state.manager = None
                st.session_state.connected = False
                st.rerun()
    
    if st.session_state.connected:
        st.sidebar.success("✅ Connecté à Neo4j")
    else:
        st.sidebar.warning("⚠️ Non connecté")
    
    if st.session_state.connected:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 Légende")
        st.sidebar.markdown("""
        **Niveaux:**
        - 🟣 Stratégique
        - 🔵 Opérationnel
        - ⬜ Contingent (pointillés)
        
        **Liens d'influence:**
        - 🔴 Op → Strat (Niveau 1)
        - 🟣 Strat → Strat (Niveau 2)
        - 🔵 Op → Op (Niveau 3)
        """)


def main():
    """Fonction principale de l'application"""
    init_session_state()
    
    st.markdown('<p class="main-header">🎯 Risk Influence Map - Phase 1</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Système de cartographie dynamique des risques stratégiques et opérationnels</p>', unsafe_allow_html=True)
    
    connection_sidebar()
    
    if not st.session_state.connected:
        st.info("👈 Veuillez vous connecter à Neo4j via la barre latérale pour commencer.")
        
        with st.expander("📖 Instructions Phase 1", expanded=True):
            st.markdown("""
            ### Nouveautés Phase 1
            
            ✨ **Architecture à deux niveaux**
            - Risques **Stratégiques** (orientés conséquences business)
            - Risques **Opérationnels** (orientés causes)
            
            🔗 **Trois types de liens d'influence**
            - Niveau 1: Opérationnel → Stratégique
            - Niveau 2: Stratégique → Stratégique
            - Niveau 3: Opérationnel → Opérationnel
            
            ⚠️ **Gestion des risques contingents**
            - Risques futurs liés aux décisions structurantes
            - Timeline des décisions
            - Visualisation en pointillés
            
            🏷️ **Multi-catégorisation**
            - Programme, Produit, Industriel, Supply Chain
            - Filtres multi-critères
            
            📊 **Import/Export Excel**
            - Alimentation initiale facilitée
            - Sauvegarde et partage
            """)
        return
    
    manager = st.session_state.manager
    
    # Statistiques en haut
    stats = manager.get_statistics()
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🎯 Total Risques", stats["total_risks"])
    with col2:
        st.metric("🟣 Stratégiques", stats["strategic_risks"])
    with col3:
        st.metric("🔵 Opérationnels", stats["operational_risks"])
    with col4:
        st.metric("⚠️ Contingents", stats["contingent_risks"])
    with col5:
        st.metric("🔗 Influences", stats["total_influences"])
    
    st.markdown("---")
    
    # Onglets principaux
    tab_viz, tab_risks, tab_influences, tab_import = st.tabs([
        "📊 Visualisation",
        "🎯 Risques",
        "🔗 Influences",
        "📥 Import/Export"
    ])
    
    # === ONGLET VISUALISATION ===
    with tab_viz:
        col_filters, col_display = st.columns([1, 3])
        
        with col_filters:
            st.markdown("### Filtres")
            
            level_filter = st.multiselect(
                "Niveau",
                ["Strategic", "Operational"],
                default=["Strategic", "Operational"]
            )
            
            all_categories = ["Programme", "Produit", "Industriel", "Supply Chain"]
            category_filter = st.multiselect(
                "Catégories",
                all_categories,
                default=all_categories
            )
            
            status_filter = st.multiselect(
                "Statut",
                ["Active", "Contingent", "Archived"],
                default=["Active", "Contingent"]
            )
            
            color_by = st.radio(
                "Couleur par:",
                ["level", "exposure"],
                format_func=lambda x: "Niveau" if x == "level" else "Exposition"
            )
            
            st.markdown("---")
            
            physics_enabled = st.checkbox(
                "🔄 Physique active",
                value=True,
                help="Décochez pour figer les nœuds après les avoir positionnés"
            )
            
            st.info("💡 Astuce : Décochez 'Physique active' puis glissez les nœuds où vous voulez. Ils resteront fixes !")
            
            if st.button("🔄 Actualiser", use_container_width=True):
                st.rerun()
        
        with col_display:
            # Construire le dictionnaire de filtres (ne pas mettre de valeurs None)
            filters = {}
            if level_filter:
                filters["level"] = level_filter
            if category_filter:
                filters["categories"] = category_filter
            if status_filter:
                filters["status"] = status_filter
            
            nodes, edges = manager.get_graph_data(filters if filters else None)
            render_graph(nodes, edges, color_by, physics_enabled)
    
    # === ONGLET RISQUES ===
    with tab_risks:
        col_form, col_list = st.columns([1, 1])
        
        with col_form:
            st.markdown("### ➕ Créer un Risque")
            
            with st.form("create_risk_form", clear_on_submit=True):
                name = st.text_input("Nom du risque *", placeholder="Ex: Retard de livraison combustible")
                
                level = st.selectbox("Niveau *", ["Strategic", "Operational"])
                
                categories = st.multiselect(
                    "Catégories *",
                    ["Programme", "Produit", "Industriel", "Supply Chain"],
                    default=["Programme"]
                )
                
                description = st.text_area("Description", placeholder="Description détaillée du risque...")
                
                status = st.selectbox("Statut", ["Active", "Contingent", "Archived"])
                
                activation_condition = None
                activation_decision_date = None
                
                if status == "Contingent":
                    activation_condition = st.text_area(
                        "Condition d'activation",
                        placeholder="Ex: Si choix du combustible X, alors..."
                    )
                    activation_decision_date = st.date_input("Date de décision").isoformat()
                
                owner = st.text_input("Owner", placeholder="Responsable du risque")
                
                col_p, col_i = st.columns(2)
                with col_p:
                    probability = st.slider("Probabilité (optionnel)", 0.0, 10.0, 5.0, 0.5)
                with col_i:
                    impact = st.slider("Impact (optionnel)", 0.0, 10.0, 5.0, 0.5)
                
                if probability > 0 and impact > 0:
                    st.info(f"**Exposition calculée:** {probability * impact:.1f}")
                
                submitted = st.form_submit_button("Créer le risque", type="primary", use_container_width=True)
                
                if submitted:
                    if name and categories:
                        if manager.create_risk(
                            name, level, categories, description, status,
                            activation_condition, activation_decision_date, owner,
                            probability if probability > 0 else None,
                            impact if impact > 0 else None
                        ):
                            st.success(f"Risque '{name}' créé avec succès !")
                            st.rerun()
                    else:
                        st.error("Le nom et au moins une catégorie sont obligatoires")
        
        with col_list:
            st.markdown("### 📋 Risques existants")
            
            risks = manager.get_all_risks()
            
            if risks:
                for risk in risks:
                    level_badge = "strategic-badge" if risk['level'] == "Strategic" else "operational-badge"
                    contingent_badge = " <span class='contingent-badge'>CONTINGENT</span>" if risk['status'] == "Contingent" else ""
                    
                    title = f"{risk['name']}{contingent_badge}"
                    
                    with st.expander(f"{'🟣' if risk['level'] == 'Strategic' else '🔵'} {risk['name']}", expanded=False):
                        st.markdown(f"**Niveau:** {risk['level']}")
                        st.markdown(f"**Catégories:** {', '.join(risk['categories'])}")
                        st.markdown(f"**Statut:** {risk['status']}")
                        
                        if risk['status'] == "Contingent":
                            st.markdown(f"**Condition:** {risk.get('activation_condition', 'N/A')}")
                            st.markdown(f"**Décision:** {risk.get('activation_decision_date', 'N/A')}")
                        
                        if risk.get('exposure'):
                            st.markdown(f"**Exposition:** {risk['exposure']:.2f}")
                        
                        st.markdown(f"**Owner:** {risk.get('owner', 'Non défini')}")
                        
                        if risk.get('description'):
                            st.markdown(f"**Description:** {risk['description']}")
                        
                        col_edit, col_del = st.columns(2)
                        
                        with col_del:
                            if st.button("🗑️ Supprimer", key=f"del_{risk['id']}", use_container_width=True):
                                if manager.delete_risk(risk['id']):
                                    st.success("Risque supprimé")
                                    st.rerun()
            else:
                st.info("Aucun risque créé.")
    
    # === ONGLET INFLUENCES ===
    with tab_influences:
        col_form, col_list = st.columns([1, 1])
        
        risks = manager.get_all_risks()
        risk_options = {f"{r['name']} [{r['level']}]": r['id'] for r in risks}
        
        with col_form:
            st.markdown("### ➕ Créer une Influence")
            
            if len(risks) < 2:
                st.warning("Vous devez avoir au moins 2 risques pour créer une influence.")
            else:
                with st.form("create_influence_form", clear_on_submit=True):
                    source_name = st.selectbox("Risque source", list(risk_options.keys()))
                    target_name = st.selectbox("Risque cible",
                        [n for n in risk_options.keys() if n != source_name])
                    
                    st.info("ℹ️ Le type d'influence (Niveau 1/2/3) est déterminé automatiquement selon les niveaux source/cible")
                    
                    strength = st.selectbox("Force de l'influence", [
                        "Weak", "Moderate", "Strong", "Critical"
                    ])
                    
                    confidence = st.slider("Niveau de confiance", 0.0, 1.0, 0.8, 0.1)
                    
                    description = st.text_area("Description",
                        placeholder="Décrivez comment ce risque influence l'autre...")
                    
                    submitted = st.form_submit_button("Créer l'influence", type="primary", use_container_width=True)
                    
                    if submitted:
                        source_id = risk_options[source_name]
                        target_id = risk_options[target_name]
                        
                        if manager.create_influence(source_id, target_id, "", strength, description, confidence):
                            st.success("Influence créée !")
                            st.rerun()
        
        with col_list:
            st.markdown("### 📋 Influences existantes")
            
            influences = manager.get_all_influences()
            
            if influences:
                for inf in influences:
                    type_emoji = "🔴" if "Level1" in inf['influence_type'] else ("🟣" if "Level2" in inf['influence_type'] else "🔵")
                    
                    with st.expander(f"{type_emoji} {inf['source_name']} → {inf['target_name']}"):
                        st.markdown(f"**Type:** {inf['influence_type']}")
                        st.markdown(f"**Force:** {inf['strength']}")
                        st.markdown(f"**Confiance:** {inf['confidence']:.0%}")
                        
                        if inf.get('description'):
                            st.markdown(f"**Description:** {inf['description']}")
                        
                        if st.button("🗑️ Supprimer", key=f"del_inf_{inf['id']}", use_container_width=True):
                            if manager.delete_influence(inf['id']):
                                st.success("Influence supprimée")
                                st.rerun()
            else:
                st.info("Aucune influence créée.")
    
    # === ONGLET IMPORT/EXPORT ===
    with tab_import:
        st.markdown("### 📥 Import/Export Excel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export vers Excel")
            if st.button("📤 Exporter les données", use_container_width=True):
                filepath = "/tmp/rim_export.xlsx"
                manager.export_to_excel(filepath)
                
                with open(filepath, 'rb') as f:
                    st.download_button(
                        "⬇️ Télécharger le fichier Excel",
                        f.read(),
                        file_name=f"RIM_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        with col2:
            st.markdown("#### Import depuis Excel")
            uploaded_file = st.file_uploader("Choisir un fichier Excel", type=['xlsx'])
            
            if uploaded_file is not None:
                if st.button("📥 Importer les données", use_container_width=True):
                    filepath = f"/tmp/{uploaded_file.name}"
                    with open(filepath, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    result = manager.import_from_excel(filepath)
                    
                    if result["errors"]:
                        st.warning(f"Import terminé avec erreurs")
                        for error in result["errors"]:
                            st.error(error)
                    else:
                        st.success(f"Import réussi !")
                    
                    st.info(f"Risques créés: {result['risks_created']}, Influences créées: {result['influences_created']}")
                    
                    if result["risks_created"] > 0 or result["influences_created"] > 0:
                        st.rerun()


if __name__ == "__main__":
    main()