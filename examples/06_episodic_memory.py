from swiftagent import SwiftAgent
import asyncio

agent = SwiftAgent(
    name="Bob",
    description="friendly, human-like agent",
    instruction="respond like a bubbly human",
    episodic_memory=True,
)


async def main():
    user_input = input("Ask Bob a question: ")

    await agent.run(user_input)

    print("Sleeping 10 seconds")

    await asyncio.sleep(10)

    await agent.run(
        "What was the last thing I asked you, and how many seconds ago did I ask?"
    )


asyncio.run(main())
