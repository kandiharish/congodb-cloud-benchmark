import csv
from neo4j import GraphDatabase
from .base import BaseGraphAdapter

class CognoDBAdapter(BaseGraphAdapter):
    def __init__(self, uri, username, password):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    def close(self):
        if self.driver:
            self.driver.close()

    def health_check(self) -> bool:
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS num")
                record = result.single()
                return record["num"] == 1
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def cleanup(self, reset: bool = False):
        if not reset:
            print("Reset flag not set. Skipping destructive cleanup.")
            return
            
        print("PERFORMING DESTRUCTIVE RESET...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            
            indexes = session.run("SHOW INDEXES")
            for index in indexes:
                # Do not drop LOOKUP indexes which are built-in
                if index.get("type") != "LOOKUP":
                    try:
                        session.run(f"DROP INDEX {index['name']}")
                    except Exception as e:
                        print(f"Failed to drop index: {e}")
                        
            constraints = session.run("SHOW CONSTRAINTS")
            for constraint in constraints:
                try:
                    session.run(f"DROP CONSTRAINT {constraint['name']}")
                except Exception as e:
                    print(f"Failed to drop constraint: {e}")

    def create_schema(self):
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            except Exception as e:
                print(f"Error creating constraint: {e}")
                
            try:
                session.run("CREATE INDEX user_age_idx IF NOT EXISTS FOR (u:User) ON (u.age)")
            except Exception as e:
                print(f"Error creating index: {e}")
                
        print("Schema creation completed")

    def load_nodes(self, nodes_csv_path: str):
        batch = []
        batch_size = 5000
        total_read = 0
        total_written = 0
        
        with open(nodes_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_read += 1
                node_data = {"id": row["id"]}
                if row.get("age"):
                    node_data["age"] = int(row["age"])
                batch.append(node_data)
                
                if len(batch) >= batch_size:
                    total_written += self._write_node_batch(batch)
                    print(f"Node batch {total_written}/{total_read}")
                    batch = []
                    
            if batch:
                total_written += self._write_node_batch(batch)
                print(f"Node batch {total_written}/{total_read}")
                
        return total_read, total_written

    def _write_node_batch(self, batch):
        query = """
        UNWIND $batch AS row
        CREATE (u:User {id: row.id})
        SET u += CASE WHEN row.age IS NOT NULL THEN {age: row.age} ELSE {} END
        """
        try:
            with self.driver.session() as session:
                session.run(query, batch=batch)
            return len(batch)
        except Exception as e:
            print(f"Failed to write node batch: {e}")
            return 0

    def load_relationships(self, rels_csv_path: str):
        batch = []
        batch_size = 5000
        total_read = 0
        total_written = 0
        
        with open(rels_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_read += 1
                batch.append({"source": row["source"], "target": row["target"]})
                
                if len(batch) >= batch_size:
                    total_written += self._write_rel_batch(batch)
                    print(f"Relationship batch {total_written}/{total_read}")
                    batch = []
                    
            if batch:
                total_written += self._write_rel_batch(batch)
                print(f"Relationship batch {total_written}/{total_read}")
                
        return total_read, total_written
        
    def _write_rel_batch(self, batch):
        query = """
        UNWIND $batch AS row
        MATCH (s:User {id: row.source})
        MATCH (t:User {id: row.target})
        CREATE (s)-[:FOLLOWS]->(t)
        """
        try:
            with self.driver.session() as session:
                session.run(query, batch=batch)
            return len(batch)
        except Exception as e:
            print(f"Failed to write rel batch: {e}")
            return 0

    def validate_counts(self, expected_nodes: int, expected_rels: int):
        with self.driver.session() as session:
            nodes_res = session.run("MATCH (n:User) RETURN count(n) AS c").single()["c"]
            rels_res = session.run("MATCH ()-[r:FOLLOWS]->() RETURN count(r) AS c").single()["c"]
            
        print(f"Database User count: {nodes_res}")
        print(f"Database FOLLOWS count: {rels_res}")
        print(f"Expected User count: {expected_nodes}")
        print(f"Expected FOLLOWS count: {expected_rels}")
        
        match = (nodes_res == expected_nodes and rels_res == expected_rels)
        print(f"Counts match: {'YES' if match else 'NO'}")
        return match

    def run_query(self, query: str, params: dict = None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
