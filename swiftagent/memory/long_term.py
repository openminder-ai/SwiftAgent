from typing import List, Any

from .base import Memory, MemoryItem, MemoryItemType
from swiftagent.prebuilt.storage.chroma import ChromaDatabase, ChromaCollection


class LongTermMemory(Memory):
    """
    Long-term memory that persists both text and action items in a vector store.
    We store `type` and `timestamp` in the Chroma metadata so we can reconstruct them.
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
        This will store a plain text string as a TEXT item (with no timestamp).
        """
        item = MemoryItem(
            item_type=MemoryItemType.TEXT,
            content=information,
            # If you want a timestamp here, you can generate a local one,
            # or rely on caller passing one. E.g.
            # timestamp=datetime.now().strftime("%H:%M:%S %d/%m/%y"),
        )
        self.ingest_item(item)
        return self

    def ingest_item(self, item: MemoryItem):
        """
        Ingest a MemoryItem (either TEXT or ACTION).
        We'll store `item.content` as the main text,
        plus `type` and `timestamp` in the metadata.
        """
        text = item.content
        metadata = {
            "type": item.item_type.value,
            "timestamp": item.timestamp,  # <-- store local-time stamp if present
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

    def recall(self, phrase: str, number: int = 5) -> List[dict]:
        """
        Recall both text and action items from the vector store that match `phrase`.
        Returns up to `number` best matches. Instead of returning a plain string,
        we return a dictionary with text, type, timestamp, etc.
        """
        results = self.collection.search_by_text(
            phrase, k=number, include_text=True
        )
        # Construct a more structured return
        output = []
        for r in results:
            meta = r["metadata"]
            output.append(
                {
                    "text": r["text"],
                    "type": meta.get("type", "UNKNOWN"),
                    "timestamp": meta.get("timestamp", "???"),
                    # you can also add "score" or "distance" if you want
                }
            )
        return output

    def recall_actions(self, phrase: str, number: int = 5) -> List[dict]:
        """
        Specifically recall 'ACTION' items from LTM that match `phrase`.
        We'll filter after the search_by_text.
        """
        results = self.collection.search_by_text(
            phrase, k=number * 2, include_text=True
        )
        filtered = []
        for r in results:
            if r["metadata"].get("type") == "ACTION":
                filtered.append(
                    {
                        "text": r["text"],
                        "type": "ACTION",
                        "timestamp": r["metadata"].get("timestamp", "???"),
                    }
                )
                if len(filtered) >= number:
                    break
        return filtered

    def recall_text(self, phrase: str, number: int = 5) -> List[dict]:
        """
        Specifically recall 'TEXT' items from LTM that match `phrase`.
        """
        results = self.collection.search_by_text(
            phrase, k=number * 2, include_text=True
        )
        filtered = []
        for r in results:
            if r["metadata"].get("type") == "TEXT":
                filtered.append(
                    {
                        "text": r["text"],
                        "type": "TEXT",
                        "timestamp": r["metadata"].get("timestamp", "???"),
                    }
                )
                if len(filtered) >= number:
                    break
        return filtered
