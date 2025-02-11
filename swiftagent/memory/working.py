# swiftagent/memory/working.py

from typing import List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

from .base import Memory, MemoryItemType, MemoryItem
from .long_term import LongTermMemory


class WorkingMemory(Memory):
    """
    Short-term (working) memory that stores recent text or action events for the agent.

    - Holds two separate lists:
       1) `text_history`   (List[MemoryItem]) for TextMemory
       2) `action_history` (List[MemoryItem]) for ActionMemory

    - Each has a configurable max size. Once the capacity is exceeded,
      the oldest item is evicted.

    - Upon eviction, we optionally call `decide_salient_for_ltm` to see if the item
      should be put into `LongTermMemory`.
    """

    def __init__(
        self,
        max_text_items: int = 10,
        max_action_items: int = 10,
        auto_evict: bool = True,
    ):
        """
        Args:
            max_text_items: Maximum number of text items to store in short-term memory.
            max_action_items: Maximum number of action items to store in short-term memory.
            auto_evict: If True, automatically evict oldest items once capacity is hit.
        """
        self.max_text_items = max_text_items
        self.max_action_items = max_action_items
        self.auto_evict = auto_evict

        # Internal lists for text and actions
        self.text_history: List[MemoryItem] = []
        self.action_history: List[MemoryItem] = []

    def ingest(self, information: str) -> "WorkingMemory":
        """
        For compliance with the base Memory interface:
        This method just ingests a plain string as 'TEXT' by default.
        If you need more granular calls, use `add_text` or `add_action`.
        """
        self.add_text(information)
        return self

    def recall(self, phrase: str, number: int = 5) -> List[Any]:
        """
        For compliance with base Memory interface:
        In short-term memory, 'recall' might just return the *most recent*
        items that contain the phrase (very naive) or everything if phrase is empty.

        By default, returns up to `number` items from the text side.
        (You could expand to also recall actions, or unify both.)
        """
        if not phrase:
            # Return the last `number` text items
            return [m.content for m in self.text_history[-number:]]

        # Return the last matching items
        matching = []
        for item in reversed(self.text_history):
            if phrase.lower() in item.content.lower():
                matching.append(item.content)
            if len(matching) >= number:
                break
        return matching

    def add_text(self, text_content: str) -> None:
        """
        Add a text entry to short-term memory.
        If `auto_evict` is True, we evict if we're over capacity.
        """
        item = MemoryItem(item_type=MemoryItemType.TEXT, content=text_content)
        self.text_history.append(item)
        self._maybe_evict_text_items()

    def add_action(self, action_content: str) -> None:
        """
        Add an action entry to short-term memory.
        If `auto_evict` is True, we evict if we're over capacity.
        """
        item = MemoryItem(
            item_type=MemoryItemType.ACTION, content=action_content
        )
        self.action_history.append(item)
        self._maybe_evict_action_items()

    def get_recent_text(self, limit: int = 5) -> List[str]:
        """
        Return the last `limit` text items.
        """
        return [m.content for m in self.text_history[-limit:]]

    def get_recent_actions(self, limit: int = 5) -> List[str]:
        """
        Return the last `limit` action items.
        """
        return [m.content for m in self.action_history[-limit:]]

    def _maybe_evict_text_items(self):
        """
        Evict the oldest text items if over capacity.
        """
        while len(self.text_history) > self.max_text_items:
            oldest_item = self.text_history.pop(0)
            # Optionally call logic to store in LTM
            self._handle_eviction(oldest_item)

    def _maybe_evict_action_items(self):
        """
        Evict the oldest action items if over capacity.
        """
        while len(self.action_history) > self.max_action_items:
            oldest_item = self.action_history.pop(0)
            # Optionally call logic to store in LTM
            self._handle_eviction(oldest_item)

    def _handle_eviction(self, item: MemoryItem):
        """
        Called whenever an item is evicted from short-term memory.
        By default does nothing, but you can connect it to LTM if you like.
        """
        # Example: if "is_salient" -> store in LTM
        # This is just a stub. If you want to do it automatically, you can do:
        #   if self.decide_salient_for_ltm(item.content):
        #       self.long_term_memory.ingest_item(item)
        pass

    async def evict_all(self, long_term_memory: LongTermMemory) -> None:
        """
        Explicitly evict all short-term items (e.g. at end of conversation or agent reset).
        Optionally store them into LTM if they are salient.
        """
        for item in self.text_history:
            # Decide if it should be stored
            if await self.decide_salient_for_ltm(item.content):
                long_term_memory.ingest_item(item)
        for item in self.action_history:
            if await self.decide_salient_for_ltm(item.content):
                long_term_memory.ingest_item(item)

        self.text_history.clear()
        self.action_history.clear()

    async def decide_salient_for_ltm(self, content: str) -> bool:
        """
        (Optional) Call an LLM or heuristic to check if `content` is important enough
        to store in long-term memory. For now, always return `False` by default.

        Example usage (pseudocode):
            # call your LLM with a short prompt:
            # "Is this item important? Return yes or no: content"
            # parse the response
        """
        return False
