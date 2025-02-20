# tests/test_suite.py

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from swiftagent import SwiftAgent
from swiftagent.suite import SwiftSuite
from swiftagent.application.types import RuntimeType


@pytest.mark.asyncio
@patch("websockets.serve")
async def test_suite_run_hosted(mock_serve):
    """
    Confirm that SwiftSuite in HOSTED mode calls websockets.serve.
    We cancel the infinite task to avoid blocking the test.
    """
    suite = SwiftSuite(
        name="TestSuite",
        agents=[SwiftAgent(name="AgentA"), SwiftAgent(name="AgentB")],
    )
    task = asyncio.create_task(
        suite.run(host="localhost", port=8080, runtime=RuntimeType.HOSTED)
    )
    await asyncio.sleep(0.05)
    mock_serve.assert_called_once()
    task.cancel()


@pytest.mark.asyncio
async def test_suite_basic_init():
    """Simple test verifying suite initialization and agent placeholders."""
    agent_1 = SwiftAgent(name="FirstAgent")
    agent_2 = SwiftAgent(name="SecondAgent")

    suite = SwiftSuite(agents=[agent_1, agent_2])
    assert (
        len(suite.agents) == 0
    ), "Agents dict is empty until they actually join via websockets."
    assert suite.agents_to_be_joined == [agent_1, agent_2]
