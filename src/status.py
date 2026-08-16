import os
from dotenv import load_dotenv

from .databases.cognodb import CognoDBAdapter
from .databases.neo4j import Neo4jAdapter
from .databases.memgraph import MemgraphAdapter
from .databases.falkordb import FalkorDBAdapter
from .databases.apache_age import ApacheAGEAdapter

def get_database_status():
    load_dotenv()
    
    databases = {
        "CognoDB": CognoDBAdapter(
            uri=os.getenv("COGNODB_URI", ""),
            username=os.getenv("COGNODB_USERNAME", ""),
            password=os.getenv("COGNODB_PASSWORD", "")
        ),
        "Neo4j": Neo4jAdapter(
            uri=os.getenv("NEO4J_URI", ""),
            username=os.getenv("NEO4J_USERNAME", ""),
            password=os.getenv("NEO4J_PASSWORD", "")
        ),
        "Memgraph": MemgraphAdapter(
            uri=os.getenv("MEMGRAPH_URI", ""),
            username=os.getenv("MEMGRAPH_USERNAME", ""),
            password=os.getenv("MEMGRAPH_PASSWORD", "")
        ),
        "FalkorDB": FalkorDBAdapter(
            uri=os.getenv("FALKORDB_URI", ""),
            username=os.getenv("FALKORDB_USERNAME", ""),
            password=os.getenv("FALKORDB_PASSWORD", "")
        ),
        "Apache AGE": ApacheAGEAdapter(
            host=os.getenv("APACHE_AGE_HOST", ""),
            port=os.getenv("APACHE_AGE_PORT", ""),
            database=os.getenv("APACHE_AGE_DATABASE", ""),
            username=os.getenv("APACHE_AGE_USERNAME", ""),
            password=os.getenv("APACHE_AGE_PASSWORD", "")
        )
    }

    results = {}
    for name, adapter in databases.items():
        try:
            adapter.connect()
            is_healthy = adapter.health_check()
            results[name] = "CONNECTED" if is_healthy else "UNAVAILABLE"
        except Exception:
            results[name] = "UNAVAILABLE"
        finally:
            try:
                adapter.close()
            except:
                pass

    return results

if __name__ == "__main__":
    statuses = get_database_status()
    for db, status in statuses.items():
        print(f"{db.ljust(12)} {status}")
