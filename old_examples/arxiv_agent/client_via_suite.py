import asyncio

from swiftagent import SwiftClient


async def suite_client_demo():
    client = SwiftClient(
        host="localhost",
        port=8001,
        client_name="MyWsClient",
    )

    await client.send(
        "tell me about ProLLM",
        "PersistentWeatherAgent",
        "suite",
    )


asyncio.run(suite_client_demo())
