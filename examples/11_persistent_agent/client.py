import asyncio
from swiftagent import SwiftClient

async def example_client_usage():
    client = SwiftClient(host="localhost", port=8001)

    await client.send('What is the weather in Tokyo?')


asyncio.run(example_client_usage())
