import asyncio

from swiftagent import SwiftAgent
from swiftagent.memory import SemanticMemory

# 1. Create semantic memory store
my_sem_store = SemanticMemory(name="MyFactsDB")

# 2. Create an agent with that semantic store
agent = SwiftAgent(
    name="FactAgent",
    description="Agent that can recall facts from semantic memory",
    semantic_memory_sections=[my_sem_store]  # single store
)

# 3. Ingest some data into the semantic memory
my_sem_store.ingest("SwiftAgent is a framework for building AI agents in Python.")
my_sem_store.ingest("The capital of France is Paris.")

async def main():
    await agent.run("What is SwiftAgent?")

asyncio.run(main())