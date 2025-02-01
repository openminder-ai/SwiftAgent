from swiftagent import (
    SwiftAgent,
)
from swiftagent.application.types import (
    ApplicationType,
)

from swiftagent.actions.wrapper import action

from pprint import (
    pprint,
)

agent = SwiftAgent(name="cow")

import asyncio


@agent.action(
    name="get_weather",
    description="gets weather for a city",
)
async def action_test(
    city: str,
) -> int:
    await asyncio.sleep(1)
    if "london" in city.lower():
        return 54
    elif "herndon" in city.lower():
        return 14
    else:
        return 113


async def main():
    print(
        await agent.run(
            task="""
    What is the difference in temperatures in the cities of london and herndon
    """
        )
    )

    # await agent.run(type_=ApplicationType.PERSISTENT)


asyncio.run(main())
