from typing import Callable, Optional
from functools import wraps
from swiftagent.actions.base import Action


def action(
    name: Optional[str] = None,
    description: Optional[str] = None,
    params: Optional[dict[str, str]] = None,
    strict: bool = True,
):
    """
    Standalone decorator that transforms a function into an Action-compatible format.
    Creates the Action object directly within the decorator.

    Args:
        name: Name of the action
        description: Description of what the action does
        params: Dictionary of parameter descriptions
        strict: Whether to enforce strict parameter checking
    """

    def decorator(func: Callable):
        # Create the Action object directly here
        action_instance = Action(
            func=func,
            name=name,
            description=description or func.__doc__ or "",
            params=params or {},
            strict=strict,
        )

        # Store the action instance on the function itself
        func.__action_instance__ = action_instance

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Preserve the action instance on the wrapper
        wrapper.__action_instance__ = action_instance
        return wrapper

    return decorator
