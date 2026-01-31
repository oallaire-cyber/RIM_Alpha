"""
Exposure Calculator Service for RIM.

Calculates risk exposure scores considering:
- Base exposure (Likelihood × Impact)
- Mitigation effectiveness (multiplicative reduction)
- Influence limitation (upstream risks limit downstream mitigation effectiveness)

The calculation is designed to be extensible for future complexity increases.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Effectiveness scores for mitigations (0 to 1 scale)
EFFECTIVENESS_SCORES = {
    "Critical": 0.9,
    "High": 0.7,
    "Medium": 0.5,
    "Low": 0.3
}

# Influence strength scores (0 to 1 scale)
INFLUENCE_STRENGTH_SCORES = {
    "Critical": 1.0,
    "Strong": 0.75,
    "Moderate": 0.5,
    "Weak": 0.25
}

# Maximum likelihood and impact values (for normalization)
MAX_LIKELIHOOD = 10.0
MAX_IMPACT = 10.0
MAX_BASE_EXPOSURE = MAX_LIKELIHOOD * MAX_IMPACT  # 100


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RiskExposureResult:
    """Result of exposure calculation for a single risk."""
    risk_id: str
    risk_name: str
    level: str  # Strategic or Operational
    
    # Base values
    likelihood: float
    impact: float
    base_exposure: float
    
    # Mitigation effect
    mitigation_factor: float  # 1.0 = no mitigation, 0.1 = 90% mitigated
    mitigated_exposure: float
    mitigation_count: int
    
    # Influence limitation effect
    influence_limitation: float  # 0.0 = no limitation, 1.0 = full limitation
    effective_mitigation_factor: float
    upstream_risk_count: int
    
    # Final result
    final_exposure: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/display."""
        return {
            "risk_id": self.risk_id,
            "risk_name": self.risk_name,
            "level": self.level,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "base_exposure": round(self.base_exposure, 2),
            "mitigation_factor": round(self.mitigation_factor, 3),
            "mitigated_exposure": round(self.mitigated_exposure, 2),
            "mitigation_count": self.mitigation_count,
            "influence_limitation": round(self.influence_limitation, 3),
            "effective_mitigation_factor": round(self.effective_mitigation_factor, 3),
            "upstream_risk_count": self.upstream_risk_count,
            "final_exposure": round(self.final_exposure, 2)
        }


