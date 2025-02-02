from abc import ABC, abstractmethod
from typing import List, Any


class Memory(ABC):
    """
    Abstract base class defining the interface for semantic memory implementations.

    This class provides the basic structure for creating semantic memory systems
    that can ingest information and recall it based on semantic similarity.
    """

    @abstractmethod
    def ingest(self, information: str) -> "Memory":
        """
        Ingest information into the semantic memory.

        Args:
            information (str): The information to be stored in the semantic memory.

        Returns:
            BaseSemanticMemory: The instance of the semantic memory for method chaining.

        Raises:
            NotImplementedError: If the child class doesn't implement this method.
        """
        raise NotImplementedError("Subclass must implement ingest method")

    @abstractmethod
    def recall(self, phrase: str, number: int) -> List[Any]:
        """
        Recall information from the semantic memory based on a search phrase.

        Args:
            phrase (str): The search phrase to find relevant information.
            number (int): The number of results to return.

        Returns:
            List[Any]: A list of search results matching the query.

        Raises:
            NotImplementedError: If the child class doesn't implement this method.
        """
        raise NotImplementedError("Subclass must implement recall method")
