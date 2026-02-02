"""
Shared test fixtures and utilities for RIM tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# SAMPLE DATA FIXTURES
# =============================================================================

@pytest.fixture
def sample_risk_data():
    """Sample risk data for testing."""
    return {
        "id": "risk-001",
        "name": "Test Strategic Risk",
        "level": "Strategic",
        "origin": "New",
        "categories": ["Programme", "Produit"],
        "status": "Active",
        "description": "A test risk for unit testing",
        "owner": "Test Owner",
        "probability": 5.0,
        "impact": 8.0,
        "exposure": 40.0,
        "activation_condition": None,
        "activation_decision_date": None,
        "current_score_type": "Qualitative",
    }


@pytest.fixture
def sample_operational_risk_data():
    """Sample operational risk data for testing."""
    return {
        "id": "risk-002",
        "name": "Test Operational Risk",
        "level": "Operational",
        "origin": "Legacy",
        "categories": ["Industriel"],
        "status": "Active",
        "description": "An operational risk for testing",
        "owner": "Ops Team",
        "probability": 7.0,
        "impact": 4.0,
        "exposure": 28.0,
    }


@pytest.fixture
def sample_mitigation_data():
    """Sample mitigation data for testing."""
    return {
        "id": "mit-001",
        "name": "Test Mitigation",
        "type": "Dedicated",
        "status": "Implemented",
        "description": "A test mitigation action",
        "owner": "Risk Manager",
        "source_entity": "",
    }


@pytest.fixture
def sample_tpo_data():
    """Sample TPO data for testing."""
    return {
        "id": "tpo-001",
        "reference": "TPO-01",
        "name": "Test Program Objective",
        "cluster": "Business Efficiency",
        "description": "A test TPO for unit testing",
    }


@pytest.fixture
def sample_influence_data():
    """Sample influence relationship data for testing."""
    return {
        "id": "inf-001",
        "source_id": "risk-002",
        "target_id": "risk-001",
        "type": "Level1_Op_to_Strat",
        "strength": "Strong",
        "confidence": 0.8,
        "description": "Test influence relationship",
    }


@pytest.fixture
def sample_tpo_impact_data():
    """Sample TPO impact relationship data for testing."""
    return {
        "id": "impact-001",
        "risk_id": "risk-001",
        "tpo_id": "tpo-001",
        "impact_level": "High",
        "description": "Test TPO impact",
    }


@pytest.fixture
def sample_mitigates_data():
    """Sample mitigates relationship data for testing."""
    return {
        "id": "mitigates-001",
        "mitigation_id": "mit-001",
        "risk_id": "risk-001",
        "effectiveness": "High",
        "notes": "Test mitigation link",
    }


# =============================================================================
# RISK NETWORK FIXTURES (for service tests)
# =============================================================================

@pytest.fixture
def sample_risk_network():
    """
    Sample risk network for testing services.
    
    Network structure:
    - op_risk_1 --[Strong]--> strat_risk_1 --[High]--> TPO-01
    - op_risk_2 --[Moderate]--> strat_risk_1
    - op_risk_1 --[Weak]--> op_risk_2
    - mit_1 --[High]--> strat_risk_1
    - mit_2 --[Medium]--> op_risk_1
    """
    risks = [
        {
            "id": "strat-001",
            "name": "Strategic Risk Alpha",
            "level": "Strategic",
            "origin": "New",
            "categories": ["Programme"],
            "status": "Active",
            "probability": 6.0,
            "impact": 8.0,
            "exposure": 48.0,
        },
        {
            "id": "op-001",
            "name": "Operational Risk Beta",
            "level": "Operational",
            "origin": "New",
            "categories": ["Industriel"],
            "status": "Active",
            "probability": 7.0,
            "impact": 5.0,
            "exposure": 35.0,
        },
        {
            "id": "op-002",
            "name": "Operational Risk Gamma",
            "level": "Operational",
            "origin": "Legacy",
            "categories": ["Supply Chain"],
            "status": "Active",
            "probability": 4.0,
            "impact": 6.0,
            "exposure": 24.0,
        },
    ]
    
    tpos = [
        {
            "id": "tpo-001",
            "reference": "TPO-01",
            "name": "Cost Control",
            "cluster": "Business Efficiency",
            "description": "Maintain program costs within budget",
        },
    ]
    
    influences = [
        {
            "id": "inf-001",
            "source_id": "op-001",
            "target_id": "strat-001",
            "type": "Level1_Op_to_Strat",
            "strength": "Strong",
            "confidence": 0.85,
        },
        {
            "id": "inf-002",
            "source_id": "op-002",
            "target_id": "strat-001",
            "type": "Level1_Op_to_Strat",
            "strength": "Moderate",
            "confidence": 0.7,
        },
        {
            "id": "inf-003",
            "source_id": "op-001",
            "target_id": "op-002",
            "type": "Level3_Op_to_Op",
            "strength": "Weak",
            "confidence": 0.6,
        },
    ]
    
    tpo_impacts = [
        {
            "id": "impact-001",
            "risk_id": "strat-001",
            "tpo_id": "tpo-001",
            "impact_level": "High",
            "description": "Direct impact on cost control",
        },
    ]
    
    mitigations = [
        {
            "id": "mit-001",
            "name": "Process Improvement",
            "type": "Dedicated",
            "status": "Implemented",
            "description": "Improve process efficiency",
            "owner": "Process Team",
        },
        {
            "id": "mit-002",
            "name": "Training Program",
            "type": "Dedicated",
            "status": "In Progress",
            "description": "Staff training initiative",
            "owner": "HR",
        },
    ]
    
    mitigates_relationships = [
        {
            "id": "mitigates-001",
            "mitigation_id": "mit-001",
            "risk_id": "strat-001",
            "effectiveness": "High",
        },
        {
            "id": "mitigates-002",
            "mitigation_id": "mit-002",
            "risk_id": "op-001",
            "effectiveness": "Medium",
        },
    ]
    
    return {
        "risks": risks,
        "tpos": tpos,
        "influences": influences,
        "tpo_impacts": tpo_impacts,
        "mitigations": mitigations,
        "mitigates_relationships": mitigates_relationships,
    }
