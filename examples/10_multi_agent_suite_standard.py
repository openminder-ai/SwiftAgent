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
    print(
        await suite.run(
            """
        Solve the following word problem:

        Emma is organizing a class party. She buys 5 packs of paper plates for $4 each, 3 packs of plastic cups \
        for $4 each, 3 packs of plastic cups for $3 each, and a large pizza for $20. She splits the \ 
        total cost equally among herself and 6 friends. How much does each person pay? 
        """
        )
    )


asyncio.run(main())
