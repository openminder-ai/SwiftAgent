from swiftagent import SwiftAgent
from swiftagent.prebuilt.actions import YFinanceActionSet

agent = SwiftAgent(
    name="Finance1Agent",
    instruction="Use tables to display data",
    fresh_install=True,
    enable_salient_memory=False,
)

agent.add_actionset(YFinanceActionSet)

import asyncio


async def main():
    await agent.run(task="Summarize analyst recommendations for NVDA")


asyncio.run(main())
