import arxiv, asyncio

import warnings

warnings.filterwarnings("ignore")

from swiftagent import SwiftAgent
from swiftagent.memory.semantic import SemanticMemory
from swiftagent.prebuilt.storage.chroma import ChromaDatabase


memory = SemanticMemory(name="test")

memory.ingest("https://arxiv.org/pdf/0802.3355.pdf").ingest(
    "The quick brown fox jumps over the lazy dog."
).ingest("Machine learning enables computers to learn from data.").ingest(
    "Artificial intelligence is transforming industries."
)

agent = SwiftAgent()

agent.add_semantic_memory_section(memory)


async def main():
    await agent.run(task="what is PVM?")


if __name__ == "__main__":
    asyncio.run(main())
