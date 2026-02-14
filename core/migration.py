"""
Schema Migration Utilities.

Handles adding/removing/changing attributes when schema evolves.
Provides tools for comparing schemas and generating migration plans.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class MigrationAction(str, Enum):
    """Types of migration actions."""
    ADD_ATTRIBUTE = "add_attribute"
    REMOVE_ATTRIBUTE = "remove_attribute"
    CHANGE_TYPE = "change_type"
    RENAME_LABEL = "rename_label"
    ADD_ENTITY = "add_entity"
    REMOVE_ENTITY = "remove_entity"


@dataclass
class MigrationStep:
    """A single migration step."""
    action: MigrationAction
    entity_type: str
    attribute_name: str = ""
    old_value: Any = None
    new_value: Any = None
    description: str = ""


@dataclass
class MigrationPlan:
    """Complete migration plan between schema versions."""
    from_version: str
    to_version: str
    steps: List[MigrationStep] = field(default_factory=list)
    
    def is_empty(self) -> bool:
        """Check if plan has no steps."""
        return len(self.steps) == 0
    
    def summary(self) -> str:
        """Get human-readable summary."""
        if self.is_empty():
            return f"No changes from {self.from_version} to {self.to_version}"
        
        lines = [f"Migration from {self.from_version} to {self.to_version}:"]
        for step in self.steps:
            lines.append(f"  - {step.action.value}: {step.entity_type}.{step.attribute_name}")
        return "\n".join(lines)


class SchemaMigrator:
    """
    Handles schema migrations for Neo4j data.
    
    Compares old and new schemas, generates migration plans,
    and optionally executes migrations.
    """
    
    def __init__(self, connection=None):
        """
        Initialize migrator.
        
        Args:
            connection: Neo4j connection for executing migrations
        """
        self.connection = connection
    
    def compare_schemas(self, old: Dict, new: Dict) -> MigrationPlan:
        """
        Compare schemas and generate migration plan.
        
        Args:
            old: Old schema dictionary
            new: New schema dictionary
            
        Returns:
            MigrationPlan with required steps
        """
        plan = MigrationPlan(
            from_version=old.get("version", "unknown"),
            to_version=new.get("version", "unknown")
        )
        
        # Compare entity attributes
        self._compare_entity_attributes(old, new, plan)
        
        # Compare relationship attributes
        self._compare_relationship_attributes(old, new, plan)
        
        return plan
    
    def _compare_entity_attributes(
        self, old: Dict, new: Dict, plan: MigrationPlan
    ) -> None:
        """Compare attributes between old and new entity schemas."""
        # Get entity sections from both schemas
        old_entities = old.get("entities", {})
        new_entities = new.get("entities", {})
        
        # Also check for risk/mitigation at top level (V2 format)
        if "risk" in old:
            old_entities["risk"] = old["risk"]
        if "risk" in new:
            new_entities["risk"] = new["risk"]
        if "mitigation" in old:
            old_entities["mitigation"] = old["mitigation"]
        if "mitigation" in new:
            new_entities["mitigation"] = new["mitigation"]
        
        # Compare each entity type
        all_entity_ids = set(old_entities.keys()) | set(new_entities.keys())
        
        for entity_id in all_entity_ids:
            if entity_id in ("custom_entities",):
                continue  # Skip list-based sections
                
            old_entity = old_entities.get(entity_id, {})
            new_entity = new_entities.get(entity_id, {})
            
            if not old_entity and new_entity:
                plan.steps.append(MigrationStep(
                    action=MigrationAction.ADD_ENTITY,
                    entity_type=entity_id,
                    description=f"New entity type: {entity_id}"
                ))
                continue
            
            if old_entity and not new_entity:
                plan.steps.append(MigrationStep(
                    action=MigrationAction.REMOVE_ENTITY,
                    entity_type=entity_id,
                    description=f"Removed entity type: {entity_id}"
                ))
                continue
            
            # Compare attributes
            old_attrs = {a.get("name"): a for a in old_entity.get("attributes", [])}
            new_attrs = {a.get("name"): a for a in new_entity.get("attributes", [])}
            
            # Find added attributes
            for name, attr in new_attrs.items():
                if name not in old_attrs:
                    plan.steps.append(MigrationStep(
                        action=MigrationAction.ADD_ATTRIBUTE,
                        entity_type=entity_id,
                        attribute_name=name,
                        new_value=attr.get("default"),
                        description=f"Add '{name}' to {entity_id}"
                    ))
            
            # Find removed attributes
            for name in old_attrs:
                if name not in new_attrs:
                    plan.steps.append(MigrationStep(
                        action=MigrationAction.REMOVE_ATTRIBUTE,
                        entity_type=entity_id,
                        attribute_name=name,
                        description=f"Remove '{name}' from {entity_id}"
                    ))
            
            # Compare Neo4j labels for rename
            old_label = old_entity.get("neo4j_label")
            new_label = new_entity.get("neo4j_label")
            if old_label and new_label and old_label != new_label:
                plan.steps.append(MigrationStep(
                    action=MigrationAction.RENAME_LABEL,
                    entity_type=entity_id,
                    old_value=old_label,
                    new_value=new_label,
                    description=f"Rename label {old_label} to {new_label}"
                ))
    
    def _compare_relationship_attributes(
        self, old: Dict, new: Dict, plan: MigrationPlan
    ) -> None:
        """Compare relationship schemas."""
        old_rels = old.get("relationships", {})
        new_rels = new.get("relationships", {})
        
        # Also check for influences/mitigates at top level (V2 format)
        if "influences" in old:
            old_rels["influences"] = old["influences"]
        if "influences" in new:
            new_rels["influences"] = new["influences"]
        if "mitigates" in old:
            old_rels["mitigates"] = old["mitigates"]
        if "mitigates" in new:
            new_rels["mitigates"] = new["mitigates"]
        
        # Similar comparison logic as entities
        # (simplified for now - can be expanded)
        pass
    
    def execute_migration(
        self, plan: MigrationPlan, dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute migration plan.
        
        Args:
            plan: MigrationPlan to execute
            dry_run: If True, only report what would change
            
        Returns:
            Report dictionary with results
        """
        report = {
            "dry_run": dry_run,
            "from_version": plan.from_version,
            "to_version": plan.to_version,
            "steps": [],
            "errors": []
        }
        
        for step in plan.steps:
            try:
                result = self._execute_step(step, dry_run)
                report["steps"].append({
                    "step": str(step),
                    "result": result
                })
            except Exception as e:
                report["errors"].append({
                    "step": str(step),
                    "error": str(e)
                })
        
        return report
    
    def _execute_step(self, step: MigrationStep, dry_run: bool) -> Dict[str, Any]:
        """Execute a single migration step."""
        if self.connection is None:
            return {"affected": 0, "message": "No connection - dry run only"}
        
        neo4j_label = step.entity_type.title()
        
        if step.action == MigrationAction.ADD_ATTRIBUTE:
            if dry_run:
                query = f"""
                MATCH (n:{neo4j_label}) 
                WHERE n.{step.attribute_name} IS NULL 
                RETURN count(n) as cnt
                """
            else:
                query = f"""
                MATCH (n:{neo4j_label}) 
                WHERE n.{step.attribute_name} IS NULL
                SET n.{step.attribute_name} = $default_value
                RETURN count(n) as cnt
                """
            result = self.connection.execute_query(
                query, {"default_value": step.new_value}
            )
            return {"affected": result[0]["cnt"] if result else 0}
        
        elif step.action == MigrationAction.REMOVE_ATTRIBUTE:
            if dry_run:
                query = f"""
                MATCH (n:{neo4j_label}) 
                WHERE n.{step.attribute_name} IS NOT NULL 
                RETURN count(n) as cnt
                """
            else:
                query = f"""
                MATCH (n:{neo4j_label}) 
                WHERE n.{step.attribute_name} IS NOT NULL
                REMOVE n.{step.attribute_name}
                RETURN count(n) as cnt
                """
            result = self.connection.execute_query(query)
            return {"affected": result[0]["cnt"] if result else 0}
        
        elif step.action == MigrationAction.RENAME_LABEL:
            if dry_run:
                query = f"MATCH (n:{step.old_value}) RETURN count(n) as cnt"
            else:
                query = f"""
                MATCH (n:{step.old_value})
                REMOVE n:{step.old_value}
                SET n:{step.new_value}
                RETURN count(n) as cnt
                """
            result = self.connection.execute_query(query)
            return {"affected": result[0]["cnt"] if result else 0}
        
        return {"affected": 0}
