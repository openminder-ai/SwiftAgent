from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Union
import numpy as np

# Type variable for the embedding function
EmbeddingFunctionType = TypeVar("EmbeddingFunctionType")


class VectorDatabase(ABC):
    """
    Abstract base class for managing vector database connections and collections.
    """

    @abstractmethod
    def __init__(
        self,
        persist_directory: str,
        embedding_function: Optional[EmbeddingFunctionType] = None,
    ):
        """Initialize the vector database with optional embedding function."""
        pass

    @abstractmethod
    def get_or_create_collection(
        self,
        name: str,
        embedding_function: Optional[EmbeddingFunctionType] = None,
    ) -> "VectorCollection":
        """
        Get or create a collection with the given name.

        Args:
            name: Collection name
            embedding_function: Optional collection-specific embedding function
        """
        pass

    @abstractmethod
    def list_collections(self) -> List[str]:
        """List all collection names in the database."""
        pass

    @abstractmethod
    def delete_collection(self, name: str) -> bool:
        """Delete a collection by name."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all collections from the database."""
        pass


class VectorCollection(ABC):
    """
    Abstract base class for a single vector collection.
    """

    @abstractmethod
    def add_vectors(
        self,
        vectors: np.ndarray,
        texts: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Add vectors to the collection.

        Args:
            vectors: Array of vectors to add
            texts: Optional list of text content corresponding to the vectors
            metadata: Optional list of metadata dictionaries

        Returns:
            List of generated IDs for the added vectors
        """
        pass

    @abstractmethod
    def search(
        self, query_vector: np.ndarray, k: int = 5, include_text: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Vector to search for
            k: Number of results to return
            include_text: Whether to include the text content in results
        """
        pass

    @abstractmethod
    def get_vector(self, id: str, include_text: bool = True) -> Dict[str, Any]:
        """
        Get a vector by ID.

        Args:
            id: Vector ID
            include_text: Whether to include the text content
        """
        pass

    @abstractmethod
    def add_texts(
        self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Helper method to embed texts and add them to the collection.

        Args:
            texts: List of texts to embed and store
            metadata: Optional metadata for each text
        """
        pass

    @abstractmethod
    def search_by_text(
        self, text: str, k: int = 5, include_text: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search by text query.

        Args:
            text: Text to search for
            k: Number of results to return
            include_text: Whether to include the text content in results
        """
        pass

    @abstractmethod
    def delete_vectors(self, ids: List[str]) -> bool:
        """Delete vectors by their IDs."""
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