@dataclass
class GlobalExposureResult:
    """Result of global exposure calculation for the entire perimeter."""
    
    # Primary metric: Residual Risk Percentage
    residual_risk_percentage: float
    
    # Secondary metric: Weighted Risk Score (0-100)
    weighted_risk_score: float
    
    # Alert metric: Maximum single risk exposure
    max_single_exposure: float
    max_exposure_risk_id: str
    max_exposure_risk_name: str
    
    # Summary statistics
    total_risks: int
    risks_with_data: int  # Risks with likelihood and impact defined
    total_base_exposure: float
    total_final_exposure: float
    
    # Breakdown
    strategic_exposure: float
    operational_exposure: float
    mitigated_risks_count: int
    unmitigated_risks_count: int
    
    # Metadata
    calculated_at: datetime = field(default_factory=datetime.now)
    
    # Individual risk results (for detailed view)
    risk_results: List[RiskExposureResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/display."""
        return {
            "residual_risk_percentage": round(self.residual_risk_percentage, 1),
            "weighted_risk_score": round(self.weighted_risk_score, 1),
            "max_single_exposure": round(self.max_single_exposure, 2),
            "max_exposure_risk_id": self.max_exposure_risk_id,
            "max_exposure_risk_name": self.max_exposure_risk_name,
            "total_risks": self.total_risks,
            "risks_with_data": self.risks_with_data,
            "total_base_exposure": round(self.total_base_exposure, 2),
            "total_final_exposure": round(self.total_final_exposure, 2),
            "strategic_exposure": round(self.strategic_exposure, 2),
            "operational_exposure": round(self.operational_exposure, 2),
            "mitigated_risks_count": self.mitigated_risks_count,
            "unmitigated_risks_count": self.unmitigated_risks_count,
            "calculated_at": self.calculated_at.isoformat(),
            "risk_results": [r.to_dict() for r in self.risk_results]
        }
    
    def get_health_status(self) -> Tuple[str, str]:
        """
        Get health status based on weighted risk score.
        
        Returns:
            Tuple of (status_label, color_code)
        """
        score = self.weighted_risk_score
        if score <= 10:
            return ("Excellent", "#27ae60")  # Green
        elif score <= 30:
            return ("Good", "#2ecc71")  # Light green
        elif score <= 50:
            return ("Moderate", "#f39c12")  # Orange
        elif score <= 70:
            return ("Concerning", "#e67e22")  # Dark orange
        else:
            return ("Critical", "#e74c3c")  # Red


# =============================================================================
# EXPOSURE CALCULATOR CLASS
# =============================================================================

class ExposureCalculator:
    """
    Calculator for risk exposure considering mitigations and influences.
    
    The calculation follows these steps:
    1. Calculate base exposure for each risk (Likelihood × Impact)
    2. Apply mitigation factors (multiplicative)
    3. Calculate influence limitations from upstream risks
    4. Compute final exposure considering all factors
    5. Aggregate to global metrics
    """
    
    def __init__(
        self,
        risks: List[Dict[str, Any]],
        influences: List[Dict[str, Any]],
        mitigations: List[Dict[str, Any]],
        mitigates_relationships: List[Dict[str, Any]]
    ):
        """
        Initialize the calculator with data.
        
        Args:
            risks: List of risk dictionaries
            influences: List of influence relationships
            mitigations: List of mitigation dictionaries
            mitigates_relationships: List of MITIGATES relationships
        """
        self.risks = {r["id"]: r for r in risks}
        self.influences = influences
        self.mitigations = {m["id"]: m for m in mitigations}
        self.mitigates_relationships = mitigates_relationships
        
        # Build lookup structures
        self._build_influence_graph()
        self._build_mitigation_map()
        
        # Results storage
        self.risk_results: Dict[str, RiskExposureResult] = {}
    
    def _build_influence_graph(self):
        """Build adjacency lists for influence relationships."""
        # upstream_influences[risk_id] = list of (source_id, strength) tuples
        self.upstream_influences: Dict[str, List[Tuple[str, str]]] = {
            rid: [] for rid in self.risks
        }
        
        for inf in self.influences:
            source_id = inf.get("source_id") or inf.get("source")
            target_id = inf.get("target_id") or inf.get("target")
            strength = inf.get("strength", "Moderate")
            
            if target_id in self.upstream_influences:
                self.upstream_influences[target_id].append((source_id, strength))
    
    def _build_mitigation_map(self):
        """Build map of risk_id to list of (mitigation_id, effectiveness)."""
        # risk_mitigations[risk_id] = list of effectiveness values
        self.risk_mitigations: Dict[str, List[str]] = {
            rid: [] for rid in self.risks
        }
        
        for rel in self.mitigates_relationships:
            risk_id = rel.get("risk_id")
            mitigation_id = rel.get("mitigation_id")
            effectiveness = rel.get("effectiveness", "Medium")
            
            if risk_id in self.risk_mitigations:
                self.risk_mitigations[risk_id].append(effectiveness)
    
    def _calculate_base_exposure(self, risk: Dict[str, Any]) -> float:
        """
        Calculate base exposure for a risk.
        
        Formula: Likelihood × Impact
        
        Args:
            risk: Risk dictionary
        
        Returns:
            Base exposure value (0-100 scale)
        """
        likelihood = risk.get("probability") or risk.get("likelihood") or 0
        impact = risk.get("impact") or 0
        
        return float(likelihood) * float(impact)
    
    def _calculate_mitigation_factor(self, risk_id: str) -> Tuple[float, int]:
        """
        Calculate the mitigation factor for a risk.
        
        Uses multiplicative model: Factor = ∏(1 - Effectiveness_i)
        This provides diminishing returns for multiple mitigations.
        
        Args:
            risk_id: ID of the risk
        
        Returns:
            Tuple of (mitigation_factor, mitigation_count)
            Factor of 1.0 means no mitigation, 0.1 means 90% mitigated
        """
        effectivenesses = self.risk_mitigations.get(risk_id, [])
        
        if not effectivenesses:
            return 1.0, 0
        
        factor = 1.0
        for eff in effectivenesses:
            eff_score = EFFECTIVENESS_SCORES.get(eff, 0.5)
            factor *= (1.0 - eff_score)
        
        return factor, len(effectivenesses)
    
    def _calculate_influence_limitation(
        self, 
        risk_id: str,
        calculated_risks: Dict[str, RiskExposureResult]
    ) -> Tuple[float, int]:
        """
        Calculate the influence limitation factor.
        
        Upstream risks with high residual exposure limit how effective
        downstream mitigations can be.
        
        Formula:
            Limitation = Σ(Upstream_Residual_Normalized × Strength) / Count
        
        Where Upstream_Residual_Normalized = Final_Exposure / Base_Exposure
        
        Args:
            risk_id: ID of the risk being calculated
            calculated_risks: Already calculated risk results
        
        Returns:
            Tuple of (limitation_factor, upstream_count)
            Factor of 0.0 means no limitation, 1.0 means full limitation
        """
        upstream = self.upstream_influences.get(risk_id, [])
        
        if not upstream:
            return 0.0, 0
        
        total_limitation = 0.0
        valid_count = 0
        
        for source_id, strength in upstream:
            # Skip if upstream risk hasn't been calculated yet
            if source_id not in calculated_risks:
                continue
            
            upstream_result = calculated_risks[source_id]
            
            # Calculate normalized residual exposure (0-1 scale)
            if upstream_result.base_exposure > 0:
                residual_normalized = (
                    upstream_result.final_exposure / upstream_result.base_exposure
                )
            else:
                residual_normalized = 1.0  # Assume worst case if no data
            
            # Apply strength weighting
            strength_score = INFLUENCE_STRENGTH_SCORES.get(strength, 0.5)
            total_limitation += residual_normalized * strength_score
            valid_count += 1
        
        if valid_count == 0:
            return 0.0, len(upstream)
        
        # Average the limitation
        avg_limitation = total_limitation / valid_count
        
        return avg_limitation, len(upstream)
    
    def _get_calculation_order(self) -> List[str]:
        """
        Determine the order to calculate risks (topological sort).
        
        Risks with no upstream influences are calculated first,
        then their downstream risks, and so on.
        
        Returns:
            List of risk IDs in calculation order
        """
        # Count incoming influences for each risk
        in_degree = {rid: 0 for rid in self.risks}
        for rid, upstream in self.upstream_influences.items():
            in_degree[rid] = len([s for s, _ in upstream if s in self.risks])
        
        # Start with risks that have no upstream influences
        queue = [rid for rid, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Find risks that this one influences
            for rid, upstream in self.upstream_influences.items():
                for source_id, _ in upstream:
                    if source_id == current:
                        in_degree[rid] -= 1
                        if in_degree[rid] == 0 and rid not in result and rid not in queue:
                            queue.append(rid)
        
        # Add any remaining risks (handles cycles)
        for rid in self.risks:
            if rid not in result:
                result.append(rid)
        
        return result
    
    def calculate_risk_exposure(
        self,
        risk_id: str,
        calculated_risks: Dict[str, RiskExposureResult]
    ) -> Optional[RiskExposureResult]:
        """
        Calculate exposure for a single risk.
        
        Args:
            risk_id: ID of the risk
            calculated_risks: Already calculated risk results (for influence calculation)
        
        Returns:
            RiskExposureResult or None if risk has no data
        """
        risk = self.risks.get(risk_id)
        if not risk:
            return None
        
        # Get base values
        likelihood = risk.get("probability") or risk.get("likelihood") or 0
        impact = risk.get("impact") or 0
        
        # Skip risks without likelihood/impact data
        if likelihood == 0 or impact == 0:
            return None
        
        likelihood = float(likelihood)
        impact = float(impact)
        
        # Step 1: Base exposure
        base_exposure = self._calculate_base_exposure(risk)
        
        # Step 2: Mitigation factor
        mitigation_factor, mit_count = self._calculate_mitigation_factor(risk_id)
        mitigated_exposure = base_exposure * mitigation_factor
        
        # Step 3: Influence limitation
        influence_limitation, upstream_count = self._calculate_influence_limitation(
            risk_id, calculated_risks
        )
        
        # Step 4: Effective mitigation factor
        # Limitation reduces how much the mitigation can help
        # Effective_Factor = Mit_Factor + (1 - Mit_Factor) × Limitation
        effective_mitigation_factor = (
            mitigation_factor + (1.0 - mitigation_factor) * influence_limitation
        )
        
        # Step 5: Final exposure
        final_exposure = base_exposure * effective_mitigation_factor
        
        return RiskExposureResult(
            risk_id=risk_id,
            risk_name=risk.get("name", "Unknown"),
            level=risk.get("level", "Unknown"),
            likelihood=likelihood,
            impact=impact,
            base_exposure=base_exposure,
            mitigation_factor=mitigation_factor,
            mitigated_exposure=mitigated_exposure,
            mitigation_count=mit_count,
            influence_limitation=influence_limitation,
            effective_mitigation_factor=effective_mitigation_factor,
            upstream_risk_count=upstream_count,
            final_exposure=final_exposure
        )
    
    def calculate_all(self) -> GlobalExposureResult:
        """
        Calculate exposure for all risks and aggregate to global metrics.
        
        Returns:
            GlobalExposureResult with all metrics
        """
        # Clear previous results
        self.risk_results = {}
        
        # Get calculation order
        order = self._get_calculation_order()
        
        # Calculate each risk in order
        for risk_id in order:
            result = self.calculate_risk_exposure(risk_id, self.risk_results)
            if result:
                self.risk_results[risk_id] = result
        
        # Aggregate to global metrics
        return self._calculate_global_metrics()
    
    def _calculate_global_metrics(self) -> GlobalExposureResult:
        """
        Calculate global exposure metrics from individual risk results.
        
        Returns:
            GlobalExposureResult with aggregated metrics
        """
        results = list(self.risk_results.values())
        
        if not results:
            return GlobalExposureResult(
                residual_risk_percentage=0.0,
                weighted_risk_score=0.0,
                max_single_exposure=0.0,
                max_exposure_risk_id="",
                max_exposure_risk_name="N/A",
                total_risks=len(self.risks),
                risks_with_data=0,
                total_base_exposure=0.0,
                total_final_exposure=0.0,
                strategic_exposure=0.0,
                operational_exposure=0.0,
                mitigated_risks_count=0,
                unmitigated_risks_count=0,
                risk_results=[]
            )
        
        # Calculate totals
        total_base = sum(r.base_exposure for r in results)
        total_final = sum(r.final_exposure for r in results)
        
        # Residual Risk Percentage
        residual_pct = (total_final / total_base * 100) if total_base > 0 else 0
        
        # Weighted Risk Score (impact-squared weighting)
        weighted_sum = sum(r.final_exposure * (r.impact ** 2) for r in results)
        max_weighted = sum(MAX_BASE_EXPOSURE * (r.impact ** 2) for r in results)
        weighted_score = (weighted_sum / max_weighted * 100) if max_weighted > 0 else 0
        
        # Maximum single exposure
        max_result = max(results, key=lambda r: r.final_exposure)
        
        # Breakdown by level
        strategic_exp = sum(r.final_exposure for r in results if r.level == "Strategic")
        operational_exp = sum(r.final_exposure for r in results if r.level == "Operational")
        
        # Mitigation counts
        mitigated = sum(1 for r in results if r.mitigation_count > 0)
        unmitigated = len(results) - mitigated
        
        return GlobalExposureResult(
            residual_risk_percentage=residual_pct,
            weighted_risk_score=weighted_score,
            max_single_exposure=max_result.final_exposure,
            max_exposure_risk_id=max_result.risk_id,
            max_exposure_risk_name=max_result.risk_name,
            total_risks=len(self.risks),
            risks_with_data=len(results),
            total_base_exposure=total_base,
            total_final_exposure=total_final,
            strategic_exposure=strategic_exp,
            operational_exposure=operational_exp,
            mitigated_risks_count=mitigated,
            unmitigated_risks_count=unmitigated,
            risk_results=results
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_exposure(
    risks: List[Dict[str, Any]],
    influences: List[Dict[str, Any]],
    mitigations: List[Dict[str, Any]],
    mitigates_relationships: List[Dict[str, Any]]
) -> GlobalExposureResult:
    """
    Convenience function to calculate exposure for all risks.
    
    Args:
        risks: List of risk dictionaries
        influences: List of influence relationships
        mitigations: List of mitigation dictionaries
        mitigates_relationships: List of MITIGATES relationships
    
    Returns:
        GlobalExposureResult with all metrics
    """
    calculator = ExposureCalculator(
        risks=risks,
        influences=influences,
        mitigations=mitigations,
        mitigates_relationships=mitigates_relationships
    )
    return calculator.calculate_all()
