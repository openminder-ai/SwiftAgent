from swiftagent import (
    SwiftAgent,
)

from swiftagent.suite import SwiftSuite

from swiftagent.application.types import (
    ApplicationType,
)

from pprint import (
    pprint,
)


agent = SwiftAgent(name="cow")

suite = SwiftSuite(name="hi", agents=[agent])

import asyncio


@agent.action(
    name="get_weather",
    description="gets weather for a city",
)
def another_thing(
    city: str,
) -> int:
    if "london" in city.lower():
        return 54
    elif "herndon" in city.lower():
        return 14
    else:
        return 113


async def main():
    # print(await agent.run(task="""
    # What is the difference in temperatures in the cities of london and herndon
    # """))

    # await agent.run(type_=ApplicationType.PERSISTENT)
    await suite.setup(host="localhost", port=8001)


asyncio.run(main())
