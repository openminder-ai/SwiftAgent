from typing import List, Optional
from swiftagent.reasoning.base import BaseReasoning
from swiftagent.memory.working import WorkingMemory
from swiftagent.memory.long_term import LongTermMemory


class SalientMemoryReasoning(BaseReasoning):
    def __init__(
        self,
        name: str,
        instructions: str,
        working_memory: Optional[WorkingMemory] = None,
        long_term_memory: Optional[LongTermMemory] = None,
    ):
        super().__init__(name=name, instructions=instructions)
        self.working_memory = working_memory
        self.long_term_memory = long_term_memory

    async def flow(
        self, task: str = "", llm: str = "gpt-4o-mini", **kwargs
    ) -> List[dict]:
        """
        The main method that runs the reasoning loop.
        We'll build an LLM prompt that includes:
          - last N items of short-term memory
          - top M similar items from long-term memory
          - system instructions
          - user request
        Then we let the base reasoning code handle the rest (action calls, etc.)

        Return a list of messages (including final response).
        """
        # Step 1: Collect short-term memory
        st_texts = []
        st_actions = []
        if self.working_memory:
            st_texts = self.working_memory.get_recent_text(
                5
            )  # last 5 text items
            st_actions = self.working_memory.get_recent_actions(
                5
            )  # last 5 action items

        # Step 2: Optionally recall from LTM
        ltm_snippets = []
        if self.long_term_memory and task.strip():
            ltm_snippets = self.long_term_memory.recall(task, number=3)

        # Step 3: Build a system message that incorporates all of that
        memory_context = "\n".join(
            ["## Short-Term TEXT:\n"]
            + st_texts
            + ["\n## Short-Term ACTIONS:\n"]
            + st_actions
            + ["\n## Long-Term Memory (Relevant Snippets):\n"]
            + ltm_snippets
        )

        system_message = f"""You are an AI agent with the following memory context:
{memory_context}

Your core instructions: {self.instructions or '(none)'}
"""

        # We'll build a minimal messages list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": task},
        ]

        # Step 4: Let the base reasoning handle the chain-of-thought + tool calls
        #   This is where BaseReasoning typically calls the LLM with 'messages'.
        #   We'll also store the final result back into short-term memory.
        final_messages = await super().flow(
            messages=messages, llm=llm, **kwargs
        )

        # Step 5: Optionally store the final agent reply in short-term memory
        if self.working_memory and final_messages:
            # The last message in final_messages is presumably the final assistant msg
            last_msg = final_messages[-1]
            if last_msg.get("role") == "assistant":
                self.working_memory.add_text(
                    f"[Agent Response] {last_msg['content']}"
                )

        return final_messages
