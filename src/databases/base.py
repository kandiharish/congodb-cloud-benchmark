from abc import ABC, abstractmethod

class BaseGraphAdapter(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def create_schema(self):
        pass

    @abstractmethod
    def cleanup(self, reset: bool = False):
        pass

    @abstractmethod
    def load_nodes(self, nodes_csv_path: str):
        pass

    @abstractmethod
    def load_relationships(self, rels_csv_path: str):
        pass

    @abstractmethod
    def validate_counts(self, expected_nodes: int, expected_rels: int):
        pass

    @abstractmethod
    def run_query(self, query: str, params: dict = None):
        pass
