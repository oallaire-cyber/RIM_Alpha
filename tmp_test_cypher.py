import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from core import get_registry, load_schema
from database.manager import RiskGraphManager

def main():
    manager = RiskGraphManager(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="risk2024secure"
    )
    if not manager.connect():
        print("Failed to connect!")
        return

    query = """
    MATCH (r:Risk)
    OPTIONAL MATCH path = shortestPath((r)-[:INFLUENCES*0..10]->(b:Risk))
    WHERE EXISTS { (b)-[:IMPACTS_TPO]->(:TPO) }
    WITH r, min(length(path)) as inf_dist
    WITH r, r.name as name, r.level as stored_level, 
         CASE WHEN inf_dist IS NULL THEN -1 ELSE inf_dist + 1 END as dist
    RETURN name, stored_level, dist
    ORDER BY dist, name
    """
    results = manager.execute_query(query)
    for res in results:
        print(f"Risk: {res['name']}, Stored: {res['stored_level']}, Dist: {res['dist']}")

    manager.close()

if __name__ == "__main__":
    main()
