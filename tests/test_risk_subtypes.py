"""
Tests for the Risk Subtype system (v2.11.0).

Tests schema_loader parsing, round-tripping, and get_subtypes_for_level() helper.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.schema_loader import (
    SchemaLoader,
    RiskSubtypeConfig,
    RiskSubtypeFieldConfig,
    RiskEntityConfig,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def schema():
    """Load the default schema."""
    loader = SchemaLoader()
    return loader.load_schema("default")


@pytest.fixture
def loader():
    """Create a SchemaLoader instance."""
    return SchemaLoader()


# =============================================================================
# SCHEMA LOADING TESTS
# =============================================================================

class TestSubtypeParsing:
    """Test that subtypes are correctly parsed from schema.yaml."""

    def test_schema_has_subtypes(self, schema):
        """The default schema should define risk subtypes."""
        assert hasattr(schema.risk, "subtypes")
        assert isinstance(schema.risk.subtypes, list)
        assert len(schema.risk.subtypes) > 0

    def test_schema_has_nine_subtypes(self, schema):
        """Default schema should define exactly 9 subtypes."""
        assert len(schema.risk.subtypes) == 9

    def test_subtype_ids(self, schema):
        """Verify all expected subtype IDs are present."""
        ids = {st.id for st in schema.risk.subtypes}
        expected = {
            "generic",
            "cyber_entry_point",
            "cyber_target_oriented",
            "supply_chain",
            "engineering_technical",
            "programme_schedule",
            "regulatory_compliance",
            "financial_contractual",
            "strategic",
        }
        assert ids == expected

    def test_subtype_dataclass_type(self, schema):
        """Each subtype should be a RiskSubtypeConfig."""
        for st in schema.risk.subtypes:
            assert isinstance(st, RiskSubtypeConfig)

    def test_subtype_has_label(self, schema):
        """Every subtype should have a non-empty label."""
        for st in schema.risk.subtypes:
            assert st.label, f"Subtype {st.id} missing label"

    def test_subtype_has_applies_to(self, schema):
        """Every subtype should have at least one level in applies_to."""
        for st in schema.risk.subtypes:
            assert len(st.applies_to) > 0, f"Subtype {st.id} has empty applies_to"

    def test_generic_applies_to_both_levels(self, schema):
        """Generic subtype should apply to both business and operational."""
        generic = next(st for st in schema.risk.subtypes if st.id == "generic")
        assert "business" in generic.applies_to
        assert "operational" in generic.applies_to

    def test_strategic_applies_to_business_only(self, schema):
        """Strategic subtype should apply to business only."""
        strategic = next(st for st in schema.risk.subtypes if st.id == "strategic")
        assert "business" in strategic.applies_to
        assert "operational" not in strategic.applies_to

    def test_generic_has_no_extension_fields(self, schema):
        """Generic subtype should have zero extension fields."""
        generic = next(st for st in schema.risk.subtypes if st.id == "generic")
        assert len(generic.extension_fields) == 0


class TestSubtypeExtensionFields:
    """Test extension field parsing for subtypes."""

    def test_cyber_entry_point_has_three_fields(self, schema):
        """Cyber entry point subtype should define 3 extension fields."""
        st = next(s for s in schema.risk.subtypes if s.id == "cyber_entry_point")
        assert len(st.extension_fields) == 3

    def test_extension_field_dataclass_type(self, schema):
        """Extension fields should be RiskSubtypeFieldConfig instances."""
        st = next(s for s in schema.risk.subtypes if s.id == "cyber_entry_point")
        for f in st.extension_fields:
            assert isinstance(f, RiskSubtypeFieldConfig)

    def test_extension_field_names(self, schema):
        """Verify extension field names for cyber_entry_point."""
        st = next(s for s in schema.risk.subtypes if s.id == "cyber_entry_point")
        names = {f.name for f in st.extension_fields}
        assert "entry_point_type" in names
        assert "exploitation_technique" in names
        assert "detection_difficulty" in names

    def test_enum_field_has_values(self, schema):
        """Enum extension fields should have a non-empty values list."""
        st = next(s for s in schema.risk.subtypes if s.id == "cyber_entry_point")
        entry_point = next(f for f in st.extension_fields if f.name == "entry_point_type")
        assert entry_point.type == "enum"
        assert len(entry_point.values) > 0
        assert "Network" in entry_point.values

    def test_string_field_has_empty_values(self, schema):
        """String extension fields should have an empty values list."""
        st = next(s for s in schema.risk.subtypes if s.id == "cyber_entry_point")
        technique = next(f for f in st.extension_fields if f.name == "exploitation_technique")
        assert technique.type == "string"
        assert len(technique.values) == 0

    def test_boolean_field_type(self, schema):
        """Supply chain subtype should include a boolean field."""
        st = next(s for s in schema.risk.subtypes if s.id == "supply_chain")
        single_source = next(f for f in st.extension_fields if f.name == "single_source")
        assert single_source.type == "boolean"

    def test_integer_field_type(self, schema):
        """Programme schedule subtype should include an integer field."""
        st = next(s for s in schema.risk.subtypes if s.id == "programme_schedule")
        buffer_field = next(f for f in st.extension_fields if f.name == "schedule_buffer_weeks")
        assert buffer_field.type == "integer"

    def test_float_field_type(self, schema):
        """Financial/contractual subtype should include a float field."""
        st = next(s for s in schema.risk.subtypes if s.id == "financial_contractual")
        ceiling = next(f for f in st.extension_fields if f.name == "financial_ceiling_meur")
        assert ceiling.type == "float"

    def test_all_fields_not_required(self, schema):
        """All extension fields should have required=False."""
        for st in schema.risk.subtypes:
            for f in st.extension_fields:
                assert f.required is False, f"{st.id}.{f.name} is required=True"


class TestGetSubtypesForLevel:
    """Test the get_subtypes_for_level() helper."""

    def test_business_level_includes_generic(self, schema):
        """Business level should include the generic subtype."""
        results = schema.risk.get_subtypes_for_level("business")
        ids = {st.id for st in results}
        assert "generic" in ids

    def test_business_level_includes_strategic(self, schema):
        """Business level should include strategic."""
        results = schema.risk.get_subtypes_for_level("business")
        ids = {st.id for st in results}
        assert "strategic" in ids

    def test_business_level_excludes_cyber_entry_point(self, schema):
        """Business level should not include cyber_entry_point."""
        results = schema.risk.get_subtypes_for_level("business")
        ids = {st.id for st in results}
        assert "cyber_entry_point" not in ids

    def test_operational_level_includes_generic(self, schema):
        """Operational level should include the generic subtype."""
        results = schema.risk.get_subtypes_for_level("operational")
        ids = {st.id for st in results}
        assert "generic" in ids

    def test_operational_level_includes_cyber_entry_point(self, schema):
        """Operational level should include cyber_entry_point."""
        results = schema.risk.get_subtypes_for_level("operational")
        ids = {st.id for st in results}
        assert "cyber_entry_point" in ids

    def test_operational_level_excludes_strategic(self, schema):
        """Operational level should not include strategic."""
        results = schema.risk.get_subtypes_for_level("operational")
        ids = {st.id for st in results}
        assert "strategic" not in ids

    def test_unknown_level_returns_empty(self, schema):
        """An unknown level should return an empty list."""
        results = schema.risk.get_subtypes_for_level("tactical")
        assert results == []

    def test_case_insensitive_level(self, schema):
        """Level matching should be case-insensitive (via .lower())."""
        results = schema.risk.get_subtypes_for_level("Business")
        ids = {st.id for st in results}
        assert "generic" in ids

    def test_business_level_count(self, schema):
        """Business level should have exactly 5 applicable subtypes."""
        results = schema.risk.get_subtypes_for_level("business")
        # generic, programme_schedule, regulatory_compliance, financial_contractual, strategic
        assert len(results) == 5

    def test_operational_level_count(self, schema):
        """Operational level should have exactly 8 applicable subtypes."""
        results = schema.risk.get_subtypes_for_level("operational")
        # generic, cyber_entry_point, cyber_target_oriented, supply_chain,
        # engineering_technical, programme_schedule, regulatory_compliance, financial_contractual
        assert len(results) == 8


class TestSubtypeRoundTrip:
    """Test serialization round-trip via _risk_entity_to_dict."""

    def test_round_trip_preserves_subtype_count(self, schema, loader):
        """Saving and reloading should preserve subtype count."""
        original_count = len(schema.risk.subtypes)
        
        # Serialize
        d = loader._risk_entity_to_dict(schema.risk)
        assert "subtypes" in d
        assert len(d["subtypes"]) == original_count

    def test_round_trip_preserves_ids(self, schema, loader):
        """Serialized subtypes should have the same IDs."""
        d = loader._risk_entity_to_dict(schema.risk)
        serialized_ids = {st["id"] for st in d["subtypes"]}
        original_ids = {st.id for st in schema.risk.subtypes}
        assert serialized_ids == original_ids

    def test_round_trip_preserves_extension_fields(self, schema, loader):
        """Serialization should preserve extension field details."""
        d = loader._risk_entity_to_dict(schema.risk)
        cyber_ep = next(st for st in d["subtypes"] if st["id"] == "cyber_entry_point")
        assert len(cyber_ep["extension_fields"]) == 3
        
        entry_point_field = next(f for f in cyber_ep["extension_fields"] if f["name"] == "entry_point_type")
        assert entry_point_field["type"] == "enum"
        assert "Network" in entry_point_field["values"]

    def test_round_trip_preserves_applies_to(self, schema, loader):
        """Serialization should preserve applies_to lists."""
        d = loader._risk_entity_to_dict(schema.risk)
        generic = next(st for st in d["subtypes"] if st["id"] == "generic")
        assert "business" in generic["applies_to"]
        assert "operational" in generic["applies_to"]

    def test_full_save_reload_round_trip(self, schema, loader, tmp_path):
        """Full round-trip: save schema to disk, reload, verify subtypes match."""
        # Save to temp dir
        temp_schemas_dir = tmp_path / "schemas"
        temp_schemas_dir.mkdir()
        temp_loader = SchemaLoader(temp_schemas_dir)
        temp_loader.save_schema(schema, "test_roundtrip")
        
        # Reload
        reloaded = temp_loader.load_schema("test_roundtrip")
        
        # Verify
        assert len(reloaded.risk.subtypes) == len(schema.risk.subtypes)
        for orig, reloaded_st in zip(schema.risk.subtypes, reloaded.risk.subtypes):
            assert orig.id == reloaded_st.id
            assert orig.label == reloaded_st.label
            assert orig.applies_to == reloaded_st.applies_to
            assert len(orig.extension_fields) == len(reloaded_st.extension_fields)


class TestSubtypeFieldConfigDefaults:
    """Test default values for RiskSubtypeFieldConfig."""

    def test_default_type_is_string(self):
        """Default field type should be 'string'."""
        field = RiskSubtypeFieldConfig(name="test_field")
        assert field.type == "string"

    def test_default_required_is_false(self):
        """Default required should be False."""
        field = RiskSubtypeFieldConfig(name="test_field")
        assert field.required is False

    def test_default_description_is_empty(self):
        """Default description should be empty string."""
        field = RiskSubtypeFieldConfig(name="test_field")
        assert field.description == ""

    def test_default_values_is_empty_list(self):
        """Default values should be empty list."""
        field = RiskSubtypeFieldConfig(name="test_field")
        assert field.values == []
