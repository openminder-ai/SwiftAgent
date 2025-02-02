import chromadb
from chromadb.config import Settings

from swiftagent.core.storage import VectorCollection, VectorDatabase
from typing import List, Optional, Dict, Any
import numpy as np

from chromadb.utils import embedding_functions
from swiftagent.core.embedder import SwiftEmbedder as EmbeddingFunction


class ChromaDatabase(VectorDatabase):
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_function: Optional[EmbeddingFunction | Any] = None,
    ):
        """
        Initialize ChromaDB database.

        Args:
            persist_directory: Directory for persistent storage.
            embedding_function: A custom embedding function instance that provides:
                - embed(text: str) -> np.ndarray
                - embedm(texts: List[str]) -> List[np.ndarray]
        """
        self._client = chromadb.PersistentClient(
            path=persist_directory, settings=Settings(allow_reset=True)
        )

        if embedding_function is None:
            self._embedding_function = (
                embedding_functions.DefaultEmbeddingFunction()
            )
        else:
            self._embedding_function = embedding_function

    def get_collection(
        self,
        name: str,
        embedding_function: Optional[EmbeddingFunction | Any] = None,
    ) -> "ChromaCollection":
        """
        Get or create a collection.

        Args:
            name: Collection name.
            embedding_function: Optional collection-specific embedding function.
                If not provided, uses the database-level embedding function.
        """
        ef = embedding_function or self._embedding_function

        collection = self._client.get_or_create_collection(
            name=name, embedding_function=ef
        )

        return ChromaCollection(collection, embedding_function=ef)

    def list_collections(self) -> List[str]:
        return self._client.list_collections()

    def delete_collection(self, name: str) -> bool:
        try:
            self._client.delete_collection(name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False

    def clear(self):
        return self._client.reset()


class ChromaCollection(VectorCollection):
    def __init__(
        self,
        collection: chromadb.Collection,
        embedding_function: Optional[EmbeddingFunction | Any] = None,
    ):
        """
        Initialize ChromaDB collection wrapper.

        Args:
            collection: ChromaDB collection instance.
            embedding_function: The embedding function to use at the collection level.
        """
        self._collection = collection
        self._embedding_function = embedding_function
        self._dimension: Optional[int] = None

    def add_vectors(
        self,
        vectors: np.ndarray,
        texts: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Add vectors to the collection with optional texts and metadata.

        Args:
            vectors: Array of vectors to add
            texts: Optional list of text content corresponding to the vectors
            metadata: Optional list of metadata dictionaries
        """
        ids = [
            f"vec_{i}_{np.random.randint(0, 1000000)}"
            for i in range(len(vectors))
        ]

        # Handle metadata
        if metadata is None:
            metadata = [{"default": True} for _ in range(len(vectors))]

        # Add text content to metadata if provided
        if texts is not None:
            if len(texts) != len(vectors):
                raise ValueError("Number of texts must match number of vectors")
            for i, text in enumerate(texts):
                metadata[i]["text_content"] = text

        if self._dimension is None:
            self._dimension = vectors.shape[1]

        self._collection.add(
            embeddings=vectors.tolist(),
            metadatas=metadata,
            ids=ids,
            documents=(
                texts if texts is not None else None
            ),  # Store texts in documents field
        )

        return ids

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
        query_vector = (
            query_vector.reshape(1, -1)
            if len(query_vector.shape) == 1
            else query_vector
        )
        results = self._collection.query(
            query_embeddings=query_vector.tolist(),
            n_results=k,
            include=(
                ["metadatas", "distances", "documents"]
                if include_text
                else ["metadatas", "distances"]
            ),
        )

        return [
            {
                "id": results["ids"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "text": (
                    results["documents"][0][i]
                    if include_text and "documents" in results
                    else None
                ),
            }
            for i in range(len(results["ids"][0]))
        ]

    def get_vector(self, id: str, include_text: bool = True) -> Dict[str, Any]:
        """
        Get a vector by ID.

        Args:
            id: Vector ID
            include_text: Whether to include the text content
        """
        include = ["embeddings", "metadatas"]
        if include_text:
            include.append("documents")

        result = self._collection.get(ids=[id], include=include)
        if not result["ids"]:
            raise KeyError(f"Vector with id {id} not found")

        response = {
            "id": result["ids"][0],
            "vector": np.array(result["embeddings"][0]),
            "metadata": result["metadatas"][0],
        }

        if include_text and "documents" in result and result["documents"]:
            response["text"] = result["documents"][0]

        return response

    def add_texts(
        self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Helper method to embed texts and add them to the collection.

        Args:
            texts: List of texts to embed and store
            metadata: Optional metadata for each text
        """
        if not self._embedding_function:
            raise ValueError(
                "No embedding function set at the collection level."
            )
        vectors = np.array(self._embedding_function(texts))
        return self.add_vectors(vectors, texts=texts, metadata=metadata)

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
        if not self._embedding_function:
            raise ValueError(
                "No embedding function set at the collection level."
            )
        query_vector = self._embedding_function([text])[0]
        return self.search(query_vector, k, include_text=include_text)

    def delete_vectors(self, ids: List[str]) -> bool:
        try:
            self._collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            return False

    def clear(self) -> bool:
        try:
            self._collection.delete(ids=self._collection.get()["ids"])
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            raise ValueError("No vectors have been added yet")
        return self._dimension

    @property
    def size(self) -> int:
        return self._collection.count()

    @property
    def name(self) -> str:
        return self._collection.name
