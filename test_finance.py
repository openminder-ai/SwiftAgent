from dotenv import load_dotenv

load_dotenv()

from swiftagent import SwiftAgent
from swiftagent.prebuilt.actions import YFinanceActionSet


agent = SwiftAgent(
    name="Finance2Agent",
    instruction="Use tables to display data",
    auto_load=False,
    auto_save=False,
    episodic_memory=True,
)

agent.add_actionset(YFinanceActionSet)

import asyncio


async def main():
    await agent.run(task="Summarize analyst recommendations for Apple")


asyncio.run(main())
