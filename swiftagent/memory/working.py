# swiftagent/memory/working.py
import time
from datetime import datetime
from typing import List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

from .base import Memory, MemoryItemType, MemoryItem
from .long_term import LongTermMemory


class WorkingMemory(Memory):
    """
    Short-term (working) memory that stores recent items (both TEXT and ACTION)
    in a single timeline: `self.history`.

    Each entry is a MemoryItem, containing:
      - item_type: TEXT or ACTION
      - content: The actual string
      - timestamp: Local time in "hh:mm:ss dd/mm/yy" format

    We maintain a max capacity (`max_items`). If we exceed capacity,
    the oldest item is evicted. You can optionally store evicted items into LTM.
    """

    def __init__(
        self,
        max_items: int = 20,
        auto_evict: bool = True,
    ):
        """
        Args:
            max_items: Maximum number of items to store in short-term memory (both text & actions).
            auto_evict: If True, automatically evict oldest items once capacity is hit.
        """
        self.max_items = max_items
        self.auto_evict = auto_evict

        # Unified list of memory items. Each item is a MemoryItem.
        self.history: List[MemoryItem] = []

        # Optionally link to a LongTermMemory, so that when we evict,
        # we can push them to LTM if they are "salient".
        self.long_term_memory: Optional[LongTermMemory] = None

    def ingest(self, information: str) -> "WorkingMemory":
        """
        For compliance with the base Memory interface:
        This method just ingests a plain string as 'TEXT' by default.
        If you need more granular calls, use add_item() directly.
        """
        self.add_item(MemoryItemType.TEXT, information)
        return self

    def recall(self, phrase: str, number: int = 5) -> List[Any]:
        """
        Return up to `number` memory items (TEXT or ACTION) that match `phrase`.
        Here, we do a naive substring match in the `content`.

        (You can customize this logic however you like.)
        """
        if not phrase:
            # Return the last `number` items if no phrase given
            return self.history[-number:]

        # Otherwise search from the end
        matching = []
        for item in reversed(self.history):
            if phrase.lower() in item.content.lower():
                matching.append(item)
            if len(matching) >= number:
                break
        return matching

    def add_item(self, item_type: MemoryItemType, content: str):
        """
        Add a new MemoryItem (TEXT or ACTION) into the unified history,
        automatically tagging it with a local-time timestamp.
        """
        # Generate local-time timestamp in "hh:mm:ss dd/mm/yy"
        local_timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%y")

        item = MemoryItem(
            item_type=item_type,
            content=content,
            timestamp=local_timestamp,
        )
        self.history.append(item)

        if self.auto_evict:
            self._maybe_evict_items()

    def add_text(self, text_content: str) -> None:
        """
        Convenience method to add a text item to memory.
        """
        self.add_item(MemoryItemType.TEXT, text_content)

    def add_action(self, action_content: str) -> None:
        """
        Convenience method to add an action item to memory.
        """
        self.add_item(MemoryItemType.ACTION, action_content)

    def get_recent_items(self, limit: int = 5) -> List[MemoryItem]:
        """
        Return the last `limit` items from the unified memory stream.
        """
        return self.history[-limit:]

    def _maybe_evict_items(self):
        """
        Evict oldest items if over capacity.
        """
        while len(self.history) > self.max_items:
            oldest_item = self.history.pop(0)
            self._handle_eviction(oldest_item)

    def _handle_eviction(self, item: MemoryItem):
        """
        Called whenever an item is evicted from short-term memory.
        By default does nothing, but you can connect it to LTM if you like.
        """
        if self.long_term_memory and self.decide_salient_for_ltm(item.content):
            self.long_term_memory.ingest_item(item)

    async def evict_all(self, long_term_memory: LongTermMemory) -> None:
        """
        Explicitly evict all short-term items (e.g. at end of conversation or agent reset).
        If you want them in LTM, decide here.
        """
        while self.history:
            oldest_item = self.history.pop(0)
            if await self.decide_salient_for_ltm(oldest_item.content):
                long_term_memory.ingest_item(oldest_item)

    async def decide_salient_for_ltm(self, content: str) -> bool:
        """
        (Optional) Call an LLM or heuristic to check if `content` is important enough
        to store in long-term memory. For now, always True by default.
        """
        return True
