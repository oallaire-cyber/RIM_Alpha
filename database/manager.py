"""
Risk Graph Manager - Facade for database operations.

Provides a unified interface for all database operations,
maintaining backward compatibility with the existing application.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection
from database.queries import risks, tpos, mitigations, influences, analysis


class RiskGraphManager:
    """
    Facade class for all database operations.
    
    This class provides a single interface to all database operations,
    delegating to specialized query modules while maintaining backward
    compatibility with the original monolithic implementation.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize the manager with connection parameters.
        
        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self._connection: Optional[Neo4jConnection] = None
    
    @property
    def driver(self):
        """Backward compatibility property for driver access."""
        if self._connection:
            return self._connection._driver
        return None
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._connection = Neo4jConnection(self.uri, self.user, self.password)
            self._connection.connect()
            return True
        except Exception as e:
            import streamlit as st
            st.error(f"Connection error: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute_query(self, query: str, parameters: dict = None) -> list:
        """
        Execute a Cypher query directly.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            List of result records
        """
        if not self._connection:
            raise RuntimeError("Not connected to database")
        return self._connection.execute_query(query, parameters)
    
    # =========================================================================
    # RISK OPERATIONS
    # =========================================================================
    
    def create_risk(
        self,
        name: str,
        level: str,
        categories: List[str],
        description: str,
        status: str,
        activation_condition: str = None,
        activation_decision_date: str = None,
        owner: str = "",
        probability: float = None,
        impact: float = None,
        origin: str = "New"
    ) -> bool:
        """Create a new risk node."""
        result = risks.create_risk(
            self._connection, name, level, categories, description, status,
            origin, owner, probability, impact, activation_condition,
            activation_decision_date
        )
        return result is not None
    
    def get_all_risks(
        self,
        level_filter=None,
        category_filter=None,
        status_filter=None,
        origin_filter=None
    ) -> list:
        """Retrieve all risks with optional filters."""
        return risks.get_all_risks(
            self._connection, level_filter, category_filter,
            status_filter, origin_filter
        )
    
    def get_risk_by_id(self, risk_id: str) -> Optional[Dict]:
        """Retrieve a risk by its ID."""
        return risks.get_risk_by_id(self._connection, risk_id)
    
    def get_risk_by_name(self, name: str) -> Optional[Dict]:
        """Retrieve a risk by its name."""
        return risks.get_risk_by_name(self._connection, name)
    
    def update_risk(
        self,
        risk_id: str,
        name: str,
        level: str,
        categories: List[str],
        description: str,
        status: str,
        activation_condition: str,
        activation_decision_date: str,
        owner: str,
        probability: float,
        impact: float,
        origin: str = "New"
    ) -> bool:
        """Update an existing risk."""
        return risks.update_risk(
            self._connection, risk_id, name, level, categories, description,
            status, origin, owner, probability, impact, activation_condition,
            activation_decision_date
        )
    
    def delete_risk(self, risk_id: str) -> bool:
        """Delete a risk and all its relationships."""
        return risks.delete_risk(self._connection, risk_id)
    
    # =========================================================================
    # INFLUENCE OPERATIONS
    # =========================================================================
    
    def create_influence(
        self,
        source_id: str,
        target_id: str,
        influence_type: str,  # Ignored - auto-determined
        strength: str,
        description: str = "",
        confidence: float = 0.8
    ) -> bool:
        """Create an influence relationship between two risks."""
        result = influences.create_influence(
            self._connection, source_id, target_id, strength, description, confidence
        )
        return result is not None
    
    def get_all_influences(self) -> list:
        """Retrieve all influence relationships."""
        return influences.get_all_influences(self._connection)
    
    def get_influences_from_risk(self, risk_id: str) -> list:
        """Get all influences originating from a specific risk."""
        return influences.get_influences_from_risk(self._connection, risk_id)
    
    def get_influences_to_risk(self, risk_id: str) -> list:
        """Get all influences pointing to a specific risk."""
        return influences.get_influences_to_risk(self._connection, risk_id)
    
    def update_influence(
        self,
        influence_id: str,
        strength: str,
        description: str,
        confidence: float
    ) -> bool:
        """Update an influence relationship."""
        return influences.update_influence(
            self._connection, influence_id, strength, description, confidence
        )
    
    def delete_influence(self, influence_id: str) -> bool:
        """Delete an influence relationship."""
        return influences.delete_influence(self._connection, influence_id)
    
    # =========================================================================
    # TPO OPERATIONS
    # =========================================================================
    
    def create_tpo(
        self,
        reference: str,
        name: str,
        cluster: str,
        description: str = ""
    ) -> bool:
        """Create a new TPO node."""
        result = tpos.create_tpo(self._connection, reference, name, cluster, description)
        return result is not None
    
    def get_all_tpos(self, cluster_filter: list = None) -> list:
        """Retrieve all TPOs with optional cluster filter."""
        return tpos.get_all_tpos(self._connection, cluster_filter)
    
    def get_tpo_by_id(self, tpo_id: str) -> Optional[Dict]:
        """Retrieve a TPO by its ID."""
        return tpos.get_tpo_by_id(self._connection, tpo_id)
    
    def get_tpo_by_reference(self, reference: str) -> Optional[Dict]:
        """Retrieve a TPO by its reference code."""
        return tpos.get_tpo_by_reference(self._connection, reference)
    
    def update_tpo(
        self,
        tpo_id: str,
        reference: str,
        name: str,
        cluster: str,
        description: str
    ) -> bool:
        """Update an existing TPO."""
        return tpos.update_tpo(
            self._connection, tpo_id, reference, name, cluster, description
        )
    
    def delete_tpo(self, tpo_id: str) -> bool:
        """Delete a TPO and all its relationships."""
        return tpos.delete_tpo(self._connection, tpo_id)
    
    # =========================================================================
    # TPO IMPACT OPERATIONS
    # =========================================================================
    
    def create_tpo_impact(
        self,
        risk_id: str,
        tpo_id: str,
        impact_level: str,
        description: str = ""
    ) -> bool:
        """Create an impact relationship from a Strategic Risk to a TPO."""
        try:
            result = tpos.create_tpo_impact(
                self._connection, risk_id, tpo_id, impact_level, description
            )
            return result is not None
        except ValueError as e:
            import streamlit as st
            st.error(str(e))
            return False
    
    def get_all_tpo_impacts(self) -> list:
        """Retrieve all TPO impact relationships."""
        return tpos.get_all_tpo_impacts(self._connection)
    
    def get_tpo_impacts_for_risk(self, risk_id: str) -> list:
        """Get all TPO impacts for a specific risk."""
        return tpos.get_tpo_impacts_for_risk(self._connection, risk_id)
    
    def get_risks_impacting_tpo(self, tpo_id: str) -> list:
        """Get all risks that impact a specific TPO."""
        return tpos.get_risks_impacting_tpo(self._connection, tpo_id)
    
    def update_tpo_impact(
        self,
        impact_id: str,
        impact_level: str,
        description: str
    ) -> bool:
        """Update a TPO impact relationship."""
        return tpos.update_tpo_impact(
            self._connection, impact_id, impact_level, description
        )
    
    def delete_tpo_impact(self, impact_id: str) -> bool:
        """Delete a TPO impact relationship."""
        return tpos.delete_tpo_impact(self._connection, impact_id)
    
    # =========================================================================
    # MITIGATION OPERATIONS
    # =========================================================================
    
    def create_mitigation(
        self,
        name: str,
        mitigation_type: str,
        status: str,
        description: str = "",
        owner: str = "",
        source_entity: str = ""
    ) -> bool:
        """Create a new mitigation node."""
        result = mitigations.create_mitigation(
            self._connection, name, mitigation_type, status,
            description, owner, source_entity
        )
        return result is not None
    
    def get_all_mitigations(
        self,
        type_filter: list = None,
        status_filter: list = None
    ) -> list:
        """Retrieve all mitigations with optional filters."""
        return mitigations.get_all_mitigations(
            self._connection, type_filter, status_filter
        )
    
    def get_mitigation_by_id(self, mitigation_id: str) -> Optional[Dict]:
        """Retrieve a mitigation by its ID."""
        return mitigations.get_mitigation_by_id(self._connection, mitigation_id)
    
    def get_mitigation_by_name(self, name: str) -> Optional[Dict]:
        """Retrieve a mitigation by its name."""
        return mitigations.get_mitigation_by_name(self._connection, name)
    
    def update_mitigation(
        self,
        mitigation_id: str,
        name: str,
        mitigation_type: str,
        status: str,
        description: str,
        owner: str,
        source_entity: str
    ) -> bool:
        """Update an existing mitigation."""
        return mitigations.update_mitigation(
            self._connection, mitigation_id, name, mitigation_type,
            status, description, owner, source_entity
        )
    
    def delete_mitigation(self, mitigation_id: str) -> bool:
        """Delete a mitigation and all its relationships."""
        return mitigations.delete_mitigation(self._connection, mitigation_id)
    
    # =========================================================================
    # MITIGATES RELATIONSHIP OPERATIONS
    # =========================================================================
    
    def create_mitigates_link(
        self,
        mitigation_id: str,
        risk_id: str,
        effectiveness: str,
        description: str = ""
    ) -> bool:
        """Create a MITIGATES relationship from a Mitigation to a Risk."""
        result = mitigations.create_mitigates_relationship(
            self._connection, mitigation_id, risk_id, effectiveness, description
        )
        return result is not None
    
    def get_all_mitigates_relationships(self) -> list:
        """Retrieve all MITIGATES relationships."""
        return mitigations.get_all_mitigates_relationships(self._connection)
    
    def get_mitigations_for_risk(self, risk_id: str) -> list:
        """Get all mitigations that mitigate a specific risk."""
        return mitigations.get_mitigations_for_risk(self._connection, risk_id)
    
    def get_risks_for_mitigation(self, mitigation_id: str) -> list:
        """Get all risks mitigated by a specific mitigation."""
        return mitigations.get_risks_for_mitigation(self._connection, mitigation_id)
    
    def update_mitigates_link(
        self,
        relationship_id: str,
        effectiveness: str,
        description: str
    ) -> bool:
        """Update a MITIGATES relationship."""
        return mitigations.update_mitigates_relationship(
            self._connection, relationship_id, effectiveness, description
        )
    
    def delete_mitigates_link(self, relationship_id: str) -> bool:
        """Delete a MITIGATES relationship."""
        return mitigations.delete_mitigates_relationship(self._connection, relationship_id)
    
    # Alias methods for consistent naming
    def create_mitigates_relationship(
        self,
        mitigation_id: str,
        risk_id: str,
        effectiveness: str,
        description: str = ""
    ) -> bool:
        """Alias for create_mitigates_link."""
        return self.create_mitigates_link(mitigation_id, risk_id, effectiveness, description)
    
    def delete_mitigates_relationship(self, relationship_id: str) -> bool:
        """Alias for delete_mitigates_link."""
        return self.delete_mitigates_link(relationship_id)
    
    def get_unmitigated_risks(self) -> list:
        """Get all risks that have no mitigations."""
        return mitigations.get_unmitigated_risks(self._connection)
    
    def get_risk_mitigation_summary(self) -> list:
        """Get mitigation summary for all risks."""
        return mitigations.get_risk_mitigation_summary(self._connection)
    
    # =========================================================================
    # STATISTICS & ANALYSIS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        return analysis.get_statistics(self._connection)
    
    def get_graph_data(self, filters: dict = None) -> tuple:
        """Get all data needed for graph visualization."""
        return analysis.get_graph_data(self._connection, filters)
    
    def get_all_edges_scored(self) -> list:
        """Get all edges with importance scores for progressive disclosure."""
        return analysis.get_all_edges_scored(self._connection)
    
    def get_all_nodes_for_selection(self) -> list:
        """Get all nodes formatted for dropdown selection."""
        return analysis.get_all_nodes_for_selection(self._connection)
    
    # =========================================================================
    # INFLUENCE NETWORK ANALYSIS
    # =========================================================================
    
    def get_influence_network(
        self,
        node_id: str,
        direction: str = "both",
        max_depth: int = None,
        level_filter: str = "all",
        include_tpos: bool = True
    ) -> tuple:
        """Get the influence network around a specific node."""
        return analysis.get_influence_network(
            self._connection, node_id, direction, max_depth,
            level_filter, include_tpos
        )
    
    def get_downstream_risks(self, risk_id: str, max_depth: int = 10) -> list:
        """Get all risks downstream (influenced by) a specific risk."""
        return influences.get_downstream_risks(self._connection, risk_id, max_depth)
    
    def get_upstream_risks(self, risk_id: str, max_depth: int = 10) -> list:
        """Get all risks upstream (influencing) a specific risk."""
        return influences.get_upstream_risks(self._connection, risk_id, max_depth)
    
    def get_influence_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> List[List[Dict]]:
        """Find all paths between two risks."""
        return influences.get_influence_path(
            self._connection, source_id, target_id, max_depth
        )
    
    def get_most_influential_risks(self, limit: int = 10) -> list:
        """Get risks with the most outgoing influences."""
        return influences.get_most_influential_risks(self._connection, limit)
    
    def get_most_influenced_risks(self, limit: int = 10) -> list:
        """Get risks with the most incoming influences."""
        return influences.get_most_influenced_risks(self._connection, limit)
    
    # =========================================================================
    # ADVANCED ANALYSIS (TO BE MOVED TO SERVICES MODULE IN PHASE 3)
    # =========================================================================
    
    def get_influence_analysis(self) -> Dict[str, Any]:
        """
        Comprehensive influence analysis including:
        - Top Propagators (risks with highest downstream impact)
        - Convergence Points (most influenced risks/TPOs)
        - Critical Paths (strongest influence chains)
        - Bottlenecks (nodes appearing in many paths)
        - Risk Clusters (tightly interconnected groups)
        """
        analysis = {
            "top_propagators": [],
            "convergence_points": [],
            "critical_paths": [],
            "bottlenecks": [],
            "risk_clusters": []
        }
        
        # Strength values for scoring
        strength_values = {"Critical": 4, "Strong": 3, "Moderate": 2, "Weak": 1}
        impact_values = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        
        # Get all nodes and edges for analysis
        all_risks = self.get_all_risks()
        all_tpos = self.get_all_tpos()
        all_influences = self.get_all_influences()
        all_tpo_impacts = self.get_all_tpo_impacts()
        
        if not all_risks:
            return analysis
        
        # Build adjacency structures
        risk_dict = {r["id"]: dict(r) for r in all_risks}
        tpo_dict = {t["id"]: dict(t) for t in all_tpos}
        
        # Outgoing edges (for propagation analysis)
        outgoing = {}  # node_id -> [(target_id, strength, edge_type)]
        # Incoming edges (for convergence analysis)
        incoming = {}  # node_id -> [(source_id, strength, edge_type)]
        
        for inf in all_influences:
            source = inf["source_id"]
            target = inf["target_id"]
            strength = strength_values.get(inf.get("strength", "Moderate"), 2)
            confidence = inf.get("confidence", 0.8) or 0.8
            score = strength * confidence
            
            if source not in outgoing:
                outgoing[source] = []
            outgoing[source].append((target, score, "INFLUENCES"))
            
            if target not in incoming:
                incoming[target] = []
            incoming[target].append((source, score, "INFLUENCES"))
        
        for impact in all_tpo_impacts:
            source = impact["risk_id"]
            target = impact["tpo_id"]
            impact_score = impact_values.get(impact.get("impact_level", "Medium"), 2)
            
            if source not in outgoing:
                outgoing[source] = []
            outgoing[source].append((target, impact_score * 1.5, "IMPACTS_TPO"))  # Boost TPO impacts
            
            if target not in incoming:
                incoming[target] = []
            incoming[target].append((source, impact_score * 1.5, "IMPACTS_TPO"))
        
        # === 1. TOP PROPAGATORS ===
        propagation_scores = {}
        
        for risk_id, risk_data in risk_dict.items():
            score = 0
            tpos_reached = set()
            risks_reached = set()
            paths_to_tpo = []
            
            # BFS with score accumulation
            visited = set()
            queue = [(risk_id, 1.0, 0, [risk_id])]
            
            while queue:
                current, cum_strength, depth, path = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                if current != risk_id:
                    decay = 0.85 ** depth
                    
                    if current in tpo_dict:
                        tpos_reached.add(current)
                        node_value = 10
                        score += node_value * cum_strength * decay
                        paths_to_tpo.append({"path": path, "score": cum_strength * decay})
                    elif current in risk_dict:
                        risks_reached.add(current)
                        node_value = 5 if risk_dict[current]["level"] == "Strategic" else 2
                        score += node_value * cum_strength * decay
                
                if current in outgoing and depth < 10:
                    for target, edge_score, edge_type in outgoing[current]:
                        if target not in visited:
                            new_strength = cum_strength * (edge_score / 4)
                            queue.append((target, new_strength, depth + 1, path + [target]))
            
            propagation_scores[risk_id] = {
                "id": risk_id,
                "name": risk_data["name"],
                "level": risk_data["level"],
                "score": round(score, 1),
                "tpos_reached": len(tpos_reached),
                "risks_reached": len(risks_reached),
                "tpo_ids": list(tpos_reached),
                "paths_to_tpo": sorted(paths_to_tpo, key=lambda x: -x["score"])[:3]
            }
        
        sorted_propagators = sorted(propagation_scores.values(), key=lambda x: -x["score"])
        analysis["top_propagators"] = sorted_propagators[:5]
        
        # === 2. CONVERGENCE POINTS ===
        convergence_scores = {}
        convergence_candidates = list(risk_dict.keys()) + list(tpo_dict.keys())
        
        for node_id in convergence_candidates:
            if node_id not in incoming:
                continue
            
            score = 0
            unique_sources = set()
            path_count = 0
            
            visited = set()
            queue = [(node_id, 1.0, 0)]
            
            while queue:
                current, cum_strength, depth = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                if current != node_id and current in risk_dict:
                    unique_sources.add(current)
                    source_weight = 1.0 if risk_dict[current]["level"] == "Operational" else 0.7
                    decay = 0.85 ** depth
                    score += cum_strength * source_weight * decay
                    path_count += 1
                
                if current in incoming and depth < 10:
                    for source, edge_score, edge_type in incoming[current]:
                        if source not in visited and source in risk_dict:
                            new_strength = cum_strength * (edge_score / 4)
                            queue.append((source, new_strength, depth + 1))
            
            if len(unique_sources) > 0:
                convergence_multiplier = 1 + (path_count / len(unique_sources)) * 0.2
                score *= convergence_multiplier
            
            is_tpo = node_id in tpo_dict
            node_data = tpo_dict[node_id] if is_tpo else risk_dict.get(node_id, {})
            
            convergence_scores[node_id] = {
                "id": node_id,
                "name": node_data.get("reference", "") + ": " + node_data.get("name", "") if is_tpo else node_data.get("name", ""),
                "level": "TPO" if is_tpo else node_data.get("level", ""),
                "node_type": "TPO" if is_tpo else "Risk",
                "score": round(score, 1),
                "source_count": len(unique_sources),
                "path_count": path_count,
                "is_high_convergence": path_count > len(unique_sources) * 1.5 if unique_sources else False
            }
        
        sorted_convergence = sorted([c for c in convergence_scores.values() if c["score"] > 0], key=lambda x: -x["score"])
        analysis["convergence_points"] = sorted_convergence[:5]
        
        # === 3. CRITICAL PATHS ===
        critical_paths = []
        
        for risk_id, risk_data in risk_dict.items():
            if risk_data["level"] != "Operational":
                continue
            
            visited = set()
            queue = [(risk_id, 1.0, [{"id": risk_id, "name": risk_data["name"], "type": "Operational"}], [])]
            
            while queue:
                current, cum_strength, path_nodes, path_edges = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                if current in tpo_dict and len(path_nodes) > 1:
                    critical_paths.append({
                        "path": path_nodes,
                        "edges": path_edges,
                        "strength": round(cum_strength, 3),
                        "length": len(path_nodes) - 1
                    })
                    continue
                
                if current in outgoing and len(path_nodes) < 6:
                    for target, edge_score, edge_type in outgoing[current]:
                        if target not in visited:
                            new_strength = cum_strength * (edge_score / 4)
                            
                            if target in tpo_dict:
                                target_info = {"id": target, "name": tpo_dict[target]["reference"], "type": "TPO"}
                            elif target in risk_dict:
                                target_info = {"id": target, "name": risk_dict[target]["name"], "type": risk_dict[target]["level"]}
                            else:
                                continue
                            
                            queue.append((target, new_strength, path_nodes + [target_info], path_edges + [{"type": edge_type, "score": edge_score}]))
        
        critical_paths.sort(key=lambda x: -x["strength"])
        analysis["critical_paths"] = critical_paths[:5]
        
        # === 4. BOTTLENECKS ===
        node_path_count = {}
        total_paths_to_tpo = 0
        
        for risk_id, risk_data in risk_dict.items():
            visited_paths = set()
            queue = [(risk_id, [risk_id])]
            
            while queue:
                current, path = queue.pop(0)
                path_key = tuple(path)
                
                if path_key in visited_paths:
                    continue
                visited_paths.add(path_key)
                
                if current in tpo_dict and len(path) > 1:
                    total_paths_to_tpo += 1
                    for node in path[1:-1]:
                        if node in risk_dict:
                            if node not in node_path_count:
                                node_path_count[node] = 0
                            node_path_count[node] += 1
                    continue
                
                if current in outgoing and len(path) < 6:
                    for target, _, _ in outgoing[current]:
                        if target not in path:
                            queue.append((target, path + [target]))
        
        bottlenecks = []
        for node_id, count in node_path_count.items():
            if count >= 2 and node_id in risk_dict:
                bottlenecks.append({
                    "id": node_id,
                    "name": risk_dict[node_id]["name"],
                    "level": risk_dict[node_id]["level"],
                    "path_count": count,
                    "total_paths": total_paths_to_tpo,
                    "percentage": round(count / max(total_paths_to_tpo, 1) * 100, 1)
                })
        
        bottlenecks.sort(key=lambda x: -x["path_count"])
        analysis["bottlenecks"] = bottlenecks[:5]
        
        # === 5. RISK CLUSTERS ===
        undirected = {}
        for source in outgoing:
            if source not in risk_dict:
                continue
            for target, score, _ in outgoing[source]:
                if target not in risk_dict:
                    continue
                if source not in undirected:
                    undirected[source] = set()
                if target not in undirected:
                    undirected[target] = set()
                undirected[source].add(target)
                undirected[target].add(source)
        
        visited = set()
        clusters = []
        
        for start_node in undirected:
            if start_node in visited:
                continue
            
            cluster = set()
            queue = [start_node]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                cluster.add(current)
                
                for neighbor in undirected.get(current, []):
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            if len(cluster) >= 2:
                internal_edges = 0
                for node in cluster:
                    for target, _, _ in outgoing.get(node, []):
                        if target in cluster:
                            internal_edges += 1
                
                levels = [risk_dict[n]["level"] for n in cluster if n in risk_dict]
                categories = []
                for n in cluster:
                    if n in risk_dict:
                        categories.extend(risk_dict[n].get("categories", []))
                
                primary_category = max(set(categories), key=categories.count) if categories else "Mixed"
                
                clusters.append({
                    "nodes": list(cluster),
                    "node_names": [risk_dict[n]["name"] for n in cluster if n in risk_dict],
                    "size": len(cluster),
                    "internal_edges": internal_edges,
                    "density": round(internal_edges / (len(cluster) * (len(cluster) - 1)) if len(cluster) > 1 else 0, 2),
                    "primary_category": primary_category,
                    "levels": {"Strategic": levels.count("Strategic"), "Operational": levels.count("Operational")}
                })
        
        clusters.sort(key=lambda x: (-x["size"], -x["density"]))
        analysis["risk_clusters"] = clusters[:5]
        
        return analysis
    
    def get_mitigation_analysis(self) -> Dict[str, Any]:
        """
        Comprehensive mitigation analysis including:
        - Coverage overview (risks with/without mitigations)
        - Mitigation effectiveness distribution
        - Unmitigated high-priority risks
        - Cross-reference with influence analysis
        """
        analysis = {
            "coverage_stats": {},
            "unmitigated_risks": [],
            "partially_mitigated_risks": [],
            "well_covered_risks": [],
            "mitigation_effectiveness": {},
            "high_priority_unmitigated": [],
            "risk_mitigation_summary": []
        }
        
        # Get all data
        all_risks = self.get_all_risks()
        all_mitigations = self.get_all_mitigations()
        all_mitigates = self.get_all_mitigates_relationships()
        
        if not all_risks:
            return analysis
        
        # Build risk-to-mitigations mapping
        risk_mitigations = {}  # risk_id -> list of {mitigation, effectiveness}
        for rel in all_mitigates:
            risk_id = rel.get("risk_id")
            if not risk_id:
                continue
            if risk_id not in risk_mitigations:
                risk_mitigations[risk_id] = []
            risk_mitigations[risk_id].append({
                "mitigation_id": rel.get("mitigation_id"),
                "mitigation_name": rel.get("mitigation_name", "Unknown"),
                "mitigation_type": rel.get("mitigation_type", "Unknown"),
                "effectiveness": rel.get("effectiveness", "Medium"),
                "description": rel.get("description", "")
            })
        
        # Build mitigation-to-risks mapping
        mitigation_risks = {}  # mitigation_id -> list of {risk, effectiveness}
        for rel in all_mitigates:
            mit_id = rel.get("mitigation_id")
            if not mit_id:
                continue
            if mit_id not in mitigation_risks:
                mitigation_risks[mit_id] = []
            mitigation_risks[mit_id].append({
                "risk_id": rel.get("risk_id"),
                "risk_name": rel.get("risk_name", "Unknown"),
                "risk_level": rel.get("risk_level", "Unknown"),
                "effectiveness": rel.get("effectiveness", "Medium")
            })
        
        # Calculate coverage statistics
        total_risks = len(all_risks)
        mitigated_risk_ids = set(risk_mitigations.keys())
        all_risk_ids = set(r["id"] for r in all_risks)
        unmitigated_risk_ids = all_risk_ids - mitigated_risk_ids
        
        analysis["coverage_stats"] = {
            "total_risks": total_risks,
            "mitigated_risks": len(mitigated_risk_ids),
            "unmitigated_risks": len(unmitigated_risk_ids),
            "coverage_percentage": round(len(mitigated_risk_ids) / total_risks * 100, 1) if total_risks > 0 else 0,
            "total_mitigations": len(all_mitigations),
            "total_links": len(all_mitigates)
        }
        
        # Categorize risks by mitigation coverage
        effectiveness_values = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        
        risk_dict = {r["id"]: dict(r) for r in all_risks}
        
        for risk in all_risks:
            risk_id = risk["id"]
            mits = risk_mitigations.get(risk_id, [])
            
            # Calculate mitigation score
            mit_score = 0
            for mit in mits:
                eff_value = effectiveness_values.get(mit.get("effectiveness", "Medium"), 2)
                mit_score += eff_value
            
            # Check mitigation statuses
            implemented_count = 0
            proposed_count = 0
            for mit in mits:
                mit_detail = self.get_mitigation_by_id(mit.get("mitigation_id"))
                if mit_detail:
                    status = mit_detail.get("status", "Unknown")
                    if status == "Implemented":
                        implemented_count += 1
                    elif status in ["Proposed", "In Progress"]:
                        proposed_count += 1
            
            risk_summary = {
                "id": risk_id,
                "name": risk["name"],
                "level": risk["level"],
                "origin": risk.get("origin", "New"),
                "exposure": risk.get("exposure") or 0,
                "categories": risk.get("categories", []),
                "mitigation_count": len(mits),
                "implemented_count": implemented_count,
                "proposed_count": proposed_count,
                "mitigation_score": mit_score,
                "mitigations": mits
            }
            
            analysis["risk_mitigation_summary"].append(risk_summary)
            
            if len(mits) == 0:
                analysis["unmitigated_risks"].append(risk_summary)
            elif implemented_count == 0:
                analysis["partially_mitigated_risks"].append(risk_summary)
            elif implemented_count >= 2 or (implemented_count >= 1 and mit_score >= 6):
                analysis["well_covered_risks"].append(risk_summary)
        
        # Sort unmitigated by exposure
        analysis["unmitigated_risks"].sort(key=lambda x: -(x["exposure"] or 0))
        analysis["partially_mitigated_risks"].sort(key=lambda x: -(x["exposure"] or 0))
        
        # Get influence analysis to cross-reference
        try:
            influence_analysis = self.get_influence_analysis()
            
            top_propagator_ids = set(p["id"] for p in influence_analysis.get("top_propagators", []))
            convergence_ids = set(c["id"] for c in influence_analysis.get("convergence_points", []) if c.get("node_type") == "Risk")
            bottleneck_ids = set(b["id"] for b in influence_analysis.get("bottlenecks", []))
            
            high_priority_ids = top_propagator_ids | convergence_ids | bottleneck_ids
            
            for risk_summary in analysis["unmitigated_risks"]:
                if risk_summary["id"] in high_priority_ids:
                    flags = []
                    if risk_summary["id"] in top_propagator_ids:
                        flags.append("Top Propagator")
                    if risk_summary["id"] in convergence_ids:
                        flags.append("Convergence Point")
                    if risk_summary["id"] in bottleneck_ids:
                        flags.append("Bottleneck")
                    risk_summary["influence_flags"] = flags
                    analysis["high_priority_unmitigated"].append(risk_summary)
            
            for risk_summary in analysis["partially_mitigated_risks"]:
                if risk_summary["id"] in high_priority_ids:
                    flags = []
                    if risk_summary["id"] in top_propagator_ids:
                        flags.append("Top Propagator")
                    if risk_summary["id"] in convergence_ids:
                        flags.append("Convergence Point")
                    if risk_summary["id"] in bottleneck_ids:
                        flags.append("Bottleneck")
                    risk_summary["influence_flags"] = flags
        except Exception:
            pass
        
        # Mitigation effectiveness distribution
        effectiveness_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for rel in all_mitigates:
            eff = rel.get("effectiveness", "Medium")
            if eff in effectiveness_dist:
                effectiveness_dist[eff] += 1
        
        analysis["mitigation_effectiveness"] = effectiveness_dist
        
        return analysis
    
    def get_risk_mitigation_details(self, risk_id: str) -> Dict[str, Any]:
        """
        Get detailed mitigation information for a specific risk.
        Includes cross-reference with influence analysis.
        """
        risk = self.get_risk_by_id(risk_id)
        if not risk:
            return None
        
        risk_mitigations = self.get_mitigations_for_risk(risk_id)
        
        # Reformat mitigations to expected structure
        formatted_mitigations = []
        for m in risk_mitigations:
            formatted_mitigations.append({
                "id": m.get("id"),
                "mitigation_id": m.get("id"),
                "mitigation_name": m.get("name"),
                "name": m.get("name"),
                "type": m.get("type"),
                "mitigation_type": m.get("type"),
                "status": m.get("status"),
                "owner": m.get("owner"),
                "effectiveness": m.get("effectiveness", "Medium"),
                "description": m.get("rel_description", "")
            })
        
        # Get influence analysis for this risk
        influence_info = {}
        try:
            influence_analysis = self.get_influence_analysis()
            
            for prop in influence_analysis.get("top_propagators", []):
                if prop["id"] == risk_id:
                    influence_info["is_top_propagator"] = True
                    influence_info["propagation_score"] = prop["score"]
                    influence_info["tpos_reached"] = prop.get("tpos_reached", 0)
                    break
            
            for conv in influence_analysis.get("convergence_points", []):
                if conv["id"] == risk_id:
                    influence_info["is_convergence_point"] = True
                    influence_info["convergence_score"] = conv["score"]
                    influence_info["source_count"] = conv.get("source_count", 0)
                    break
            
            for bn in influence_analysis.get("bottlenecks", []):
                if bn["id"] == risk_id:
                    influence_info["is_bottleneck"] = True
                    influence_info["path_percentage"] = bn.get("percentage", 0)
                    break
        except Exception:
            pass
        
        # Calculate coverage assessment
        effectiveness_values = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        total_score = sum(effectiveness_values.get(m.get("effectiveness", "Medium"), 2) for m in formatted_mitigations)
        implemented = [m for m in formatted_mitigations if m.get("status") == "Implemented"]
        
        if len(formatted_mitigations) == 0:
            coverage_status = "unmitigated"
        elif len(implemented) == 0:
            coverage_status = "proposed_only"
        elif len(implemented) >= 2 or total_score >= 6:
            coverage_status = "well_covered"
        else:
            coverage_status = "partially_covered"
        
        return {
            "risk": risk,
            "mitigations": formatted_mitigations,
            "mitigation_count": len(formatted_mitigations),
            "implemented_count": len(implemented),
            "total_effectiveness_score": total_score,
            "coverage_status": coverage_status,
            "influence_info": influence_info
        }
    
    def get_mitigation_impact_details(self, mitigation_id: str) -> Dict[str, Any]:
        """
        Get detailed impact information for a specific mitigation.
        Shows all risks it addresses and their strategic importance.
        """
        mitigation = self.get_mitigation_by_id(mitigation_id)
        if not mitigation:
            return None
        
        addressed_risks = self.get_risks_for_mitigation(mitigation_id)
        
        # Get influence analysis to check strategic importance
        strategic_impacts = []
        try:
            influence_analysis = self.get_influence_analysis()
            
            top_propagator_ids = set(p["id"] for p in influence_analysis.get("top_propagators", []))
            convergence_ids = set(c["id"] for c in influence_analysis.get("convergence_points", []) if c.get("node_type") == "Risk")
            bottleneck_ids = set(b["id"] for b in influence_analysis.get("bottlenecks", []))
            
            for risk in addressed_risks:
                flags = []
                if risk["id"] in top_propagator_ids:
                    flags.append("Top Propagator")
                if risk["id"] in convergence_ids:
                    flags.append("Convergence Point")
                if risk["id"] in bottleneck_ids:
                    flags.append("Bottleneck")
                if flags:
                    strategic_impacts.append({
                        "risk_id": risk["id"],
                        "risk_name": risk["name"],
                        "flags": flags
                    })
        except Exception:
            pass
        
        # Count by risk level
        strategic_count = sum(1 for r in addressed_risks if r.get("level") == "Strategic")
        operational_count = sum(1 for r in addressed_risks if r.get("level") == "Operational")
        
        # Calculate total exposure covered
        total_exposure = sum(r.get("exposure") or 0 for r in addressed_risks)
        
        return {
            "mitigation": mitigation,
            "risks": addressed_risks,  # Use 'risks' key expected by panel
            "addressed_risks": addressed_risks,  # Also include for backward compatibility
            "risk_count": len(addressed_risks),
            "strategic_count": strategic_count,
            "operational_count": operational_count,
            "total_exposure_covered": round(total_exposure, 2),
            "strategic_impacts": strategic_impacts,
            "addresses_high_priority": len(strategic_impacts) > 0
        }
    
    def get_coverage_gap_analysis(self) -> Dict[str, Any]:
        """
        Analyze gaps in mitigation coverage.
        
        Note: Full implementation in services/mitigation_analysis.py (Phase 3)
        """
        unmitigated = self.get_unmitigated_risks()
        all_risks = self.get_all_risks()
        
        # Calculate average exposure
        exposures = [r.get("exposure", 0) or 0 for r in all_risks]
        avg_exposure = sum(exposures) / len(exposures) if exposures else 0
        high_threshold = avg_exposure * 1.2
        
        # Critical unmitigated (high exposure, no mitigations)
        critical_unmitigated = [
            r for r in unmitigated
            if (r.get("exposure") or 0) >= high_threshold
        ]
        
        # Strategic gaps (strategic risks without adequate coverage)
        strategic_unmitigated = [
            r for r in unmitigated
            if r.get("level") == "Strategic"
        ]
        
        # Category coverage
        category_coverage = {}
        for category in ["Programme", "Produit", "Industriel", "Supply Chain"]:
            cat_risks = [r for r in all_risks if category in (r.get("categories") or [])]
            cat_unmitigated = [r for r in unmitigated if category in (r.get("categories") or [])]
            
            total = len(cat_risks)
            mitigated = total - len(cat_unmitigated)
            percentage = (mitigated / total * 100) if total > 0 else 100
            
            category_coverage[category] = {
                "total": total,
                "mitigated": mitigated,
                "unmitigated": len(cat_unmitigated),
                "percentage": percentage
            }
        
        return {
            "critical_unmitigated": critical_unmitigated,
            "strategic_gaps": strategic_unmitigated,
            "category_coverage": category_coverage,
            "high_exposure_threshold": high_threshold
        }
    
    # =========================================================================
    # IMPORT/EXPORT OPERATIONS
    # =========================================================================
    
    def export_to_excel(self, filepath: str) -> bool:
        """
        Export all data to an Excel file.
        
        Args:
            filepath: Path to save the Excel file
        
        Returns:
            True if export successful
        """
        from services.export_service import export_to_excel
        
        return export_to_excel(
            filepath=filepath,
            risks=self.get_all_risks(),
            influences=self.get_all_influences(),
            tpos=self.get_all_tpos(),
            tpo_impacts=self.get_all_tpo_impacts(),
            mitigations=self.get_all_mitigations(),
            mitigates_relationships=self.get_all_mitigates_relationships()
        )
    
    def export_to_excel_bytes(self) -> bytes:
        """
        Export all data to Excel and return as bytes.
        
        Returns:
            Excel file content as bytes
        """
        from services.export_service import export_to_excel_bytes
        
        return export_to_excel_bytes(
            risks=self.get_all_risks(),
            influences=self.get_all_influences(),
            tpos=self.get_all_tpos(),
            tpo_impacts=self.get_all_tpo_impacts(),
            mitigations=self.get_all_mitigations(),
            mitigates_relationships=self.get_all_mitigates_relationships()
        )
    
    def import_from_excel(self, filepath: str) -> dict:
        """
        Import data from an Excel file.
        
        Args:
            filepath: Path to the Excel file
        
        Returns:
            ImportResult as dictionary with created counts and errors
        """
        from services.import_service import ExcelImporter
        
        importer = ExcelImporter(
            create_risk_fn=self.create_risk,
            create_tpo_fn=self.create_tpo,
            create_influence_fn=self.create_influence,
            create_tpo_impact_fn=self.create_tpo_impact,
            create_mitigation_fn=self.create_mitigation,
            create_mitigates_fn=self.create_mitigates_relationship,
            get_all_risks_fn=self.get_all_risks,
            get_all_tpos_fn=self.get_all_tpos,
            get_all_mitigations_fn=self.get_all_mitigations
        )
        
        result = importer.import_from_excel(filepath)
        return result.to_dict()
