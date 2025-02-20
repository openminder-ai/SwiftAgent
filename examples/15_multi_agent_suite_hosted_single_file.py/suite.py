from swiftagent import SwiftAgent, SwiftSuite
import asyncio

math_agent = SwiftAgent(
    name="MathAgent",
    description="really good at solving numerical math problems",
)
extract_agent = SwiftAgent(
    name="ExtractAgent",
    description="really good at extracting numerical info from word problems and making into numerical math problems",
)

suite = SwiftSuite(agents=[math_agent, extract_agent])


async def main():
    await suite.run(runtime="hosted", host="localhost", port=8001)


asyncio.run(main())
