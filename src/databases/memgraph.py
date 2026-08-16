from .cognodb import CognoDBAdapter

class MemgraphAdapter(CognoDBAdapter):
    """
    Memgraph Adapter.
    Inherits all OpenCypher and neo4j driver logic from CognoDBAdapter 
    because Memgraph supports the Bolt protocol and OpenCypher.
    """
    pass
