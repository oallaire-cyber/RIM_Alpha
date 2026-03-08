"""
Backup Service.

Provides full-graph JSON backup and restore capabilities for the RIM platform.
All entity types — including schema-driven ContextNodes and ContextEdges — are
captured in a single portable JSON document.

Backup format:

    {
        "schema_version": "2.18.0",
        "exported_at": "2026-03-08T18:16:00",
        "risks": [...],
        "tpos": [...],
        "influences": [...],
        "tpo_impacts": [...],
        "mitigations": [...],
        "mitigates": [...],
        "context_nodes": {"<type_id>": [...], ...},
        "context_edges": {"<rel_type_id>": [...], ...}
    }

Restore behaviour:
    - Inserts in topological order: core nodes first, then core edges,
      then context nodes, then context edges.
    - Upserts by 'name' for nodes — rows whose name already exists are skipped.
    - Returns a summary dict with created/skipped counts per entity type.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database.manager import RiskGraphManager

# Current backup format version (increment on breaking schema changes)
BACKUP_VERSION = "2.18.0"


# =============================================================================
# EXPORT
# =============================================================================


def export_graph_to_json(
    manager: "RiskGraphManager",
    registry=None,
) -> Dict[str, Any]:
    """
    Export the full graph to a JSON-serialisable dict.

    Collects all core entity types plus every ContextNode and ContextEdge
    type known to the schema registry.

    Args:
        manager: Connected RiskGraphManager instance.
        registry: SchemaRegistry instance. If None, only core data is exported.

    Returns:
        A dict suitable for json.dumps(), keyed as described in the module
        docstring above.
    """
    from core import get_registry as _get_registry

    if registry is None:
        registry = _get_registry()

    data: Dict[str, Any] = {
        "schema_version": BACKUP_VERSION,
        "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        # Core nodes
        "risks": [dict(r) for r in manager.get_all_risks()],
        "tpos": [dict(t) for t in manager.get_all_tpos()],
        "mitigations": [dict(m) for m in manager.get_all_mitigations()],
        # Core edges
        "influences": [dict(i) for i in manager.get_semantic_influences()],
        "tpo_impacts": [dict(i) for i in manager.get_all_tpo_impacts()],
        "mitigates": [dict(r) for r in manager.get_all_mitigates_relationships()],
        # Context data - populated below
        "context_nodes": {},
        "context_edges": {},
    }

    # --- ContextNode types ---
    if registry:
        for entity_type in registry.entity_types.values():
            type_id = entity_type.type_id
            # Skip the two hardcoded core types
            if type_id in ("risk", "mitigation"):
                continue
            entities = manager.get_entities(type_id) or []
            if entities:
                data["context_nodes"][type_id] = [dict(e) for e in entities]

        # --- ContextEdge types ---
        kernel_rel_ids = {"influences", "mitigates"}
        for rel_type in registry.relationship_types.values():
            rel_id = getattr(rel_type, "type_id", None) or getattr(rel_type, "id", None)
            if not rel_id or rel_id in kernel_rel_ids:
                continue
            edges = manager.get_relationships(rel_id) or []
            if edges:
                data["context_edges"][rel_id] = [dict(e) for e in edges]

    return data


# =============================================================================
# RESTORE
# =============================================================================


def import_graph_from_json(
    manager: "RiskGraphManager",
    data: Dict[str, Any],
    registry=None,
) -> Dict[str, Any]:
    """
    Restore a graph from a JSON backup dict produced by export_graph_to_json().

    Insertion order (topological):
        1. Core nodes:  Risks → TPOs → Mitigations
        2. Core edges:  Influences → TPO Impacts → Mitigates
        3. Context nodes (in schema order)
        4. Context edges (in schema order)

    Upsert behaviour:
        - Nodes: if a node with the same 'name' already exists, the row is skipped.
        - Edges: if source or target name cannot be resolved, the row is skipped
          with a warning entry.

    Args:
        manager: Connected RiskGraphManager instance.
        data: Backup dict as produced by export_graph_to_json().
        registry: SchemaRegistry instance. If None, only core data is restored.

    Returns:
        Summary dict with 'created' and 'skipped' counts per entity type,
        plus an 'errors' list.
    """
    from core import get_registry as _get_registry

    if registry is None:
        registry = _get_registry()

    summary: Dict[str, Any] = {
        "errors": [],
        "risks_created": 0, "risks_skipped": 0,
        "tpos_created": 0, "tpos_skipped": 0,
        "mitigations_created": 0, "mitigations_skipped": 0,
        "influences_created": 0, "influences_skipped": 0,
        "tpo_impacts_created": 0, "tpo_impacts_skipped": 0,
        "mitigates_created": 0, "mitigates_skipped": 0,
        "context_nodes_created": 0, "context_nodes_skipped": 0,
        "context_edges_created": 0, "context_edges_skipped": 0,
    }

    # ------------------------------------------------------------------
    # Build name → id maps from existing DB state before inserting
    # ------------------------------------------------------------------
    existing_risks = {r["name"]: r["id"] for r in manager.get_all_risks()}
    existing_tpos = {t["reference"]: t["id"] for t in manager.get_all_tpos()}
    existing_mits = {m["name"]: m["id"] for m in manager.get_all_mitigations()}

    # ------------------------------------------------------------------
    # 1. Core Nodes
    # ------------------------------------------------------------------

    # Risks
    for risk_data in data.get("risks", []):
        name = risk_data.get("name", "")
        if name in existing_risks:
            summary["risks_skipped"] += 1
            continue
        try:
            # Strip internal IDs — let Neo4j assign new ones
            row = {k: v for k, v in risk_data.items() if k not in ("id", "element_id")}
            result = manager.create_risk(**_risk_kwargs(row))
            if result:
                existing_risks[name] = result.get("id", "")
                summary["risks_created"] += 1
            else:
                summary["risks_skipped"] += 1
        except Exception as e:
            summary["risks_skipped"] += 1
            summary["errors"].append(f"Risk '{name}': {e}")

    # TPOs
    for tpo_data in data.get("tpos", []):
        ref = tpo_data.get("reference", "")
        if ref in existing_tpos:
            summary["tpos_skipped"] += 1
            continue
        try:
            row = {k: v for k, v in tpo_data.items() if k not in ("id", "element_id")}
            result = manager.create_tpo(**_tpo_kwargs(row))
            if result:
                existing_tpos[ref] = result.get("id", "")
                summary["tpos_created"] += 1
            else:
                summary["tpos_skipped"] += 1
        except Exception as e:
            summary["tpos_skipped"] += 1
            summary["errors"].append(f"TPO '{ref}': {e}")

    # Mitigations
    for mit_data in data.get("mitigations", []):
        name = mit_data.get("name", "")
        if name in existing_mits:
            summary["mitigations_skipped"] += 1
            continue
        try:
            row = {k: v for k, v in mit_data.items() if k not in ("id", "element_id")}
            result = manager.create_mitigation(**_mit_kwargs(row))
            if result:
                existing_mits[name] = result.get("id", "")
                summary["mitigations_created"] += 1
            else:
                summary["mitigations_skipped"] += 1
        except Exception as e:
            summary["mitigations_skipped"] += 1
            summary["errors"].append(f"Mitigation '{name}': {e}")

    # ------------------------------------------------------------------
    # 2. Core Edges
    # ------------------------------------------------------------------

    # Influences (Risk → Risk)
    for inf in data.get("influences", []):
        src_id = existing_risks.get(inf.get("source_name", ""))
        tgt_id = existing_risks.get(inf.get("target_name", ""))
        if not src_id or not tgt_id:
            summary["influences_skipped"] += 1
            continue
        try:
            result = manager.create_influence(
                source_id=src_id,
                target_id=tgt_id,
                influence_type=inf.get("type") or inf.get("influence_type", ""),
                strength=inf.get("strength", "Moderate"),
                confidence=inf.get("confidence"),
                description=inf.get("description", ""),
            )
            if result:
                summary["influences_created"] += 1
            else:
                summary["influences_skipped"] += 1
        except Exception as e:
            summary["influences_skipped"] += 1
            summary["errors"].append(f"Influence {inf.get('source_name')} → {inf.get('target_name')}: {e}")

    # TPO Impacts (Risk → TPO)
    for imp in data.get("tpo_impacts", []):
        risk_id = existing_risks.get(imp.get("risk_name", ""))
        tpo_id = existing_tpos.get(imp.get("tpo_reference", "") or imp.get("tpo_ref", ""))
        if not risk_id or not tpo_id:
            summary["tpo_impacts_skipped"] += 1
            continue
        try:
            result = manager.create_tpo_impact(
                risk_id=risk_id,
                tpo_id=tpo_id,
                impact_level=imp.get("impact_level", "Medium"),
                description=imp.get("description", ""),
            )
            if result:
                summary["tpo_impacts_created"] += 1
            else:
                summary["tpo_impacts_skipped"] += 1
        except Exception as e:
            summary["tpo_impacts_skipped"] += 1
            summary["errors"].append(f"TPO Impact: {e}")

    # Mitigates (Mitigation → Risk)
    for rel in data.get("mitigates", []):
        mit_id = existing_mits.get(rel.get("mitigation_name", ""))
        risk_id = existing_risks.get(rel.get("risk_name", ""))
        if not mit_id or not risk_id:
            summary["mitigates_skipped"] += 1
            continue
        try:
            result = manager.create_mitigates_relationship(
                mitigation_id=mit_id,
                risk_id=risk_id,
                effectiveness=rel.get("effectiveness", "Medium"),
                description=rel.get("description", ""),
            )
            if result:
                summary["mitigates_created"] += 1
            else:
                summary["mitigates_skipped"] += 1
        except Exception as e:
            summary["mitigates_skipped"] += 1
            summary["errors"].append(f"Mitigates: {e}")

    # ------------------------------------------------------------------
    # 3. Context Nodes
    # ------------------------------------------------------------------

    # Build unified name → id map for edge resolution later
    node_name_to_id: Dict[str, str] = {}
    node_name_to_id.update(existing_risks)
    node_name_to_id.update({k: v for k, v in existing_tpos.items()})

    if registry:
        for type_id, entities in data.get("context_nodes", {}).items():
            entity_type = registry.get_entity_type(type_id)
            if entity_type is None:
                skipped = len(entities)
                summary["context_nodes_skipped"] += skipped
                summary["errors"].append(
                    f"[SCHEMA] Context node type '{type_id}' not found in schema — "
                    f"{skipped} record(s) skipped. Update schema.yaml to enable restore."
                )
                continue

            existing_cn = {e["name"]: e["id"] for e in (manager.get_entities(type_id) or []) if e.get("name")}

            for entity_data in entities:
                name = entity_data.get("name", "")
                if name in existing_cn:
                    summary["context_nodes_skipped"] += 1
                    continue
                try:
                    row = {k: v for k, v in entity_data.items() if k not in ("id", "element_id")}
                    result = manager.create_entity(type_id, row)
                    if result:
                        new_id = result.get("id", "")
                        existing_cn[name] = new_id
                        node_name_to_id[name] = new_id
                        summary["context_nodes_created"] += 1
                    else:
                        summary["context_nodes_skipped"] += 1
                except Exception as e:
                    summary["context_nodes_skipped"] += 1
                    summary["errors"].append(f"Context node [{type_id}] '{name}': {e}")

    # ------------------------------------------------------------------
    # 4. Context Edges
    # ------------------------------------------------------------------

    if registry:
        kernel_rel_ids = {"influences", "mitigates"}
        for rel_type_id, edges in data.get("context_edges", {}).items():
            if rel_type_id in kernel_rel_ids:
                continue
            rel_type = registry.get_relationship_type(rel_type_id)
            if rel_type is None:
                skipped = len(edges)
                summary["context_edges_skipped"] += skipped
                summary["errors"].append(
                    f"[SCHEMA] Context edge type '{rel_type_id}' not found in schema — "
                    f"{skipped} record(s) skipped. Update schema.yaml to enable restore."
                )
                continue

            for edge_data in edges:
                src_name = edge_data.get("source_name", "")
                tgt_name = edge_data.get("target_name", "")
                src_id = node_name_to_id.get(src_name)
                tgt_id = node_name_to_id.get(tgt_name)

                if not src_id or not tgt_id:
                    summary["context_edges_skipped"] += 1
                    summary["errors"].append(
                        f"Context edge [{rel_type_id}]: "
                        f"could not resolve '{src_name}' → '{tgt_name}', skipped"
                    )
                    continue

                try:
                    props = {
                        k: v for k, v in edge_data.items()
                        if k not in ("id", "element_id", "source_name", "target_name",
                                     "source_id", "target_id")
                    }
                    result = manager.create_relationship(rel_type_id, src_id, tgt_id, props)
                    if result:
                        summary["context_edges_created"] += 1
                    else:
                        summary["context_edges_skipped"] += 1
                except Exception as e:
                    summary["context_edges_skipped"] += 1
                    summary["errors"].append(f"Context edge [{rel_type_id}]: {e}")

    return summary


# =============================================================================
# PRIVATE HELPERS – kwarg builders for core entity creation
# =============================================================================


def _risk_kwargs(d: Dict[str, Any]) -> Dict[str, Any]:
    """Extract create_risk keyword arguments from a flat dict."""
    return {
        "name": d.get("name", ""),
        "level": d.get("level", "Operational"),
        "origin": d.get("origin", "New"),
        "categories": d.get("categories", []),
        "status": d.get("status", "Active"),
        "description": d.get("description", ""),
        "owner": d.get("owner", ""),
        "probability": d.get("probability"),
        "impact": d.get("impact"),
        "exposure": d.get("exposure"),
        "activation_condition": d.get("activation_condition"),
        "activation_decision_date": d.get("activation_decision_date"),
        "subtype": d.get("subtype"),
        "current_score_type": d.get("current_score_type"),
    }


def _tpo_kwargs(d: Dict[str, Any]) -> Dict[str, Any]:
    """Extract create_tpo keyword arguments from a flat dict."""
    return {
        "reference": d.get("reference", ""),
        "name": d.get("name", ""),
        "cluster": d.get("cluster", ""),
        "description": d.get("description", ""),
    }


def _mit_kwargs(d: Dict[str, Any]) -> Dict[str, Any]:
    """Extract create_mitigation keyword arguments from a flat dict."""
    return {
        "name": d.get("name", ""),
        "mitigation_type": d.get("type") or d.get("mitigation_type", "Dedicated"),
        "status": d.get("status", "Proposed"),
        "description": d.get("description", ""),
        "owner": d.get("owner", ""),
        "source_entity": d.get("source_entity", ""),
        "capex": d.get("capex"),
        "opex": d.get("opex"),
    }
