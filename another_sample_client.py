import asyncio
from swiftagent.client import SwiftAgentClient


async def suite_client_demo():
    client = SwiftAgentClient(
        host="localhost", port=8001, client_name="MyWsClient"  # the SwiftSuite port
    )

    await client.connect_ws()

    # Suppose you have an agent named "Alice" in that suite
    ws_result = await client.process_query_ws(
        "cow",
        "What is the difference in temperatures in the cities of london and herndon!",
    )
    print("WS result:", ws_result)

    # Cleanly close
    await client.close_ws()


asyncio.run(suite_client_demo())
