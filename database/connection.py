"""
Neo4j database connection management.

Provides connection handling, session management, and query execution.
"""

from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError


class Neo4jConnection:
    """
    Manages Neo4j database connections.
    
    Provides connection lifecycle management, query execution,
    and transaction handling.
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize connection parameters.
        
        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            username: Database username
            password: Database password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self._driver: Optional[Driver] = None
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._driver is not None
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        
        Raises:
            ConnectionError: If connection fails with details
        """
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            return True
        except AuthError as e:
            raise ConnectionError(f"Authentication failed: {e}")
        except ServiceUnavailable as e:
            raise ConnectionError(f"Database unavailable: {e}")
        except Exception as e:
            raise ConnectionError(f"Connection error: {e}")
    
    def close(self):
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    @contextmanager
    def session(self) -> Session:
        """
        Get a database session as context manager.
        
        Yields:
            Neo4j Session object
        
        Raises:
            RuntimeError: If not connected
        """
        if not self._driver:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Execute a Cypher query and return results as list of dictionaries.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            List of result records as dictionaries
        
        Raises:
            RuntimeError: If not connected
            Exception: If query execution fails
        """
        if not self._driver:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        with self.session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Execute a write query within a transaction.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            List of result records as dictionaries
        """
        def _execute(tx):
            result = tx.run(query, parameters or {})
            return [dict(record) for record in result]
        
        with self.session() as session:
            return session.execute_write(_execute)
    
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Execute a read query within a transaction.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            List of result records as dictionaries
        """
        def _execute(tx):
            result = tx.run(query, parameters or {})
            return [dict(record) for record in result]
        
        with self.session() as session:
            return session.execute_read(_execute)


class ConnectionPool:
    """
    Simple connection pool for managing multiple connections.
    
    Note: For most Streamlit applications, a single connection
    stored in session_state is sufficient. This class is provided
    for more complex scenarios.
    """
    
    _instance: Optional['ConnectionPool'] = None
    _connection: Optional[Neo4jConnection] = None
    
    @classmethod
    def get_instance(cls) -> 'ConnectionPool':
        """Get singleton instance of connection pool."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_connection(self, uri: str, username: str, password: str) -> Neo4jConnection:
        """
        Get or create a connection with the given credentials.
        
        Args:
            uri: Neo4j connection URI
            username: Database username
            password: Database password
        
        Returns:
            Connected Neo4jConnection instance
        """
        # For simplicity, maintain a single connection
        # If credentials change, create new connection
        if self._connection is None or not self._connection.is_connected:
            self._connection = Neo4jConnection(uri, username, password)
            self._connection.connect()
        elif (self._connection.uri != uri or 
              self._connection.username != username):
            # Credentials changed, reconnect
            self._connection.close()
            self._connection = Neo4jConnection(uri, username, password)
            self._connection.connect()
        
        return self._connection
    
    def close_all(self):
        """Close all connections."""
        if self._connection:
            self._connection.close()
            self._connection = None
