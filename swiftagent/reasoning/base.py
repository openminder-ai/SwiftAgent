from swiftagent.llm.adapter import (
    LLMAdapter,
)

from swiftagent.actions import (
    Action,
)

from swiftagent.actions.formatter import ActionFormatter

from swiftagent.memory.semantic import SemanticMemory

import json

import inspect

from pprint import pprint


class BaseReasoning:
    def __init__(self, name: str, instructions: str):
        self.actions: dict[
            str,
            Action,
        ] = {}

        self.semantic_memories: list[SemanticMemory] = []
        self.resources = {}
        self.formatter = ActionFormatter()

        self.instructions = instructions

    def set_action(
        self,
        action: Action,
    ):
        self.actions[action.name] = action

        return self

    def set_resources(
        self,
        resources,
    ):
        pass

        return self

    def add_semantic_memory_section(
        self, semantic_memory_section: SemanticMemory
    ):
        self.semantic_memories.append(semantic_memory_section)

        return self

    async def flow(
        self,
        memory: None = None,
        task: str = "",
        llm: str = "gpt-4o",
    ):
        system_message = (
            f"You are an AI agent{'.' if self.instructions is None else ', with instructions '+self.instructions} "
            + "You have  access to the following tools"
            + self.formatter.format_actions(list(self.actions.values()))
            + "\n"
            + """
        Solve the goal the user has, taking as many steps as needed. \
        Any actions that you choose (tool calls), their results will be shown \
        in the next step, so proceed in a step-by-step manner.

        Respond in JSON format, with the format

        {
            "response": "your response here (SHOULD BE A STRING)",
            "is_final": true or false, true if you are done, false if still need to keep going
        }
        """
        )

        recall_semantic_information = "\n".join(
            [
                "\n".join(
                    [
                        memory.get("text")
                        for memory in memory_container.recall(task, 2)
                    ]
                )
                for memory_container in self.semantic_memories
            ]
        )

        initial_user_message = f"""
        User Task: {task}

        You also have the following semantic memory information:
        {recall_semantic_information}
        """

        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": initial_user_message,
            },
        ]

        done = False

        passable_actions = self.formatter.format_actions_for_llm_call(
            list(self.actions.values())
        )

        while not done:
            if len(self.actions) != 0:
                completion = await LLMAdapter.inference(
                    model=llm,
                    messages=messages,
                    tools=passable_actions,
                    tool_choice="auto",
                    response_format={"type": "json_object"},
                )
            else:
                completion = await LLMAdapter.inference(
                    model=llm,
                    messages=messages,
                    response_format={"type": "json_object"},
                )

            (
                response,
                actions,
            ) = (
                completion.choices[0].message.content,
                completion.choices[0].message.tool_calls,
            )

            if actions:
                messages.append(completion.choices[0].message)

                for action in actions:
                    try:
                        (
                            action_name,
                            action_args,
                        ) = (
                            action.function.name,
                            json.loads(action.function.arguments),
                        )
                    except:
                        print("failed here")
                    action_to_call = self.actions.get(action_name)

                    # Check if the function is async
                    if inspect.iscoroutinefunction(action_to_call.func):
                        action_response = await action_to_call.func(
                            **action_args
                        )
                    else:
                        action_response = action_to_call.func(**action_args)

                    messages.append(
                        {
                            "tool_call_id": action.id,
                            "role": "tool",
                            "name": action_name,
                            "content": str(action_response),
                        }
                    )

            if response:

                # parse json
                response: dict = json.loads(response)

                (
                    response,
                    is_final,
                ) = response.get(
                    "response"
                ), response.get("is_final")

                messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                if not is_final:
                    messages.append(
                        {
                            "role": "user",
                            "content": "Go on!",
                        }
                    )

                done = is_final

        return messages
