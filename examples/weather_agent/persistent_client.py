from swiftagent.client.base import SwiftClient
import asyncio


async def main():
    client = SwiftClient()

    await client.process_query(
        "What is the difference in temperatures in the cities of london and herndon",
        agent_name="PersistentWeatherAgent",
    )


asyncio.run(main())
