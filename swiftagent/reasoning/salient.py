# swiftagent/reasoning/salient.py

from typing import List, Optional
import json
import inspect

from swiftagent.reasoning.base import BaseReasoning
from swiftagent.llm.adapter import LLMAdapter
from swiftagent.actions.formatter import ActionFormatter
from swiftagent.actions.base import Action
from swiftagent.memory.working import WorkingMemory
from swiftagent.memory.long_term import LongTermMemory
from swiftagent.memory.semantic import SemanticMemory


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
        self.formatter = ActionFormatter()  # For listing available actions

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

        # Gather short-term memory (we might or might not use it in the prompt)
        st_texts = []
        st_actions = []
        if self.working_memory:
            st_texts = self.working_memory.get_recent_text(5)
            st_actions = self.working_memory.get_recent_actions(5)

        # Gather relevant items from LTM
        ltm_snippets = []
        if self.long_term_memory and task.strip():
            ltm_snippets = self.long_term_memory.recall(task, number=3)

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
                "## Recent Short-Term Text:",
                *st_texts,
                "\n## Recent Short-Term Actions:",
                *st_actions,
                "\n## Long-Term Memory (Relevant Snippets):",
                *ltm_snippets,
                "\n## Semantic Memory (Relevant Snippets):",
                *semantic_snippets,
            ]
        )

        # Build system message: describe your instructions + available tools
        available_tools_str = self.formatter.format_actions(
            list(self.actions.values())
        )
        system_message = f"""You are an AI agent named '{self.name}'.
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
                messages.append(
                    {
                        "role": "assistant",
                        "content": response_json_str,
                    }
                )
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
                        "content": response_json_str,
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
