import asyncio
from swiftagent import SwiftAgent

agent = SwiftAgent(name="PersistentAgent")


async def main():
    await agent.run(mode="persistent", host="localhost", port=8001)


if __name__ == "__main__":
    asyncio.run(main())
