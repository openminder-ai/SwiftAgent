# import arxiv, asyncio

# from swiftagent import SwiftAgent

# agent = SwiftAgent()

# async def main():
#     await agent.run(task="tell me about ProLLM")


# if __name__ == "__main__":
#     asyncio.run(main())

from swiftagent.memory.semantic import SemanticMemory
from swiftagent.prebuilt.storage.chroma import ChromaDatabase, ChromaCollection

container_collection = ChromaDatabase("./chroma_db").get_or_create_collection(
    "semantic_test"
)

memory = SemanticMemory(name="test", container_collection=container_collection)

# memory.ingest('https://arxiv.org/pdf/0802.3355.pdf') \
#       .ingest("The quick brown fox jumps over the lazy dog.") \
#       .ingest("Machine learning enables computers to learn from data.") \
#       .ingest("Artificial intelligence is transforming industries.")


print(memory.recall("what is PVM", 2))
