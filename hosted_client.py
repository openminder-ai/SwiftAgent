# multi_agent_client.py
import asyncio
from swiftagent.client.base import SwiftClient


async def main():
    # Initialize SwiftClient, pointing to the same host/port as the SwiftSuite
    client = SwiftClient(
        host="localhost", port=8001, client_name="MyMultiAgentClient"
    )

    # This calls our new 'process_multi_agent_query_ws' method (assuming your SwiftClient has it)
    query_str = "Summarize analyst recommendations and share the latest news for NVDA. Use markdown, including tables."
    final_pipeline_result = await client.process_multi_agent_query_ws(
        query=query_str
    )

    # Print or do whatever you want with the final pipeline dictionary
    print("==== FINAL MULTI-AGENT OUTPUT ====")
    for unique_id, output_str in final_pipeline_result.items():
        print(f"{unique_id}:\n{output_str}\n-----------------")

    await client._close_connection_to_suite()


if __name__ == "__main__":
    asyncio.run(main())
