"""
Tests for core schema registry and related modules.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core import (
    get_registry,
    load_schema,
    SchemaValidationError,
)
from core.schema_registry import reset_registry


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(autouse=True)
def reset_global_registry():
    """Reset the global registry before each test."""
    reset_registry()
    yield
    reset_registry()


@pytest.fixture
def loaded_registry():
    """Load the default schema."""
    return load_schema("default")


# =============================================================================
# SCHEMA LOADING TESTS
# =============================================================================

class TestSchemaLoading:
    """Tests for schema loading."""
    
    def test_load_default_schema(self, loaded_registry):
        """Test that default schema loads successfully."""
        assert loaded_registry.schema_name == "Default"
        assert loaded_registry.schema_version is not None
    
    def test_kernel_entities_present(self, loaded_registry):
        """Test that mandatory kernel entities are loaded."""
        assert loaded_registry.has_entity("risk")
        assert loaded_registry.has_entity("mitigation")
        
        risk_type = loaded_registry.get_risk_type()
        assert risk_type.is_risk_type is True
        assert risk_type.is_mitigation_type is False
        
        mit_type = loaded_registry.get_mitigation_type()
        assert mit_type.is_mitigation_type is True
        assert mit_type.is_risk_type is False
    
    def test_kernel_relationships_present(self, loaded_registry):
        """Test that mandatory kernel relationships are loaded."""
        assert loaded_registry.has_relationship("influences")
        assert loaded_registry.has_relationship("mitigates")
        
        influence_type = loaded_registry.get_influence_type()
        assert influence_type.is_influence_type is True
        assert influence_type.is_mitigates_type is False
        
        mitigates_type = loaded_registry.get_mitigates_type()
        assert mitigates_type.is_mitigates_type is True
        assert mitigates_type.is_influence_type is False
    
    def test_additional_entities_loaded(self, loaded_registry):
        """Test that additional entities are loaded."""
        # TPO should be loaded as additional entity
        assert loaded_registry.has_entity("tpo")
        
        additional = loaded_registry.get_additional_entity_types()
        assert "tpo" in additional
        assert "risk" not in additional  # Kernel shouldn't be in additional
        assert "mitigation" not in additional


# =============================================================================
# RISK ENTITY TESTS
# =============================================================================

class TestRiskEntity:
    """Tests for risk entity type."""
    
    def test_risk_levels(self, loaded_registry):
        """Test that risk levels are loaded."""
        levels = loaded_registry.get_risk_levels()
        assert len(levels) >= 2  # At least 2 levels
        
        level_ids = loaded_registry.get_risk_level_ids()
        assert "business" in level_ids or "strategic" in level_ids or len(level_ids) >= 1
    
    def test_risk_level_labels(self, loaded_registry):
        """Test risk level labels."""
        labels = loaded_registry.get_risk_level_labels()
        assert len(labels) >= 2
        # Check for either Strategic/Operational or Business/Operational
        assert any(l in labels for l in ["Strategic", "Business", "Operational"])
    
    def test_risk_categorical_groups(self, loaded_registry):
        """Test risk categorical groups."""
        risk_type = loaded_registry.get_risk_type()
        
        # Should have levels at minimum
        assert "levels" in risk_type.categorical_groups
        
        # Check levels have required properties
        levels = risk_type.categorical_groups["levels"]
        for level in levels:
            assert "id" in level or "label" in level


# =============================================================================
# INFLUENCE RELATIONSHIP TESTS
# =============================================================================

class TestInfluenceRelationship:
    """Tests for influence relationship type."""
    
    def test_influence_types_loaded(self, loaded_registry):
        """Test that influence types are loaded."""
        influence_types = loaded_registry.get_influence_types()
        assert len(influence_types) >= 1
    
    def test_influence_strengths_loaded(self, loaded_registry):
        """Test that influence strengths are loaded."""
        strengths = loaded_registry.get_influence_strengths()
        assert len(strengths) >= 2  # At least Weak, Strong
    
    def test_influence_constraints(self, loaded_registry):
        """Test influence type constraints."""
        influence_type = loaded_registry.get_influence_type()
        
        # Should have from_entity_types = ["risk"]
        assert "risk" in influence_type.from_entity_types
        assert "risk" in influence_type.to_entity_types
    
    def test_influence_type_level_matching(self, loaded_registry):
        """Test influence type determination by levels."""
        influence_type = loaded_registry.get_influence_type()
        
        # Get valid types for specific level combinations
        # (Results depend on schema constraints)
        risk_levels = loaded_registry.get_risk_level_ids()
        
        if len(risk_levels) >= 2:
            # Try to get valid types for first two levels
            level1, level2 = risk_levels[0], risk_levels[1]
            valid = influence_type.get_valid_influence_types_for_levels(level1, level2)
            # Should return at least one type or empty if no match
            assert isinstance(valid, list)


# =============================================================================
# ENTITY TYPE TESTS
# =============================================================================

class TestEntityTypeDefinition:
    """Tests for entity type definitions."""
    
    def test_entity_neo4j_label(self, loaded_registry):
        """Test Neo4j labels are set."""
        risk_type = loaded_registry.get_risk_type()
        assert risk_type.neo4j_label == "Risk"
        
        mit_type = loaded_registry.get_mitigation_type()
        assert mit_type.neo4j_label == "Mitigation"
    
    def test_entity_has_visual_properties(self, loaded_registry):
        """Test visual properties are loaded."""
        risk_type = loaded_registry.get_risk_type()
        
        # Should have color, shape, emoji
        assert risk_type.color is not None
        assert risk_type.shape is not None
        assert risk_type.emoji is not None


# =============================================================================
# REGISTRY ACCESSORS
# =============================================================================

class TestRegistryAccessors:
    """Tests for registry accessor methods."""
    
    def test_get_entity_by_neo4j_label(self, loaded_registry):
        """Test getting entity by Neo4j label."""
        entity = loaded_registry.get_entity_type_by_neo4j_label("Risk")
        assert entity is not None
        assert entity.id == "risk"
    
    def test_get_ui_config(self, loaded_registry):
        """Test UI configuration access."""
        ui_config = loaded_registry.get_ui_config()
        assert isinstance(ui_config, dict)
    
    def test_get_analysis_config(self, loaded_registry):
        """Test analysis configuration access."""
        analysis_config = loaded_registry.get_analysis_config()
        assert isinstance(analysis_config, dict)


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

class TestBackwardCompatibility:
    """Tests for V1 schema format compatibility."""
    
    def test_v1_entities_section_parsed(self, loaded_registry):
        """Test that entities section is parsed (V1 format)."""
        # The default schema uses V1 format with entities section
        assert loaded_registry.has_entity("risk")
        assert loaded_registry.has_entity("mitigation")
    
    def test_v1_relationships_section_parsed(self, loaded_registry):
        """Test that relationships section is parsed (V1 format)."""
        assert loaded_registry.has_relationship("influences")
        assert loaded_registry.has_relationship("mitigates")
