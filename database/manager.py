"""
Risk Graph Manager - Facade for database operations.

Provides a unified interface for all database operations,
maintaining backward compatibility with the existing application.
"""

from typing import List, Dict, Any, Optional
from database.connection import Neo4jConnection
from database.queries import risks, mitigations, influences, analysis, generic_entity, generic_relationship


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
        origin: str = "New",
        subtype: str = None,
        ext_fields: dict = None,
    ) -> Optional[str]:
        """Create a new risk node. Returns the created node ID or None."""
        result = risks.create_risk(
            self._connection, name, level, categories, description, status,
            origin, owner, probability, impact, activation_condition,
            activation_decision_date, subtype=subtype, ext_fields=ext_fields
        )
        return result
    
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
        origin: str = "New",
        subtype: str = None,
        ext_fields: dict = None,
    ) -> bool:
        """Update an existing risk."""
        return risks.update_risk(
            self._connection, risk_id, name, level, categories, description,
            status, origin, owner, probability, impact, activation_condition,
            activation_decision_date, subtype=subtype, ext_fields=ext_fields
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
        
    def get_semantic_influences(self) -> list:
        """
        Retrieve all relationships that have semantic type 'influence'.
        This includes the kernel INFLUENCES, MITIGATES, and any custom
        relationships configured as semantic: influence in the schema.
        
        Returns:
            List of normalized relationship dictionaries with source_id and target_id.
        """
        from core import get_registry
        registry = get_registry()
        semantic_rels = []
        
        # Kernel: influences
        inf_type = registry.get_influence_type()
        if inf_type and inf_type.semantic == "influence":
            semantic_rels.extend(self.get_all_influences())
            
        # Kernel: mitigates
        mitigates_type = registry.get_mitigates_type()
        if mitigates_type and mitigates_type.semantic == "influence":
            mitigates = self.get_all_mitigates_relationships()
            # Normalize to source_id/target_id format for the exposure engine
            for m in mitigates:
                m_normalized = dict(m)
                m_normalized["source_id"] = m.get("mitigation_id")
                m_normalized["target_id"] = m.get("risk_id")
                semantic_rels.append(m_normalized)
                
        # Additional relationships configured as 'influence'
        for rel_id, rel_def in registry.get_additional_relationship_types().items():
            if rel_def.semantic == "influence":
                custom_rels = self.get_relationships(rel_id)
                semantic_rels.extend(custom_rels)
                
        return semantic_rels
    
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
    # MITIGATION OPERATIONS
    # =========================================================================
    
    def create_mitigation(
        self,
        name: str,
        mitigation_type: str,
        status: str,
        description: str = "",
        owner: str = "",
        source_entity: str = "",
        ext_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new mitigation node. Returns the created node ID or None."""
        result = mitigations.create_mitigation(
            self._connection, name, mitigation_type, status,
            description, owner, source_entity, ext_fields
        )
        return result
    
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
    # GENERIC ENTITY OPERATIONS (Context Nodes / Additional Entities)
    # =========================================================================
    
    def create_generic_entity(self, entity_type, data: dict) -> dict:
        """Create a generic entity."""
        return generic_entity.create_entity(self.driver, entity_type, data)
        
    def get_generic_entities(self, entity_type, filters: dict = None) -> list:
        """Get generic entities of a specific type."""
        return generic_entity.get_all_entities(self.driver, entity_type, filters)
        
    def get_generic_entity_by_id(self, entity_type, entity_id: str) -> Optional[dict]:
        """Get a generic entity by ID."""
        return generic_entity.get_entity_by_id(self.driver, entity_type, entity_id)
        
    def update_generic_entity(self, entity_type, entity_id: str, data: dict) -> Optional[dict]:
        """Update a generic entity."""
        return generic_entity.update_entity(self.driver, entity_type, entity_id, data)
        
    def delete_generic_entity(self, entity_type, entity_id: str, cascade: bool = True) -> bool:
        """Delete a generic entity."""
        return generic_entity.delete_entity(self.driver, entity_type, entity_id, cascade)

    # =========================================================================
    # GENERIC RELATIONSHIP OPERATIONS (Context Edges)
    # =========================================================================
    
    def create_generic_relationship(self, rel_type, source_id: str, target_id: str, 
                                    source_type, target_type, data: dict = None) -> dict:
        """Create a generic relationship."""
        return generic_relationship.create_relationship(
            self.driver, rel_type, source_id, target_id, source_type, target_type, data
        )
        
    def get_generic_relationships(self, rel_type, filters: dict = None) -> list:
        """Get generic relationships of a specific type."""
        return generic_relationship.get_all_relationships(self.driver, rel_type, filters)
        
    def get_generic_relationship_by_id(self, rel_type, rel_id: str) -> Optional[dict]:
        """Get a generic relationship by ID."""
        return generic_relationship.get_relationship_by_id(self.driver, rel_type, rel_id)
        
    def update_generic_relationship(self, rel_type, rel_id: str, data: dict) -> Optional[dict]:
        """Update a generic relationship."""
        return generic_relationship.update_relationship(self.driver, rel_type, rel_id, data)
        
    def delete_generic_relationship(self, rel_type, rel_id: str) -> bool:
        """Delete a generic relationship."""
        return generic_relationship.delete_relationship(self.driver, rel_type, rel_id)

    # =========================================================================
    # STATISTICS & ANALYSIS
    # =========================================================================
    
    def get_statistics(self, active_scopes: list = None) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        return analysis.get_statistics(self._connection, active_scopes)
    
    def get_graph_data(self, filters: dict = None) -> tuple:
        """Get all data needed for graph visualization."""
        return analysis.get_graph_data(self._connection, filters)
    
    def get_all_edges_scored(self) -> list:
        """Get all edges with importance scores for progressive disclosure."""
        return analysis.get_all_edges_scored(self._connection)
    
    def get_all_nodes_for_selection(self, active_scopes: list = None) -> list:
        """Get all nodes formatted for dropdown selection."""
        return analysis.get_all_nodes_for_selection(self._connection, active_scopes)
    
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
    
    def get_influence_analysis(self, active_scopes: list = None) -> Dict[str, Any]:
        """
        Comprehensive influence analysis including:
        - Top Propagators (risks with highest downstream impact)
        - Convergence Points (most influenced risks/TPOs)
        - Critical Paths (strongest influence chains)
        - Bottlenecks (nodes appearing in many paths)
        - Risk Clusters (tightly interconnected groups)
        
        Args:
            active_scopes: Optional list of active AnalysisScopeConfig objects.
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
        all_influences = self.get_semantic_influences()
        
        # Pre-filter by scope if provided
        if active_scopes:
            scope_node_ids = set()
            scope_include_neighbors = False
            for scope in active_scopes:
                scope_node_ids.update(scope.node_ids)
                if getattr(scope, "include_connected_edges", False):
                    scope_include_neighbors = True
            
            filtered_risks = [r for r in all_risks if r["id"] in scope_node_ids]
            filtered_risk_ids = {r["id"] for r in filtered_risks}
            
            if scope_include_neighbors:
                neighbor_risk_ids = set()
                for inf in all_influences:
                    src, tgt = inf["source_id"], inf["target_id"]
                    if src in filtered_risk_ids:
                        neighbor_risk_ids.add(tgt)
                    if tgt in filtered_risk_ids:
                        neighbor_risk_ids.add(src)
                filtered_risk_ids.update(neighbor_risk_ids)
                filtered_risks = [r for r in all_risks if r["id"] in filtered_risk_ids]
            
            all_risks = filtered_risks
            
            all_influences = [
                i for i in all_influences
                if i["source_id"] in filtered_risk_ids and i["target_id"] in filtered_risk_ids
            ]
        
        if not all_risks:
            return analysis
        
        # Build adjacency structures
        risk_dict = {r["id"]: dict(r) for r in all_risks}
        
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
        
        # === 1. TOP PROPAGATORS ===
        propagation_scores = {}
        
        for risk_id, risk_data in risk_dict.items():
            score = 0
            risks_reached = set()
            
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
                    
                    if current in risk_dict:
                        risks_reached.add(current)
                        node_value = 5 if risk_dict[current]["level"] == "Business" else 2
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
                "risks_reached": len(risks_reached),
            }
        
        sorted_propagators = sorted(propagation_scores.values(), key=lambda x: -x["score"])
        analysis["top_propagators"] = sorted_propagators[:5]
        
        # === 2. CONVERGENCE POINTS ===
        convergence_scores = {}
        convergence_candidates = list(risk_dict.keys())
        
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
            
            node_data = risk_dict.get(node_id, {})
            
            convergence_scores[node_id] = {
                "id": node_id,
                "name": node_data.get("name", ""),
                "level": node_data.get("level", ""),
                "node_type": "Risk",
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
                    "levels": {"Business": levels.count("Business"), "Operational": levels.count("Operational")}
                })
        
        clusters.sort(key=lambda x: (-x["size"], -x["density"]))
        analysis["risk_clusters"] = clusters[:5]
        
        return analysis
    
    def get_mitigation_analysis(self, active_scopes: list = None) -> Dict[str, Any]:
        """
        Comprehensive mitigation analysis including:
        - Coverage overview (risks with/without mitigations)
        - Mitigation effectiveness distribution
        - Unmitigated high-priority risks
        - Cross-reference with influence analysis
        
        Args:
            active_scopes: Optional list of active AnalysisScopeConfig objects.
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
        
        # Pre-filter by scope if provided
        if active_scopes:
            scope_node_ids = set()
            scope_include_neighbors = False
            for scope in active_scopes:
                scope_node_ids.update(scope.node_ids)
                if getattr(scope, "include_connected_edges", False):
                    scope_include_neighbors = True
            
            filtered_risks = [r for r in all_risks if r["id"] in scope_node_ids]
            filtered_risk_ids = {r["id"] for r in filtered_risks}
            
            if scope_include_neighbors:
                all_influences = self.get_semantic_influences()
                neighbor_risk_ids = set()
                for inf in all_influences:
                    src, tgt = inf["source_id"], inf["target_id"]
                    if src in filtered_risk_ids:
                        neighbor_risk_ids.add(tgt)
                    if tgt in filtered_risk_ids:
                        neighbor_risk_ids.add(src)
                filtered_risk_ids.update(neighbor_risk_ids)
                filtered_risks = [r for r in all_risks if r["id"] in filtered_risk_ids]
                
            all_risks = filtered_risks
            
            # Keep mitigates relationships targeting scoped risks
            all_mitigates = [mr for mr in all_mitigates if mr.get("risk_id") in filtered_risk_ids]
            # Keep only mitigations connected to scoped risks
            connected_mit_ids = {mr["mitigation_id"] for mr in all_mitigates}
            all_mitigations = [m for m in all_mitigations if m["id"] in connected_mit_ids]
        
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
            influence_analysis = self.get_influence_analysis(active_scopes=active_scopes)
            
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
        strategic_count = sum(1 for r in addressed_risks if r.get("level") == "Business")
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
        
        # Business gaps (business risks without adequate coverage)
        strategic_unmitigated = [
            r for r in unmitigated
            if r.get("level") == "Business"
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
        Export all data (core + context) to an Excel file.

        Sheets produced:
          Core:    Risks, Influences, Mitigations, Mitigates
          Context: CN_{type_id} per ContextNode type, CE_{rel_id} per ContextEdge type

        Args:
            filepath: Path to save the Excel file

        Returns:
            True if export successful
        """
        from services.export_service import export_to_excel
        from core import get_registry

        registry = get_registry()
        context_nodes_data, context_edges_data = self._collect_context_data(registry)

        return export_to_excel(
            filepath=filepath,
            risks=self.get_all_risks(),
            influences=self.get_semantic_influences(),
            mitigations=self.get_all_mitigations(),
            mitigates_relationships=self.get_all_mitigates_relationships(),
            context_nodes_data=context_nodes_data,
            context_edges_data=context_edges_data,
        )

    def export_to_excel_bytes(self) -> bytes:
        """
        Export all data (core + context) to Excel and return as bytes.

        Returns:
            Excel file content as bytes
        """
        from services.export_service import export_to_excel_bytes
        from core import get_registry

        registry = get_registry()
        context_nodes_data, context_edges_data = self._collect_context_data(registry)

        return export_to_excel_bytes(
            risks=self.get_all_risks(),
            influences=self.get_semantic_influences(),
            mitigations=self.get_all_mitigations(),
            mitigates_relationships=self.get_all_mitigates_relationships(),
            context_nodes_data=context_nodes_data,
            context_edges_data=context_edges_data,
        )

    def import_from_excel(self, filepath: str) -> dict:
        """
        Import data from an Excel file (core + context sheets).

        Args:
            filepath: Path to the Excel file

        Returns:
            ImportResult as dictionary with created/skipped counts and errors
        """
        from services.import_service import ExcelImporter
        from core import get_registry

        registry = get_registry()

        importer = ExcelImporter(
            create_risk_fn=self.create_risk,
            create_influence_fn=self.create_influence,
            create_mitigation_fn=self.create_mitigation,
            create_mitigates_fn=self.create_mitigates_relationship,
            get_all_risks_fn=self.get_all_risks,
            get_all_mitigations_fn=self.get_all_mitigations,
            # Context data callbacks
            create_generic_entity_fn=self.create_entity,
            get_generic_entities_fn=self.get_entities,
            create_generic_relationship_fn=self.create_relationship,
            registry=registry,
        )

        result = importer.import_from_excel(filepath)
        return result.to_dict()

    def export_to_json(self) -> Dict[str, Any]:
        """
        Export the full graph as a JSON-serialisable dict (backup).

        Returns:
            Dict with schema_version, exported_at, and all entity collections.
        """
        from services.backup_service import export_graph_to_json
        from core import get_registry

        return export_graph_to_json(manager=self, registry=get_registry())

    def import_from_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore the graph from a JSON backup dict (upserts by name).

        Args:
            data: Backup dict as produced by export_to_json().

        Returns:
            Summary dict with created/skipped counts and error list.
        """
        from services.backup_service import import_graph_from_json
        from core import get_registry

        return import_graph_from_json(manager=self, data=data, registry=get_registry())

    def _collect_context_data(
        self, registry
    ) -> tuple:
        """
        Collect all ContextNode and ContextEdge data keyed by type_id.

        Returns:
            Tuple of (context_nodes_data, context_edges_data) dicts.
        """
        kernel_rel_ids = {"influences", "mitigates"}
        core_entity_ids = {"risk", "mitigation"}

        context_nodes_data: Dict[str, list] = {}
        for entity_type in registry.entity_types.values():
            type_id = entity_type.type_id
            if type_id in core_entity_ids:
                continue
            entities = self.get_entities(type_id) or []
            if entities:
                context_nodes_data[type_id] = entities

        context_edges_data: Dict[str, list] = {}
        for rel_type in registry.relationship_types.values():
            rel_id = getattr(rel_type, "type_id", None) or getattr(rel_type, "id", None)
            if not rel_id or rel_id in kernel_rel_ids:
                continue
            edges = self.get_relationships(rel_id) or []
            if edges:
                context_edges_data[rel_id] = edges

        return context_nodes_data, context_edges_data
    
    # =========================================================================
    # EXPOSURE CALCULATION
    # =========================================================================
    
    def calculate_exposure(self, scope_node_ids=None, include_neighbors=False) -> Dict[str, Any]:
        """
        Calculate exposure scores for all risks (or scoped risks).
        
        This method runs the exposure calculation considering:
        - Base exposure (Likelihood × Impact)
        - Mitigation effectiveness
        - Influence limitations from upstream risks
        
        Args:
            scope_node_ids: Optional list of node IDs to restrict calculation to.
                           When provided, only risks within this set (and their
                           connected mitigations/influences) are included.
            include_neighbors: If True and scope_node_ids is set, also include
                             1-hop risk neighbors of the scoped risks.
        
        Returns:
            GlobalExposureResult as dictionary with all metrics
        """
        from services.exposure_calculator import calculate_exposure
        
        # Gather all required data
        risks = self.get_all_risks()
        influences = self.get_semantic_influences()
        mitigations = self.get_all_mitigations()
        mitigates_rels = self.get_all_mitigates_relationships()
        
        # Apply scope filtering if active
        if scope_node_ids is not None:
            scope_set = set(scope_node_ids)
            
            # Step 1: Get risk IDs in scope
            risk_ids = {r["id"] for r in risks if r["id"] in scope_set}
            
            # Step 2: Optionally expand to 1-hop risk neighbors
            if include_neighbors:
                for inf in influences:
                    src, tgt = inf.get("source_id"), inf.get("target_id")
                    if src in risk_ids:
                        risk_ids.add(tgt)
                    if tgt in risk_ids:
                        risk_ids.add(src)
            
            # Step 3: Filter risks to scoped set
            risks = [r for r in risks if r["id"] in risk_ids]
            
            # Step 4: Keep influences between scoped risks
            influences = [
                i for i in influences
                if i.get("source_id") in risk_ids and i.get("target_id") in risk_ids
            ]
            
            # Step 5: Keep mitigates relationships that target scoped risks,
            # then keep only the mitigations involved in those relationships
            mitigates_rels = [
                mr for mr in mitigates_rels
                if mr.get("risk_id") in risk_ids
            ]
            connected_mit_ids = {mr["mitigation_id"] for mr in mitigates_rels}
            mitigations = [m for m in mitigations if m["id"] in connected_mit_ids]
        
        # Run calculation
        result = calculate_exposure(
            risks=risks,
            influences=influences,
            mitigations=mitigations,
            mitigates_relationships=mitigates_rels
        )
        
        return result.to_dict()
    
    # =========================================================================
    # GENERIC ENTITY OPERATIONS (Schema-Driven)
    # =========================================================================
    
    def create_entity(self, entity_type_id: str, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create any entity type using schema registry.
        
        Args:
            entity_type_id: Entity type ID from schema (e.g., "risk", "mitigation", "tpo")
            data: Entity data dictionary
            
        Returns:
            Created entity or None
        """
        from core import get_registry
        from database.queries.generic_entity import create_entity, EntityValidationError
        
        registry = get_registry()
        entity_type = registry.get_entity_type(entity_type_id)
        
        if not entity_type:
            raise ValueError(f"Unknown entity type: {entity_type_id}")
        
        if not self._connection:
            raise RuntimeError("Not connected to database")
        
        try:
            return create_entity(self._connection._driver, entity_type, data)
        except EntityValidationError as e:
            import streamlit as st
            st.error(str(e))
            return None
    
    def get_entities(
        self, entity_type_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Get all entities of a type with optional filters.
        
        Args:
            entity_type_id: Entity type ID from schema
            filters: Optional attribute filters
            
        Returns:
            List of entity dictionaries
        """
        from core import get_registry
        from database.queries.generic_entity import get_all_entities
        
        registry = get_registry()
        entity_type = registry.get_entity_type(entity_type_id)
        
        if not entity_type:
            return []
        
        if not self._connection:
            return []
        
        return get_all_entities(self._connection._driver, entity_type, filters)
    
    def get_entity_by_id(
        self, entity_type_id: str, entity_id: str
    ) -> Optional[Dict]:
        """
        Get a single entity by ID.
        
        Args:
            entity_type_id: Entity type ID from schema
            entity_id: Entity ID
            
        Returns:
            Entity dictionary or None
        """
        from core import get_registry
        from database.queries.generic_entity import get_entity_by_id
        
        registry = get_registry()
        entity_type = registry.get_entity_type(entity_type_id)
        
        if not entity_type or not self._connection:
            return None
        
        return get_entity_by_id(self._connection._driver, entity_type, entity_id)
    
    def update_entity(
        self, entity_type_id: str, entity_id: str, data: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        Update an entity.
        
        Args:
            entity_type_id: Entity type ID from schema
            entity_id: Entity ID
            data: Updated data
            
        Returns:
            Updated entity or None
        """
        from core import get_registry
        from database.queries.generic_entity import update_entity, EntityValidationError
        
        registry = get_registry()
        entity_type = registry.get_entity_type(entity_type_id)
        
        if not entity_type or not self._connection:
            return None
        
        try:
            return update_entity(self._connection._driver, entity_type, entity_id, data)
        except EntityValidationError as e:
            import streamlit as st
            st.error(str(e))
            return None
    
    def delete_entity(self, entity_type_id: str, entity_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_type_id: Entity type ID from schema
            entity_id: Entity ID
            
        Returns:
            True if deleted
        """
        from core import get_registry
        from database.queries.generic_entity import delete_entity
        
        registry = get_registry()
        entity_type = registry.get_entity_type(entity_type_id)
        
        if not entity_type or not self._connection:
            return False
        
        return delete_entity(self._connection._driver, entity_type, entity_id)
    
    # =========================================================================
    # GENERIC RELATIONSHIP OPERATIONS (Schema-Driven)
    # =========================================================================
    
    def create_relationship(
        self,
        rel_type_id: str,
        source_id: str,
        target_id: str,
        source_entity_type_id: str,
        target_entity_type_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        """
        Create a relationship using schema registry.
        
        Args:
            rel_type_id: Relationship type ID from schema
            source_id: Source entity ID
            target_id: Target entity ID
            source_entity_type_id: Source entity type ID
            target_entity_type_id: Target entity type ID
            data: Relationship properties
            
        Returns:
            Created relationship or None
        """
        from core import get_registry
        from database.queries.generic_relationship import (
            create_relationship, ConstraintViolationError, RelationshipValidationError
        )
        
        registry = get_registry()
        rel_type = registry.get_relationship_type(rel_type_id)
        source_entity_type = registry.get_entity_type(source_entity_type_id)
        target_entity_type = registry.get_entity_type(target_entity_type_id)
        
        if not rel_type or not source_entity_type or not target_entity_type:
            return None
        
        if not self._connection:
            return None
        
        try:
            return create_relationship(
                self._connection._driver,
                rel_type,
                source_id,
                target_id,
                source_entity_type,
                target_entity_type,
                data
            )
        except (ConstraintViolationError, RelationshipValidationError) as e:
            import streamlit as st
            st.error(str(e))
            return None
    
    def get_relationships(
        self, rel_type_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Get all relationships of a type.
        
        Args:
            rel_type_id: Relationship type ID from schema
            filters: Optional property filters
            
        Returns:
            List of relationship dictionaries
        """
        from core import get_registry
        from database.queries.generic_relationship import get_all_relationships
        
        registry = get_registry()
        rel_type = registry.get_relationship_type(rel_type_id)
        
        if not rel_type or not self._connection:
            return []
        
        return get_all_relationships(self._connection._driver, rel_type, filters)
    
    def delete_relationship(self, rel_type_id: str, rel_id: str) -> bool:
        """
        Delete a relationship.
        
        Args:
            rel_type_id: Relationship type ID from schema
            rel_id: Relationship ID
            
        Returns:
            True if deleted
        """
        from core import get_registry
        from database.queries.generic_relationship import delete_relationship
        
        registry = get_registry()
        rel_type = registry.get_relationship_type(rel_type_id)
        
        if not rel_type or not self._connection:
            return False
        
        return delete_relationship(self._connection._driver, rel_type, rel_id)

    # =========================================================================
    # UNIFIED UI ROUTERS (Schema-Agnostic CRUD)
    # =========================================================================

    def create_unified_entity(self, entity_type_id: str, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Universal entity creator that routes to specific handlers (Risks)
        or generic ones (Context Nodes).
        """
        from core import get_registry
        
        if entity_type_id == "risk":
            # Extract risk-specific fields from flat data dictionary
            return self.create_risk(
                name=data.get("name", "New Risk"),
                level=data.get("level", "Operational"),
                categories=data.get("categories", []),
                description=data.get("description", ""),
                status=data.get("status", "Active"),
                activation_condition=data.get("activation_condition"),
                activation_decision_date=data.get("activation_decision_date"),
                owner=data.get("owner", ""),
                probability=data.get("probability"),
                impact=data.get("impact"),
                origin=data.get("origin", "New"),
                subtype=data.get("subtype"),
                ext_fields=data.get("ext_fields", {})
            )
        elif entity_type_id == "mitigation":
            return self.create_mitigation(
                name=data.get("name", "New Mitigation"),
                mitigation_type=data.get("type", "Preventive"),
                status=data.get("status", "Active"),
                description=data.get("description", ""),
                owner=data.get("owner", ""),
                source_entity=data.get("source_entity", ""),
                ext_fields=data.get("ext_fields")
            )
        else:
            registry = get_registry()
            type_def = registry.get_entity_type(entity_type_id)
            if not type_def:
                raise ValueError(f"Unknown entity type: {entity_type_id}")
            return self.create_generic_entity(type_def, data)

    def get_unified_entities(self, entity_type_id: str) -> List[Dict]:
        """Universal entity fetcher."""
        from core import get_registry
        
        if entity_type_id == "risk":
            return self.get_all_risks()
        elif entity_type_id == "mitigation":
            return self.get_all_mitigations()
        else:
            registry = get_registry()
            type_def = registry.get_entity_type(entity_type_id)
            if not type_def:
                return []
            return self.get_generic_entities(type_def)

    def update_unified_entity(self, entity_type_id: str, id: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Universal entity updater."""
        from core import get_registry
        
        if entity_type_id == "risk":
            # Update specific
            success = self.update_risk(
                risk_id=id,
                name=data.get("name", "Unknown Risk"),
                level=data.get("level", "Operational"),
                categories=data.get("categories", []),
                description=data.get("description", ""),
                status=data.get("status", "Active"),
                activation_condition=data.get("activation_condition"),
                activation_decision_date=data.get("activation_decision_date"),
                owner=data.get("owner", ""),
                probability=data.get("probability"),
                impact=data.get("impact"),
                origin=data.get("origin", "New"),
                subtype=data.get("subtype"),
                ext_fields=data.get("ext_fields", {})
            )
            return self.get_risk_by_id(id) if success else None
        elif entity_type_id == "mitigation":
            success = self.update_mitigation(
                mitigation_id=id,
                name=data.get("name", "Unknown Mitigation"),
                mitigation_type=data.get("type", "Preventive"),
                status=data.get("status", "Active"),
                description=data.get("description", ""),
                owner=data.get("owner", ""),
                source_entity=data.get("source_entity", "")
            )
            return self.get_mitigation_by_id(id) if success else None
        else:
            return self.update_generic_entity(entity_type_id, id, data)

    def delete_unified_entity(self, entity_type_id: str, id: str) -> bool:
        """Universal entity deleter."""
        if entity_type_id == "risk":
            return self.delete_risk(id)
        elif entity_type_id == "mitigation":
            return self.delete_mitigation(id)
        else:
            return self.delete_entity(entity_type_id, id)

    def create_unified_relationship(self, rel_type_id: str, source_id: str, target_id: str, source_type_id: str, target_type_id: str, data: Dict[str, Any]) -> Optional[bool]:
        """Universal relationship creator."""
        if rel_type_id == "influences":
            return self.create_influence(
                source_id=source_id,
                target_id=target_id,
                influence_type="INFLUENCES",
                strength=data.get("strength", "Moderate"),
                description=data.get("description", ""),
                confidence=float(data.get("confidence", 0.8))
            )
        elif rel_type_id == "mitigates":
            return self.create_mitigates_link(
                mitigation_id=source_id,
                risk_id=target_id,
                effectiveness=data.get("effectiveness", "Minor"),
                description=data.get("description", "")
            )
            
        # Context edges
        res = self.create_relationship(
            rel_type_id=rel_type_id,
            source_id=source_id,
            target_id=target_id,
            source_entity_type_id=source_type_id,
            target_entity_type_id=target_type_id,
            data=data
        )
        return res is not None

    def get_unified_relationships(self, rel_type_id: str) -> List[Dict]:
        """Universal relationship getter."""
        if rel_type_id == "influences":
            return self.get_all_influences()
        elif rel_type_id == "mitigates":
            return self.get_all_mitigates_relationships()
        else:
            return self.get_relationships(rel_type_id=rel_type_id)

    def update_unified_relationship(self, rel_type_id: str, id: str, data: Dict[str, Any]) -> bool:
        """Universal relationship updater."""
        if rel_type_id == "influences":
            return self.update_influence(
                influence_id=id,
                strength=data.get("strength", "Moderate"),
                description=data.get("description", ""),
                confidence=float(data.get("confidence", 0.8))
            )
        elif rel_type_id == "mitigates":
            return self.update_mitigates_link(
                relationship_id=id,
                effectiveness=data.get("effectiveness", "Minor"),
                description=data.get("description", "")
            )
        else:
            self.update_generic_relationship(rel_type_id, id, data)
            return True

    def delete_unified_relationship(self, rel_type_id: str, id: str) -> bool:
        """Universal relationship deleter."""
        if rel_type_id == "influences":
            return self.delete_influence(id)
        elif rel_type_id == "mitigates":
            return self.delete_mitigates_link(id)
        else:
            return self.delete_relationship(rel_type_id, id)

