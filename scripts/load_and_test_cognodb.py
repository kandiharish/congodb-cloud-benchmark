import os
import json
import time
from dotenv import load_dotenv
from src.databases.cognodb import CognoDBAdapter

def main():
    load_dotenv()
    uri = os.getenv("COGNODB_URI")
    user = os.getenv("COGNODB_USERNAME")
    password = os.getenv("COGNODB_PASSWORD")
    
    if not uri or not password:
        print("Missing CognoDB credentials in .env")
        return

    print("Connecting to CognoDB...")
    adapter = CognoDBAdapter(uri, user, password)
    adapter.connect()

    results = {
        "database": "CognoDB",
        "connection_status": "FAILED",
        "schema_status": "FAILED",
        "loading": {},
        "validation": {},
        "sample_workloads": {}
    }

    try:
        if not adapter.health_check():
            print("Health check failed!")
            return
        
        results["connection_status"] = "CONNECTED"
        print("Health check passed.")

        print("Creating schema...")
        adapter.create_schema()
        results["schema_status"] = "CREATED"

        print("Loading nodes...")
        t0 = time.time()
        nodes_loaded, _ = adapter.load_nodes("data/processed/nodes.csv")
        t_nodes = time.time() - t0
        results["loading"]["nodes"] = {"count": nodes_loaded, "time_seconds": t_nodes}
        print(f"Loaded {nodes_loaded} nodes in {t_nodes:.2f}s")

        print("Loading relationships...")
        t0 = time.time()
        rels_loaded, _ = adapter.load_relationships("data/processed/relationships.csv")
        t_rels = time.time() - t0
        results["loading"]["relationships"] = {"count": rels_loaded, "time_seconds": t_rels}
        print(f"Loaded {rels_loaded} relationships in {t_rels:.2f}s")

        print("Validating counts...")
        valid = adapter.validate_counts(47168, 130000)
        results["validation"]["counts_match"] = valid

        print("Sample Workloads...")
        # 1-hop traversal
        t0 = time.time()
        res_1hop = adapter.run_query("MATCH (n:User {id: 1})-[:FOLLOWS]->(m) RETURN count(m) as c")
        t_1hop = time.time() - t0
        results["sample_workloads"]["1-hop"] = {"time_seconds": t_1hop, "result": res_1hop[0]['c'] if res_1hop else None}

        # Point lookup
        t0 = time.time()
        res_point = adapter.run_query("MATCH (n:User {id: 42}) RETURN n.age as age")
        t_point = time.time() - t0
        results["sample_workloads"]["point_lookup"] = {"time_seconds": t_point, "result": res_point[0]['age'] if res_point else None}

        # Indexed lookup (age > 25)
        t0 = time.time()
        res_idx = adapter.run_query("MATCH (n:User) WHERE n.age > 25 RETURN count(n) as c")
        t_idx = time.time() - t0
        results["sample_workloads"]["indexed_lookup"] = {"time_seconds": t_idx, "result": res_idx[0]['c'] if res_idx else None}

        print("All tests completed.")

    except Exception as e:
        print(f"Error during execution: {e}")
        results["error"] = str(e)
    finally:
        adapter.close()
        os.makedirs("results/raw", exist_ok=True)
        with open("results/raw/cognodb.json", "w") as f:
            json.dump(results, f, indent=2)
        print("Saved results to results/raw/cognodb.json")

if __name__ == "__main__":
    main()
