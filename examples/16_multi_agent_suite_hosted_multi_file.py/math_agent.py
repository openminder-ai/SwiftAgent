import asyncio
from swiftagent import SwiftAgent

math_agent = SwiftAgent(
    name="MathAgent",
    description="really good at solving numerical math problems",
)


async def main():
    await math_agent.run(host="localhost", port="8001", runtime="hosted")


asyncio.run(main())
