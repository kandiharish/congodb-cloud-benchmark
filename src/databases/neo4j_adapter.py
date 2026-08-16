from .cognodb import CognoDBAdapter

class Neo4jAdapter(CognoDBAdapter):
    """
    Neo4j AuraDB Adapter.
    Inherits all OpenCypher and neo4j driver logic from CognoDBAdapter 
    because they share the same underlying driver architecture and query dialect.
    """
    pass
