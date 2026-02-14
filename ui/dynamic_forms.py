"""
Dynamic Form Generation - Schema-driven Streamlit forms.

Generates Streamlit forms dynamically based on entity and relationship
definitions from the schema registry.
"""

from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from core import EntityTypeDefinition, RelationshipTypeDefinition, get_registry
from core.attribute import AttributeType


def build_entity_form(
    entity_type: EntityTypeDefinition,
    existing_data: Optional[Dict[str, Any]] = None,
    key_prefix: str = "entity"
) -> Dict[str, Any]:
    """
    Build a complete form for an entity type.
    
    Args:
        entity_type: Entity type definition
        existing_data: Existing values for edit mode
        key_prefix: Prefix for Streamlit widget keys
        
    Returns:
        Dictionary of form field values
    """
    existing_data = existing_data or {}
    form_data = {}
    
    # Name is always required
    form_data["name"] = st.text_input(
        "Name *",
        value=existing_data.get("name", ""),
        key=f"{key_prefix}_name"
    )
    
    # Categorical groups (levels, categories, statuses, etc.)
    for group_name, items in entity_type.categorical_groups.items():
        form_data.update(
            _build_categorical_field(
                group_name, items, existing_data, key_prefix
            )
        )
    
    # Description
    form_data["description"] = st.text_area(
        "Description",
        value=existing_data.get("description", ""),
        key=f"{key_prefix}_description"
    )
    
    # Additional attributes from schema
    for attr in entity_type.attributes:
        if attr.name in ("name", "description"):
            continue  # Already handled
        
        value = _build_attribute_field(
            attr.name,
            attr.type,
            existing_data.get(attr.name, attr.default),
            attr.description,
            attr.choices,
            attr.min_value,
            attr.max_value,
            attr.required,
            key_prefix
        )
        form_data[attr.name] = value
    
    return form_data


def _build_categorical_field(
    group_name: str,
    items: List[Dict[str, Any]],
    existing_data: Dict[str, Any],
    key_prefix: str
) -> Dict[str, Any]:
    """
    Build form field for a categorical group.
    
    Args:
        group_name: Name of the group (levels, categories, etc.)
        items: List of valid items
        existing_data: Existing values
        key_prefix: Streamlit key prefix
        
    Returns:
        Dictionary with the field value
    """
    labels = [item.get("label", item.get("id")) for item in items]
    
    # Determine field name (singular for single-select, plural for multi)
    field_name = group_name.rstrip("s") if group_name.endswith("ies") is False else group_name[:-3] + "y"
    if group_name == "categories":
        field_name = "categories"  # Keep as multi-select
    
    display_name = group_name.replace("_", " ").title()
    
    result = {}
    
    if group_name in ("levels", "statuses", "types", "origins", "clusters"):
        # Single select
        current = existing_data.get(field_name.rstrip("es") if field_name.endswith("es") else field_name, "")
        if not current and existing_data.get(group_name[:-1]):  # Try singular form
            current = existing_data.get(group_name[:-1], "")
        
        # Also try common field names
        field_variants = [field_name, group_name[:-1], group_name, "level", "status", "type", "origin", "cluster"]
        for variant in field_variants:
            if variant in existing_data and existing_data[variant]:
                current = existing_data[variant]
                break
        
        index = 0
        if current in labels:
            index = labels.index(current)
        
        selected = st.selectbox(
            display_name.rstrip("s") + " *",
            options=labels,
            index=index,
            key=f"{key_prefix}_{group_name}"
        )
        
        # Store with singular field name
        singular = group_name[:-1] if group_name.endswith("s") else group_name
        if group_name == "statuses":
            singular = "status"
        result[singular] = selected
        
    else:
        # Multi-select (categories)
        current = existing_data.get(group_name, [])
        if isinstance(current, str):
            current = [current] if current else []
        
        selected = st.multiselect(
            display_name,
            options=labels,
            default=[c for c in current if c in labels],
            key=f"{key_prefix}_{group_name}"
        )
        result[group_name] = selected
    
    return result


