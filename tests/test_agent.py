# tests/test_agent.py

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from swiftagent import SwiftAgent
from swiftagent.application.types import RuntimeType


@pytest.mark.asyncio
async def test_agent_basic_init():
    """Test agent creation with minimal args."""
    agent = SwiftAgent(name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.verbose is True  # default is True
    assert not agent.auto_save


@pytest.mark.asyncio
async def test_agent_action_registration():
    """Register an action via decorator and confirm it appears in agent._actions."""
    agent = SwiftAgent(name="ActionAgent")

    @agent.action(name="say_hello", description="Say hello to someone")
    def greet(name: str) -> str:
        return f"Hello, {name}"

    assert "say_hello" in agent._actions
    assert greet("Alice") == "Hello, Alice"


@pytest.mark.asyncio
@patch("swiftagent.llm.adapter.LLMAdapter.inference")
async def test_agent_run_standard(mock_llm):
    """
    Mock the LLM so we can test that agent.run() processes the user query
    and returns the final 'response' from the LLM JSON.
    """
    mock_llm.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"response":"Mocked Reply","is_final":true}',
                    tool_calls=[],
                )
            )
        ]
    )

    agent = SwiftAgent(name="MockAgent")
    output = await agent.run(task="Hello Agent", runtime=RuntimeType.STANDARD)
    assert output == "Mocked Reply"

    mock_llm.assert_called_once()


@pytest.mark.asyncio
@patch("swiftagent.llm.adapter.LLMAdapter.inference")
async def test_agent_episodic_memory_init(mock_llm):
    """If `episodic_memory=True`, agent should have working and long-term memory."""
    mock_llm.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"response":"Done","is_final":true}', tool_calls=[]
                )
            )
        ]
    )
    agent = SwiftAgent(name="MemoryAgent", episodic_memory=True)
    assert agent.working_memory is not None
    assert agent.long_term_memory is not None

    result = await agent.run(
        task="Testing memory", runtime=RuntimeType.STANDARD
    )
    assert result == "Done"
