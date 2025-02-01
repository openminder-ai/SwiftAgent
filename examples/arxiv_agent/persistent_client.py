import asyncio

from swiftagent.client.base import SwiftClient


async def main():
    client = SwiftClient()

    await client.send(
        "tell me about ProLLM",
        agent_name="PersistentWeatherAgent",
    )


asyncio.run(main())
