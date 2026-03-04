import pytest

from core import get_registry
from visualization.node_styles import create_node_config
from visualization.colors import get_color_by_exposure

@pytest.fixture(autouse=True)
def ensure_registry_loaded():
    """Ensure the schema registry is loaded before tests run."""
    registry = get_registry()
    if not registry.entity_types:
        from config.schema_loader import SchemaLoader
        loader = SchemaLoader()
        loader.load_schema("default")
    yield

def test_opacity_lifecycle_ghosting():
    """Test F21: Lifecycle & Status Ghosting (Opacity = 50%)"""
    # Test a contingent risk
    node_contingent = {
        "id": "risk_1",
        "node_type": "Risk",
        "status": "Contingent",
        "name": "Contingent Risk"
    }
    
    # Should be 50% opacity
    config = create_node_config(node_contingent, lifecycle_ghosting=True)
    assert "rgba" in config["color"]["background"]
    assert "0.5)" in config["color"]["background"], "Contingent risk should have 0.5 opacity"
    
    # Should be 100% opacity if ghosting is False
    config_off = create_node_config(node_contingent, lifecycle_ghosting=False)
    assert "0.5)" not in config_off["color"]["background"]
    
    # Test a proposed mitigation
    node_proposed = {
        "id": "mit_1",
        "node_type": "Mitigation",
        "status": "Proposed",
        "name": "Proposed Mitigation"
    }
    
    # Should be 50% opacity
    config_mit = create_node_config(node_proposed, lifecycle_ghosting=True)
    assert "0.5)" in config_mit["color"]["background"], "Proposed mitigation should have 0.5 opacity"

def test_opacity_exposure_driven():
    """Test F20: Exposure-Driven Opacity"""
    # Test a critical risk (exposure = 80.0), threshold = 60
    node_critical = {
        "id": "risk_2",
        "node_type": "Risk",
        "exposure": 80.0,
        "name": "Critical Risk"
    }
    
    # Exposure 80.0 >= 60.0 threshold, so 100% opacity
    config = create_node_config(node_critical, exposure_opacity=True, high_exposure_threshold=60.0)
    assert "rgba" in config["color"]["background"]
    assert "1.0)" in config["color"]["background"], "Critical risk should have full 1.0 opacity"

    # Test an ultra-low risk (exposure = 20.0), threshold = 60
    node_low = {
        "id": "risk_3",
        "node_type": "Risk",
        "exposure": 20.0,
        "name": "Low Risk"
    }
    
    # Threshold = 60.0. Exposure 20.0 < 60.0.
    # Opacity = 0.2 + 0.8 * (20.0 / 60.0) = 0.2 + 0.266... = ~0.466
    config_low = create_node_config(node_low, exposure_opacity=True, high_exposure_threshold=60.0)
    assert "1.0)" not in config_low["color"]["background"]
    # Check that opacity is transparent
    assert "0.466" in config_low["color"]["background"]
    
    # Test threshold at 0%
    config_0_thresh = create_node_config(node_low, exposure_opacity=True, high_exposure_threshold=0.0)
    assert "1.0)" in config_0_thresh["color"]["background"], "0% threshold should make everything opaque"

def test_opacity_combined():
    """Test combined F20 and F21 behaviors."""
    # Contingent low-exposure risk
    node_combined = {
        "id": "risk_4",
        "node_type": "Risk",
        "status": "Contingent",
        "exposure": 0.0,
        "name": "Negligible Contingent Risk"
    }
    
    # Lifecycle ghosting halves opacity (* 0.5)
    # Exposure opacity for 0 exposure drops it to base (* 0.2)
    # Result = 1.0 * 0.5 * 0.2 = 0.1
    config = create_node_config(node_combined, exposure_opacity=True, lifecycle_ghosting=True)
    assert "0.1)" in config["color"]["background"], f"Expected 0.1 opacity, got: {config['color']['background']}"
