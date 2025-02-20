import asyncio
from swiftagent import SwiftClient

async def example_client_usage():
    client = SwiftClient(host="localhost", port=8001, mode='suite')

    await client.send("""
    Solve the following word problem:

    Emma is organizing a class party. She buys 5 packs of paper plates for $4 each, 3 packs of plastic cups \
    for $4 each, 3 packs of plastic cups for $3 each, and a large pizza for $20. She splits the \ 
    total cost equally among herself and 6 friends. How much does each person pay?                
    """)


asyncio.run(example_client_usage())
