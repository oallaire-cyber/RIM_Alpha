"""
Tests for F18 – Import/Export and Backup/Restore for Context Data.

All tests are pure unit tests using mocks and BytesIO. No database
connection required.
"""

import io
import json
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import field


# ===========================================================================
# Helpers
# ===========================================================================


def _make_registry(extra_entity_types=None, extra_rel_types=None):
    """Build a lightweight mock registry."""
    registry = MagicMock()

    entity_types = {}
    if extra_entity_types:
        for type_id, props in extra_entity_types.items():
            et = MagicMock()
            et.type_id = type_id
            prop_objs = []
            for p in props:
                pm = MagicMock()
                pm.name = p
                prop_objs.append(pm)
            et.properties = prop_objs
            entity_types[type_id] = et

    registry.entity_types = entity_types
    registry.get_entity_type.side_effect = lambda tid: entity_types.get(tid)

    rel_types = {}
    if extra_rel_types:
        for rel_id, props in extra_rel_types.items():
            rt = MagicMock()
            rt.type_id = rel_id
            prop_objs = []
            for p in props:
                pm = MagicMock()
                pm.name = p
                prop_objs.append(pm)
            rt.properties = prop_objs
            rel_types[rel_id] = rt

    registry.relationship_types = rel_types
    registry.get_relationship_type.side_effect = lambda rid: rel_types.get(rid)

    return registry


# ===========================================================================
# 1. Excel export – context sheets appear in output
# ===========================================================================


class TestExportService:

    def test_get_context_node_sheets_produces_cn_prefix(self):
        """_get_context_node_sheets() must key output with CN_{type_id}."""
        from services.export_service import _get_context_node_sheets

        data = {
            "scenario": [{"name": "S1", "description": "Test"}],
        }
        sheets = _get_context_node_sheets(data)
        assert "CN_scenario" in sheets
        assert len(sheets["CN_scenario"]) == 1
        assert "name" in sheets["CN_scenario"].columns

    def test_get_context_node_sheets_drops_id_column(self):
        """Internal 'id' column must not appear in CN sheet."""
        from services.export_service import _get_context_node_sheets

        sheets = _get_context_node_sheets({"scenario": [{"id": "abc", "name": "S1"}]})
        assert "id" not in sheets["CN_scenario"].columns

    def test_get_context_edge_sheets_produces_ce_prefix(self):
        """_get_context_edge_sheets() must key output with CE_{rel_type_id}."""
        from services.export_service import _get_context_edge_sheets

        data = {
            "depends_on": [{"source_name": "A", "target_name": "B", "weight": 1}],
        }
        sheets = _get_context_edge_sheets(data)
        assert "CE_depends_on" in sheets
        df = sheets["CE_depends_on"]
        # source_name / target_name must appear first
        assert list(df.columns[:2]) == ["source_name", "target_name"]

    def test_export_to_excel_bytes_includes_context_sheets(self):
        """export_to_excel_bytes() must produce CN_* sheets in the output workbook."""
        import openpyxl
        from services.export_service import export_to_excel_bytes

        result = export_to_excel_bytes(
            risks=[],
            influences=[],
            tpos=[],
            tpo_impacts=[],
            mitigations=[],
            mitigates_relationships=[],
            context_nodes_data={"scenario": [{"name": "S1", "description": "D"}]},
            context_edges_data={},
        )
        assert result is not None
        wb = openpyxl.load_workbook(io.BytesIO(result))
        assert "CN_scenario" in wb.sheetnames

    def test_export_to_excel_bytes_backward_compatible(self):
        """Calling export_to_excel_bytes without context args must not raise."""
        from services.export_service import export_to_excel_bytes

        result = export_to_excel_bytes(
            risks=[],
            influences=[],
            tpos=[],
            tpo_impacts=[],
            mitigations=[],
            mitigates_relationships=[],
        )
        # Must succeed even without context params
        assert result is not None


# ===========================================================================
# 2. ImportResult – context counters
# ===========================================================================


