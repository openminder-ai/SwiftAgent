import python_weather, asyncio

from swiftagent import SwiftAgent

agent = SwiftAgent(
    name="WeatherAgent",
    instruction="be conciser and to the point",
    auto_load=False,
    auto_save=False,
    episodic_memory=True,
)


@agent.action(description="get weather for a city")
async def get_weather_for_city(city: str) -> None:
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        weather = await client.get(city)
        return weather.temperature


async def main():
    await agent.run(
        task="What is the difference in temperatures in the cities of london and herndon"
    )


if __name__ == "__main__":
    asyncio.run(main())
