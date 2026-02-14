"""
Abstract AnalysisEngine base class and EngineManager.

Engines are modular analysis components that activate based on schema requirements.
The ExposureEngine is mandatory; others are plugins that auto-activate when their
required entities and relationships are present in the schema.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from enum import Enum


class EngineStatus(str, Enum):
    """Engine activation status."""
    INACTIVE = "inactive"  # Not activated (requirements not met)
    ACTIVE = "active"      # Activated and ready
    ERROR = "error"        # Activation failed


@dataclass
class EngineResult:
    """Result from an engine calculation."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class AnalysisEngine(ABC):
    """
    Abstract base class for analysis engines.
    
    Each engine declares its required entities and relationships.
    The EngineManager activates engines whose requirements are satisfied
    by the current schema.
    
    Subclasses must implement:
      - ID, NAME, DESCRIPTION class attributes
      - REQUIRED_ENTITIES: list of required entity type IDs
      - REQUIRED_RELATIONSHIPS: list of required relationship type IDs
      - calculate(): main calculation method
    """
    
    # Subclasses must define these
    ID: str = "base"
    NAME: str = "Base Engine"
    DESCRIPTION: str = "Abstract base engine"
    
    # Requirements (empty means always available)
    REQUIRED_ENTITIES: List[str] = []
    REQUIRED_RELATIONSHIPS: List[str] = []
    
    def __init__(self, registry=None):
        """
        Initialize engine with schema registry.
        
        Args:
            registry: SchemaRegistry instance (optional)
        """
        self.registry = registry
        self._status = EngineStatus.INACTIVE
    
    @property
    def status(self) -> EngineStatus:
        """Current engine status."""
        return self._status
    
    def is_available(self, registry=None) -> bool:
        """
        Check if engine requirements are satisfied by schema.
        
        Args:
            registry: SchemaRegistry to check against
            
        Returns:
            True if all required entities and relationships exist
        """
        reg = registry or self.registry
        if reg is None:
            return False
        
        # Check required entities
        for entity_id in self.REQUIRED_ENTITIES:
            if not reg.has_entity(entity_id):
                return False
        
        # Check required relationships
        for rel_id in self.REQUIRED_RELATIONSHIPS:
            if not reg.has_relationship(rel_id):
                return False
        
        return True
    
    def activate(self, registry=None) -> bool:
        """
        Activate the engine if requirements are met.
        
        Args:
            registry: SchemaRegistry to use
            
        Returns:
            True if activation succeeded
        """
        reg = registry or self.registry
        if self.is_available(reg):
            self.registry = reg
            self._status = EngineStatus.ACTIVE
            return True
        else:
            self._status = EngineStatus.INACTIVE
            return False
    
    def deactivate(self) -> None:
        """Deactivate the engine."""
        self._status = EngineStatus.INACTIVE
    
    @abstractmethod
    def calculate(self, *args, **kwargs) -> EngineResult:
        """
        Perform the engine's main calculation.
        
        Subclasses must implement this method.
        
        Returns:
            EngineResult with calculation results
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get engine information."""
        return {
            "id": self.ID,
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "status": self._status.value,
            "required_entities": self.REQUIRED_ENTITIES,
            "required_relationships": self.REQUIRED_RELATIONSHIPS,
        }


class EngineManager:
    """
    Manages discovery and activation of analysis engines.
    
    Automatically activates engines whose requirements are met by the schema.
    """
    
    def __init__(self):
        """Initialize with no engines registered."""
        self._engines: Dict[str, AnalysisEngine] = {}
        self._engine_classes: List[Type[AnalysisEngine]] = []
        self._registry = None
    
    def register_engine_class(self, engine_class: Type[AnalysisEngine]) -> None:
        """
        Register an engine class for discovery.
        
        Args:
            engine_class: AnalysisEngine subclass
        """
        if engine_class not in self._engine_classes:
            self._engine_classes.append(engine_class)
    
    def initialize(self, registry) -> Dict[str, bool]:
        """
        Initialize all registered engines with schema.
        
        Creates instances and activates those with satisfied requirements.
        
        Args:
            registry: SchemaRegistry instance
            
        Returns:
            Dict of engine_id -> activation_success
        """
        self._registry = registry
        results = {}
        
        for engine_class in self._engine_classes:
            engine = engine_class(registry)
            self._engines[engine.ID] = engine
            results[engine.ID] = engine.activate(registry)
        
        return results
    
    def get_engine(self, engine_id: str) -> Optional[AnalysisEngine]:
        """Get an engine by ID."""
        return self._engines.get(engine_id)
    
    def get_active_engines(self) -> List[AnalysisEngine]:
        """Get all active engines."""
        return [e for e in self._engines.values() if e.status == EngineStatus.ACTIVE]
    
    def get_inactive_engines(self) -> List[AnalysisEngine]:
        """Get all inactive engines."""
        return [e for e in self._engines.values() if e.status == EngineStatus.INACTIVE]
    
    def list_engines(self) -> List[Dict[str, Any]]:
        """Get info for all engines."""
        return [e.get_info() for e in self._engines.values()]
    
    def has_engine(self, engine_id: str) -> bool:
        """Check if an engine is registered."""
        return engine_id in self._engines
    
    def is_active(self, engine_id: str) -> bool:
        """Check if an engine is active."""
        engine = self._engines.get(engine_id)
        return engine is not None and engine.status == EngineStatus.ACTIVE


# Global engine manager instance
_engine_manager: Optional[EngineManager] = None


def get_engine_manager() -> EngineManager:
    """Get the global engine manager instance."""
    global _engine_manager
    if _engine_manager is None:
        _engine_manager = EngineManager()
    return _engine_manager


def reset_engine_manager() -> None:
    """Reset the global engine manager (for testing)."""
    global _engine_manager
    _engine_manager = None
