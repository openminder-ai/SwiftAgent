from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import numpy as np


class VectorDatabase(ABC):
    """
    Abstract base class for managing vector database connections and collections.
    """

    @abstractmethod
    def get_collection(self, name: str) -> "VectorCollection":
        """Get or create a collection with the given name."""
        pass

    @abstractmethod
    def list_collections(self) -> List[str]:
        """List all collection names in the database."""
        pass

    @abstractmethod
    def delete_collection(self, name: str) -> bool:
        """Delete a collection by name."""
        pass


class VectorCollection(ABC):
    """
    Abstract base class for a single vector collection.
    """

    @abstractmethod
    def add_vectors(
        self,
        vectors: np.ndarray,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Add vectors to the collection."""
        pass

    @abstractmethod
    def search(
        self, query_vector: np.ndarray, k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by their IDs."""
        pass

    @abstractmethod
    def get_vector(self, id: str) -> Dict[str, Any]:
        """Get a vector by ID."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all vectors from the collection."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get vector dimension."""
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        """Get number of vectors."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get collection name."""
        pass
