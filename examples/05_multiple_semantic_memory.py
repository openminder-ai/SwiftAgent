import asyncio

from swiftagent import SwiftAgent
from swiftagent.memory import SemanticMemory

memory_about_python = SemanticMemory(name="python_facts")
memory_about_cities = SemanticMemory(name="city_facts")

memory_about_python.ingest("Python is an interpreted language created by Guido van Rossum.")

agent = SwiftAgent(
    name="MultiMemoryAgent",
    semantic_memory_sections=[memory_about_python, memory_about_cities]
)

memory_about_cities.ingest("Tokyo is the capital of Japan.")

async def main():
    await agent.run("Who created Python and what is the capital of Japan?")

asyncio.run(main())