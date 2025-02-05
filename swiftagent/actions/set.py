from typing import Any, Callable, Dict, List, Optional
import inspect

# Assuming you have your existing Action class available:
from swiftagent.actions.base import Action


class ActionSet:
    """
    A container for grouping multiple actions together.

    You can register actions into the set using the .action() decorator.

    Example:

        utils_actions = ActionSet(name="utils", description="Utility functions")

        @utils_actions.action(
            name="add",
            description="Adds two numbers",
            params={"a": "The first number", "b": "The second number"}
        )
        def add(a: int, b: int) -> int:
            return a + b

        @utils_actions.action(
            name="subtract",
            description="Subtracts two numbers",
            params={"a": "The minuend", "b": "The subtrahend"}
        )
        def subtract(a: int, b: int) -> int:
            return a - b
    """

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        strict: bool = True,
    ):
        self.name = name
        self.description = description or ""
        self.strict = strict
        self._actions: Dict[str, Action] = {}

    def action(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
        strict: Optional[bool] = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a function as an Action within this ActionSet.

        The decorated function is wrapped as an Action and stored in the set.
        If you do not provide a name or description here, the function’s name and
        docstring (if available) are used.

        Args:
            name: Optional custom name for the action.
            description: Optional description of the action.
            params: Optional dictionary describing each parameter.
            strict: Optional override of the ActionSet’s strict flag for this action.

        Returns:
            A decorator that returns the wrapped action function.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # Use the provided strict if not None, otherwise fall back to the set default.
            actual_strict = strict if strict is not None else self.strict

            # Create an Action instance (this will also wrap the function)
            action_instance = Action(
                func=func,
                name=name or func.__name__,
                description=description or func.__doc__ or "",
                params=params or {},
                strict=actual_strict,
            )
            # Store the action using its name as the key
            self._actions[action_instance.name] = action_instance

            # Return the wrapped function so that it behaves like the original.
            return action_instance.wrapped_func

        return decorator

    def add_action(
        self,
        action: Any | None = None,
    ) -> None:
        """Manually add an action to the agent."""
        if action is None:
            if hasattr(action, "__action_instance__"):
                action_instance: Action = action.__action_instance__
                self._actions[action_instance.name] = action_instance
                return

    @property
    def actions(self) -> List[Action]:
        """
        Returns the list of Action instances that have been registered.
        """
        return list(self._actions.values())