class TestImportResult:

    def test_context_fields_present_in_to_dict(self):
        """ImportResult.to_dict() must include all four context counter keys."""
        from services.import_service import ImportResult

        r = ImportResult()
        r.context_nodes_created = 3
        r.context_nodes_skipped = 1
        r.context_edges_created = 2
        r.context_edges_skipped = 0

        d = r.to_dict()
        assert d["context_nodes_created"] == 3
        assert d["context_nodes_skipped"] == 1
        assert d["context_edges_created"] == 2
        assert d["context_edges_skipped"] == 0

    def test_default_context_counters_are_zero(self):
        """ImportResult must default all context counters to 0."""
        from services.import_service import ImportResult

        r = ImportResult()
        d = r.to_dict()
        for key in ("context_nodes_created", "context_nodes_skipped",
                    "context_edges_created", "context_edges_skipped"):
            assert d[key] == 0


# ===========================================================================
# 3. _import_context_nodes – unknown type produces [SCHEMA] warning with YAML
# ===========================================================================


class TestImportContextNodes:

    def _make_excel_bytes_with_sheet(self, sheet_name: str, rows: list) -> bytes:
        """Build a minimal .xlsx file in memory with one sheet."""
        import pandas as pd

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        buf.seek(0)
        return buf.getvalue()

    def _write_temp_excel(self, tmp_path, sheet_name, rows):
        p = tmp_path / "test.xlsx"
        p.write_bytes(self._make_excel_bytes_with_sheet(sheet_name, rows))
        return str(p)

    def test_unknown_type_is_skipped_with_yaml_snippet(self, tmp_path):
        """CN_ sheet whose type is unknown → [SCHEMA] warning with YAML scaffold."""
        from services.import_service import ExcelImporter, ImportResult

        registry = _make_registry()  # no entity types registered

        importer = ExcelImporter(
            create_risk_fn=MagicMock(),
            create_tpo_fn=MagicMock(),
            create_influence_fn=MagicMock(),
            create_tpo_impact_fn=MagicMock(),
            create_mitigation_fn=MagicMock(),
            create_mitigates_fn=MagicMock(),
            get_all_risks_fn=MagicMock(return_value=[]),
            get_all_tpos_fn=MagicMock(return_value=[]),
            get_all_mitigations_fn=MagicMock(return_value=[]),
            create_generic_entity_fn=MagicMock(),
            registry=registry,
        )

        filepath = self._write_temp_excel(
            tmp_path, "CN_ghost",
            [{"name": "G1", "extra_col": "val"}]
        )

        result = ImportResult()
        importer._import_context_nodes(filepath, result)

        # Should have appended a warning
        assert result.warnings
        combined = "\n".join(result.warnings)
        assert "[SCHEMA]" in combined
        assert "ghost" in combined
        assert "schema.yaml" in combined
        # Must include YAML snippet hints
        assert "context_nodes" in combined

    def test_unknown_columns_emit_per_sheet_warning(self, tmp_path):
        """Extra columns on a known CN_ sheet emit a one-time [SCHEMA] warning."""
        from services.import_service import ExcelImporter, ImportResult

        registry = _make_registry(extra_entity_types={"scenario": ["name", "description"]})

        create_fn = MagicMock(return_value={"id": "x"})
        importer = ExcelImporter(
            create_risk_fn=MagicMock(),
            create_tpo_fn=MagicMock(),
            create_influence_fn=MagicMock(),
            create_tpo_impact_fn=MagicMock(),
            create_mitigation_fn=MagicMock(),
            create_mitigates_fn=MagicMock(),
            get_all_risks_fn=MagicMock(return_value=[]),
            get_all_tpos_fn=MagicMock(return_value=[]),
            get_all_mitigations_fn=MagicMock(return_value=[]),
            create_generic_entity_fn=create_fn,
            registry=registry,
        )

        filepath = self._write_temp_excel(
            tmp_path, "CN_scenario",
            [{"name": "S1", "description": "D1", "unknown_field": "X"}]
        )

        result = ImportResult()
        importer._import_context_nodes(filepath, result)

        schema_warnings = [w for w in result.warnings if "[SCHEMA]" in w]
        assert schema_warnings
        w = schema_warnings[0]
        assert "unknown_field" in w
        assert "context_nodes.scenario.properties" in w

    def test_valid_context_node_is_created(self, tmp_path):
        """Valid CN_ sheet row calls create_generic_entity and increments counter."""
        from services.import_service import ExcelImporter, ImportResult

        registry = _make_registry(extra_entity_types={"scenario": ["name", "description"]})
        create_fn = MagicMock(return_value={"id": "new-1"})

        importer = ExcelImporter(
            create_risk_fn=MagicMock(),
            create_tpo_fn=MagicMock(),
            create_influence_fn=MagicMock(),
            create_tpo_impact_fn=MagicMock(),
            create_mitigation_fn=MagicMock(),
            create_mitigates_fn=MagicMock(),
            get_all_risks_fn=MagicMock(return_value=[]),
            get_all_tpos_fn=MagicMock(return_value=[]),
            get_all_mitigations_fn=MagicMock(return_value=[]),
            create_generic_entity_fn=create_fn,
            registry=registry,
        )

        import pandas as pd
        buf = io.BytesIO()
        pd.DataFrame([
            {"name": "Scenario A", "description": "First"},
            {"name": "Scenario B", "description": "Second"},
        ]).to_excel(buf, sheet_name="CN_scenario", index=False)
        buf.seek(0)
        p = tmp_path / "valid.xlsx"
        p.write_bytes(buf.getvalue())

        result = ImportResult()
        importer._import_context_nodes(str(p), result)

        assert result.context_nodes_created == 2
        assert result.context_nodes_skipped == 0
        assert create_fn.call_count == 2


