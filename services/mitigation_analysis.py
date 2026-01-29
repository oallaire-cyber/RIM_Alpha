"""
Mitigation Analysis Service.

Provides comprehensive mitigation coverage analysis including:
- Coverage statistics (risks with/without mitigations)
- Risk treatment details
- Mitigation impact assessment
- Coverage gap identification
- Cross-reference with influence analysis
"""

from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass, field
from config.settings import EFFECTIVENESS_VALUES


@dataclass
class CoverageStats:
    """Statistics about mitigation coverage."""
    total_risks: int
    mitigated_risks: int
    unmitigated_risks: int
    coverage_percentage: float
    total_mitigations: int
    total_links: int


@dataclass
class RiskMitigationSummary:
    """Summary of mitigation status for a single risk."""
    id: str
    name: str
    level: str
    origin: str
    exposure: float
    categories: List[str]
    mitigation_count: int
    implemented_count: int
    proposed_count: int
    mitigation_score: int
    mitigations: List[Dict[str, Any]]
    coverage_status: str = ""
    influence_flags: List[str] = field(default_factory=list)


class MitigationAnalyzer:
    """
    Analyzes mitigation coverage in the risk network.
    
    This class performs analysis on mitigation relationships
    to identify coverage gaps and prioritize risk treatment.
    """
    
    def __init__(
        self,
        risks: List[Dict[str, Any]],
        mitigations: List[Dict[str, Any]],
        mitigates_relationships: List[Dict[str, Any]],
        influence_analysis: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the analyzer with risk and mitigation data.
        
        Args:
            risks: List of risk dictionaries
            mitigations: List of mitigation dictionaries
            mitigates_relationships: List of MITIGATES relationship dictionaries
            influence_analysis: Optional pre-computed influence analysis results
        """
        self.risks = risks
        self.mitigations = mitigations
        self.mitigates_rels = mitigates_relationships
        self.influence_analysis = influence_analysis
        
        # Build indexed dictionaries
        self.risk_dict = {r["id"]: dict(r) for r in risks}
        self.mitigation_dict = {m["id"]: dict(m) for m in mitigations}
        
        # Build mappings
        self.risk_to_mitigations: Dict[str, List[Dict]] = {}
        self.mitigation_to_risks: Dict[str, List[Dict]] = {}
        self._build_mappings()
        
        # Extract high-priority IDs from influence analysis
        self.high_priority_ids: Set[str] = set()
        self.propagator_ids: Set[str] = set()
        self.convergence_ids: Set[str] = set()
        self.bottleneck_ids: Set[str] = set()
        self._extract_influence_priorities()
    
    def _build_mappings(self):
        """Build risk-to-mitigations and mitigation-to-risks mappings."""
        for rel in self.mitigates_rels:
            risk_id = rel["risk_id"]
            mit_id = rel["mitigation_id"]
            
            # Risk to mitigations
            if risk_id not in self.risk_to_mitigations:
                self.risk_to_mitigations[risk_id] = []
            
            self.risk_to_mitigations[risk_id].append({
                "mitigation_id": mit_id,
                "mitigation_name": rel.get("mitigation_name", ""),
                "mitigation_type": rel.get("mitigation_type", "Unknown"),
                "effectiveness": rel.get("effectiveness", "Medium"),
                "description": rel.get("description", ""),
                "status": self.mitigation_dict.get(mit_id, {}).get("status", "Unknown")
            })
            
            # Mitigation to risks
            if mit_id not in self.mitigation_to_risks:
                self.mitigation_to_risks[mit_id] = []
            
            self.mitigation_to_risks[mit_id].append({
                "risk_id": risk_id,
                "risk_name": rel.get("risk_name", ""),
                "risk_level": rel.get("risk_level", "Unknown"),
                "effectiveness": rel.get("effectiveness", "Medium")
            })
    
    def _extract_influence_priorities(self):
        """Extract high-priority risk IDs from influence analysis."""
        if not self.influence_analysis:
            return
        
        self.propagator_ids = set(
            p["id"] for p in self.influence_analysis.get("top_propagators", [])
        )
        self.convergence_ids = set(
            c["id"] for c in self.influence_analysis.get("convergence_points", [])
            if c.get("node_type") == "Risk"
        )
        self.bottleneck_ids = set(
            b["id"] for b in self.influence_analysis.get("bottlenecks", [])
        )
        self.high_priority_ids = self.propagator_ids | self.convergence_ids | self.bottleneck_ids
    
    def _get_coverage_status(
        self,
        mitigation_count: int,
        implemented_count: int,
        mitigation_score: int
    ) -> str:
        """
        Determine coverage status based on mitigation metrics.
        
        Args:
            mitigation_count: Total number of mitigations
            implemented_count: Number of implemented mitigations
            mitigation_score: Sum of effectiveness scores
        
        Returns:
            Coverage status string
        """
        if mitigation_count == 0:
            return "unmitigated"
        elif implemented_count == 0:
            return "proposed_only"
        elif implemented_count >= 2 or (implemented_count >= 1 and mitigation_score >= 6):
            return "well_covered"
        else:
            return "partially_covered"
    
    def _get_influence_flags(self, risk_id: str) -> List[str]:
        """Get influence analysis flags for a risk."""
        flags = []
        if risk_id in self.propagator_ids:
            flags.append("Top Propagator")
        if risk_id in self.convergence_ids:
            flags.append("Convergence Point")
        if risk_id in self.bottleneck_ids:
            flags.append("Bottleneck")
        return flags
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform comprehensive mitigation analysis.
        
        Returns:
            Dictionary containing all analysis results
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
        
        # Calculate coverage statistics
        total_risks = len(self.risks)
        mitigated_ids = set(self.risk_to_mitigations.keys())
        all_risk_ids = set(r["id"] for r in self.risks)
        unmitigated_ids = all_risk_ids - mitigated_ids
        
        analysis["coverage_stats"] = {
            "total_risks": total_risks,
            "mitigated_risks": len(mitigated_ids),
            "unmitigated_risks": len(unmitigated_ids),
            "coverage_percentage": round(
                len(mitigated_ids) / total_risks * 100, 1
            ) if total_risks > 0 else 0,
            "total_mitigations": len(self.mitigations),
            "total_links": len(self.mitigates_rels)
        }
        
        # Analyze each risk
        for risk in self.risks:
            risk_id = risk["id"]
            mits = self.risk_to_mitigations.get(risk_id, [])
            
            # Calculate mitigation score
            mit_score = sum(
                EFFECTIVENESS_VALUES.get(m.get("effectiveness", "Medium"), 2)
                for m in mits
            )
            
            # Count by status
            implemented_count = sum(1 for m in mits if m.get("status") == "Implemented")
            proposed_count = sum(1 for m in mits if m.get("status") in ["Proposed", "In Progress"])
            
            # Determine coverage status
            coverage_status = self._get_coverage_status(
                len(mits), implemented_count, mit_score
            )
            
            # Get influence flags
            influence_flags = self._get_influence_flags(risk_id)
            
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
                "mitigations": mits,
                "coverage_status": coverage_status,
                "influence_flags": influence_flags
            }
            
            analysis["risk_mitigation_summary"].append(risk_summary)
            
            # Categorize by coverage
            if coverage_status == "unmitigated":
                analysis["unmitigated_risks"].append(risk_summary)
                if risk_id in self.high_priority_ids:
                    analysis["high_priority_unmitigated"].append(risk_summary)
            elif coverage_status == "proposed_only":
                analysis["partially_mitigated_risks"].append(risk_summary)
            elif coverage_status == "well_covered":
                analysis["well_covered_risks"].append(risk_summary)
        
        # Sort by exposure
        analysis["unmitigated_risks"].sort(key=lambda x: -(x["exposure"] or 0))
        analysis["partially_mitigated_risks"].sort(key=lambda x: -(x["exposure"] or 0))
        analysis["high_priority_unmitigated"].sort(key=lambda x: -(x["exposure"] or 0))
        
        # Effectiveness distribution
        effectiveness_dist = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for rel in self.mitigates_rels:
            eff = rel.get("effectiveness", "Medium")
            if eff in effectiveness_dist:
                effectiveness_dist[eff] += 1
        analysis["mitigation_effectiveness"] = effectiveness_dist
        
        return analysis
    
    def get_risk_details(self, risk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed mitigation information for a specific risk.
        
        Args:
            risk_id: Risk UUID
        
        Returns:
            Dictionary with risk mitigation details or None if not found
        """
        if risk_id not in self.risk_dict:
            return None
        
        risk = self.risk_dict[risk_id]
        mits = self.risk_to_mitigations.get(risk_id, [])
        
        # Calculate metrics
        mit_score = sum(
            EFFECTIVENESS_VALUES.get(m.get("effectiveness", "Medium"), 2)
            for m in mits
        )
        implemented = [m for m in mits if m.get("status") == "Implemented"]
        
        coverage_status = self._get_coverage_status(
            len(mits), len(implemented), mit_score
        )
        
        # Build influence info
        influence_info = {}
        if self.influence_analysis:
            for prop in self.influence_analysis.get("top_propagators", []):
                if prop["id"] == risk_id:
                    influence_info["is_top_propagator"] = True
                    influence_info["propagation_score"] = prop["score"]
                    influence_info["tpos_reached"] = prop["tpos_reached"]
                    break
            
            for conv in self.influence_analysis.get("convergence_points", []):
                if conv["id"] == risk_id:
                    influence_info["is_convergence_point"] = True
                    influence_info["convergence_score"] = conv["score"]
                    influence_info["source_count"] = conv["source_count"]
                    break
            
            for bn in self.influence_analysis.get("bottlenecks", []):
                if bn["id"] == risk_id:
                    influence_info["is_bottleneck"] = True
                    influence_info["path_percentage"] = bn["percentage"]
                    break
        
        return {
            "risk": risk,
            "mitigations": mits,
            "mitigation_count": len(mits),
            "implemented_count": len(implemented),
            "total_effectiveness_score": mit_score,
            "coverage_status": coverage_status,
            "influence_info": influence_info
        }
    
    def get_mitigation_details(self, mitigation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed impact information for a specific mitigation.
        
        Args:
            mitigation_id: Mitigation UUID
        
        Returns:
            Dictionary with mitigation impact details or None if not found
        """
        if mitigation_id not in self.mitigation_dict:
            return None
        
        mitigation = self.mitigation_dict[mitigation_id]
        addressed_risks = self.mitigation_to_risks.get(mitigation_id, [])
        
        # Get full risk data for addressed risks
        risks_with_data = []
        for risk_ref in addressed_risks:
            risk_id = risk_ref["risk_id"]
            if risk_id in self.risk_dict:
                risk_data = dict(self.risk_dict[risk_id])
                risk_data["effectiveness"] = risk_ref["effectiveness"]
                risks_with_data.append(risk_data)
        
        # Count by level
        strategic_count = sum(1 for r in risks_with_data if r.get("level") == "Strategic")
        operational_count = sum(1 for r in risks_with_data if r.get("level") == "Operational")
        
        # Calculate total exposure covered
        total_exposure = sum(r.get("exposure") or 0 for r in risks_with_data)
        
        # Check strategic importance
        strategic_impacts = []
        for risk in risks_with_data:
            flags = self._get_influence_flags(risk["id"])
            if flags:
                strategic_impacts.append({
                    "risk_id": risk["id"],
                    "risk_name": risk["name"],
                    "flags": flags
                })
        
        return {
            "mitigation": mitigation,
            "risks": risks_with_data,
            "risk_count": len(risks_with_data),
            "strategic_count": strategic_count,
            "operational_count": operational_count,
            "total_exposure_covered": round(total_exposure, 2),
            "strategic_impacts": strategic_impacts,
            "addresses_high_priority": len(strategic_impacts) > 0
        }
    
    def get_coverage_gaps(self) -> Dict[str, Any]:
        """
        Identify coverage gaps in the mitigation strategy.
        
        Returns:
            Dictionary containing gap analysis results
        """
        gaps = {
            "critical_unmitigated": [],
            "high_priority_unmitigated": [],
            "proposed_only_high_exposure": [],
            "strategic_gaps": [],
            "category_coverage": {}
        }
        
        # Calculate average exposure for threshold
        exposures = [r.get("exposure") or 0 for r in self.risks if r.get("exposure")]
        avg_exposure = sum(exposures) / len(exposures) if exposures else 5.0
        high_exposure_threshold = avg_exposure * 1.2
        
        # Category tracking
        category_stats: Dict[str, Dict[str, int]] = {}
        
        for risk in self.risks:
            risk_id = risk["id"]
            mits = self.risk_to_mitigations.get(risk_id, [])
            exposure = risk.get("exposure") or 0
            
            # Track category stats
            for cat in risk.get("categories", []):
                if cat not in category_stats:
                    category_stats[cat] = {"total": 0, "mitigated": 0}
                category_stats[cat]["total"] += 1
                if len(mits) > 0:
                    category_stats[cat]["mitigated"] += 1
            
            risk_info = {
                "id": risk_id,
                "name": risk["name"],
                "level": risk["level"],
                "exposure": exposure,
                "categories": risk.get("categories", []),
                "is_high_priority": risk_id in self.high_priority_ids,
                "influence_flags": self._get_influence_flags(risk_id)
            }
            
            # Analyze unmitigated risks
            if len(mits) == 0:
                if risk_id in self.high_priority_ids:
                    gaps["high_priority_unmitigated"].append(risk_info)
                elif exposure >= high_exposure_threshold:
                    gaps["critical_unmitigated"].append(risk_info)
                
                if risk["level"] == "Strategic":
                    gaps["strategic_gaps"].append(risk_info)
            else:
                # Check if only proposed mitigations
                implemented = [m for m in mits if m.get("status") == "Implemented"]
                if len(implemented) == 0 and exposure >= high_exposure_threshold:
                    risk_info["proposed_mitigations"] = [m["mitigation_name"] for m in mits]
                    gaps["proposed_only_high_exposure"].append(risk_info)
                
                # Strategic risks with weak mitigation
                if risk["level"] == "Strategic":
                    total_eff = sum(
                        EFFECTIVENESS_VALUES.get(m.get("effectiveness", "Medium"), 2)
                        for m in implemented
                    )
                    if total_eff < 4:  # Less than one "High" effectiveness
                        risk_info["implemented_effectiveness"] = total_eff
                        if risk_info not in gaps["strategic_gaps"]:
                            gaps["strategic_gaps"].append(risk_info)
        
        # Sort by exposure
        gaps["critical_unmitigated"].sort(key=lambda x: -x["exposure"])
        gaps["high_priority_unmitigated"].sort(key=lambda x: -x["exposure"])
        gaps["proposed_only_high_exposure"].sort(key=lambda x: -x["exposure"])
        gaps["strategic_gaps"].sort(key=lambda x: -x["exposure"])
        
        # Calculate category coverage
        for cat, stats in category_stats.items():
            coverage = round(
                stats["mitigated"] / stats["total"] * 100, 1
            ) if stats["total"] > 0 else 0
            
            gaps["category_coverage"][cat] = {
                "total": stats["total"],
                "mitigated": stats["mitigated"],
                "unmitigated": stats["total"] - stats["mitigated"],
                "coverage_percentage": coverage
            }
        
        return gaps


def analyze_mitigation_coverage(
    risks: List[Dict[str, Any]],
    mitigations: List[Dict[str, Any]],
    mitigates_relationships: List[Dict[str, Any]],
    influence_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to perform complete mitigation analysis.
    
    Args:
        risks: List of risk dictionaries
        mitigations: List of mitigation dictionaries
        mitigates_relationships: List of MITIGATES relationship dictionaries
        influence_analysis: Optional pre-computed influence analysis results
    
    Returns:
        Dictionary containing all analysis results
    """
    analyzer = MitigationAnalyzer(
        risks, mitigations, mitigates_relationships, influence_analysis
    )
    return analyzer.analyze()
