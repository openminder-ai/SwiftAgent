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


@action(
    name="get_weather",
    description="gets weather for a city",
)
def action_test(
    city: str,
) -> int:
    if "london" in city.lower():
        return 54
    elif "herndon" in city.lower():
        return 14
    else:
        return 113


agent.add_action(action_test)


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
