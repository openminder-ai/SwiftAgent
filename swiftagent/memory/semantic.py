from swiftagent.constants import CACHE_DIR
from swiftagent.core.storage import VectorCollection

from swiftagent.memory.base import Memory

from swiftagent.memory.utils import (
    text_splitter,
    determine_type,
    source_to_markdown,
)

from typing import Any

from swiftagent.prebuilt.storage.chroma import ChromaDatabase


class SemanticMemory(Memory):
    def __init__(
        self,
        name: str = "default_semantic_memory",
        container_collection: VectorCollection | None = None,
        text_splitter: Any = text_splitter,
    ):
        if container_collection is None:
            container_collection = ChromaDatabase(
                str(CACHE_DIR / "chroma_db")
            ).get_or_create_collection(f"semantic_memory_{name}")
        self.container_collection = container_collection
        self.text_splitter = text_splitter
        self.name = name

    def ingest(self, information: str | list[str]):
        if type(information) == list:
            for i in information:
                self.ingest(i)
            return self

        information_type = determine_type(information)

        if not information_type == "plain_string":
            information = source_to_markdown(information)

        _split_texts = self.text_splitter(information)

        self.container_collection.add_texts(_split_texts)

        return self

    def recall(self, phrase: str, number: int):
        search_results = self.container_collection.search_by_text(
            phrase, k=number
        )
        return search_results
