"""
Influence Analysis Service.

Provides comprehensive influence network analysis including:
- Top Propagators (risks with highest downstream impact)
- Convergence Points (most influenced risks/TPOs)
- Critical Paths (strongest influence chains)
- Bottlenecks (nodes appearing in many paths)
- Risk Clusters (tightly interconnected groups)
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from config.settings import (
    STRENGTH_VALUES, IMPACT_VALUES,
    PROPAGATION_DECAY, MAX_INFLUENCE_DEPTH, CONVERGENCE_MULTIPLIER_FACTOR
)


@dataclass
class PropagationResult:
    """Result of propagation analysis for a single risk."""
    id: str
    name: str
    level: str
    score: float
    tpos_reached: int
    risks_reached: int
    tpo_ids: List[str] = field(default_factory=list)
    paths_to_tpo: List[Dict] = field(default_factory=list)


@dataclass
class ConvergenceResult:
    """Result of convergence analysis for a single node."""
    id: str
    name: str
    level: str
    node_type: str
    score: float
    source_count: int
    path_count: int
    is_high_convergence: bool


@dataclass
class CriticalPath:
    """A critical influence path from operational risk to TPO."""
    path: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    strength: float
    length: int


@dataclass
class Bottleneck:
    """A bottleneck node in the influence network."""
    id: str
    name: str
    level: str
    path_count: int
    total_paths: int
    percentage: float


@dataclass
class RiskCluster:
    """A cluster of tightly connected risks."""
    nodes: List[str]
    node_names: List[str]
    size: int
    internal_edges: int
    density: float
    primary_category: str
    levels: Dict[str, int]


class InfluenceAnalyzer:
    """
    Analyzes influence relationships in the risk network.
    
    This class performs graph analysis on the risk influence network
    to identify key structural properties and high-impact risks.
    """
    
    def __init__(
        self,
        risks: List[Dict[str, Any]],
        tpos: List[Dict[str, Any]],
        influences: List[Dict[str, Any]],
        tpo_impacts: List[Dict[str, Any]]
    ):
        """
        Initialize the analyzer with network data.
        
        Args:
            risks: List of risk dictionaries
            tpos: List of TPO dictionaries
            influences: List of influence relationship dictionaries
            tpo_impacts: List of TPO impact relationship dictionaries
        """
        self.risks = risks
        self.tpos = tpos
        self.influences = influences
        self.tpo_impacts = tpo_impacts
        
        # Build indexed dictionaries
        self.risk_dict = {r["id"]: dict(r) for r in risks}
        self.tpo_dict = {t["id"]: dict(t) for t in tpos}
        
        # Build adjacency structures
        self.outgoing: Dict[str, List[Tuple[str, float, str]]] = {}
        self.incoming: Dict[str, List[Tuple[str, float, str]]] = {}
        self._build_adjacency()
    
    def _build_adjacency(self):
        """Build outgoing and incoming adjacency lists."""
        # Process influence edges
        for inf in self.influences:
            source = inf["source_id"]
            target = inf["target_id"]
            strength = STRENGTH_VALUES.get(inf.get("strength", "Moderate"), 2)
            confidence = inf.get("confidence", 0.8) or 0.8
            score = strength * confidence
            
            if source not in self.outgoing:
                self.outgoing[source] = []
            self.outgoing[source].append((target, score, "INFLUENCES"))
            
            if target not in self.incoming:
                self.incoming[target] = []
            self.incoming[target].append((source, score, "INFLUENCES"))
        
        # Process TPO impact edges (with boost)
        for impact in self.tpo_impacts:
            source = impact["risk_id"]
            target = impact["tpo_id"]
            impact_score = IMPACT_VALUES.get(impact.get("impact_level", "Medium"), 2)
            boosted_score = impact_score * 1.5  # TPO impacts get a boost
            
            if source not in self.outgoing:
                self.outgoing[source] = []
            self.outgoing[source].append((target, boosted_score, "IMPACTS_TPO"))
            
            if target not in self.incoming:
                self.incoming[target] = []
            self.incoming[target].append((source, boosted_score, "IMPACTS_TPO"))
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive influence analysis.
        
        Returns:
            Dictionary containing all analysis results
        """
        return {
            "top_propagators": self.get_top_propagators(),
            "convergence_points": self.get_convergence_points(),
            "critical_paths": self.get_critical_paths(),
            "bottlenecks": self.get_bottlenecks(),
            "risk_clusters": self.get_risk_clusters()
        }
    
    def get_top_propagators(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Calculate top propagators - risks with highest downstream impact.
        
        Uses BFS with score accumulation and decay to measure how much
        influence each risk has on the overall network.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of top propagator dictionaries
        """
        propagation_scores = {}
        
        for risk_id, risk_data in self.risk_dict.items():
            score = 0
            tpos_reached: Set[str] = set()
            risks_reached: Set[str] = set()
            paths_to_tpo = []
            
            # BFS with score accumulation
            visited: Set[str] = set()
            queue = [(risk_id, 1.0, 0, [risk_id])]  # (node, cumulative_strength, depth, path)
            
            while queue:
                current, cum_strength, depth, path = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                if current != risk_id:
                    decay = PROPAGATION_DECAY ** depth
                    
                    if current in self.tpo_dict:
                        tpos_reached.add(current)
                        node_value = 10  # TPOs are highest value
                        score += node_value * cum_strength * decay
                        paths_to_tpo.append({
                            "path": path,
                            "score": cum_strength * decay
                        })
                    elif current in self.risk_dict:
                        risks_reached.add(current)
                        node_value = 5 if self.risk_dict[current]["level"] == "Strategic" else 2
                        score += node_value * cum_strength * decay
                
                # Continue traversal
                if current in self.outgoing and depth < MAX_INFLUENCE_DEPTH:
                    for target, edge_score, edge_type in self.outgoing[current]:
                        if target not in visited:
                            new_strength = cum_strength * (edge_score / 4)  # Normalize
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
        
        # Sort and return top propagators
        sorted_propagators = sorted(
            propagation_scores.values(),
            key=lambda x: -x["score"]
        )
        return sorted_propagators[:limit]
    
    def get_convergence_points(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Calculate convergence points - nodes where multiple influences converge.
        
        Analyzes both strategic risks and TPOs as potential convergence points.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of convergence point dictionaries
        """
        convergence_scores = {}
        
        # Analyze both risks and TPOs as potential convergence points
        convergence_candidates = list(self.risk_dict.keys()) + list(self.tpo_dict.keys())
        
        for node_id in convergence_candidates:
            if node_id not in self.incoming:
                continue
            
            score = 0
            unique_sources: Set[str] = set()
            path_count = 0
            
            # BFS upstream
            visited: Set[str] = set()
            queue = [(node_id, 1.0, 0)]  # (node, cumulative_strength, depth)
            
            while queue:
                current, cum_strength, depth = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                if current != node_id and current in self.risk_dict:
                    unique_sources.add(current)
                    source_weight = 1.0 if self.risk_dict[current]["level"] == "Operational" else 0.7
                    decay = PROPAGATION_DECAY ** depth
                    score += cum_strength * source_weight * decay
                    path_count += 1
                
                # Continue upstream
                if current in self.incoming and depth < MAX_INFLUENCE_DEPTH:
                    for source, edge_score, edge_type in self.incoming[current]:
                        if source not in visited and source in self.risk_dict:
                            new_strength = cum_strength * (edge_score / 4)
                            queue.append((source, new_strength, depth + 1))
            
            # Convergence bonus for multiple paths
            if len(unique_sources) > 0:
                convergence_multiplier = 1 + (path_count / len(unique_sources)) * CONVERGENCE_MULTIPLIER_FACTOR
                score *= convergence_multiplier
            
            is_tpo = node_id in self.tpo_dict
            node_data = self.tpo_dict[node_id] if is_tpo else self.risk_dict.get(node_id, {})
            
            convergence_scores[node_id] = {
                "id": node_id,
                "name": (node_data.get("reference", "") + ": " + node_data.get("name", "")) if is_tpo else node_data.get("name", ""),
                "level": "TPO" if is_tpo else node_data.get("level", ""),
                "node_type": "TPO" if is_tpo else "Risk",
                "score": round(score, 1),
                "source_count": len(unique_sources),
                "path_count": path_count,
                "is_high_convergence": path_count > len(unique_sources) * 1.5 if unique_sources else False
            }
        
        # Sort and return top convergence points
        sorted_convergence = sorted(
            [c for c in convergence_scores.values() if c["score"] > 0],
            key=lambda x: -x["score"]
        )
        return sorted_convergence[:limit]
    
    def get_critical_paths(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find strongest paths from operational risks to TPOs.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of critical path dictionaries
        """
        critical_paths = []
        
        for risk_id, risk_data in self.risk_dict.items():
            if risk_data["level"] != "Operational":
                continue
            
            # Find paths to TPOs
            visited: Set[str] = set()
            queue = [(
                risk_id,
                1.0,
                [{"id": risk_id, "name": risk_data["name"], "type": "Operational"}],
                []
            )]
            
            while queue:
                current, cum_strength, path_nodes, path_edges = queue.pop(0)
                
                if current in visited:
                    continue
                visited.add(current)
                
                # Check if we reached a TPO
                if current in self.tpo_dict and len(path_nodes) > 1:
                    critical_paths.append({
                        "path": path_nodes,
                        "edges": path_edges,
                        "strength": round(cum_strength, 3),
                        "length": len(path_nodes) - 1
                    })
                    continue
                
                # Continue traversal
                if current in self.outgoing and len(path_nodes) < 6:
                    for target, edge_score, edge_type in self.outgoing[current]:
                        if target not in visited:
                            new_strength = cum_strength * (edge_score / 4)
                            
                            if target in self.tpo_dict:
                                target_info = {
                                    "id": target,
                                    "name": self.tpo_dict[target]["reference"],
                                    "type": "TPO"
                                }
                            elif target in self.risk_dict:
                                target_info = {
                                    "id": target,
                                    "name": self.risk_dict[target]["name"],
                                    "type": self.risk_dict[target]["level"]
                                }
                            else:
                                continue
                            
                            queue.append((
                                target,
                                new_strength,
                                path_nodes + [target_info],
                                path_edges + [{"type": edge_type, "score": edge_score}]
                            ))
        
        # Sort by strength and return top paths
        critical_paths.sort(key=lambda x: -x["strength"])
        return critical_paths[:limit]
    
    def get_bottlenecks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Identify bottleneck nodes - nodes appearing in many paths to TPOs.
        
        These are potential single points of failure in the influence network.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of bottleneck dictionaries
        """
        node_path_count: Dict[str, int] = {}
        total_paths_to_tpo = 0
        
        for risk_id, risk_data in self.risk_dict.items():
            # Find all paths to TPOs
            visited_paths: Set[tuple] = set()
            queue = [(risk_id, [risk_id])]
            
            while queue:
                current, path = queue.pop(0)
                path_key = tuple(path)
                
                if path_key in visited_paths:
                    continue
                visited_paths.add(path_key)
                
                if current in self.tpo_dict and len(path) > 1:
                    total_paths_to_tpo += 1
                    for node in path[1:-1]:  # Exclude start and end
                        if node in self.risk_dict:
                            if node not in node_path_count:
                                node_path_count[node] = 0
                            node_path_count[node] += 1
                    continue
                
                if current in self.outgoing and len(path) < 6:
                    for target, _, _ in self.outgoing[current]:
                        if target not in path:
                            queue.append((target, path + [target]))
        
        # Calculate bottleneck scores
        bottlenecks = []
        for node_id, count in node_path_count.items():
            if count >= 2 and node_id in self.risk_dict:
                bottlenecks.append({
                    "id": node_id,
                    "name": self.risk_dict[node_id]["name"],
                    "level": self.risk_dict[node_id]["level"],
                    "path_count": count,
                    "total_paths": total_paths_to_tpo,
                    "percentage": round(count / max(total_paths_to_tpo, 1) * 100, 1)
                })
        
        bottlenecks.sort(key=lambda x: -x["path_count"])
        return bottlenecks[:limit]
    
    def get_risk_clusters(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find tightly connected groups of risks using connected components.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of cluster dictionaries
        """
        # Build undirected adjacency for clustering
        undirected: Dict[str, Set[str]] = {}
        
        for source in self.outgoing:
            if source not in self.risk_dict:
                continue
            for target, score, _ in self.outgoing[source]:
                if target not in self.risk_dict:
                    continue
                if source not in undirected:
                    undirected[source] = set()
                if target not in undirected:
                    undirected[target] = set()
                undirected[source].add(target)
                undirected[target].add(source)
        
        # Find connected components
        visited: Set[str] = set()
        clusters = []
        
        for start_node in undirected:
            if start_node in visited:
                continue
            
            # BFS to find cluster
            cluster: Set[str] = set()
            queue = [start_node]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                cluster.add(current)
                
                for neighbor in undirected.get(current, set()):
                    if neighbor not in visited:
                        queue.append(neighbor)
            
            if len(cluster) >= 2:
                # Count internal edges
                internal_edges = 0
                for node in cluster:
                    for target, _, _ in self.outgoing.get(node, []):
                        if target in cluster:
                            internal_edges += 1
                
                # Determine cluster category
                levels = [self.risk_dict[n]["level"] for n in cluster if n in self.risk_dict]
                categories = []
                for n in cluster:
                    if n in self.risk_dict:
                        categories.extend(self.risk_dict[n].get("categories", []))
                
                primary_category = max(set(categories), key=categories.count) if categories else "Mixed"
                
                clusters.append({
                    "nodes": list(cluster),
                    "node_names": [self.risk_dict[n]["name"] for n in cluster if n in self.risk_dict],
                    "size": len(cluster),
                    "internal_edges": internal_edges,
                    "density": round(internal_edges / (len(cluster) * (len(cluster) - 1)) if len(cluster) > 1 else 0, 2),
                    "primary_category": primary_category,
                    "levels": {
                        "Strategic": levels.count("Strategic"),
                        "Operational": levels.count("Operational")
                    }
                })
        
        # Sort by size and density
        clusters.sort(key=lambda x: (-x["size"], -x["density"]))
        return clusters[:limit]
    
    def get_propagator_ids(self) -> Set[str]:
        """Get IDs of top propagators."""
        return set(p["id"] for p in self.get_top_propagators(10))
    
    def get_convergence_ids(self, risks_only: bool = True) -> Set[str]:
        """Get IDs of convergence points."""
        points = self.get_convergence_points(10)
        if risks_only:
            return set(c["id"] for c in points if c.get("node_type") == "Risk")
        return set(c["id"] for c in points)
    
    def get_bottleneck_ids(self) -> Set[str]:
        """Get IDs of bottleneck nodes."""
        return set(b["id"] for b in self.get_bottlenecks(10))
    
    def get_high_priority_ids(self) -> Set[str]:
        """Get IDs of all high-priority risks (propagators, convergence points, bottlenecks)."""
        return self.get_propagator_ids() | self.get_convergence_ids() | self.get_bottleneck_ids()


def analyze_influence_network(
    risks: List[Dict[str, Any]],
    tpos: List[Dict[str, Any]],
    influences: List[Dict[str, Any]],
    tpo_impacts: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Convenience function to perform complete influence analysis.
    
    Args:
        risks: List of risk dictionaries
        tpos: List of TPO dictionaries
        influences: List of influence relationship dictionaries
        tpo_impacts: List of TPO impact relationship dictionaries
    
    Returns:
        Dictionary containing all analysis results
    """
    analyzer = InfluenceAnalyzer(risks, tpos, influences, tpo_impacts)
    return analyzer.analyze()
