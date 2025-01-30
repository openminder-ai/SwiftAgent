from swiftagent.llm.adapter import (
    LLMAdapter,
)

from swiftagent.actions import (
    Action,
    ActionFormatter,
)

import json


class BaseReasoning:
    def __init__(self, name: str):
        self.actions: dict[str, Action] = {}
        self.resources = {}
        self.formatter = ActionFormatter()

    def set_action(self, action: Action):
        self.actions[action.name] = action

        return self

    def set_resources(self, resources):
        pass

        return self

    async def flow(
        self,
        memory: None = None,
        task: str = "",
        llm: str = "gpt-4o-mini",
    ):
        system_message = (
            "You are an AI agent who has access to the following tools"
            + self.formatter.format_actions(
                list(self.actions.values())
            )
            + "\n"
            + """
        Solve the goal the user has, taking as many steps as needed. \
        Any actions that you choose (tool calls), their results will be shown \
        in the next step, so proceed in a step-by-step manner.

        Respond in JSON format, with the format

        {
            "response": "your response here",
            "is_final": true or false, true if you are done, false if still need to keep going
        }
        """
        )

        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": task,
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
                    (
                        action_name,
                        action_args,
                    ) = (
                        action.function.name,
                        json.loads(action.function.arguments),
                    )
                    action_to_call = self.actions.get(action_name)

                    action_response = action_to_call.func(
                        **action_args
                    )

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
