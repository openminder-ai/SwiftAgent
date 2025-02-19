import asyncio

from swiftagent import SwiftAgent
from swiftagent.actions.set import ActionSet
from swiftagent.application.types import RuntimeType

# Example action set for math
math_actions = ActionSet(name="math_stuff", description="Some math utilities")

@math_actions.action(name="multiply", description="Multiply two numbers")
def multiply(a: float, b: float) -> float:
    return a * b

@math_actions.action(name="subtract", description="Subtract b from a")
def subtract(a: float, b: float) -> float:
    return a - b

# 1. Create agent
agent = SwiftAgent(name="MathAgent", description="Agent with multiple actions")

# 2. Add the entire ActionSet
agent.add_actionset(math_actions)

async def main():
    await agent.run("Compute 3*5, then subtract 2, and then add 7")

asyncio.run(main())