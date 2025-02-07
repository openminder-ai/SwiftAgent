from swiftagent.memory import SemanticMemory
from swiftagent import SwiftAgent

agent = SwiftAgent()

memory = SemanticMemory(name="cow")
memory.ingest("The fairest maiden of them all is Drew Carwyther")

agent.add_semantic_memory_section(memory)

import asyncio


async def main():
    print(await agent.run(task="who is the fairest maiden of them all?"))


asyncio.run(main())
