from swiftagent import SwiftAgent

from swiftagent.prebuilt.actions.exa import exa_actions

agent = SwiftAgent(
    name="ta", fresh_install=True, description="Web browsing agent :))"
)
agent.add_actionset(exa_actions)

from swiftagent.memory import SemanticMemory

m = SemanticMemory("sm1")

m.container_collection.clear()

m.ingest(["the brown fox wore red shoes", "the brown fox wore leather shoes"])

agent.add_semantic_memory_section(m)

import asyncio


async def main():
    await agent.run(task="what shoes did the brown fox wear?")


asyncio.run(main())
