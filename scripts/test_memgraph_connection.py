import os
import sys
from neo4j import GraphDatabase

def test_memgraph():
    uri = "bolt://localhost:7687"
    # Memgraph community edition defaults to no auth or empty string
    username = ""
    password = ""
    
    reachable = False
    auth_pass = False
    query_pass = False
    error_msg = "None"
    
    print(f"Attempting to connect to Memgraph at {uri}")
    
    try:
        # Connect
        driver = GraphDatabase.driver(uri, auth=(username, password))
        reachable = True
        
        # Test auth and query
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            if record and record["test"] == 1:
                auth_pass = True
                query_pass = True
                
        driver.close()
    except Exception as e:
        error_msg = str(e)
        
    print(f"\n- Server Reachable: {'PASS' if reachable else 'FAIL'}")
    print(f"- Authentication/Connection: {'PASS' if auth_pass else 'FAIL'}")
    print(f"- RETURN 1 query: {'PASS' if query_pass else 'FAIL'}")
    print(f"- Error: {error_msg}")
    
    print("\nRecommended Environment Variables:")
    print("MEMGRAPH_URI")
    print("MEMGRAPH_USERNAME")
    print("MEMGRAPH_PASSWORD")

if __name__ == "__main__":
    test_memgraph()