def _build_attribute_field(
    name: str,
    attr_type: AttributeType,
    current_value: Any,
    description: str,
    choices: List[str],
    min_value: Optional[float],
    max_value: Optional[float],
    required: bool,
    key_prefix: str
) -> Any:
    """Build a form field for an attribute."""
    label = name.replace("_", " ").title()
    if required:
        label += " *"
    
    help_text = description if description else None
    
    if attr_type == AttributeType.STRING:
        return st.text_input(
            label,
            value=current_value or "",
            help=help_text,
            key=f"{key_prefix}_{name}"
        )
    
    elif attr_type == AttributeType.INT:
        return st.number_input(
            label,
            value=int(current_value) if current_value else 0,
            min_value=int(min_value) if min_value else None,
            max_value=int(max_value) if max_value else None,
            step=1,
            help=help_text,
            key=f"{key_prefix}_{name}"
        )
    
    elif attr_type == AttributeType.FLOAT:
        return st.number_input(
            label,
            value=float(current_value) if current_value else 0.0,
            min_value=min_value,
            max_value=max_value,
            step=0.1,
            help=help_text,
            key=f"{key_prefix}_{name}"
        )
    
    elif attr_type == AttributeType.BOOL:
        return st.checkbox(
            label,
            value=bool(current_value) if current_value else False,
            help=help_text,
            key=f"{key_prefix}_{name}"
        )
    
    elif attr_type == AttributeType.DATE:
        from datetime import date
        val = current_value if isinstance(current_value, date) else None
        return st.date_input(
            label,
            value=val,
            help=help_text,
            key=f"{key_prefix}_{name}"
        )
    
    elif attr_type == AttributeType.ENUM:
        if choices:
            index = choices.index(current_value) if current_value in choices else 0
            return st.selectbox(
                label,
                options=choices,
                index=index,
                help=help_text,
                key=f"{key_prefix}_{name}"
            )
        return st.text_input(label, value=current_value or "", key=f"{key_prefix}_{name}")
    
    elif attr_type == AttributeType.LIST_STRING:
        # Multiselect if choices, else text area
        if choices:
            current = current_value if isinstance(current_value, list) else []
            return st.multiselect(
                label,
                options=choices,
                default=[c for c in current if c in choices],
                help=help_text,
                key=f"{key_prefix}_{name}"
            )
        else:
            val = ", ".join(current_value) if isinstance(current_value, list) else (current_value or "")
            text = st.text_area(
                label + " (comma-separated)",
                value=val,
                help=help_text,
                key=f"{key_prefix}_{name}"
            )
            return [item.strip() for item in text.split(",") if item.strip()]
    
    # Default fallback
    return st.text_input(label, value=str(current_value) if current_value else "", key=f"{key_prefix}_{name}")


