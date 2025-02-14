from swiftagent import SwiftAgent

from swiftagent.prebuilt.actions.exa import exa_actions

agent = SwiftAgent(
    name="ta", fresh_install=True, description="Web browsing agent :))"
)
agent.add_actionset(exa_actions)

# import asyncio

# async def main():
#     await agent.run(task='what happened in the news today?')

# asyncio.run(main())
