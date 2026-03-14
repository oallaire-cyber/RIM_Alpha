"""
Tests for generic database operations (entities).
"""

import pytest
from unittest.mock import MagicMock, patch
from database.queries.generic_entity import (
    create_entity,
    get_all_entities,
    get_entity_by_id,
    update_entity,
    delete_entity,
    EntityValidationError
)
from core.entity import EntityTypeDefinition
from core.attribute import AttributeDefinition, AttributeType

@pytest.fixture
def mock_driver():
    """Mock Neo4j driver."""
    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session
    return driver, session

@pytest.fixture
def entity_type():
    """Simple entity type for testing."""
    return EntityTypeDefinition(
        id="test_type",
        label="Test Type",
        neo4j_label="TestNode",
        attributes=[
            AttributeDefinition(name="name", type=AttributeType.STRING, required=True),
            AttributeDefinition(name="age", type=AttributeType.INT, required=False)
        ]
    )

class TestGenericEntityCRUD:
    """Tests for generic entity CRUD operations."""

    def test_create_entity_success(self, mock_driver, entity_type):
        """Test successful entity creation."""
        driver, session = mock_driver
        
        # Mock result
        mock_result = MagicMock()
        mock_record = {
            "n": {"id": "123", "name": "Test Name", "age": 30},
            "nodeId": "node_123"
        }
        mock_result.single.return_value = mock_record
        session.run.return_value = mock_result
        
        data = {"name": "Test Name", "age": 30}
        result = create_entity(driver, entity_type, data)
        
        assert result["id"] == "123"
        assert result["name"] == "Test Name"
        assert result["_element_id"] == "node_123"
        
        # Verify query
        args, kwargs = session.run.call_args
        assert "CREATE (n:TestNode" in args[0]
        assert args[1]["name"] == "Test Name"

    def test_create_entity_validation_failure(self, mock_driver, entity_type):
        """Test entity creation failure due to validation."""
        driver, _ = mock_driver
        
        # Missing required field 'name'
        data = {"age": 30}
        
        with pytest.raises(EntityValidationError):
            create_entity(driver, entity_type, data)

    def test_get_all_entities(self, mock_driver, entity_type):
        """Test retrieving all entities with filters."""
        driver, session = mock_driver
        
        # Mock results
        mock_records = [
            {"n": {"id": "1", "name": "A"}, "nodeId": "id1"},
            {"n": {"id": "2", "name": "B"}, "nodeId": "id2"}
        ]
        mock_result = MagicMock()
        mock_result.single.return_value = {"labels": ["TestNode"]}
        mock_result.__iter__.return_value = iter(mock_records)
        session.run.return_value = mock_result
        
        results = get_all_entities(driver, entity_type, filters={"name": "A"})
        
        assert len(results) == 2
        assert results[0]["name"] == "A"
        
        # Verify query has WHERE clause
        args, kwargs = session.run.call_args
        assert "WHERE n.name =" in args[0]

    def test_get_entity_by_id(self, mock_driver, entity_type):
        """Test retrieving entity by ID."""
        driver, session = mock_driver
        
        mock_result = MagicMock()
        mock_result.single.return_value = {"n": {"id": "123", "name": "T"}, "nodeId": "id123"}
        session.run.return_value = mock_result
        
        result = get_entity_by_id(driver, entity_type, "123")
        
        assert result["id"] == "123"
        assert "MATCH (n:TestNode {id: $id})" in session.run.call_args[0][0]

    def test_update_entity(self, mock_driver, entity_type):
        """Test updating an entity."""
        driver, session = mock_driver
        
        mock_result = MagicMock()
        mock_result.single.return_value = {"n": {"id": "123", "name": "New"}, "nodeId": "id123"}
        session.run.return_value = mock_result
        
        result = update_entity(driver, entity_type, "123", {"name": "New"})
        
        assert result["name"] == "New"
        args, _ = session.run.call_args
        assert "SET n.name = $name" in args[0]

    def test_delete_entity(self, mock_driver, entity_type):
        """Test deleting an entity."""
        driver, session = mock_driver
        
        mock_result = MagicMock()
        mock_result.single.return_value = {"deleted": 1}
        session.run.return_value = mock_result
        
        success = delete_entity(driver, entity_type, "123")
        
        assert success is True
        assert "DETACH DELETE n" in session.run.call_args[0][0]
