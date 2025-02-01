import asyncio
from swiftagent.client import SwiftClient


async def suite_client_demo():
    client = SwiftClient(
        host="localhost",
        port=8001,
        client_name="MyWsClient",
    )

    await client._connect_to_suite()

    await client.process_query_ws(
        "PersistentWeatherAgent",
        "What is the difference in temperatures in the cities of london and herndon",
    )

    # Cleanly close
    await client._close_connection_to_suite()


asyncio.run(suite_client_demo())