# ===========================================================================
# 4. backup_service – export shape + restore round-trip with mocks
# ===========================================================================


class TestBackupService:

    def _make_manager(self):
        m = MagicMock()
        m.get_all_risks.return_value = [{"id": "r1", "name": "Risk A", "level": "Business"}]
        m.get_all_tpos.return_value = []
        m.get_all_mitigations.return_value = []
        m.get_semantic_influences.return_value = []
        m.get_all_tpo_impacts.return_value = []
        m.get_all_mitigates_relationships.return_value = []
        m.get_entities.return_value = []
        m.get_relationships.return_value = []
        return m

    def test_export_graph_to_json_has_required_keys(self):
        """export_graph_to_json() must produce a dict with all top-level keys."""
        from services.backup_service import export_graph_to_json, BACKUP_VERSION

        registry = _make_registry()
        mgr = self._make_manager()

        data = export_graph_to_json(mgr, registry)

        for key in ("schema_version", "exported_at", "risks", "tpos", "mitigations",
                    "influences", "tpo_impacts", "mitigates",
                    "context_nodes", "context_edges"):
            assert key in data, f"Missing key: {key}"

        assert data["schema_version"] == BACKUP_VERSION
        assert len(data["risks"]) == 1
        assert data["risks"][0]["name"] == "Risk A"

    def test_export_includes_context_nodes(self):
        """export_graph_to_json() must include context entity data when present."""
        from services.backup_service import export_graph_to_json

        registry = _make_registry(extra_entity_types={"scenario": ["name"]})
        registry.entity_types["scenario"].type_id = "scenario"

        mgr = self._make_manager()
        mgr.get_entities.side_effect = lambda tid: (
            [{"id": "s1", "name": "S1"}] if tid == "scenario" else []
        )

        data = export_graph_to_json(mgr, registry)
        assert "scenario" in data["context_nodes"]
        assert data["context_nodes"]["scenario"][0]["name"] == "S1"

    def test_json_serializable(self):
        """export_graph_to_json() output must be JSON-serializable."""
        from services.backup_service import export_graph_to_json

        registry = _make_registry()
        data = export_graph_to_json(self._make_manager(), registry)
        # Should not raise
        dumped = json.dumps(data, default=str)
        loaded = json.loads(dumped)
        assert loaded["risks"][0]["name"] == "Risk A"
