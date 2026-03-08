import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import Neo4jConnection
from config.settings import NEO4J_DEFAULT_URI, NEO4J_DEFAULT_USER, NEO4J_DEFAULTS

def migrate_tpos():
    print("Connecting to Neo4j...")
    conn = Neo4jConnection(
        uri=os.environ.get("NEO4J_URI", NEO4J_DEFAULT_URI),
        username=os.environ.get("NEO4J_USER", NEO4J_DEFAULT_USER),
        password=os.environ.get("NEO4J_PASSWORD", NEO4J_DEFAULTS.get("password", ""))
    )
    
    try:
        conn.connect()
        print("Connected successfully.")
        
        # 1. Migrate Nodes
        print("Migrating TPO nodes to ContextNode...")
        node_query = """
        MATCH (t:TPO)
        SET t:ContextNode,
            t.node_type = 'tpo',
            t.zone = 'upper'
        REMOVE t:TPO
        RETURN count(t) as migrated_count
        """
        result = conn.execute_query(node_query)
        if result:
            print(f"Migrated {result[0]['migrated_count']} TPO nodes.")
            
        print("Migration complete!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_tpos()
