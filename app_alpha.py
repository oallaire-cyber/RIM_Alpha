"""
Risk Influence Map - Phase 1
Streamlit application for risk management with strategic/operational approach
Now includes Top Program Objectives (TPO) support
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
    .tpo-badge {
        background-color: #f1c40f;
        color: #333;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)


# TPO Cluster constants
TPO_CLUSTERS = [
    "Product Efficiency",
    "Business Efficiency", 
    "Industrial Efficiency",
    "Sustainability",
    "Safety"
]

# Risk Categories constants
RISK_CATEGORIES = ["Programme", "Produit", "Industriel", "Supply Chain"]

# Risk Levels constants
RISK_LEVELS = ["Strategic", "Operational"]

# Risk Statuses constants
RISK_STATUSES = ["Active", "Contingent", "Archived"]


# ============================================================================
# FILTER MANAGER CLASS
# ============================================================================

class FilterManager:
    """Centralized filter management for the Risk Influence Map"""
    
    # Predefined filter presets
    PRESETS = {
        "full_view": {
            "name": "🌐 Full View",
            "description": "Show all risks and TPOs",
            "config": {
                "risks": {
                    "levels": RISK_LEVELS.copy(),
                    "categories": RISK_CATEGORIES.copy(),
                    "statuses": ["Active", "Contingent"]
                },
                "tpos": {
                    "enabled": True,
                    "clusters": TPO_CLUSTERS.copy()
                }
            }
        },
        "strategic_only": {
            "name": "🟣 Strategic Focus",
            "description": "Strategic risks and TPOs only",
            "config": {
                "risks": {
                    "levels": ["Strategic"],
                    "categories": RISK_CATEGORIES.copy(),
                    "statuses": ["Active", "Contingent"]
                },
                "tpos": {
                    "enabled": True,
                    "clusters": TPO_CLUSTERS.copy()
                }
            }
        },
        "operational_only": {
            "name": "🔵 Operational Focus",
            "description": "Operational risks only, no TPOs",
            "config": {
                "risks": {
                    "levels": ["Operational"],
                    "categories": RISK_CATEGORIES.copy(),
                    "statuses": ["Active", "Contingent"]
                },
                "tpos": {
                    "enabled": False,
                    "clusters": []
                }
            }
        },
        "active_only": {
            "name": "✅ Active Risks Only",
            "description": "Only active risks (no contingent)",
            "config": {
                "risks": {
                    "levels": RISK_LEVELS.copy(),
                    "categories": RISK_CATEGORIES.copy(),
                    "statuses": ["Active"]
                },
                "tpos": {
                    "enabled": True,
                    "clusters": TPO_CLUSTERS.copy()
                }
            }
        },
        "contingent_only": {
            "name": "⚠️ Contingent Risks",
            "description": "Only contingent/future risks",
            "config": {
                "risks": {
                    "levels": RISK_LEVELS.copy(),
                    "categories": RISK_CATEGORIES.copy(),
                    "statuses": ["Contingent"]
                },
                "tpos": {
                    "enabled": False,
                    "clusters": []
                }
            }
        },
        "risks_no_tpo": {
            "name": "🎯 Risks Only",
            "description": "All risks without TPOs",
            "config": {
                "risks": {
                    "levels": RISK_LEVELS.copy(),
                    "categories": RISK_CATEGORIES.copy(),
                    "statuses": ["Active", "Contingent"]
                },
                "tpos": {
                    "enabled": False,
                    "clusters": []
                }
            }
        }
    }
    
    def __init__(self):
        """Initialize with default filter state"""
        self.reset_to_default()
    
    def reset_to_default(self):
        """Reset filters to default (full view)"""
        self.filters = {
            "risks": {
                "levels": RISK_LEVELS.copy(),
                "categories": RISK_CATEGORIES.copy(),
                "statuses": ["Active", "Contingent"]
            },
            "tpos": {
                "enabled": True,
                "clusters": TPO_CLUSTERS.copy()
            }
        }
    
    def apply_preset(self, preset_key: str):
        """Apply a predefined filter preset"""
        if preset_key in self.PRESETS:
            # Deep copy the preset config
            preset_config = self.PRESETS[preset_key]["config"]
            self.filters = {
                "risks": {
                    "levels": preset_config["risks"]["levels"].copy(),
                    "categories": preset_config["risks"]["categories"].copy(),
                    "statuses": preset_config["risks"]["statuses"].copy()
                },
                "tpos": {
                    "enabled": preset_config["tpos"]["enabled"],
                    "clusters": preset_config["tpos"]["clusters"].copy()
                }
            }
            return True
        return False
    
    def set_risk_levels(self, levels: list):
        """Set risk level filter"""
        self.filters["risks"]["levels"] = levels
    
    def set_risk_categories(self, categories: list):
        """Set risk category filter"""
        self.filters["risks"]["categories"] = categories
    
    def set_risk_statuses(self, statuses: list):
        """Set risk status filter"""
        self.filters["risks"]["statuses"] = statuses
    
    def set_tpo_enabled(self, enabled: bool):
        """Enable or disable TPO display"""
        self.filters["tpos"]["enabled"] = enabled
        if not enabled:
            self.filters["tpos"]["clusters"] = []
    
    def set_tpo_clusters(self, clusters: list):
        """Set TPO cluster filter"""
        self.filters["tpos"]["clusters"] = clusters
    
    def select_all_levels(self):
        """Select all risk levels"""
        self.filters["risks"]["levels"] = RISK_LEVELS.copy()
    
    def deselect_all_levels(self):
        """Deselect all risk levels"""
        self.filters["risks"]["levels"] = []
    
    def select_all_categories(self):
        """Select all risk categories"""
        self.filters["risks"]["categories"] = RISK_CATEGORIES.copy()
    
    def deselect_all_categories(self):
        """Deselect all risk categories"""
        self.filters["risks"]["categories"] = []
    
    def select_all_statuses(self):
        """Select all risk statuses"""
        self.filters["risks"]["statuses"] = RISK_STATUSES.copy()
    
    def deselect_all_statuses(self):
        """Deselect all risk statuses"""
        self.filters["risks"]["statuses"] = []
    
    def select_all_clusters(self):
        """Select all TPO clusters"""
        self.filters["tpos"]["clusters"] = TPO_CLUSTERS.copy()
    
    def deselect_all_clusters(self):
        """Deselect all TPO clusters"""
        self.filters["tpos"]["clusters"] = []
    
    def get_filters_for_query(self) -> dict:
        """Convert filters to format expected by get_graph_data()"""
        query_filters = {
            "show_tpos": self.filters["tpos"]["enabled"]
        }
        
        if self.filters["risks"]["levels"]:
            query_filters["level"] = self.filters["risks"]["levels"]
        
        if self.filters["risks"]["categories"]:
            query_filters["categories"] = self.filters["risks"]["categories"]
        
        if self.filters["risks"]["statuses"]:
            query_filters["status"] = self.filters["risks"]["statuses"]
        
        if self.filters["tpos"]["enabled"] and self.filters["tpos"]["clusters"]:
            query_filters["tpo_clusters"] = self.filters["tpos"]["clusters"]
        
        return query_filters
    
    def get_filter_summary(self) -> str:
        """Get a human-readable summary of current filters"""
        parts = []
        
        # Risk levels
        if len(self.filters["risks"]["levels"]) == len(RISK_LEVELS):
            parts.append("All levels")
        elif self.filters["risks"]["levels"]:
            parts.append(f"Levels: {', '.join(self.filters['risks']['levels'])}")
        else:
            parts.append("No levels selected")
        
        # Risk categories
        if len(self.filters["risks"]["categories"]) == len(RISK_CATEGORIES):
            parts.append("All categories")
        elif self.filters["risks"]["categories"]:
            parts.append(f"{len(self.filters['risks']['categories'])} categories")
        else:
            parts.append("No categories")
        
        # TPOs
        if self.filters["tpos"]["enabled"]:
            if len(self.filters["tpos"]["clusters"]) == len(TPO_CLUSTERS):
                parts.append("All TPOs")
            elif self.filters["tpos"]["clusters"]:
                parts.append(f"{len(self.filters['tpos']['clusters'])} TPO clusters")
            else:
                parts.append("No TPO clusters")
        else:
            parts.append("TPOs hidden")
        
        return " | ".join(parts)
    
    def validate(self) -> tuple:
        """Validate current filter configuration. Returns (is_valid, message)"""
        # Check if at least something is selected
        has_risks = (
            len(self.filters["risks"]["levels"]) > 0 and
            len(self.filters["risks"]["categories"]) > 0 and
            len(self.filters["risks"]["statuses"]) > 0
        )
        has_tpos = (
            self.filters["tpos"]["enabled"] and
            len(self.filters["tpos"]["clusters"]) > 0
        )
        
        if not has_risks and not has_tpos:
            return False, "No data to display. Please select at least one filter option."
        
        if not has_risks and has_tpos:
            return True, "Showing TPOs only (no risk filters match)."
        
        return True, None


# ============================================================================
# NEO4J MANAGEMENT CLASS
# ============================================================================

class RiskGraphManager:
    """Neo4j database manager for risks and TPOs"""
    
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
    
    # --- TPO MANAGEMENT (NODES) ---
    
    def create_tpo(self, reference: str, name: str, cluster: str, description: str = "") -> bool:
        """Creates a new Top Program Objective node"""
        query = """
        CREATE (t:TPO {
            id: randomUUID(),
            reference: $reference,
            name: $name,
            cluster: $cluster,
            description: $description,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN t.id as id
        """
        try:
            result = self.execute_query(query, {
                "reference": reference,
                "name": name,
                "cluster": cluster,
                "description": description
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"TPO creation error: {e}")
            return False
    
    def get_all_tpos(self, cluster_filter: list = None) -> list:
        """Retrieves all TPOs with optional cluster filter"""
        conditions = []
        params = {}
        
        if cluster_filter and len(cluster_filter) > 0:
            conditions.append("t.cluster IN $clusters")
            params["clusters"] = cluster_filter
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
        MATCH (t:TPO)
        {where_clause}
        RETURN t.id as id, t.reference as reference, t.name as name,
               t.cluster as cluster, t.description as description
        ORDER BY t.reference
        """
        return self.execute_query(query, params)
    
    def get_tpo_by_id(self, tpo_id: str) -> dict:
        """Retrieves a TPO by its ID"""
        query = """
        MATCH (t:TPO {id: $id})
        RETURN t.id as id, t.reference as reference, t.name as name,
               t.cluster as cluster, t.description as description
        """
        result = self.execute_query(query, {"id": tpo_id})
        return dict(result[0]) if result else None
    
    def update_tpo(self, tpo_id: str, reference: str, name: str, 
                   cluster: str, description: str) -> bool:
        """Updates an existing TPO"""
        query = """
        MATCH (t:TPO {id: $id})
        SET t.reference = $reference,
            t.name = $name,
            t.cluster = $cluster,
            t.description = $description,
            t.updated_at = datetime()
        RETURN t.id
        """
        try:
            result = self.execute_query(query, {
                "id": tpo_id,
                "reference": reference,
                "name": name,
                "cluster": cluster,
                "description": description
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"TPO update error: {e}")
            return False
    
    def delete_tpo(self, tpo_id: str) -> bool:
        """Deletes a TPO and all its relationships"""
        query = """
        MATCH (t:TPO {id: $id})
        DETACH DELETE t
        """
        try:
            self.execute_query(query, {"id": tpo_id})
            return True
        except Exception as e:
            st.error(f"TPO deletion error: {e}")
            return False
    
    # --- TPO IMPACT MANAGEMENT (Strategic Risk -> TPO links) ---
    
    def create_tpo_impact(self, risk_id: str, tpo_id: str, 
                          impact_level: str, description: str = "") -> bool:
        """Creates an impact relationship from a Strategic Risk to a TPO"""
        # First verify the risk is Strategic
        check_query = """
        MATCH (r:Risk {id: $risk_id})
        RETURN r.level as level
        """
        check_result = self.execute_query(check_query, {"risk_id": risk_id})
        
        if not check_result or check_result[0]["level"] != "Strategic":
            st.error("Only Strategic risks can impact TPOs")
            return False
        
        query = """
        MATCH (r:Risk {id: $risk_id})
        MATCH (t:TPO {id: $tpo_id})
        CREATE (r)-[i:IMPACTS_TPO {
            id: randomUUID(),
            impact_level: $impact_level,
            description: $description,
            created_at: datetime()
        }]->(t)
        RETURN i.id as id
        """
        try:
            result = self.execute_query(query, {
                "risk_id": risk_id,
                "tpo_id": tpo_id,
                "impact_level": impact_level,
                "description": description
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"TPO impact creation error: {e}")
            return False
    
    def get_all_tpo_impacts(self) -> list:
        """Retrieves all TPO impact relationships"""
        query = """
        MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
        RETURN i.id as id, r.id as risk_id, r.name as risk_name,
               t.id as tpo_id, t.reference as tpo_reference, t.name as tpo_name,
               i.impact_level as impact_level, i.description as description
        ORDER BY t.reference
        """
        return self.execute_query(query)
    
    def update_tpo_impact(self, impact_id: str, impact_level: str, description: str) -> bool:
        """Updates a TPO impact relationship"""
        query = """
        MATCH ()-[i:IMPACTS_TPO {id: $id}]->()
        SET i.impact_level = $impact_level,
            i.description = $description
        RETURN i.id
        """
        try:
            result = self.execute_query(query, {
                "id": impact_id,
                "impact_level": impact_level,
                "description": description
            })
            return len(result) > 0
        except Exception as e:
            st.error(f"TPO impact update error: {e}")
            return False
    
    def delete_tpo_impact(self, impact_id: str) -> bool:
        """Deletes a TPO impact relationship"""
        query = """
        MATCH ()-[i:IMPACTS_TPO {id: $id}]->()
        DELETE i
        """
        try:
            self.execute_query(query, {"id": impact_id})
            return True
        except Exception as e:
            st.error(f"TPO impact deletion error: {e}")
            return False
    
    # --- STATISTICS AND GRAPH ---
    
    def get_statistics(self) -> dict:
        """Retrieves graph statistics including TPOs"""
        stats = {
            "total_risks": 0,
            "strategic_risks": 0,
            "operational_risks": 0,
            "contingent_risks": 0,
            "total_influences": 0,
            "total_tpos": 0,
            "total_tpo_impacts": 0,
            "avg_exposure": 0,
            "categories": {},
            "tpo_clusters": {},
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
        
        # TPOs
        result = self.execute_query("MATCH (t:TPO) RETURN count(t) as count")
        stats["total_tpos"] = result[0]["count"] if result else 0
        
        # TPO Impacts
        result = self.execute_query("MATCH ()-[i:IMPACTS_TPO]->() RETURN count(i) as count")
        stats["total_tpo_impacts"] = result[0]["count"] if result else 0
        
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
        
        # By TPO cluster
        result = self.execute_query("""
            MATCH (t:TPO)
            RETURN t.cluster as cluster, count(t) as count
            ORDER BY count DESC
        """)
        stats["tpo_clusters"] = {r["cluster"]: r["count"] for r in result}
        
        return stats
    
    def get_graph_data(self, filters: dict = None) -> tuple:
        """Retrieves data for graph visualization including TPOs"""
        # Build filter conditions for risks
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
        
        # Build WHERE clause for risks
        where_clause = "WHERE " + " AND ".join(conditions) if len(conditions) > 0 else ""
        
        nodes_query = f"""
            MATCH (r:Risk)
            {where_clause}
            RETURN r.id as id, r.name as name, r.level as level,
                   r.categories as categories, r.status as status,
                   r.exposure as exposure, r.owner as owner,
                   'Risk' as node_type
        """
        risk_nodes = self.execute_query(nodes_query, params)
        
        # Get TPO nodes if display is enabled
        tpo_nodes = []
        show_tpos = filters.get("show_tpos", True) if filters else True
        
        if show_tpos:
            tpo_conditions = []
            tpo_params = {}
            
            # Filter TPOs by cluster
            cluster_list = filters.get("tpo_clusters") if filters else None
            if cluster_list and len(cluster_list) > 0:
                tpo_conditions.append("t.cluster IN $clusters")
                tpo_params["clusters"] = cluster_list
            
            tpo_where = "WHERE " + " AND ".join(tpo_conditions) if tpo_conditions else ""
            
            tpo_query = f"""
                MATCH (t:TPO)
                {tpo_where}
                RETURN t.id as id, t.reference as reference, t.name as name,
                       t.cluster as cluster, t.description as description,
                       'TPO' as node_type
            """
            tpo_nodes = self.execute_query(tpo_query, tpo_params)
        
        # Combine nodes
        nodes = list(risk_nodes) if risk_nodes else []
        nodes.extend(tpo_nodes if tpo_nodes else [])
        
        # Retrieve only links between filtered risk nodes
        edges = []
        if risk_nodes and len(risk_nodes) > 0:
            node_ids = [n["id"] for n in risk_nodes]
            edges_query = """
                MATCH (source:Risk)-[i:INFLUENCES]->(target:Risk)
                WHERE source.id IN $node_ids AND target.id IN $node_ids
                RETURN source.id as source, target.id as target,
                       i.influence_type as influence_type, i.strength as strength,
                       'INFLUENCES' as edge_type
            """
            edges = self.execute_query(edges_query, {"node_ids": node_ids})
        
        # Retrieve TPO impact edges (only if TPOs are shown)
        tpo_edges = []
        if show_tpos and tpo_nodes and len(tpo_nodes) > 0:
            tpo_ids = [n["id"] for n in tpo_nodes]
            risk_ids = [n["id"] for n in risk_nodes] if risk_nodes else []
            
            if risk_ids:
                tpo_edges_query = """
                    MATCH (r:Risk)-[i:IMPACTS_TPO]->(t:TPO)
                    WHERE r.id IN $risk_ids AND t.id IN $tpo_ids
                    RETURN r.id as source, t.id as target,
                           i.impact_level as impact_level, i.description as description,
                           'IMPACTS_TPO' as edge_type
                """
                tpo_edges = self.execute_query(tpo_edges_query, {
                    "risk_ids": risk_ids,
                    "tpo_ids": tpo_ids
                })
        
        # Combine edges
        all_edges = list(edges) if edges else []
        all_edges.extend(tpo_edges if tpo_edges else [])
        
        return nodes if nodes else [], all_edges if all_edges else []
    
    def export_to_excel(self, filepath: str):
        """Exports risks, influences, TPOs and TPO impacts to Excel"""
        risks = self.get_all_risks()
        influences = self.get_all_influences()
        tpos = self.get_all_tpos()
        tpo_impacts = self.get_all_tpo_impacts()
        
        df_risks = pd.DataFrame([dict(r) for r in risks])
        df_influences = pd.DataFrame([dict(i) for i in influences])
        df_tpos = pd.DataFrame([dict(t) for t in tpos])
        df_tpo_impacts = pd.DataFrame([dict(i) for i in tpo_impacts])
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            if not df_risks.empty:
                df_risks.to_excel(writer, sheet_name='Risks', index=False)
            if not df_influences.empty:
                df_influences.to_excel(writer, sheet_name='Influences', index=False)
            if not df_tpos.empty:
                df_tpos.to_excel(writer, sheet_name='TPOs', index=False)
            if not df_tpo_impacts.empty:
                df_tpo_impacts.to_excel(writer, sheet_name='TPO_Impacts', index=False)
    
    def import_from_excel(self, filepath: str) -> dict:
        """Imports risks, influences, TPOs and TPO impacts from Excel with detailed logging"""
        import logging
        from datetime import datetime
        
        result = {
            "risks_created": 0, 
            "risks_skipped": 0,
            "influences_created": 0,
            "influences_skipped": 0, 
            "tpos_created": 0,
            "tpos_skipped": 0,
            "tpo_impacts_created": 0,
            "tpo_impacts_skipped": 0,
            "errors": [],
            "warnings": [],
            "logs": []
        }
        
        def log(message: str, level: str = "INFO"):
            """Add a log entry with timestamp"""
            timestamp = datetime.now().strftime("%H:%M:%S")
            result["logs"].append(f"[{timestamp}] {level}: {message}")
        
        log(f"Starting import from {filepath}")
        
        # Mapping from old IDs (in Excel) to new IDs (in database)
        risk_id_mapping = {}  # old_id -> new_id
        risk_name_to_id = {}  # name -> new_id
        tpo_id_mapping = {}   # old_id -> new_id
        tpo_ref_to_id = {}    # reference -> new_id
        
        try:
            # ============ IMPORT RISKS ============
            log("Processing Risks sheet...")
            try:
                df_risks = pd.read_excel(filepath, sheet_name='Risks')
                log(f"Found {len(df_risks)} risks in Excel file")
                
                for idx, row in df_risks.iterrows():
                    row_num = idx + 2  # Excel row number (1-indexed + header)
                    try:
                        risk_name = row.get('name', 'Unknown')
                        
                        # Validate required fields
                        if pd.isna(row.get('name')):
                            result["warnings"].append(f"Row {row_num}: Missing risk name, skipped")
                            result["risks_skipped"] += 1
                            continue
                        
                        if pd.isna(row.get('level')) or row.get('level') not in ['Strategic', 'Operational']:
                            result["warnings"].append(f"Row {row_num} ({risk_name}): Invalid level '{row.get('level')}', skipped")
                            result["risks_skipped"] += 1
                            continue
                        
                        categories = row.get('categories', ['Programme'])
                        # Handle categories - could be string representation of list or actual list
                        if isinstance(categories, str):
                            try:
                                import ast
                                categories = ast.literal_eval(categories)
                            except:
                                categories = [c.strip().strip("[]'\"") for c in categories.split(',')]
                        elif pd.isna(categories) or not isinstance(categories, list):
                            categories = ['Programme']
                            result["warnings"].append(f"Row {row_num} ({risk_name}): Invalid categories, defaulting to ['Programme']")
                        
                        # Handle NaN values safely
                        description = row.get('description', '')
                        if pd.isna(description):
                            description = ''
                        
                        status = row.get('status', 'Active')
                        if pd.isna(status) or status not in ['Active', 'Contingent', 'Archived']:
                            status = 'Active'
                            result["warnings"].append(f"Row {row_num} ({risk_name}): Invalid status, defaulting to 'Active'")
                        
                        activation_condition = row.get('activation_condition')
                        if pd.isna(activation_condition):
                            activation_condition = None
                            
                        activation_decision_date = row.get('activation_decision_date')
                        if pd.isna(activation_decision_date):
                            activation_decision_date = None
                        elif hasattr(activation_decision_date, 'isoformat'):
                            activation_decision_date = activation_decision_date.isoformat()
                        elif isinstance(activation_decision_date, str):
                            pass  # Keep as string
                        else:
                            activation_decision_date = str(activation_decision_date)
                        
                        owner = row.get('owner', '')
                        if pd.isna(owner):
                            owner = ''
                        
                        probability = row.get('probability')
                        if pd.isna(probability):
                            probability = None
                        else:
                            try:
                                probability = float(probability)
                            except (ValueError, TypeError):
                                probability = None
                                result["warnings"].append(f"Row {row_num} ({risk_name}): Invalid probability value")
                            
                        impact = row.get('impact')
                        if pd.isna(impact):
                            impact = None
                        else:
                            try:
                                impact = float(impact)
                            except (ValueError, TypeError):
                                impact = None
                                result["warnings"].append(f"Row {row_num} ({risk_name}): Invalid impact value")
                        
                        if self.create_risk(
                            name=risk_name,
                            level=row['level'],
                            categories=categories,
                            description=description,
                            status=status,
                            activation_condition=activation_condition,
                            activation_decision_date=activation_decision_date,
                            owner=owner,
                            probability=probability,
                            impact=impact
                        ):
                            result["risks_created"] += 1
                            log(f"Created risk: {risk_name}")
                        else:
                            result["risks_skipped"] += 1
                            result["warnings"].append(f"Row {row_num} ({risk_name}): Failed to create in database")
                            
                    except Exception as e:
                        result["risks_skipped"] += 1
                        result["errors"].append(f"Row {row_num} - Risk error '{row.get('name', 'unknown')}': {str(e)}")
                        log(f"Error processing risk row {row_num}: {str(e)}", "ERROR")
                        
            except ValueError as e:
                if "Worksheet" in str(e) and "Risks" in str(e):
                    log("No 'Risks' sheet found in Excel file", "WARNING")
                    result["warnings"].append("No 'Risks' sheet found in Excel file")
                else:
                    raise e
            except Exception as e:
                result["errors"].append(f"Risks sheet error: {str(e)}")
                log(f"Error reading Risks sheet: {str(e)}", "ERROR")
            
            # Build risk name to ID mapping from database
            log("Building risk name mapping from database...")
            all_risks = self.get_all_risks()
            for risk in all_risks:
                risk_name_to_id[risk['name']] = risk['id']
            log(f"Mapped {len(risk_name_to_id)} risks by name")
            
            # ============ IMPORT TPOs ============
            log("Processing TPOs sheet...")
            try:
                df_tpos = pd.read_excel(filepath, sheet_name='TPOs')
                log(f"Found {len(df_tpos)} TPOs in Excel file")
                
                for idx, row in df_tpos.iterrows():
                    row_num = idx + 2
                    try:
                        tpo_ref = row.get('reference', 'Unknown')
                        
                        # Validate required fields
                        if pd.isna(row.get('reference')):
                            result["warnings"].append(f"TPO Row {row_num}: Missing reference, skipped")
                            result["tpos_skipped"] += 1
                            continue
                        
                        if pd.isna(row.get('name')):
                            result["warnings"].append(f"TPO Row {row_num} ({tpo_ref}): Missing name, skipped")
                            result["tpos_skipped"] += 1
                            continue
                        
                        cluster = row.get('cluster', 'Business Efficiency')
                        if pd.isna(cluster) or cluster not in TPO_CLUSTERS:
                            cluster = 'Business Efficiency'
                            result["warnings"].append(f"TPO Row {row_num} ({tpo_ref}): Invalid cluster, defaulting to 'Business Efficiency'")
                        
                        description = row.get('description', '')
                        if pd.isna(description):
                            description = ''
                            
                        if self.create_tpo(
                            reference=row['reference'],
                            name=row['name'],
                            cluster=cluster,
                            description=description
                        ):
                            result["tpos_created"] += 1
                            log(f"Created TPO: {tpo_ref}")
                        else:
                            result["tpos_skipped"] += 1
                            result["warnings"].append(f"TPO Row {row_num} ({tpo_ref}): Failed to create in database")
                            
                    except Exception as e:
                        result["tpos_skipped"] += 1
                        result["errors"].append(f"TPO Row {row_num} - Error '{row.get('reference', 'unknown')}': {str(e)}")
                        log(f"Error processing TPO row {row_num}: {str(e)}", "ERROR")
                        
            except ValueError as e:
                if "Worksheet" in str(e):
                    log("No 'TPOs' sheet found in Excel file", "WARNING")
                else:
                    raise e
            except Exception as e:
                log(f"TPOs sheet not found or error: {str(e)}", "WARNING")
            
            # Build TPO reference to ID mapping
            log("Building TPO reference mapping from database...")
            all_tpos = self.get_all_tpos()
            for tpo in all_tpos:
                tpo_ref_to_id[tpo['reference']] = tpo['id']
            log(f"Mapped {len(tpo_ref_to_id)} TPOs by reference")
            
            # ============ IMPORT INFLUENCES ============
            log("Processing Influences sheet...")
            try:
                df_influences = pd.read_excel(filepath, sheet_name='Influences')
                log(f"Found {len(df_influences)} influences in Excel file")
                
                for idx, row in df_influences.iterrows():
                    row_num = idx + 2
                    try:
                        # Try to find source and target by name
                        source_name = row.get('source_name')
                        target_name = row.get('target_name')
                        
                        if pd.isna(source_name) or pd.isna(target_name):
                            # Fallback: try source_id and target_id columns but they won't work for re-import
                            result["warnings"].append(f"Influence Row {row_num}: Missing source_name or target_name, skipped")
                            result["influences_skipped"] += 1
                            continue
                        
                        source_id = risk_name_to_id.get(source_name)
                        target_id = risk_name_to_id.get(target_name)
                        
                        if not source_id:
                            result["warnings"].append(f"Influence Row {row_num}: Source risk '{source_name}' not found in database, skipped")
                            result["influences_skipped"] += 1
                            continue
                            
                        if not target_id:
                            result["warnings"].append(f"Influence Row {row_num}: Target risk '{target_name}' not found in database, skipped")
                            result["influences_skipped"] += 1
                            continue
                        
                        description = row.get('description', '')
                        if pd.isna(description):
                            description = ''
                        
                        confidence = row.get('confidence', 0.8)
                        if pd.isna(confidence):
                            confidence = 0.8
                        else:
                            try:
                                confidence = float(confidence)
                            except:
                                confidence = 0.8
                        
                        strength = row.get('strength', 'Moderate')
                        if pd.isna(strength) or strength not in ['Weak', 'Moderate', 'Strong', 'Critical']:
                            strength = 'Moderate'
                        
                        if self.create_influence(
                            source_id=source_id,
                            target_id=target_id,
                            influence_type=row.get('influence_type', ''),
                            strength=strength,
                            description=description,
                            confidence=confidence
                        ):
                            result["influences_created"] += 1
                            log(f"Created influence: {source_name} → {target_name}")
                        else:
                            result["influences_skipped"] += 1
                            
                    except Exception as e:
                        result["influences_skipped"] += 1
                        result["errors"].append(f"Influence Row {row_num} - Error: {str(e)}")
                        log(f"Error processing influence row {row_num}: {str(e)}", "ERROR")
                        
            except ValueError as e:
                if "Worksheet" in str(e):
                    log("No 'Influences' sheet found in Excel file", "WARNING")
                else:
                    raise e
            except Exception as e:
                log(f"Influences sheet not found or error: {str(e)}", "WARNING")
            
            # ============ IMPORT TPO IMPACTS ============
            log("Processing TPO_Impacts sheet...")
            try:
                df_impacts = pd.read_excel(filepath, sheet_name='TPO_Impacts')
                log(f"Found {len(df_impacts)} TPO impacts in Excel file")
                
                for idx, row in df_impacts.iterrows():
                    row_num = idx + 2
                    try:
                        # Try to find by name/reference
                        risk_name = row.get('risk_name')
                        tpo_reference = row.get('tpo_reference')
                        
                        if pd.isna(risk_name) or pd.isna(tpo_reference):
                            result["warnings"].append(f"TPO Impact Row {row_num}: Missing risk_name or tpo_reference, skipped")
                            result["tpo_impacts_skipped"] += 1
                            continue
                        
                        risk_id = risk_name_to_id.get(risk_name)
                        tpo_id = tpo_ref_to_id.get(tpo_reference)
                        
                        if not risk_id:
                            result["warnings"].append(f"TPO Impact Row {row_num}: Risk '{risk_name}' not found, skipped")
                            result["tpo_impacts_skipped"] += 1
                            continue
                            
                        if not tpo_id:
                            result["warnings"].append(f"TPO Impact Row {row_num}: TPO '{tpo_reference}' not found, skipped")
                            result["tpo_impacts_skipped"] += 1
                            continue
                        
                        description = row.get('description', '')
                        if pd.isna(description):
                            description = ''
                        
                        impact_level = row.get('impact_level', 'Medium')
                        if pd.isna(impact_level) or impact_level not in ['Low', 'Medium', 'High', 'Critical']:
                            impact_level = 'Medium'
                        
                        if self.create_tpo_impact(
                            risk_id=risk_id,
                            tpo_id=tpo_id,
                            impact_level=impact_level,
                            description=description
                        ):
                            result["tpo_impacts_created"] += 1
                            log(f"Created TPO impact: {risk_name} → {tpo_reference}")
                        else:
                            result["tpo_impacts_skipped"] += 1
                            
                    except Exception as e:
                        result["tpo_impacts_skipped"] += 1
                        result["errors"].append(f"TPO Impact Row {row_num} - Error: {str(e)}")
                        log(f"Error processing TPO impact row {row_num}: {str(e)}", "ERROR")
                        
            except ValueError as e:
                if "Worksheet" in str(e):
                    log("No 'TPO_Impacts' sheet found in Excel file", "WARNING")
                else:
                    raise e
            except Exception as e:
                log(f"TPO_Impacts sheet not found or error: {str(e)}", "WARNING")
                
        except Exception as e:
            result["errors"].append(f"Global import error: {str(e)}")
            log(f"Global error during import: {str(e)}", "ERROR")
        
        # Final summary log
        log("=" * 50)
        log(f"Import completed:")
        log(f"  Risks: {result['risks_created']} created, {result['risks_skipped']} skipped")
        log(f"  TPOs: {result['tpos_created']} created, {result['tpos_skipped']} skipped")
        log(f"  Influences: {result['influences_created']} created, {result['influences_skipped']} skipped")
        log(f"  TPO Impacts: {result['tpo_impacts_created']} created, {result['tpo_impacts_skipped']} skipped")
        log(f"  Errors: {len(result['errors'])}, Warnings: {len(result['warnings'])}")
        
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
    """Generates a layered layout (TPO at top, Strategic in middle, Operational at bottom)"""
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    strategic = [n for n in nodes if n.get("level") == "Strategic"]
    operational = [n for n in nodes if n.get("level") == "Operational"]
    
    positions = {}
    
    # TPOs at very top
    y_tpo = 50
    x_spacing = 800 / max(len(tpos), 1)
    for i, node in enumerate(tpos):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": y_tpo
        }
    
    # Strategic in middle
    y_strategic = 250
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
    """Generates a layout grouped by categories in 2x2 grid (risks only), TPOs on top"""
    categories = ["Programme", "Produit", "Industriel", "Supply Chain"]
    positions = {}
    
    # Place TPOs at the top
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    x_spacing = 800 / max(len(tpos), 1)
    for i, node in enumerate(tpos):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": 50
        }
    
    # 2x2 grid for risks
    grid_positions = [
        (200, 250),   # Programme (top left)
        (600, 250),   # Produit (top right)
        (200, 500),   # Industriel (bottom left)
        (600, 500)    # Supply Chain (bottom right)
    ]
    
    risk_nodes = [n for n in nodes if n.get("node_type") != "TPO"]
    
    for cat_idx, category in enumerate(categories):
        cat_nodes = [n for n in risk_nodes if category in n.get("categories", [])]
        base_x, base_y = grid_positions[cat_idx]
        
        for i, node in enumerate(cat_nodes):
            offset_x = (i % 3) * 100 - 100
            offset_y = (i // 3) * 80
            positions[node["id"]] = {
                "x": base_x + offset_x,
                "y": base_y + offset_y
            }
    
    return positions


def generate_tpo_cluster_layout(nodes: list) -> dict:
    """Generates a layout grouped by TPO clusters with risks below"""
    positions = {}
    
    # Group TPOs by cluster
    clusters = TPO_CLUSTERS
    cluster_positions = {
        "Product Efficiency": (100, 50),
        "Business Efficiency": (300, 50),
        "Industrial Efficiency": (500, 50),
        "Sustainability": (700, 50),
        "Safety": (900, 50)
    }
    
    tpos = [n for n in nodes if n.get("node_type") == "TPO"]
    cluster_counts = {c: 0 for c in clusters}
    
    for node in tpos:
        cluster = node.get("cluster", "Product Efficiency")
        base_x, base_y = cluster_positions.get(cluster, (500, 50))
        offset = cluster_counts[cluster] * 60
        positions[node["id"]] = {
            "x": base_x,
            "y": base_y + offset
        }
        cluster_counts[cluster] += 1
    
    # Place strategic risks in middle
    strategic = [n for n in nodes if n.get("level") == "Strategic"]
    x_spacing = 800 / max(len(strategic), 1)
    for i, node in enumerate(strategic):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": 350
        }
    
    # Place operational risks at bottom
    operational = [n for n in nodes if n.get("level") == "Operational"]
    x_spacing = 800 / max(len(operational), 1)
    for i, node in enumerate(operational):
        positions[node["id"]] = {
            "x": 100 + (i * x_spacing),
            "y": 550
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

def truncate_label(text: str, max_length: int = 25) -> str:
    """Truncate text and add ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def wrap_label(text: str, max_width: int = 20) -> str:
    """Wrap text into multiple lines for better display"""
    if len(text) <= max_width:
        return text
    
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Limit to 3 lines max
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2][:max_width-3] + "..."
    
    return '\n'.join(lines)

def render_graph(nodes: list, edges: list, color_by: str = "level", physics_enabled: bool = True, positions: dict = None, capture_positions: bool = False):
    """Generates and displays the interactive graph with PyVis (with optional positions)"""
    if not nodes:
        st.info("No risks to display. Create your first risk!")
        return None
    
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#333333",
        directed=True
    )
    
    # Configuration with physics option - increased font sizes
    net.set_options(f"""
    {{
        "nodes": {{
            "font": {{
                "size": 18,
                "face": "Arial",
                "multi": "html",
                "bold": {{"color": "#333333", "size": 18}},
                "vadjust": -5
            }},
            "borderWidth": 2,
            "shadow": true,
            "widthConstraint": {{
                "minimum": 50,
                "maximum": 180
            }}
        }},
        "edges": {{
            "arrows": {{"to": {{"enabled": true, "scaleFactor": 1.0}}}},
            "smooth": {{"type": "curvedCW", "roundness": 0.2}},
            "shadow": true,
            "font": {{"size": 12, "face": "Arial"}}
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
        node_type = node.get("node_type", "Risk")
        
        if node_type == "TPO":
            # TPO Node - Yellow Hexagon
            color = "#f1c40f"  # Yellow
            shape = "hexagon"
            size = 35  # Increased size
            
            title = f"""
            <div style="max-width: 300px;">
            <b>🎯 {node['reference']}: {node['name']}</b><br>
            <b>Type:</b> Top Program Objective<br>
            <b>Cluster:</b> {node.get('cluster', 'N/A')}<br>
            <b>Description:</b> {node.get('description', 'N/A')}
            </div>
            """
            
            # Use reference as label for TPOs (short)
            label = f"{node['reference']}"
            
            node_config = {
                "label": label,
                "title": title,
                "color": color,
                "size": size,
                "shape": shape,
                "borderWidthSelected": 4,
                "font": {"color": "#333333", "size": 16, "face": "Arial", "bold": True}
            }
        else:
            # Risk Node
            exposure = node.get("exposure") or 0
            level = node.get("level", "Operational")
            status = node.get("status", "Active")
            
            if color_by == "level":
                color = get_color_by_level(level)
            else:
                color = get_color_by_exposure(exposure)
            
            # Increased base size for better visibility
            size = 25 + (exposure * 1.5) if exposure else 25
            
            # Style for contingent
            if status == "Contingent":
                shape = "box"
                border_style = "dashes"
            else:
                shape = "dot"
                border_style = None
            
            categories_str = ", ".join(node.get("categories", [])) if node.get("categories") else "N/A"
            
            # Format exposure correctly
            exposure_str = f"{exposure:.2f}" if exposure else "N/A"
            
            title = f"""
            <div style="max-width: 350px;">
            <b>{node['name']}</b><br>
            <b>Level:</b> {level}<br>
            <b>Status:</b> {status}<br>
            <b>Categories:</b> {categories_str}<br>
            <b>Exposure:</b> {exposure_str}<br>
            <b>Owner:</b> {node.get('owner', 'N/A')}
            </div>
            """
            
            # Wrap long labels for better display
            label = wrap_label(node["name"], max_width=20)
            
            node_config = {
                "label": label,
                "title": title,
                "color": color,
                "size": size,
                "shape": shape,
                "borderWidthSelected": 4,
                "font": {"color": "#333333", "size": 16, "face": "Arial"}
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
        edge_type = edge.get("edge_type", "INFLUENCES")
        
        if edge_type == "IMPACTS_TPO":
            # TPO Impact Edge - Dashed Blue Line
            color = "#3498db"  # Blue
            width = 2
            dashes = True
            impact_level = edge.get("impact_level", "Medium")
            
            # Adjust width based on impact level
            if impact_level == "Critical":
                width = 4
            elif impact_level == "High":
                width = 3
            elif impact_level == "Medium":
                width = 2
            else:  # Low
                width = 1.5
            
            title = f"Impacts TPO ({impact_level})"
            if edge.get("description"):
                title += f"<br>{edge['description']}"
            
            net.add_edge(
                edge["source"],
                edge["target"],
                title=title,
                width=width,
                color=color,
                dashes=dashes
            )
        else:
            # Regular Influence Edge
            strength = edge.get("strength", "Moderate")
            influence_type = edge.get("influence_type", "Unknown")
            
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
    
    # Inject JavaScript for position capture if requested
    if capture_positions:
        position_capture_js = """
        <style>
            #captureBtn {
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 9999;
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            #captureBtn:hover {
                background-color: #2980b9;
            }
            #positionOutput {
                position: fixed;
                top: 50px;
                right: 10px;
                z-index: 9999;
                width: 300px;
                max-height: 200px;
                overflow-y: auto;
                background: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
                font-size: 11px;
                display: none;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }
            #copyBtn {
                position: fixed;
                top: 10px;
                right: 180px;
                z-index: 9999;
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                display: none;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            #copyBtn:hover {
                background-color: #229954;
            }
            #statusMsg {
                position: fixed;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 9999;
                padding: 10px 20px;
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                display: none;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
        </style>
        <button id="captureBtn" onclick="capturePositions()">📍 Capture Positions</button>
        <button id="copyBtn" onclick="copyPositions()">📋 Copy to Clipboard</button>
        <div id="positionOutput"></div>
        <div id="statusMsg"></div>
        <script>
            var capturedPositions = null;
            
            function capturePositions() {
                var positions = network.getPositions();
                var result = {};
                
                for (var nodeId in positions) {
                    result[nodeId] = {
                        x: Math.round(positions[nodeId].x),
                        y: Math.round(positions[nodeId].y)
                    };
                }
                
                capturedPositions = JSON.stringify(result, null, 2);
                
                document.getElementById('positionOutput').innerText = capturedPositions;
                document.getElementById('positionOutput').style.display = 'block';
                document.getElementById('copyBtn').style.display = 'block';
                
                showStatus('✅ Positions captured! Click "Copy to Clipboard"');
            }
            
            function copyPositions() {
                if (capturedPositions) {
                    navigator.clipboard.writeText(capturedPositions).then(function() {
                        showStatus('✅ Copied! Paste in the "Position Data" field and click Save');
                    }).catch(function(err) {
                        // Fallback for older browsers
                        var textarea = document.createElement('textarea');
                        textarea.value = capturedPositions;
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textarea);
                        showStatus('✅ Copied! Paste in the "Position Data" field and click Save');
                    });
                }
            }
            
            function showStatus(msg) {
                var statusEl = document.getElementById('statusMsg');
                statusEl.innerText = msg;
                statusEl.style.display = 'block';
                setTimeout(function() {
                    statusEl.style.display = 'none';
                }, 4000);
            }
        </script>
        """
        # Insert before closing body tag
        html_content = html_content.replace('</body>', position_capture_js + '</body>')
    
    try:
        os.unlink(tmp_path)
    except PermissionError:
        pass
    
    st.components.v1.html(html_content, height=720, scrolling=False)
    
    return None


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
        **Node Types:**
        - 🟣 Strategic Risk
        - 🔵 Operational Risk
        - ⬜ Contingent (dashed border)
        - 🟡 TPO (hexagon)
        
        **Influence Links:**
        - 🔴 Op → Strat (Level 1)
        - 🟣 Strat → Strat (Level 2)
        - 🔵 Op → Op (Level 3)
        - 🔵 ╌╌ Risk → TPO (dashed blue)
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
            
            🎯 **Top Program Objectives (TPO)**
            - Link Strategic Risks to TPOs
            - Cluster-based organization
            - Yellow hexagon visualization
            
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
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("🎯 Total Risks", stats["total_risks"])
    with col2:
        st.metric("🟣 Strategic", stats["strategic_risks"])
    with col3:
        st.metric("🔵 Operational", stats["operational_risks"])
    with col4:
        st.metric("⚠️ Contingent", stats["contingent_risks"])
    with col5:
        st.metric("🟡 TPOs", stats["total_tpos"])
    with col6:
        st.metric("🔗 Links", stats["total_influences"] + stats["total_tpo_impacts"])
    
    st.markdown("---")
    
    # Main tabs
    tab_viz, tab_risks, tab_tpos, tab_influences, tab_tpo_impacts, tab_import = st.tabs([
        "📊 Visualization",
        "🎯 Risks",
        "🏆 TPOs",
        "🔗 Influences",
        "📌 TPO Impacts",
        "📥 Import/Export"
    ])
    
    # === VISUALIZATION TAB ===
    with tab_viz:
        col_filters, col_display = st.columns([1, 3])
        
        with col_filters:
            st.markdown("### 🎛️ Filters")
            
            # Initialize filter manager in session state
            if "filter_manager" not in st.session_state:
                st.session_state.filter_manager = FilterManager()
            
            filter_mgr = st.session_state.filter_manager
            
            # ===== FILTER PRESETS =====
            with st.expander("⚡ Quick Presets", expanded=False):
                preset_cols = st.columns(2)
                col_idx = 0
                for preset_key, preset_data in FilterManager.PRESETS.items():
                    with preset_cols[col_idx % 2]:
                        if st.button(
                            preset_data["name"],
                            key=f"preset_{preset_key}",
                            use_container_width=True,
                            help=preset_data["description"]
                        ):
                            filter_mgr.apply_preset(preset_key)
                            st.rerun()
                    col_idx += 1
            
            # ===== RISK FILTERS =====
            st.markdown("#### 🎯 Risk Filters")
            
            # Level filter with select all/none buttons
            col_level_btns = st.columns([1, 1])
            with col_level_btns[0]:
                if st.button("All", key="level_all", use_container_width=True):
                    filter_mgr.select_all_levels()
                    st.rerun()
            with col_level_btns[1]:
                if st.button("None", key="level_none", use_container_width=True):
                    filter_mgr.deselect_all_levels()
                    st.rerun()
            
            level_filter = st.multiselect(
                "Level",
                RISK_LEVELS,
                default=filter_mgr.filters["risks"]["levels"],
                key="level_filter"
            )
            filter_mgr.set_risk_levels(level_filter)
            
            # Category filter with select all/none buttons
            col_cat_btns = st.columns([1, 1])
            with col_cat_btns[0]:
                if st.button("All", key="cat_all", use_container_width=True):
                    filter_mgr.select_all_categories()
                    st.rerun()
            with col_cat_btns[1]:
                if st.button("None", key="cat_none", use_container_width=True):
                    filter_mgr.deselect_all_categories()
                    st.rerun()
            
            category_filter = st.multiselect(
                "Categories",
                RISK_CATEGORIES,
                default=filter_mgr.filters["risks"]["categories"],
                key="category_filter"
            )
            filter_mgr.set_risk_categories(category_filter)
            
            # Status filter with select all/none buttons
            col_status_btns = st.columns([1, 1])
            with col_status_btns[0]:
                if st.button("All", key="status_all", use_container_width=True):
                    filter_mgr.select_all_statuses()
                    st.rerun()
            with col_status_btns[1]:
                if st.button("None", key="status_none", use_container_width=True):
                    filter_mgr.deselect_all_statuses()
                    st.rerun()
            
            status_filter = st.multiselect(
                "Status",
                RISK_STATUSES,
                default=filter_mgr.filters["risks"]["statuses"],
                key="status_filter"
            )
            filter_mgr.set_risk_statuses(status_filter)
            
            # ===== TPO FILTERS =====
            st.markdown("#### 🏆 TPO Filters")
            
            show_tpos = st.checkbox(
                "🟡 Show TPOs",
                value=filter_mgr.filters["tpos"]["enabled"],
                key="show_tpos"
            )
            filter_mgr.set_tpo_enabled(show_tpos)
            
            if show_tpos:
                col_tpo_btns = st.columns([1, 1])
                with col_tpo_btns[0]:
                    if st.button("All", key="tpo_all", use_container_width=True):
                        filter_mgr.select_all_clusters()
                        st.rerun()
                with col_tpo_btns[1]:
                    if st.button("None", key="tpo_none", use_container_width=True):
                        filter_mgr.deselect_all_clusters()
                        st.rerun()
                
                tpo_cluster_filter = st.multiselect(
                    "TPO Clusters",
                    TPO_CLUSTERS,
                    default=filter_mgr.filters["tpos"]["clusters"],
                    key="tpo_cluster_filter"
                )
                filter_mgr.set_tpo_clusters(tpo_cluster_filter)
            
            # Filter validation
            is_valid, validation_msg = filter_mgr.validate()
            if not is_valid:
                st.warning(validation_msg)
            elif validation_msg:
                st.info(validation_msg)
            
            # Filter summary
            st.caption(f"📊 {filter_mgr.get_filter_summary()}")
            
            st.markdown("---")
            
            # ===== DISPLAY OPTIONS =====
            st.markdown("#### 🎨 Display Options")
            
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
            
            # Capture mode checkbox
            capture_mode = st.checkbox(
                "📍 Enable position capture",
                value=False,
                help="Enable to show capture buttons on the graph"
            )
            
            if capture_mode:
                st.info("💡 **How to save a custom layout:**\n1. Disable physics\n2. Drag nodes to desired positions\n3. Click '📍 Capture Positions' on the graph\n4. Click '📋 Copy to Clipboard'\n5. Paste in the field below and click Save")
            
            st.markdown("---")
            st.markdown("### 💾 Layout Management")
            
            # Initialize layout manager
            if "layout_manager" not in st.session_state:
                st.session_state.layout_manager = LayoutManager()
            
            layout_mgr = st.session_state.layout_manager
            
            # Save section
            with st.expander("💾 Save current layout", expanded=capture_mode):
                layout_name = st.text_input(
                    "Layout name",
                    value=f"layout_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    key="save_layout_name"
                )
                
                # Manual position input area
                st.markdown("##### 📋 Position Data (paste captured positions here)")
                position_data = st.text_area(
                    "Position JSON",
                    height=150,
                    placeholder='{\n  "node-id-1": {"x": 100, "y": 200},\n  "node-id-2": {"x": 300, "y": 400}\n}',
                    key="position_data_input",
                    label_visibility="collapsed"
                )
                
                col_save_1, col_save_2 = st.columns(2)
                
                with col_save_1:
                    if st.button("💾 Save Manual Layout", key="save_manual", use_container_width=True, type="primary"):
                        if position_data and position_data.strip():
                            try:
                                positions = json.loads(position_data)
                                if isinstance(positions, dict) and len(positions) > 0:
                                    layout_mgr.save_layout(layout_name, positions)
                                    st.session_state.selected_layout_name = layout_name
                                    st.success(f"✅ Layout '{layout_name}' saved with {len(positions)} nodes!")
                                    st.rerun()
                                else:
                                    st.error("Invalid position data: must be a non-empty JSON object")
                            except json.JSONDecodeError as e:
                                st.error(f"Invalid JSON format: {e}")
                        else:
                            st.warning("⚠️ Please paste position data first (use 'Capture Positions' button on the graph)")
                
                with col_save_2:
                    if st.button("🎨 Save as Layered", key="save_layered", use_container_width=True):
                        nodes, _ = manager.get_graph_data({"show_tpos": True})
                        positions = generate_layered_layout(nodes)
                        layout_mgr.save_layout(layout_name, positions)
                        st.session_state.selected_layout_name = layout_name
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
                                if st.session_state.selected_layout_name == selected_layout:
                                    del st.session_state.selected_layout_name
                            st.success(f"✅ Layout '{selected_layout}' deleted!")
                            st.rerun()
                    
                    # Show current layout info
                    if selected_layout:
                        layout_info = saved_layouts[selected_layout]
                        st.caption(f"📅 Saved: {layout_info['saved_at'][:16]}")
                else:
                    st.info("No saved layouts. Create one above!")
            
            # Predefined layouts section
            with st.expander("🎨 Predefined layouts"):
                col_preset_1, col_preset_2 = st.columns(2)
                
                with col_preset_1:
                    if st.button("📊 Layered", key="preset_layered", use_container_width=True, help="TPO at top, Strategic middle, Operational bottom"):
                        nodes, _ = manager.get_graph_data({"show_tpos": True})
                        positions = generate_layered_layout(nodes)
                        auto_name = f"layered_{datetime.now().strftime('%Y%m%d_%H%M')}"
                        layout_mgr.save_layout(auto_name, positions)
                        st.session_state.selected_layout_name = auto_name
                        st.success("✅ Layered layout applied!")
                        st.rerun()
                
                with col_preset_2:
                    if st.button("🗂️ By categories", key="preset_categories", use_container_width=True, help="Grouping by categories in grid"):
                        nodes, _ = manager.get_graph_data({"show_tpos": True})
                        positions = generate_category_layout(nodes)
                        auto_name = f"categories_{datetime.now().strftime('%Y%m%d_%H%M')}"
                        layout_mgr.save_layout(auto_name, positions)
                        st.session_state.selected_layout_name = auto_name
                        st.success("✅ Category layout applied!")
                        st.rerun()
                
                if st.button("🏆 By TPO Clusters", key="preset_tpo_clusters", use_container_width=True, help="Group by TPO clusters"):
                    nodes, _ = manager.get_graph_data({"show_tpos": True})
                    positions = generate_tpo_cluster_layout(nodes)
                    auto_name = f"tpo_clusters_{datetime.now().strftime('%Y%m%d_%H%M')}"
                    layout_mgr.save_layout(auto_name, positions)
                    st.session_state.selected_layout_name = auto_name
                    st.success("✅ TPO Cluster layout applied!")
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
            # Get filters from FilterManager
            filters = filter_mgr.get_filters_for_query()
            
            nodes, edges = manager.get_graph_data(filters if filters else None)
            
            # Load positions if a layout is selected
            positions = None
            if "selected_layout_name" in st.session_state:
                layout_name = st.session_state.selected_layout_name
                positions = st.session_state.layout_manager.load_layout(layout_name)
                if positions:
                    st.info(f"📍 Active layout: **{layout_name}**")
            
            render_graph(nodes, edges, color_by, physics_enabled, positions, capture_positions=capture_mode)
    
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
    
    # === TPOs TAB ===
    with tab_tpos:
        col_form, col_list = st.columns([1, 1])
        
        with col_form:
            st.markdown("### ➕ Create a TPO")
            
            with st.form("create_tpo_form", clear_on_submit=True):
                reference = st.text_input("Reference *", placeholder="E.g.: TPO-01")
                
                name = st.text_input("Name *", placeholder="E.g.: Reduce production costs by 15%")
                
                cluster = st.selectbox("Cluster *", TPO_CLUSTERS)
                
                description = st.text_area("Description", placeholder="Detailed TPO description...")
                
                submitted = st.form_submit_button("Create TPO", type="primary", use_container_width=True)
                
                if submitted:
                    if reference and name and cluster:
                        if manager.create_tpo(reference, name, cluster, description):
                            st.success(f"TPO '{reference}' created successfully!")
                            st.rerun()
                    else:
                        st.error("Reference, name and cluster are required")
        
        with col_list:
            st.markdown("### 📋 Existing TPOs")
            
            tpos = manager.get_all_tpos()
            
            if tpos:
                # Group by cluster
                clusters_data = {}
                for tpo in tpos:
                    cluster = tpo.get('cluster', 'Unknown')
                    if cluster not in clusters_data:
                        clusters_data[cluster] = []
                    clusters_data[cluster].append(tpo)
                
                for cluster in TPO_CLUSTERS:
                    if cluster in clusters_data:
                        st.markdown(f"#### 📁 {cluster}")
                        for tpo in clusters_data[cluster]:
                            with st.expander(f"🟡 {tpo['reference']}: {tpo['name']}", expanded=False):
                                st.markdown(f"**Reference:** {tpo['reference']}")
                                st.markdown(f"**Name:** {tpo['name']}")
                                st.markdown(f"**Cluster:** {tpo['cluster']}")
                                
                                if tpo.get('description'):
                                    st.markdown(f"**Description:** {tpo['description']}")
                                
                                col_edit, col_del = st.columns(2)
                                
                                with col_del:
                                    if st.button("🗑️ Delete", key=f"del_tpo_{tpo['id']}", use_container_width=True):
                                        if manager.delete_tpo(tpo['id']):
                                            st.success("TPO deleted")
                                            st.rerun()
            else:
                st.info("No TPOs created.")
    
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
    
    # === TPO IMPACTS TAB ===
    with tab_tpo_impacts:
        col_form, col_list = st.columns([1, 1])
        
        # Get strategic risks and TPOs
        strategic_risks = [r for r in manager.get_all_risks() if r['level'] == 'Strategic']
        strategic_options = {f"{r['name']}": r['id'] for r in strategic_risks}
        
        tpos = manager.get_all_tpos()
        tpo_options = {f"{t['reference']}: {t['name']}": t['id'] for t in tpos}
        
        with col_form:
            st.markdown("### ➕ Create a TPO Impact")
            st.markdown("*Link a Strategic Risk to a Top Program Objective*")
            
            if len(strategic_risks) == 0:
                st.warning("You need at least 1 Strategic risk to create a TPO impact.")
            elif len(tpos) == 0:
                st.warning("You need at least 1 TPO to create a TPO impact.")
            else:
                with st.form("create_tpo_impact_form", clear_on_submit=True):
                    risk_name = st.selectbox("Strategic Risk", list(strategic_options.keys()))
                    tpo_name = st.selectbox("Target TPO", list(tpo_options.keys()))
                    
                    impact_level = st.selectbox("Impact Level", [
                        "Low", "Medium", "High", "Critical"
                    ], index=1)
                    
                    description = st.text_area("Description",
                        placeholder="Describe how this risk impacts the TPO...")
                    
                    submitted = st.form_submit_button("Create TPO Impact", type="primary", use_container_width=True)
                    
                    if submitted:
                        risk_id = strategic_options[risk_name]
                        tpo_id = tpo_options[tpo_name]
                        
                        if manager.create_tpo_impact(risk_id, tpo_id, impact_level, description):
                            st.success("TPO Impact created!")
                            st.rerun()
        
        with col_list:
            st.markdown("### 📋 Existing TPO Impacts")
            
            impacts = manager.get_all_tpo_impacts()
            
            if impacts:
                for imp in impacts:
                    level_color = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
                    emoji = level_color.get(imp['impact_level'], "⚪")
                    
                    with st.expander(f"{emoji} {imp['risk_name']} → {imp['tpo_reference']}"):
                        st.markdown(f"**Risk:** {imp['risk_name']}")
                        st.markdown(f"**TPO:** {imp['tpo_reference']}: {imp['tpo_name']}")
                        st.markdown(f"**Impact Level:** {imp['impact_level']}")
                        
                        if imp.get('description'):
                            st.markdown(f"**Description:** {imp['description']}")
                        
                        if st.button("🗑️ Delete", key=f"del_tpo_imp_{imp['id']}", use_container_width=True):
                            if manager.delete_tpo_impact(imp['id']):
                                st.success("TPO Impact deleted")
                                st.rerun()
            else:
                st.info("No TPO impacts created.")
    
    # === IMPORT/EXPORT TAB ===
    with tab_import:
        st.markdown("### 📥 Excel Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export to Excel")
            st.markdown("*Exports Risks, Influences, TPOs, and TPO Impacts*")
            if st.button("📤 Export data", use_container_width=True):
                # Use cross-platform temp directory
                import tempfile
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, "rim_export.xlsx")
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
            st.markdown("*Imports Risks, Influences, TPOs, and TPO Impacts*")
            uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
            
            if uploaded_file is not None:
                if st.button("📥 Import data", use_container_width=True):
                    # Use cross-platform temp directory
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    filepath = os.path.join(temp_dir, uploaded_file.name)
                    with open(filepath, 'wb') as f:
                        f.write(uploaded_file.getvalue())
                    
                    with st.spinner("Importing data..."):
                        result = manager.import_from_excel(filepath)
                    
                    # Display summary
                    total_created = (
                        result["risks_created"] + 
                        result["influences_created"] + 
                        result["tpos_created"] + 
                        result["tpo_impacts_created"]
                    )
                    total_skipped = (
                        result.get("risks_skipped", 0) + 
                        result.get("influences_skipped", 0) + 
                        result.get("tpos_skipped", 0) + 
                        result.get("tpo_impacts_skipped", 0)
                    )
                    
                    if result["errors"]:
                        st.error(f"⚠️ Import completed with {len(result['errors'])} errors")
                    elif total_skipped > 0:
                        st.warning(f"✅ Import completed with {total_skipped} items skipped")
                    else:
                        st.success(f"✅ Import successful! {total_created} items created")
                    
                    # Detailed summary
                    st.markdown("##### 📊 Import Summary")
                    col_sum1, col_sum2 = st.columns(2)
                    with col_sum1:
                        st.markdown(f"""
                        **Created:**
                        - Risks: {result['risks_created']}
                        - TPOs: {result['tpos_created']}
                        - Influences: {result['influences_created']}
                        - TPO Impacts: {result['tpo_impacts_created']}
                        """)
                    with col_sum2:
                        st.markdown(f"""
                        **Skipped:**
                        - Risks: {result.get('risks_skipped', 0)}
                        - TPOs: {result.get('tpos_skipped', 0)}
                        - Influences: {result.get('influences_skipped', 0)}
                        - TPO Impacts: {result.get('tpo_impacts_skipped', 0)}
                        """)
                    
                    # Show errors if any
                    if result["errors"]:
                        with st.expander(f"❌ Errors ({len(result['errors'])})", expanded=True):
                            for error in result["errors"]:
                                st.error(error)
                    
                    # Show warnings if any
                    if result.get("warnings"):
                        with st.expander(f"⚠️ Warnings ({len(result['warnings'])})", expanded=False):
                            for warning in result["warnings"]:
                                st.warning(warning)
                    
                    # Show detailed logs
                    if result.get("logs"):
                        with st.expander(f"📋 Detailed Logs ({len(result['logs'])} entries)", expanded=False):
                            log_text = "\n".join(result["logs"])
                            st.code(log_text, language="text")
                    
                    # Offer to refresh if items were created
                    if total_created > 0:
                        if st.button("🔄 Refresh to see imported data", type="primary"):
                            st.rerun()


if __name__ == "__main__":
    main()
