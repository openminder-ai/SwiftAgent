# import the module
import python_weather

import asyncio
import os


async def getweather() -> None:
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        # fetch a weather forecast from a city
        weather = await client.get("london")

        # returns the current day's forecast temperature (int)
        print(weather.temperature)

        # get the weather forecast for a few days
        for daily in weather:
            print(daily)

            # hourly forecasts
            for hourly in daily:
                print(f" --> {hourly!r}")


if __name__ == "__main__":
    # see https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    # for more details
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(getweather())
