# tests/test_actions.py

import pytest
from swiftagent.actions import Action, action, ActionSet


def test_action_decorator_basic():
    """Verify the @action decorator creates Action metadata cleanly."""

    @action(name="echo", description="Echo some text")
    def echo_func(msg: str) -> str:
        return msg

    # Check the stored action instance
    action_obj = getattr(echo_func, "__action_instance__", None)
    assert action_obj, "No action instance attached by decorator"
    assert action_obj.name == "echo"
    assert "Echo some text" in action_obj.description

    # Actual function call
    assert echo_func("Hello") == "Hello"


def test_action_init_strict_params():
    """Ensure strict mode forbids extra parameters in JSON schema."""

    def add(a: int, b: int) -> int:
        return a + b

    act = Action(
        func=add,
        name="add_integers",
        description="Add two integers",
        strict=True,
    )
    schema = act.metadata["function"]["parameters"]
    assert schema["additionalProperties"] is False


def test_action_set():
    """Test grouping multiple actions in an ActionSet."""
    math_actions = ActionSet(name="math_set", description="Basic math actions")

    @math_actions.action(name="multiply")
    def multiply(a: float, b: float) -> float:
        return a * b

    @math_actions.action(description="Subtract b from a")
    def subtract(a: float, b: float) -> float:
        return a - b

    actions = math_actions.actions
    assert len(actions) == 2
    action_names = {a.name for a in actions}
    assert {"multiply", "subtract"} == action_names
