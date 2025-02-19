import asyncio

from swiftagent.client.base import SwiftClient


async def main():
    client = SwiftClient()

    await client.send(
        "What is the difference in temperatures in the cities of london and herndon",
        agent_name="PersistentWeatherAgent",
    )


asyncio.run(main())
