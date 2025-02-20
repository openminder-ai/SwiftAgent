from swiftagent import SwiftSuite
import asyncio

suite = SwiftSuite()


async def main():
    await suite.run(runtime="hosted", host="localhost", port=8001)


asyncio.run(main())
