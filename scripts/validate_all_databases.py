import json
import os
from src.status import get_database_status

def validate_all():
    statuses = get_database_status()
    
    # Map the display names to JSON keys
    key_mapping = {
        "CognoDB": "cognodb",
        "Neo4j": "neo4j",
        "Memgraph": "memgraph",
        "FalkorDB": "falkordb",
        "Apache AGE": "apache_age"
    }
    
    json_results = {}
    for name, status in statuses.items():
        key = key_mapping[name]
        if status == "CONNECTED":
            json_results[key] = {"status": "CONNECTED"}
        else:
            json_results[key] = {
                "status": "UNAVAILABLE",
                "reason": "database environment unavailable or connection failed"
            }
            
    os.makedirs("results", exist_ok=True)
    with open("results/database_status.json", "w") as f:
        json.dump(json_results, f, indent=2)
        
    print("Saved database statuses to results/database_status.json")

if __name__ == "__main__":
    validate_all()
