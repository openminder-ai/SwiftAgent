import aiohttp
from typing import Any


class SwiftAgentClient:
    def __init__(self, agent_name: str, host: str = "localhost", port: int = 8001):
        """
        Initialize the SwiftAgent client.

        Args:
            agent_name: Name of the agent to connect to
            host: The hostname where SwiftAgent is running
            port: The port number SwiftAgent is listening on
        """
        self.base_url = f"http://{host}:{port}"
        self.agent_name = agent_name.lower()  # Normalize name for URL routing

    async def process_query(self, query: str) -> dict[str, Any]:
        """
        Send a query to the SwiftAgent server.

        Args:
            query: The query string to process

        Returns:
            Dict containing the response from the server

        Raises:
            aiohttp.ClientError: If the request fails
            ValueError: If the server returns an error response
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/{self.agent_name}",
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if result.get("status") == "error":
                        raise ValueError(f"Server error: {result.get('message')}")

                    return result["result"]

            except aiohttp.ClientError as e:
                raise aiohttp.ClientError(
                    f"Failed to communicate with SwiftAgent: {str(e)}"
                )
