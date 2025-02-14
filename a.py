from swiftagent import SwiftAgent
from swiftagent.memory import SemanticMemory

# agent = SwiftAgent(name='testagent', description='good at question answering', enable_salient_memory=True)

# memory = SemanticMemory(name='sm_1')
# # memory.ingest('the color of bob\'s pencil is red')

# agent.add_semantic_memory_section(memory)

# agent.save()

import asyncio


async def main():
    agent = SwiftAgent(name="testagent")

    print(await agent.run(task="what is the color of bob's pencil?"))


asyncio.run(main())
