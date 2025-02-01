import asyncio
from swiftagent.client import SwiftClient


async def suite_client_demo():
    client = SwiftClient(
        host="localhost",
        port=8001,
        client_name="MyWsClient",
    )

    await client.send(
        "What is the difference in temperatures in the cities of london and herndon",
        "PersistentWeatherAgent",
        "suite",
    )


asyncio.run(suite_client_demo())
