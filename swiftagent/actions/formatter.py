from swiftagent.actions.base import (
    Action,
)


class ActionFormatter:
    _instance = None

    def __new__(cls):
        if (
            cls._instance
            is None
        ):
            cls._instance = super().__new__(
                cls
            )
        return cls._instance

    def __init__(self):
        if not hasattr(
            self,
            "initialized",
        ):
            self.initialized = (
                True
            )

    def format_action(
        self, action: Action
    ):
        print(action)
        return f"Action Name: {action.name}\nAction Description: {action.description}"

    def format_actions(
        self,
        actions: list[Action],
    ):
        if len(actions) > 0:
            return "\n\n".join(
                [
                    self.format_action(
                        action
                    )
                    for action in actions
                ]
            )
        return "No Actions!"

    def format_action_for_llm_call(
        self, action: Action
    ):
        return action.metadata

    def format_actions_for_llm_call(
        self,
        actions: list[Action],
    ):
        return [
            action.metadata
            for action in actions
        ]


_ = ActionFormatter()
