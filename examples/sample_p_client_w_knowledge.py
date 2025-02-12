import asyncio
from swiftagent.client.base import SwiftClient


async def example_usage():
    client = SwiftClient(host="localhost", port=8001)

    # Create a store named "knowledge_base"
    response = await client.add_memory_store(
        agent_name="PersistentWeatherAgent", store_name="knowledge_base"
    )
    print("Add memory store response:", response)

    # Ingest some text
    response = await client.ingest_memory_store(
        agent_name="PersistentWeatherAgent",
        store_name="knowledge_base",
        content="The quick brown fox jumps over the lazy dog.",
    )

    print("Ingest memory response:", response)

    r = await client.process_query(
        "what the did the fox jump over? and was the fox quick or slow?",
        "PersistentWeatherAgent",
    )
    print("r", r)


asyncio.run(example_usage())
