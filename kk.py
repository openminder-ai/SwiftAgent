from swiftagent import SwiftAgent
from swiftagent.application.types import ApplicationType

# We do NOT set fresh_install, so fresh_install=False => load from disk if found
agent2 = SwiftAgent(
    name="WeatherAgentV2",  # This will get overridden once loaded
    # persist_path="./my_agents/WeatherAgentV2",
    # fresh_install=False,
    # enable_salient_memory=True,
)

print(agent2._actions)

# The agent2 now has all the same instructions, memory, actions, etc.
# We can run it again, or do something else
import asyncio


async def main():
    print(agent2.name)  # Should show "WeatherAgentV2" now
    response = await agent2.run(
        type_=ApplicationType.STANDARD,
        task="what question did I ask you a couple of seconds ago?",
    )

    print(agent2.working_memory.history)


asyncio.run(main())
