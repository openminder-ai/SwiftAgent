from swiftagent import SwiftAgent
import asyncio

agent = SwiftAgent()


async def main():
    await agent.run(task="what is the color of bob's pencil?")


asyncio.run(main())
