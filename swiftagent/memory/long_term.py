# swiftagent/memory/long_term.py

from typing import List, Any

from .base import Memory

from swiftagent.prebuilt.storage.chroma import ChromaDatabase, ChromaCollection

from .base import MemoryItem, MemoryItemType


class LongTermMemory(Memory):
    """
    Long-term memory that persists both text and action items in a vector store.

    By default, we store them in a single Chroma collection, with `metadata["type"]`
    = "TEXT" or "ACTION". You can also keep them separate if you prefer.
    """

    def __init__(
        self,
        name: str = "long_term_memory",
        persist_directory: str = "./chroma_ltm",
    ):
        self.name = name
        self.db = ChromaDatabase(persist_directory=persist_directory)
        self.collection: ChromaCollection = self.db.get_or_create_collection(
            name=name
        )

    def ingest(self, information: str) -> "LongTermMemory":
        """
        For minimal compliance with `Memory` base class:
        This will store a plain text string as a TEXT item.
        If you want to store actions, use `ingest_item` or `ingest_action`.
        """
        item = MemoryItem(item_type=MemoryItemType.TEXT, content=information)
        self.ingest_item(item)
        return self

    def recall(self, phrase: str, number: int = 5) -> List[Any]:
        """
        Recall both text and action items from the vector store that are similar to `phrase`.
        Returns up to `number` best matches (text or action).
        """
        results = self.collection.search_by_text(phrase, k=number)

        return [
            f"[{r['metadata'].get('type', 'UNKNOWN')}] {r['text']}"
            for r in results
        ]

    def ingest_item(self, item: MemoryItem):
        """
        Ingest a MemoryItem (either TEXT or ACTION).
        We'll store `item.content` as the main text,
        plus `type` in the metadata for filtering if needed.
        """
        text = item.content
        metadata = {
            "type": item.item_type.value
            # you could also store timestamps, etc.
        }
        self.collection.add_texts([text], [metadata])

    def ingest_text(self, text_content: str):
        """
        Helper to ingest a plain text item into LTM.
        """
        item = MemoryItem(item_type=MemoryItemType.TEXT, content=text_content)
        self.ingest_item(item)

    def ingest_action(self, action_content: str):
        """
        Helper to ingest an action item into LTM.
        """
        item = MemoryItem(
            item_type=MemoryItemType.ACTION, content=action_content
        )
        self.ingest_item(item)

    def recall_actions(self, phrase: str, number: int = 5) -> List[str]:
        """
        Specifically recall 'ACTION' items from LTM that match `phrase`.
        """
        # We could do a custom method that filters only items with metadata["type"] == "ACTION"
        # The simplest approach in Chroma is to do:
        #   .query(where={"type": "ACTION"})
        # But the `ChromaCollection` class does not (by default) expose "where" in search_by_text.
        # If you want that, you can directly do a .query(...) with a custom param.
        # For demonstration, we do a normal search_by_text, then filter locally:
        results = self.collection.search_by_text(
            phrase, k=number * 2, include_text=True
        )
        filtered = []
        for r in results:
            if r["metadata"].get("type") == "ACTION":
                filtered.append(r["text"])
                if len(filtered) >= number:
                    break
        return filtered

    def recall_text(self, phrase: str, number: int = 5) -> List[str]:
        """
        Specifically recall 'TEXT' items from LTM that match `phrase`.
        """
        results = self.collection.search_by_text(
            phrase, k=number * 2, include_text=True
        )
        filtered = []
        for r in results:
            if r["metadata"].get("type") == "TEXT":
                filtered.append(r["text"])
                if len(filtered) >= number:
                    break
        return filtered
