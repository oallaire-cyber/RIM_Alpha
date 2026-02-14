"""
Exposure Engine - Mandatory analysis engine for risk exposure calculation.

This engine is always required and active. It uses the schema's
engine_required_attributes from the risk entity to perform calculations.
"""

from typing import Any, Dict, List, Optional
from engines.base_engine import AnalysisEngine, EngineResult


class ExposureEngine(AnalysisEngine):
    """
    Mandatory exposure calculation engine.
    
    Calculates risk exposure based on probability and impact,
    using attribute names from the schema's engine_required_attributes.
    
    This engine is always available (no additional requirements beyond kernel).
    """
    
    ID = "exposure"
    NAME = "Exposure Engine"
    DESCRIPTION = "Calculates risk exposure based on probability and impact"
    
    # Kernel requirements only - always available
    REQUIRED_ENTITIES = ["risk"]
    REQUIRED_RELATIONSHIPS = []
    
    def __init__(self, registry=None):
        """Initialize exposure engine."""
        super().__init__(registry)
        self._probability_attr = "probability"
        self._impact_attr = "impact"
        self._exposure_attr = "exposure"
        self._formula = "multiply"  # Default: probability * impact
    
    def activate(self, registry=None) -> bool:
        """
        Activate and configure from schema.
        
        Reads attribute names from risk entity's engine_required_attributes.
        """
        if not super().activate(registry):
            return False
        
        # Read engine configuration from schema
        if self.registry:
            analysis_config = self.registry.get_analysis_config()
            exposure_config = analysis_config.get("exposure", {})
            
            # Get attribute mappings
            attr_map = exposure_config.get("attribute_mapping", {})
            self._probability_attr = attr_map.get("probability", "probability")
            self._impact_attr = attr_map.get("impact", "impact")
            self._exposure_attr = attr_map.get("exposure", "exposure")
            
            # Get formula (default: multiply)
            base_formula = exposure_config.get("base_formula", "probability * impact")
            if "+" in base_formula:
                self._formula = "add"
            else:
                self._formula = "multiply"
        
        return True
    
    def calculate(
        self,
        risk_data: Dict[str, Any]
    ) -> EngineResult:
        """
        Calculate exposure for a single risk.
        
        Args:
            risk_data: Risk entity data with probability and impact
            
        Returns:
            EngineResult with calculated exposure
        """
        try:
            prob = risk_data.get(self._probability_attr, 0)
            impact = risk_data.get(self._impact_attr, 0)
            
            # Convert to float
            prob = float(prob) if prob else 0.0
            impact = float(impact) if impact else 0.0
            
            # Apply formula
            if self._formula == "add":
                exposure = prob + impact
            else:
                exposure = prob * impact
            
            return EngineResult(
                success=True,
                data={
                    self._exposure_attr: exposure,
                    "probability": prob,
                    "impact": impact,
                    "formula": self._formula,
                }
            )
        except (TypeError, ValueError) as e:
            return EngineResult(
                success=False,
                errors=[f"Calculation error: {e}"]
            )
    
    def calculate_batch(
        self,
        risks: List[Dict[str, Any]]
    ) -> List[EngineResult]:
        """
        Calculate exposure for multiple risks.
        
        Args:
            risks: List of risk entity data
            
        Returns:
            List of EngineResult for each risk
        """
        return [self.calculate(risk) for risk in risks]
    
    def calculate_aggregated(
        self,
        target_risk: Dict[str, Any],
        incoming_influences: List[Dict[str, Any]],
        source_risks: List[Dict[str, Any]]
    ) -> EngineResult:
        """
        Calculate aggregated exposure considering influences.
        
        This is a more advanced calculation that considers:
        - Base exposure of the target risk
        - Influenced exposure from source risks via influence strengths
        
        Args:
            target_risk: The risk to calculate exposure for
            incoming_influences: Influence relationships pointing to target
            source_risks: Source risks for the influences
            
        Returns:
            EngineResult with aggregated exposure
        """
        # Base exposure
        base_result = self.calculate(target_risk)
        if not base_result.success:
            return base_result
        
        base_exposure = base_result.data.get(self._exposure_attr, 0)
        
        # Build source risk lookup
        source_lookup = {r.get("id"): r for r in source_risks}
        
        # Strength weights (default if not from schema)
        strength_weights = {
            "Critical": 1.0,
            "Strong": 0.75,
            "Moderate": 0.5,
            "Weak": 0.25,
        }
        
        # Try to load weights from schema
        if self.registry:
            strengths = self.registry.get_influence_strengths()
            for s in strengths:
                strength_weights[s.get("label", s.get("id"))] = s.get("value_score", 0.5)
        
        # Calculate influenced exposure
        influenced_exposure = 0.0
        influence_details = []
        
        for influence in incoming_influences:
            source_id = influence.get("source_id")
            source_risk = source_lookup.get(source_id)
            
            if source_risk:
                source_result = self.calculate(source_risk)
                if source_result.success:
                    source_exp = source_result.data.get(self._exposure_attr, 0)
                    strength = influence.get("strength", "Moderate")
                    weight = strength_weights.get(strength, 0.5)
                    contribution = source_exp * weight
                    influenced_exposure += contribution
                    
                    influence_details.append({
                        "source_id": source_id,
                        "source_exposure": source_exp,
                        "strength": strength,
                        "weight": weight,
                        "contribution": contribution,
                    })
        
        total_exposure = base_exposure + influenced_exposure
        
        return EngineResult(
            success=True,
            data={
                "base_exposure": base_exposure,
                "influenced_exposure": influenced_exposure,
                "total_exposure": total_exposure,
                "influence_details": influence_details,
            }
        )
    
    def get_attribute_names(self) -> Dict[str, str]:
        """Get the attribute names used by this engine."""
        return {
            "probability": self._probability_attr,
            "impact": self._impact_attr,
            "exposure": self._exposure_attr,
        }
