# swiftagent/reasoning/salient.py

from typing import List, Optional
import json
import inspect

from swiftagent.reasoning.base import BaseReasoning
from swiftagent.llm.adapter import LLMAdapter
from swiftagent.actions.formatter import ActionFormatter
from swiftagent.memory.working import WorkingMemory
from swiftagent.memory.long_term import LongTermMemory


class SalientMemoryReasoning(BaseReasoning):
    """
    A variant of SalientMemoryReasoning that ONLY stores:
      - The user's initial query
      - Any tool calls (action name + args + results)
      - The final user-facing answer
    Intermediate chain-of-thought is NOT stored.
    """

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
        # self.formatter = ActionFormatter()  # For listing available actions

    async def flow(
        self, task: str = "", llm: str = "gpt-4o-mini", **kwargs
    ) -> List[dict]:
        """
        This method:
          1) Gathers short-term & long-term memory
          2) Creates a system & user prompt
          3) Iterates calls to LLM (tool usage enabled)
          4) ONLY stores user query, tool calls/results, and final answer.

        Returns the list of all messages used or generated in final conversation.
        """

        st_items = []
        if self.working_memory:
            st_items = self.working_memory.get_recent_items(5)
            # Each item is MemoryItem with fields: item_type, content, timestamp

        # Convert them to text lines. For example:
        st_context_lines = []
        for it in st_items:
            # e.g. "[12:34:56 12/02/25] (TEXT) The user asked about Herndon weather"
            stamp = it.timestamp or "???"
            st_context_lines.append(
                f"[{stamp}] ({it.item_type.value}) {it.content}"
            )

        # 2) Gather relevant items from LTM
        ltm_structs = []
        if self.long_term_memory and task.strip():
            ltm_structs = self.long_term_memory.recall(task, number=3)
            # ltm_structs is a list of dict, e.g.
            # [ {"text": "...", "type": "...", "timestamp": "..."}, ...]

        # Convert them to lines
        ltm_context_lines = []
        for obj in ltm_structs:
            ts = obj.get("timestamp", "???")
            typ = obj.get("type", "UNKNOWN")
            txt = obj.get("text", "")
            ltm_context_lines.append(f"[{ts}] ({typ}) {txt}")

        # Gather any attached semantic memories
        semantic_snippets = []
        for sem_mem in self.semantic_memories:
            results = sem_mem.recall(task, number=2)
            snippet_texts = []
            for r in results:
                t = r.get("text", "")
                snippet_texts.append(t)
            semantic_snippets.extend(snippet_texts)

        # Combine them into a single "memory_context" if you want
        memory_context = "\n".join(
            [
                "## Recent Short-Term Memory:",
                *st_items,
                "\n## Long-Term Memory (Relevant Snippets):",
                *ltm_context_lines,
                "\n## Semantic Memory (Relevant Snippets):",
                *semantic_snippets,
            ]
        )

        # Build system message: describe your instructions + available tools
        available_tools_str = self.formatter.format_actions(
            list(self.actions.values())
        )
        system_message = f"""You are an AI agent named Bob.
Your instructions: {self.instructions or '(no instructions)'}
You have these tools available:
{available_tools_str}

Memory context:
{memory_context}

Produce output in JSON:
{{
  "response": "the final user-facing answer",
  "is_final": boolean
}}
If is_final=true, the conversation ends. 
"""

        # [1] Store the user query in short-term memory
        if self.working_memory and task.strip():
            self.working_memory.add_text(f"[User Query] {task}")

        # Our conversation message list
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": task},
        ]

        done = False

        # Turn actions into an LLM "tools" schema
        passable_actions = self.formatter.format_actions_for_llm_call(
            list(self.actions.values())
        )

        while not done:
            # Request LLM with optional tool usage
            if self.actions:
                completion = await LLMAdapter.inference(
                    model=llm,
                    messages=messages,
                    tools=passable_actions,
                    tool_choice="auto",
                    response_format={"type": "json_object"},
                )
            else:
                # If no actions
                completion = await LLMAdapter.inference(
                    model=llm,
                    messages=messages,
                    response_format={"type": "json_object"},
                )

            assistant_message = completion.choices[0].message
            response_json_str = assistant_message.content  # LLM's JSON string

            # Check if LLM called any tools
            actions = assistant_message.tool_calls
            if actions:
                # Append the raw JSON from the LLM as an "assistant" message
                messages.append(completion.choices[0].message)
                # Then process each tool call
                for action_call in actions:
                    try:
                        action_name = action_call.function.name
                        action_args = json.loads(action_call.function.arguments)
                    except:
                        action_name = "UNKNOWN"
                        action_args = {}
                        print("Error parsing tool call arguments")

                    # [2] Store the tool call in short-term memory (without chain-of-thought)
                    if self.working_memory:
                        self.working_memory.add_action(
                            f"Action: {action_name} | Args: {action_args}"
                        )

                    # Execute the tool
                    action_obj = self.actions.get(action_name)

                    if not action_obj:
                        tool_result = f"Error: No tool '{action_name}' found"
                    else:
                        if inspect.iscoroutinefunction(action_obj.func):
                            tool_result = await action_obj.func(**action_args)
                        else:
                            tool_result = action_obj.func(**action_args)

                    # Convert to string
                    tool_result_str = str(tool_result)

                    # [3] Store the tool result
                    if self.working_memory:
                        self.working_memory.add_text(
                            f"ActionResult({action_name}): {tool_result_str}"
                        )

                    # Insert a "tool" message with the result
                    messages.append(
                        {
                            "tool_call_id": action_call.id,
                            "role": "tool",
                            "name": action_name,
                            "content": tool_result_str,
                        }
                    )
            else:
                # If no tool calls, just add the JSON response to the conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.loads(response_json_str).get(
                            "response"
                        ),
                    }
                )

            # Parse the LLM's final JSON
            try:
                parsed_json = json.loads(response_json_str)
                user_facing_text = parsed_json.get("response", "")
                is_final = parsed_json.get("is_final", False)
            except:
                # If it messed up JSON, treat as incomplete
                user_facing_text = response_json_str
                is_final = False

            if is_final:
                # [4] Store the final user-facing answer
                if self.working_memory and user_facing_text.strip():
                    self.working_memory.add_text(
                        f"[Assistant Final Answer] {user_facing_text}"
                    )
                done = True
            else:
                # If not final, we do another user turn
                # but we do NOT store partial chain-of-thought
                messages.append(
                    {
                        "role": "user",
                        "content": "Continue.",
                    }
                )

        # Return all final messages if you want them
        return messages
