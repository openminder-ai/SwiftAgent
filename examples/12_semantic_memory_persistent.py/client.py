import asyncio
from swiftagent import SwiftClient


async def example_usage():
    client = SwiftClient(host="localhost", port=8001)

    # Create a store named "knowledge_base"
    await client.add_memory_store(
        agent_name="PersistentWeatherAgent", store_name="knowledge_base"
    )

    # Ingest some text
    await client.ingest_memory_store(
        agent_name="PersistentWeatherAgent",
        store_name="knowledge_base",
        content="The quick brown fox jumps over the lazy dog.",
    )

    await client.send(
        "what the did the fox jump over? and was the fox quick or slow?",
        "PersistentWeatherAgent",
    )


asyncio.run(example_usage())
