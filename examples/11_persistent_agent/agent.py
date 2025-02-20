import python_weather, asyncio
from swiftagent import SwiftAgent

agent = SwiftAgent(name="PersistentWeatherAgent")


@agent.action(description="get weather for a city")
async def get_weather_for_city(city: str) -> None:
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(city)
        return weather.temperature


async def main():
    await agent.run(runtime="persistent", host="localhost", port=8001)


if __name__ == "__main__":
    asyncio.run(main())