def build_relationship_form(
    rel_type: RelationshipTypeDefinition,
    source_options: List[Dict[str, Any]],
    target_options: List[Dict[str, Any]],
    existing_data: Optional[Dict[str, Any]] = None,
    key_prefix: str = "rel"
) -> Dict[str, Any]:
    """
    Build a form for creating/editing a relationship.
    
    Args:
        rel_type: Relationship type definition
        source_options: Available source entities
        target_options: Available target entities
        existing_data: Existing values for edit mode
        key_prefix: Streamlit widget key prefix
        
    Returns:
        Dictionary with form values (source_id, target_id, properties)
    """
    existing_data = existing_data or {}
    form_data = {}
    
    # Source entity selector
    source_labels = [f"{e.get('name', 'Unnamed')} ({e.get('id', '')[:8]}...)" for e in source_options]
    source_ids = [e.get("id") for e in source_options]
    
    current_source = existing_data.get("source_id", "")
    source_idx = source_ids.index(current_source) if current_source in source_ids else 0
    
    if source_labels:
        selected_source = st.selectbox(
            "Source *",
            options=source_labels,
            index=source_idx,
            key=f"{key_prefix}_source"
        )
        form_data["source_id"] = source_ids[source_labels.index(selected_source)]
    
    # Target entity selector
    target_labels = [f"{e.get('name', 'Unnamed')} ({e.get('id', '')[:8]}...)" for e in target_options]
    target_ids = [e.get("id") for e in target_options]
    
    current_target = existing_data.get("target_id", "")
    target_idx = target_ids.index(current_target) if current_target in target_ids else 0
    
    if target_labels:
        selected_target = st.selectbox(
            "Target *",
            options=target_labels,
            index=target_idx,
            key=f"{key_prefix}_target"
        )
        form_data["target_id"] = target_ids[target_labels.index(selected_target)]
    
    # Relationship properties (categorical groups)
    for group_name, items in rel_type.categorical_groups.items():
        form_data.update(
            _build_categorical_field(group_name, items, existing_data, key_prefix)
        )
    
    # Additional attributes
    for attr in rel_type.attributes:
        value = _build_attribute_field(
            attr.name,
            attr.type,
            existing_data.get(attr.name, attr.default),
            attr.description,
            attr.choices,
            attr.min_value,
            attr.max_value,
            attr.required,
            key_prefix
        )
        form_data[attr.name] = value
    
    return form_data


def build_influence_form(
    source_risk: Dict[str, Any],
    target_risk: Dict[str, Any],
    existing_data: Optional[Dict[str, Any]] = None,
    key_prefix: str = "influence"
) -> Dict[str, Any]:
    """
    Build an influence creation form with auto-detected type.
    
    Uses the schema's influence type constraints to suggest/auto-fill
    the influence type based on source and target risk levels.
    
    Args:
        source_risk: Source risk data
        target_risk: Target risk data
        existing_data: Existing values for edit mode
        key_prefix: Streamlit key prefix
        
    Returns:
        Form data dictionary
    """
    existing_data = existing_data or {}
    registry = get_registry()
    influence_type = registry.get_influence_type()
    
    form_data = {}
    
    # Get risk levels
    source_level = source_risk.get("level", "")
    target_level = target_risk.get("level", "")
    
    # Try to auto-determine influence type
    valid_types = influence_type.get_valid_influence_types_for_levels(source_level, target_level)
    
    # Influence type selector (pre-filtered by level constraints)
    all_influence_types = influence_type.get_categorical_values("types")
    
    if valid_types:
        # Filter to only valid types
        type_options = [t for t in all_influence_types if t in valid_types]
        if not type_options:
            type_options = all_influence_types
    else:
        type_options = all_influence_types
    
    current_type = existing_data.get("type", "")
    type_idx = type_options.index(current_type) if current_type in type_options else 0
    
    selected_type = st.selectbox(
        "Influence Type *",
        options=type_options,
        index=type_idx,
        help=f"Valid for {source_level} → {target_level}",
        key=f"{key_prefix}_type"
    )
    form_data["type"] = selected_type
    
    # Strength
    strengths = influence_type.get_categorical_values("strengths")
    current_strength = existing_data.get("strength", "Moderate")
    strength_idx = strengths.index(current_strength) if current_strength in strengths else 0
    
    form_data["strength"] = st.selectbox(
        "Strength *",
        options=strengths,
        index=strength_idx,
        key=f"{key_prefix}_strength"
    )
    
    # Confidence
    form_data["confidence"] = st.slider(
        "Confidence",
        min_value=0.0,
        max_value=1.0,
        value=existing_data.get("confidence", 0.8),
        step=0.05,
        key=f"{key_prefix}_confidence"
    )
    
    # Description
    form_data["description"] = st.text_area(
        "Description",
        value=existing_data.get("description", ""),
        key=f"{key_prefix}_description"
    )
    
    # Include source/target IDs
    form_data["source_id"] = source_risk.get("id")
    form_data["target_id"] = target_risk.get("id")
    
    return form_data
