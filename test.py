import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import python_weather, asyncio

from swiftagent import SwiftAgent

from swiftagent.router.base import SwiftRouter


agent1 = SwiftAgent(
    name="StockAgent",
    description="agent that is able to get stock info from a market",
)
agent2 = SwiftAgent(
    name="SynthesisAgent",
    description="agent that is able to synthesize information from multiple places",
)
agent3 = SwiftAgent(
    name="WebAgent",
    description="agent able to collect information across the news and web",
)


router = SwiftRouter(agents=[agent1, agent2, agent3])


async def main():
    from pprint import pprint

    response = await router.route(
        llm="gpt-4o",
        query="Summarize analyst recommendations and share the latest news for NVDA",
    )

    pprint(response)


if __name__ == "__main__":
    asyncio.run(main())
