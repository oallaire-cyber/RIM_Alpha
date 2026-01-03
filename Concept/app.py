"""
Risk Influence Map - Application Streamlit
Gestion et visualisation d'une carte d'influence des risques avec Neo4j
"""

import streamlit as st
from neo4j import GraphDatabase
from pyvis.network import Network
import tempfile
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Risk Influence Map",
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f4e79;
        color: white;
    }
    div[data-testid="stExpander"] {
        background-color: #f8f9fa;
        border-radius: 8px;
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
    
    def create_risk(self, name: str, category: str, description: str, 
                    probability: float, impact: float, status: str = "Actif") -> bool:
        """Crée un nouveau nœud de risque"""
        query = """
        CREATE (r:Risk {
            id: randomUUID(),
            name: $name,
            category: $category,
            description: $description,
            probability: $probability,
            impact: $impact,
            score: $probability * $impact,
            status: $status,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN r.id as id
        """
        try:
            result = self.execute_query(query, {
                "name": name,
                "category": category,
                "description": description,
                "probability": probability,
                "impact": impact,
                "status": status
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"Erreur lors de la création: {e}")
            return False
    
    def get_all_risks(self) -> list:
        """Récupère tous les risques"""
        query = """
        MATCH (r:Risk)
        RETURN r.id as id, r.name as name, r.category as category,
               r.description as description, r.probability as probability,
               r.impact as impact, r.score as score, r.status as status
        ORDER BY r.score DESC
        """
        return self.execute_query(query)
    
    def get_risk_by_id(self, risk_id: str) -> dict:
        """Récupère un risque par son ID"""
        query = """
        MATCH (r:Risk {id: $id})
        RETURN r.id as id, r.name as name, r.category as category,
               r.description as description, r.probability as probability,
               r.impact as impact, r.score as score, r.status as status
        """
        result = self.execute_query(query, {"id": risk_id})
        return dict(result[0]) if result else None
    
    def update_risk(self, risk_id: str, name: str, category: str, 
                    description: str, probability: float, impact: float, 
                    status: str) -> bool:
        """Met à jour un risque existant"""
        query = """
        MATCH (r:Risk {id: $id})
        SET r.name = $name,
            r.category = $category,
            r.description = $description,
            r.probability = $probability,
            r.impact = $impact,
            r.score = $probability * $impact,
            r.status = $status,
            r.updated_at = datetime()
        RETURN r.id
        """
        try:
            result = self.execute_query(query, {
                "id": risk_id,
                "name": name,
                "category": category,
                "description": description,
                "probability": probability,
                "impact": impact,
                "status": status
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
                         influence_type: str, strength: float, 
                         description: str = "") -> bool:
        """Crée une relation d'influence entre deux risques"""
        query = """
        MATCH (source:Risk {id: $source_id})
        MATCH (target:Risk {id: $target_id})
        CREATE (source)-[i:INFLUENCES {
            id: randomUUID(),
            type: $type,
            strength: $strength,
            description: $description,
            created_at: datetime()
        }]->(target)
        RETURN i.id as id
        """
        try:
            result = self.execute_query(query, {
                "source_id": source_id,
                "target_id": target_id,
                "type": influence_type,
                "strength": strength,
                "description": description
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
               target.id as target_id, target.name as target_name,
               i.type as type, i.strength as strength, i.description as description
        ORDER BY i.strength DESC
        """
        return self.execute_query(query)
    
    def update_influence(self, influence_id: str, influence_type: str, 
                         strength: float, description: str) -> bool:
        """Met à jour une relation d'influence"""
        query = """
        MATCH ()-[i:INFLUENCES {id: $id}]->()
        SET i.type = $type,
            i.strength = $strength,
            i.description = $description
        RETURN i.id
        """
        try:
            result = self.execute_query(query, {
                "id": influence_id,
                "type": influence_type,
                "strength": strength,
                "description": description
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
            "total_influences": 0,
            "avg_score": 0,
            "high_risks": 0,
            "categories": {}
        }
        
        # Nombre de risques
        result = self.execute_query("MATCH (r:Risk) RETURN count(r) as count")
        stats["total_risks"] = result[0]["count"] if result else 0
        
        # Nombre d'influences
        result = self.execute_query("MATCH ()-[i:INFLUENCES]->() RETURN count(i) as count")
        stats["total_influences"] = result[0]["count"] if result else 0
        
        # Score moyen
        result = self.execute_query("MATCH (r:Risk) RETURN avg(r.score) as avg")
        stats["avg_score"] = round(result[0]["avg"] or 0, 2)
        
        # Risques élevés (score > 6)
        result = self.execute_query("MATCH (r:Risk) WHERE r.score > 6 RETURN count(r) as count")
        stats["high_risks"] = result[0]["count"] if result else 0
        
        # Par catégorie
        result = self.execute_query("""
            MATCH (r:Risk) 
            RETURN r.category as category, count(r) as count 
            ORDER BY count DESC
        """)
        stats["categories"] = {r["category"]: r["count"] for r in result}
        
        return stats
    
    def get_graph_data(self) -> tuple:
        """Récupère les données pour la visualisation du graphe"""
        nodes = self.execute_query("""
            MATCH (r:Risk)
            RETURN r.id as id, r.name as name, r.category as category,
                   r.score as score, r.status as status
        """)
        
        edges = self.execute_query("""
            MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
            RETURN source.id as source, target.id as target,
                   i.type as type, i.strength as strength
        """)
        
        return nodes, edges


# ============================================================================
# FONCTIONS D'INTERFACE
# ============================================================================

def get_color_by_score(score: float) -> str:
    """Retourne une couleur selon le niveau de risque"""
    if score >= 7:
        return "#e74c3c"  # Rouge - Critique
    elif score >= 4:
        return "#f39c12"  # Orange - Élevé
    elif score >= 2:
        return "#3498db"  # Bleu - Modéré
    else:
        return "#27ae60"  # Vert - Faible

def get_color_by_category(category: str) -> str:
    """Retourne une couleur selon la catégorie"""
    colors = {
        "Stratégique": "#9b59b6",
        "Opérationnel": "#3498db",
        "Financier": "#27ae60",
        "Conformité": "#e67e22",
        "Cyber": "#e74c3c",
        "Réputation": "#1abc9c",
        "RH": "#f1c40f",
        "Environnemental": "#2ecc71"
    }
    return colors.get(category, "#95a5a6")

def render_graph(nodes: list, edges: list, color_by: str = "score"):
    """Génère et affiche le graphe interactif avec PyVis"""
    if not nodes:
        st.info("Aucun risque à afficher. Créez votre premier risque !")
        return
    
    # Création du réseau PyVis
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=True
    )
    
    # Configuration de la physique
    net.set_options("""
    {
        "nodes": {
            "font": {"size": 14, "face": "Arial"},
            "borderWidth": 2,
            "shadow": true
        },
        "edges": {
            "arrows": {"to": {"enabled": true, "scaleFactor": 0.8}},
            "smooth": {"type": "curvedCW", "roundness": 0.2},
            "shadow": true
        },
        "physics": {
            "enabled": true,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -150,
                "centralGravity": 0.01,
                "springLength": 250,
                "springConstant": 0.08
            },
            "stabilization": {"iterations": 100}
        },
        "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
        }
    }
    """)
    
    # Ajout des nœuds
    for node in nodes:
        score = node["score"] or 0
        if color_by == "score":
            color = get_color_by_score(score)
        else:
            color = get_color_by_category(node["category"])
        
        # Taille proportionnelle au score
        size = 5 + (score * 2)
        
        # Info-bulle
        title = f"""
        <b>{node['name']}</b><br>
        Catégorie: {node['category']}<br>
        Score: {score:.1f}<br>
        Statut: {node['status']}
        """
        
        net.add_node(
            node["id"],
            label=node["name"],
            title=title,
            color=color,
            size=size,
            borderWidthSelected=4
        )
    
    # Ajout des arêtes
    for edge in edges:
        strength = edge["strength"] or 1
        width = 1 + (strength * 1.5)
        
        # Couleur selon le type
        edge_colors = {
            "Amplifie": "#e74c3c",
            "Déclenche": "#9b59b6",
            "Atténue": "#27ae60",
            "Corrèle": "#3498db"
        }
        color = edge_colors.get(edge["type"], "#95a5a6")
        
        net.add_edge(
            edge["source"],
            edge["target"],
            title=f"{edge['type']} (Force: {strength})",
            width=width,
            color=color
        )
    
    # Génération du HTML
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
    tmp_path = tmp_file.name
    tmp_file.close()
    
    net.save_graph(tmp_path)
    
    with open(tmp_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    try:
        os.unlink(tmp_path)
    except PermissionError:
        pass  # Windows garde parfois le fichier verrouillé, on ignore
    
    # Affichage
    st.components.v1.html(html_content, height=620, scrolling=False)


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
    
    # Statut
    if st.session_state.connected:
        st.sidebar.success("✅ Connecté à Neo4j")
    else:
        st.sidebar.warning("⚠️ Non connecté")
    
    # Légende
    if st.session_state.connected:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 Légende")
        st.sidebar.markdown("""
        **Couleurs par score:**
        - 🔴 Critique (≥7)
        - 🟠 Élevé (4-7)
        - 🔵 Modéré (2-4)
        - 🟢 Faible (<2)
        
        **Types d'influence:**
        - 🔴 Amplifie
        - 🟣 Déclenche
        - 🟢 Atténue
        - 🔵 Corrèle
        """)


def main():
    """Fonction principale de l'application"""
    init_session_state()
    
    # En-tête
    st.markdown('<p class="main-header">🎯 Risk Influence Map</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Cartographie dynamique des risques et de leurs influences</p>', unsafe_allow_html=True)
    
    # Sidebar
    connection_sidebar()
    
    # Vérification connexion
    if not st.session_state.connected:
        st.info("👈 Veuillez vous connecter à Neo4j via la barre latérale pour commencer.")
        
        # Instructions
        with st.expander("📖 Instructions de démarrage", expanded=True):
            st.markdown("""
            ### Prérequis
            1. **Docker** installé et démarré
            2. **Neo4j** lancé dans un conteneur Docker
            
            ### Lancer Neo4j avec Docker
            ```bash
            docker run -d \\
                --name neo4j-risk \\
                -p 7474:7474 -p 7687:7687 \\
                -e NEO4J_AUTH=neo4j/password123 \\
                -v neo4j_data:/data \\
                neo4j:latest
            ```
            
            ### Connexion par défaut
            - **URI:** `bolt://localhost:7687`
            - **Utilisateur:** `neo4j`
            - **Mot de passe:** celui défini dans `NEO4J_AUTH`
            
            ### Interface Neo4j Browser
            Accessible sur [http://localhost:7474](http://localhost:7474)
            """)
        return
    
    manager = st.session_state.manager
    
    # Statistiques en haut
    stats = manager.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Risques", stats["total_risks"])
    with col2:
        st.metric("🔗 Total Influences", stats["total_influences"])
    with col3:
        st.metric("📈 Score Moyen", stats["avg_score"])
    with col4:
        st.metric("⚠️ Risques Critiques", stats["high_risks"])
    
    st.markdown("---")
    
    # Onglets principaux
    tab_viz, tab_risks, tab_influences, tab_data = st.tabs([
        "📊 Visualisation",
        "🎯 Risques",
        "🔗 Influences",
        "📋 Données"
    ])
    
    # === ONGLET VISUALISATION ===
    with tab_viz:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("### Options")
            color_by = st.radio(
                "Couleur par:",
                ["score", "category"],
                format_func=lambda x: "Score de risque" if x == "score" else "Catégorie"
            )
            
            if st.button("🔄 Actualiser", use_container_width=True):
                st.rerun()
        
        with col1:
            nodes, edges = manager.get_graph_data()
            render_graph(nodes, edges, color_by)
    
    # === ONGLET RISQUES ===
    with tab_risks:
        col_form, col_list = st.columns([1, 1])
        
        with col_form:
            st.markdown("### ➕ Créer un Risque")
            
            with st.form("create_risk_form", clear_on_submit=True):
                name = st.text_input("Nom du risque *", placeholder="Ex: Cyberattaque ransomware")
                
                category = st.selectbox("Catégorie *", [
                    "Cyber", "Opérationnel", "Stratégique", "Financier",
                    "Conformité", "Réputation", "RH", "Environnemental"
                ])
                
                description = st.text_area("Description", placeholder="Description détaillée du risque...")
                
                col_p, col_i = st.columns(2)
                with col_p:
                    probability = st.slider("Probabilité", 1.0, 10.0, 5.0, 0.5)
                with col_i:
                    impact = st.slider("Impact", 1.0, 10.0, 5.0, 0.5)
                
                st.info(f"**Score calculé:** {probability * impact:.1f}")
                
                status = st.selectbox("Statut", ["Actif", "Surveillé", "Mitigé", "Fermé"])
                
                submitted = st.form_submit_button("Créer le risque", type="primary", use_container_width=True)
                
                if submitted:
                    if name:
                        if manager.create_risk(name, category, description, probability, impact, status):
                            st.success(f"Risque '{name}' créé avec succès !")
                            st.rerun()
                    else:
                        st.error("Le nom est obligatoire")
        
        with col_list:
            st.markdown("### 📋 Risques existants")
            
            risks = manager.get_all_risks()
            
            if risks:
                for risk in risks:
                    score = risk["score"] or 0
                    color = get_color_by_score(score)
                    
                    with st.expander(f"🎯 {risk['name']} (Score: {score:.1f})"):
                        st.markdown(f"**Catégorie:** {risk['category']}")
                        st.markdown(f"**Probabilité:** {risk['probability']} | **Impact:** {risk['impact']}")
                        st.markdown(f"**Statut:** {risk['status']}")
                        
                        if risk['description']:
                            st.markdown(f"**Description:** {risk['description']}")
                        
                        col_edit, col_del = st.columns(2)
                        
                        with col_edit:
                            if st.button("✏️ Modifier", key=f"edit_{risk['id']}", use_container_width=True):
                                st.session_state[f"editing_{risk['id']}"] = True
                        
                        with col_del:
                            if st.button("🗑️ Supprimer", key=f"del_{risk['id']}", use_container_width=True):
                                if manager.delete_risk(risk['id']):
                                    st.success("Risque supprimé")
                                    st.rerun()
                        
                        # Formulaire de modification
                        if st.session_state.get(f"editing_{risk['id']}", False):
                            st.markdown("---")
                            with st.form(f"edit_form_{risk['id']}"):
                                new_name = st.text_input("Nom", value=risk['name'])
                                new_cat = st.selectbox("Catégorie", [
                                    "Cyber", "Opérationnel", "Stratégique", "Financier",
                                    "Conformité", "Réputation", "RH", "Environnemental"
                                ], index=["Cyber", "Opérationnel", "Stratégique", "Financier",
                                    "Conformité", "Réputation", "RH", "Environnemental"].index(risk['category']) if risk['category'] in ["Cyber", "Opérationnel", "Stratégique", "Financier", "Conformité", "Réputation", "RH", "Environnemental"] else 0)
                                new_desc = st.text_area("Description", value=risk['description'] or "")
                                new_prob = st.slider("Probabilité", 1.0, 10.0, float(risk['probability']), 0.5, key=f"prob_{risk['id']}")
                                new_imp = st.slider("Impact", 1.0, 10.0, float(risk['impact']), 0.5, key=f"imp_{risk['id']}")
                                new_status = st.selectbox("Statut", ["Actif", "Surveillé", "Mitigé", "Fermé"],
                                    index=["Actif", "Surveillé", "Mitigé", "Fermé"].index(risk['status']) if risk['status'] in ["Actif", "Surveillé", "Mitigé", "Fermé"] else 0)
                                
                                if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
                                    if manager.update_risk(risk['id'], new_name, new_cat, new_desc, new_prob, new_imp, new_status):
                                        st.session_state[f"editing_{risk['id']}"] = False
                                        st.success("Risque mis à jour")
                                        st.rerun()
            else:
                st.info("Aucun risque créé. Utilisez le formulaire pour ajouter votre premier risque.")
    
    # === ONGLET INFLUENCES ===
    with tab_influences:
        col_form, col_list = st.columns([1, 1])
        
        risks = manager.get_all_risks()
        risk_options = {r['name']: r['id'] for r in risks}
        
        with col_form:
            st.markdown("### ➕ Créer une Influence")
            
            if len(risks) < 2:
                st.warning("Vous devez avoir au moins 2 risques pour créer une influence.")
            else:
                with st.form("create_influence_form", clear_on_submit=True):
                    source_name = st.selectbox("Risque source", list(risk_options.keys()))
                    target_name = st.selectbox("Risque cible", 
                        [n for n in risk_options.keys() if n != source_name])
                    
                    influence_type = st.selectbox("Type d'influence", [
                        "Amplifie", "Déclenche", "Atténue", "Corrèle"
                    ])
                    
                    strength = st.slider("Force de l'influence", 1.0, 10.0, 5.0, 0.5)
                    
                    description = st.text_area("Description", 
                        placeholder="Décrivez comment ce risque influence l'autre...")
                    
                    submitted = st.form_submit_button("Créer l'influence", type="primary", use_container_width=True)
                    
                    if submitted:
                        source_id = risk_options[source_name]
                        target_id = risk_options[target_name]
                        
                        if manager.create_influence(source_id, target_id, influence_type, strength, description):
                            st.success(f"Influence '{source_name} → {target_name}' créée !")
                            st.rerun()
        
        with col_list:
            st.markdown("### 📋 Influences existantes")
            
            influences = manager.get_all_influences()
            
            if influences:
                for inf in influences:
                    with st.expander(f"🔗 {inf['source_name']} → {inf['target_name']}"):
                        st.markdown(f"**Type:** {inf['type']}")
                        st.markdown(f"**Force:** {inf['strength']}")
                        
                        if inf['description']:
                            st.markdown(f"**Description:** {inf['description']}")
                        
                        col_edit, col_del = st.columns(2)
                        
                        with col_edit:
                            if st.button("✏️ Modifier", key=f"edit_inf_{inf['id']}", use_container_width=True):
                                st.session_state[f"editing_inf_{inf['id']}"] = True
                        
                        with col_del:
                            if st.button("🗑️ Supprimer", key=f"del_inf_{inf['id']}", use_container_width=True):
                                if manager.delete_influence(inf['id']):
                                    st.success("Influence supprimée")
                                    st.rerun()
                        
                        # Formulaire de modification
                        if st.session_state.get(f"editing_inf_{inf['id']}", False):
                            st.markdown("---")
                            with st.form(f"edit_inf_form_{inf['id']}"):
                                new_type = st.selectbox("Type", ["Amplifie", "Déclenche", "Atténue", "Corrèle"],
                                    index=["Amplifie", "Déclenche", "Atténue", "Corrèle"].index(inf['type']) if inf['type'] in ["Amplifie", "Déclenche", "Atténue", "Corrèle"] else 0)
                                new_strength = st.slider("Force", 1.0, 10.0, float(inf['strength']), 0.5, key=f"str_{inf['id']}")
                                new_desc = st.text_area("Description", value=inf['description'] or "")
                                
                                if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
                                    if manager.update_influence(inf['id'], new_type, new_strength, new_desc):
                                        st.session_state[f"editing_inf_{inf['id']}"] = False
                                        st.success("Influence mise à jour")
                                        st.rerun()
            else:
                st.info("Aucune influence créée. Utilisez le formulaire pour lier vos risques.")
    
    # === ONGLET DONNÉES ===
    with tab_data:
        st.markdown("### 📊 Export et statistiques détaillées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Risques par catégorie")
            if stats["categories"]:
                import pandas as pd
                df_cat = pd.DataFrame(list(stats["categories"].items()), columns=["Catégorie", "Nombre"])
                st.bar_chart(df_cat.set_index("Catégorie"))
        
        with col2:
            st.markdown("#### Tableau des risques")
            risks = manager.get_all_risks()
            if risks:
                import pandas as pd
                df_risks = pd.DataFrame([dict(r) for r in risks])
                if not df_risks.empty:
                    st.dataframe(
                        df_risks[["name", "category", "probability", "impact", "score", "status"]].rename(columns={
                            "name": "Nom",
                            "category": "Catégorie",
                            "probability": "Probabilité",
                            "impact": "Impact",
                            "score": "Score",
                            "status": "Statut"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
        
        st.markdown("---")
        st.markdown("#### Requêtes Cypher personnalisées")
        
        with st.expander("🔧 Exécuter une requête Cypher"):
            st.warning("⚠️ Utilisez avec précaution - les requêtes sont exécutées directement sur la base.")
            
            query = st.text_area("Requête Cypher", 
                placeholder="MATCH (r:Risk) RETURN r LIMIT 10",
                height=100)
            
            if st.button("▶️ Exécuter"):
                if query:
                    try:
                        results = manager.execute_query(query)
                        st.json([dict(r) for r in results])
                    except Exception as e:
                        st.error(f"Erreur: {e}")


if __name__ == "__main__":
    main()
