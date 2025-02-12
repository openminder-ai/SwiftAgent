# import agent
from swiftagent import SwiftAgent

# import semantic memory
from swiftagent.memory import SemanticMemory

import asyncio

# initialize agent
agent = SwiftAgent()

# create semantic memory
memory1 = SemanticMemory(name="sm1")
memory2 = SemanticMemory(name="sm2")

# add memories to agent
agent.add_semantic_memory_section(memory1)
agent.add_semantic_memory_section(memory2)

# ingest text to memory 1
memory1.ingest("today is monday")

# ingest text to memory 2
memory2.ingest("the temperature on monday is 70 degrees")


async def main():
    print(await agent.run(task="what is the temperature today?"))


asyncio.run(main())
