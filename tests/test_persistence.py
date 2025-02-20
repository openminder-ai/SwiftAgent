# tests/test_persistence.py

import pytest
import os
import tempfile
import shutil
from swiftagent.application.base import SwiftAgent
from swiftagent.persistence.registry import AgentRegistry


def test_registry_save_load():
    """
    Create an agent, add an action, save it, load into a fresh agent,
    and verify the loaded action works.
    """
    temp_dir = tempfile.mkdtemp()

    agent = SwiftAgent(name="PersistMe", persist_path=temp_dir)

    @agent.action(name="greet")
    def greet(name: str) -> str:
        return f"Hello, {name}"

    AgentRegistry.save_agent_profile(agent)

    # Now load into a new agent object
    fresh_agent = SwiftAgent(name="Empty", persist_path=temp_dir)
    AgentRegistry.load_agent_profile(fresh_agent)

    assert fresh_agent.name == "PersistMe"
    assert "greet" in fresh_agent._actions
    assert fresh_agent._actions["greet"].func("Alice") == "Hello, Alice"

    shutil.rmtree(temp_dir)
