"""
Tests for Analysis Scope feature.

Covers:
- AnalysisScopeConfig dataclass
- SchemaLoader scope parsing and serialization
- FilterManager scope-aware filtering
- get_graph_data() scope filtering
- calculate_exposure() scope pre-filtering
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# DATACLASS TESTS
# =============================================================================

class TestAnalysisScopeConfig:
    """Test the AnalysisScopeConfig dataclass."""

    def test_create_minimal(self):
        from config.schema_loader import AnalysisScopeConfig
        scope = AnalysisScopeConfig(id="test", name="Test Scope")
        assert scope.id == "test"
        assert scope.name == "Test Scope"
        assert scope.description == ""
        assert scope.node_ids == []
        assert scope.include_connected_edges is True
        assert scope.show_boundary_edges is False
        assert scope.color == "#808080"

    def test_create_full(self):
        from config.schema_loader import AnalysisScopeConfig
        scope = AnalysisScopeConfig(
            id="fuel_chain",
            name="⛽ Fuel Supply Chain",
            description="All fuel supply risks",
            node_ids=["uuid-1", "uuid-2", "uuid-3"],
            include_connected_edges=True,
            show_boundary_edges=True,
            color="#e67e22",
        )
        assert scope.id == "fuel_chain"
        assert len(scope.node_ids) == 3
        assert scope.show_boundary_edges is True
        assert scope.color == "#e67e22"

    def test_node_ids_are_independent_instances(self):
        """Ensure default_factory creates separate lists per instance."""
        from config.schema_loader import AnalysisScopeConfig
        scope_a = AnalysisScopeConfig(id="a", name="A")
        scope_b = AnalysisScopeConfig(id="b", name="B")
        scope_a.node_ids.append("x")
        assert scope_b.node_ids == []  # Should NOT share list


# =============================================================================
# SCHEMA LOADER PARSING TESTS
# =============================================================================

class TestSchemaLoaderScopes:
    """Test SchemaLoader scope parsing and serialization."""

    def _get_loader(self):
        from config.schema_loader import SchemaLoader
        return SchemaLoader()

    def test_parse_scopes_empty(self):
        loader = self._get_loader()
        scopes = loader._parse_scopes([])
        assert scopes == []

    def test_parse_scopes_single(self):
        loader = self._get_loader()
        data = [
            {
                "id": "scope1",
                "name": "Test Scope",
                "description": "A test",
                "node_ids": ["n1", "n2"],
                "include_connected_edges": False,
                "show_boundary_edges": True,
                "color": "#ff0000",
            }
        ]
        scopes = loader._parse_scopes(data)
        assert len(scopes) == 1
        s = scopes[0]
        assert s.id == "scope1"
        assert s.name == "Test Scope"
        assert s.node_ids == ["n1", "n2"]
        assert s.include_connected_edges is False
        assert s.show_boundary_edges is True
        assert s.color == "#ff0000"

    def test_parse_scopes_multiple(self):
        loader = self._get_loader()
        data = [
            {"id": "s1", "name": "Scope 1"},
            {"id": "s2", "name": "Scope 2", "node_ids": ["a", "b"]},
        ]
        scopes = loader._parse_scopes(data)
        assert len(scopes) == 2
        assert scopes[0].id == "s1"
        assert scopes[1].node_ids == ["a", "b"]

    def test_parse_scope_defaults(self):
        """Missing fields should get defaults."""
        loader = self._get_loader()
        scopes = loader._parse_scopes([{"id": "x", "name": "X"}])
        s = scopes[0]
        assert s.description == ""
        assert s.node_ids == []
        assert s.include_connected_edges is True
        assert s.show_boundary_edges is False
        assert s.color == "#808080"

    def test_scope_to_dict_roundtrip(self):
        """Parse -> to_dict should produce equivalent data."""
        from config.schema_loader import AnalysisScopeConfig
        loader = self._get_loader()
        original = AnalysisScopeConfig(
            id="rt",
            name="Roundtrip",
            description="Test roundtrip",
            node_ids=["a", "b", "c"],
            include_connected_edges=True,
            show_boundary_edges=False,
            color="#abcdef",
        )
        as_dict = loader._scope_to_dict(original)
        parsed_list = loader._parse_scopes([as_dict])
        restored = parsed_list[0]
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.node_ids == original.node_ids
        assert restored.include_connected_edges == original.include_connected_edges
        assert restored.show_boundary_edges == original.show_boundary_edges
        assert restored.color == original.color


# =============================================================================
# SCHEMA CONFIG INTEGRATION
# =============================================================================

class TestSchemaConfigScopes:
    """Test that scopes integrate correctly into SchemaConfig."""

    def test_schema_config_has_scopes_field(self):
        from config.schema_loader import SchemaConfig
        config = SchemaConfig()
        assert hasattr(config, "scopes")
        assert config.scopes == []

    def test_schema_to_dict_includes_scopes(self):
        from config.schema_loader import SchemaConfig, SchemaLoader, AnalysisScopeConfig
        loader = SchemaLoader()
        config = SchemaConfig()
        config.scopes = [
            AnalysisScopeConfig(id="s1", name="Scope 1", node_ids=["x"]),
        ]
        data = loader._schema_to_dict(config)
        assert "scopes" in data
        assert len(data["scopes"]) == 1
        assert data["scopes"][0]["id"] == "s1"
        assert data["scopes"][0]["node_ids"] == ["x"]


# =============================================================================
# FILTER MANAGER SCOPE TESTS
# =============================================================================

class TestFilterManagerScopes:
    """Test FilterManager scope-related functionality."""

    def _make_scope(self, id, name, node_ids):
        from config.schema_loader import AnalysisScopeConfig
        return AnalysisScopeConfig(id=id, name=name, node_ids=node_ids)

    def _get_filter_manager(self):
        from ui.filters import FilterManager
        return FilterManager()

    def test_no_scope_by_default(self):
        fm = self._get_filter_manager()
        assert fm.active_scopes == []
        assert fm.get_scope_node_ids() is None

    def test_set_single_scope(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "Scope 1", ["a", "b", "c"])
        fm.set_active_scopes([scope])
        assert len(fm.active_scopes) == 1
        assert set(fm.get_scope_node_ids()) == {"a", "b", "c"}

    def test_set_multiple_scopes_union(self):
        fm = self._get_filter_manager()
        s1 = self._make_scope("s1", "S1", ["a", "b"])
        s2 = self._make_scope("s2", "S2", ["b", "c"])
        fm.set_active_scopes([s1, s2])
        ids = fm.get_scope_node_ids()
        assert set(ids) == {"a", "b", "c"}  # Union, deduplicated

    def test_clear_scopes(self):
        fm = self._get_filter_manager()
        fm.set_active_scopes([self._make_scope("s1", "S1", ["a"])])
        fm.clear_scopes()
        assert fm.active_scopes == []
        assert fm.get_scope_node_ids() is None

    def test_add_node_to_scope(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "S1", ["a"])
        fm.set_active_scopes([scope])
        assert fm.add_node_to_scope("s1", "b") is True
        assert "b" in fm.active_scopes[0].node_ids

    def test_add_node_duplicate_noop(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "S1", ["a"])
        fm.set_active_scopes([scope])
        assert fm.add_node_to_scope("s1", "a") is False  # Already in scope

    def test_add_node_wrong_scope_id(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "S1", ["a"])
        fm.set_active_scopes([scope])
        assert fm.add_node_to_scope("s99", "b") is False

    def test_remove_node_from_scope(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "S1", ["a", "b"])
        fm.set_active_scopes([scope])
        assert fm.remove_node_from_scope("s1", "a") is True
        assert fm.active_scopes[0].node_ids == ["b"]

    def test_remove_node_not_in_scope(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "S1", ["a"])
        fm.set_active_scopes([scope])
        assert fm.remove_node_from_scope("s1", "z") is False

    def test_get_filters_for_query_includes_scope_ids(self):
        fm = self._get_filter_manager()
        scope = self._make_scope("s1", "S1", ["a", "b"])
        fm.set_active_scopes([scope])
        q = fm.get_filters_for_query()
        assert "scope_node_ids" in q
        assert set(q["scope_node_ids"]) == {"a", "b"}

    def test_get_filters_for_query_no_scope(self):
        fm = self._get_filter_manager()
        q = fm.get_filters_for_query()
        assert "scope_node_ids" not in q

    def test_filter_summary_with_scopes(self):
        fm = self._get_filter_manager()
        fm.set_active_scopes([self._make_scope("s1", "Alpha", ["a"])])
        summary = fm.get_filter_summary()
        assert "Alpha" in summary
        assert "Scopes:" in summary

    def test_filter_summary_without_scopes(self):
        fm = self._get_filter_manager()
        summary = fm.get_filter_summary()
        assert "Scopes:" not in summary


# =============================================================================
# GET_GRAPH_DATA SCOPE FILTERING
# =============================================================================

class TestGetGraphDataScoping:
    """Test scope filtering in get_graph_data."""

    def test_scope_filters_nodes(self):
        """Nodes outside scope should be removed."""
        from database.queries.analysis import get_graph_data

        mock_conn = MagicMock()

        # Mock the individual query functions to return known data
        with patch("database.queries.analysis.risks.get_risks_with_filters") as mock_risks:
            mock_risks.return_value = [
                {"id": "r1", "name": "Risk 1", "level": "Business"},
                {"id": "r2", "name": "Risk 2", "level": "Operational"},
                {"id": "r3", "name": "Risk 3", "level": "Business"},
            ]
            with patch("database.queries.analysis.influences.get_influence_edges") as mock_inf:
                mock_inf.return_value = [
                    {"source": "r1", "target": "r2", "strength": "Strong"},
                    {"source": "r2", "target": "r3", "strength": "Moderate"},
                ]

                nodes, edges = get_graph_data(
                    mock_conn,
                    filters={
                        "scope_node_ids": ["r1", "r2"],
                        "show_tpos": False,
                        "show_mitigations": False,
                    }
                )

        node_ids = {n["id"] for n in nodes}
        assert node_ids == {"r1", "r2"}  # r3 excluded by scope

        # Only r1->r2 edge should remain (r2->r3 crosses scope boundary)
        assert len(edges) == 1
        assert edges[0]["source"] == "r1"
        assert edges[0]["target"] == "r2"

    def test_no_scope_returns_all(self):
        """Without scope_node_ids, all nodes should be returned."""
        from database.queries.analysis import get_graph_data

        mock_conn = MagicMock()
        with patch("database.queries.analysis.risks.get_risks_with_filters") as mock_risks:
            mock_risks.return_value = [
                {"id": "r1", "name": "Risk 1", "level": "Business"},
                {"id": "r2", "name": "Risk 2", "level": "Operational"},
            ]
            with patch("database.queries.analysis.influences.get_influence_edges") as mock_inf:
                mock_inf.return_value = [
                    {"source": "r1", "target": "r2", "strength": "Strong"},
                ]

                nodes, edges = get_graph_data(
                    mock_conn,
                    filters={"show_tpos": False, "show_mitigations": False}
                )

        assert len(nodes) == 2
        assert len(edges) == 1


# =============================================================================
# CALCULATE_EXPOSURE SCOPE FILTERING
# =============================================================================

class TestCalculateExposureScoping:
    """Test scope filtering in calculate_exposure."""

    def test_scope_filters_risks(self):
        """Only scoped risks should be passed to the calculator."""
        from database.manager import RiskGraphManager

        # Create a mock manager with the real calculate_exposure method bound
        manager = MagicMock(spec=RiskGraphManager)
        manager.get_all_risks.return_value = [
            {"id": "r1", "name": "R1", "level": "Business", "probability": 5, "impact": 5, "exposure": 25},
            {"id": "r2", "name": "R2", "level": "Operational", "probability": 3, "impact": 3, "exposure": 9},
        ]
        manager.get_all_influences.return_value = [
            {"source_id": "r1", "target_id": "r2", "strength": "Moderate"},
        ]
        manager.get_all_mitigations.return_value = [
            {"id": "m1", "name": "Mit1", "type": "Dedicated", "status": "Implemented"},
        ]
        manager.get_all_mitigates_relationships.return_value = [
            {"mitigation_id": "m1", "risk_id": "r1", "effectiveness": "High"},
        ]

        with patch("services.exposure_calculator.calculate_exposure") as mock_calc:
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"test": True}
            mock_calc.return_value = mock_result

            # Call the real method with the mocked manager
            result = RiskGraphManager.calculate_exposure(manager, scope_node_ids=["r1", "m1"])

            # Verify the calculator was called with filtered data
            call_args = mock_calc.call_args
            passed_risks = call_args.kwargs.get("risks", [])
            risk_ids = [r["id"] for r in passed_risks]
            assert "r1" in risk_ids
            assert "r2" not in risk_ids  # r2 excluded by scope
