# import agent
from swiftagent import SwiftAgent

# import semantic memory
from swiftagent.memory import SemanticMemory

import asyncio

# initialize agent
agent = SwiftAgent()

# create semantic memory
memory = SemanticMemory()

# add memory to agent
agent.add_semantic_memory_section(memory)

# ingest text
memory.ingest("The fairest maiden of them all is Drew Carwyther")

# ingest pdf
memory.ingest("https://arxiv.org/pdf/2501.19393v1")


async def main():
    print(await agent.run(task="who is the fairest maiden of them all?"))


asyncio.run(main())
