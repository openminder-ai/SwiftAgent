# tests/conftest.py

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """
    By default, pytest-asyncio creates a function-scoped event loop.
    This fixture makes a session-scoped loop if you want to share it.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
