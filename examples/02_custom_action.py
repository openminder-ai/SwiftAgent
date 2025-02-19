import asyncio
from swiftagent import SwiftAgent

agent = SwiftAgent(
    name="WeatherAgent",
    description="Gets weather information"
)

@agent.action(name="get_weather",description="Fetches weather info for a city")
def get_weather(city: str) -> str:
    # Imagine we do a real API call here. For the example, let's mock it.
    return f"The weather in {city} is warm and sunny (mocked)."

async def main():
    await agent.run("What's the weather in Los Angeles?")

if __name__ == "__main__":
    asyncio.run(main())