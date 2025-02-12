from swiftagent import SwiftAgent
from swiftagent.application.types import ApplicationType

# We do NOT set fresh_install, so fresh_install=False => load from disk if found
agent2 = SwiftAgent(
    name="WhateverNameHere",  # This will get overridden once loaded
    persist_path="./my_agents/WeatherAgentV2",
    fresh_install=False,
)

print(agent2._actions)

# The agent2 now has all the same instructions, memory, actions, etc.
# We can run it again, or do something else
import asyncio


async def main():
    print(agent2.name)  # Should show "WeatherAgentV2" now
    response = await agent2.run(
        type_=ApplicationType.STANDARD, task="what is weather in boston?"
    )


asyncio.run(main())
