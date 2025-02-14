# Suppose we define a new agent with some actions, want it persistent:

from swiftagent import SwiftAgent
from swiftagent.application.types import ApplicationType

agent = SwiftAgent(
    name="WeatherAgentV2",
    instruction="You are a weather-savvy agent",
    # persist_path="./my_agents/WeatherAgentV2",
    fresh_install=True,  # Means we ignore any existing data
    enable_salient_memory=True,
)


@agent.action(name="get_weather", description="get weather for a city")
async def get_weather_for_city(city: str) -> None:
    if city.lower() == "herndon":
        return 30
    else:
        return 89


# Now run it in STANDARD mode to handle a single user task:
import asyncio


async def main():
    response = await agent.run(
        type_=ApplicationType.STANDARD, task="what is weather in herndon?"
    )

    # The agent is done and has auto-saved into ./my_agents/WeatherAgentV2


asyncio.run(main())
