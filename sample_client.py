from swiftagent.client.base import (
    SwiftAgentClient,
)

import asyncio


async def main():
    client = SwiftAgentClient(agent_name="cow")

    q = await client.process_query(
        "What is the difference in temperatures in the cities of london and herndon"
    )

    print(q)


asyncio.run(main())
