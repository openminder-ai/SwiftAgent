import asyncio
from swiftagent import SwiftAgent

extract_agent = SwiftAgent(
    name="ExtractAgent",
    description="really good at extracting numerical info from word problems and making into numerical math problems",
)


async def main():
    await extract_agent.run(host="localhost", port="8001", runtime="hosted")


asyncio.run(main())
