import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

def test_connection():
    env_pass = False
    conn_pass = False
    auth_pass = False
    query_pass = False
    error_msg = "None"
    
    try:
        # 1. Load .env
        if load_dotenv():
            uri = os.environ.get("NEO4J_URI")
            username = os.environ.get("NEO4J_USERNAME")
            password = os.environ.get("NEO4J_PASSWORD")
            if uri and username and password:
                env_pass = True
            else:
                error_msg = "Missing credentials in .env"
        else:
            error_msg = "Failed to load .env"
            
        if not env_pass:
            raise Exception(error_msg)
            
        # 2. Connect
        try:
            driver = GraphDatabase.driver(uri, auth=(username, password))
            conn_pass = True
        except Exception as e:
            error_msg = str(e)
            raise e
            
        # 3. Verify Auth / 4. Query
        try:
            with driver.session() as session:
                result = session.run("RETURN 1 AS test")
                record = result.single()
                if record and record["test"] == 1:
                    auth_pass = True
                    query_pass = True
        except AuthError as e:
            error_msg = f"Authentication Error: {e}"
            raise e
        except ServiceUnavailable as e:
            error_msg = f"Service Unavailable: {e}"
            raise e
        except Exception as e:
            error_msg = str(e)
            raise e
            
        driver.close()
        
    except Exception as e:
        pass
        
    print(f"- Environment: {'PASS' if env_pass else 'FAIL'}")
    print(f"- Connection: {'PASS' if conn_pass else 'FAIL'}")
    print(f"- Authentication: {'PASS' if auth_pass else 'FAIL'}")
    print(f"- RETURN 1 query: {'PASS' if query_pass else 'FAIL'}")
    print(f"- Error: {error_msg}")

if __name__ == "__main__":
    test_connection()
