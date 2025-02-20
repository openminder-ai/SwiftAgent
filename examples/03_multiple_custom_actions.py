import asyncio
from swiftagent import SwiftAgent

agent = SwiftAgent(name="MathAgent", description="Agent with multiple actions")


@agent.action(name="multiply", description="Multiply two numbers")
def multiply(a: float, b: float) -> float:
    return a * b


@agent.action(name="subtract", description="Subtract b from a")
def subtract(a: float, b: float) -> float:
    return a - b


@agent.action(description="Add two integers")
def add_two_integers(x: int, y: int) -> int:
    return x + y


async def main():
    await agent.run("Compute 3*5, then subtract 2, and then add 7")


asyncio.run(main())
