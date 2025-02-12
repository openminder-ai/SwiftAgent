# Suppose we define a new agent with some actions, want it persistent:

from swiftagent import SwiftAgent
from swiftagent.application.types import ApplicationType

agent = SwiftAgent(
    name="WeatherAgentV2",
    instruction="You are a weather-savvy agent",
    persist_path="./my_agents/WeatherAgentV2",
    fresh_install=True,  # Means we ignore any existing data
    enable_salient_memory=True,
)


# add some action
@agent.action(
    name="say_hello",
    description="Test action",
    params={"msg": "Message to say"},
)
def say_hello(msg: str):
    return f"Hello, I say: {msg}"


# Now run it in STANDARD mode to handle a single user task:
import asyncio


async def main():
    response = await agent.run(
        type_=ApplicationType.STANDARD, task="Please say hello to the world!"
    )

    # The agent is done and has auto-saved into ./my_agents/WeatherAgentV2


asyncio.run(main())
