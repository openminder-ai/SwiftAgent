import aiohttp
from typing import (
    Any,
)

import asyncio
import websockets

import json
import uuid


class SwiftAgentClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8001,
        client_name: str = "SwiftClient",
    ):
        """
        Initialize the SwiftAgent client.

        Args:
            host: The hostname where SwiftAgent is running
            port: The port number SwiftAgent is listening on
        """
        self.base_url = f"{host}:{port}"

        self.websocket = None
        self.loop = asyncio.get_event_loop()
        self.ws_listen_task = None

        # Keep track of pending requests => Future objects (for suite-based queries)
        self.pending_ws_requests = {}
        self.client_name = client_name

    async def complete(self, query: str):
        pass

    async def connect_ws(self):
        """
        Connect to the SwiftSuite via WebSocket and register as a client.
        Also start a background listening task to handle incoming messages.
        """
        if self.websocket:
            print("Already connected via WebSocket.")
            return

        self.websocket = await websockets.connect(f"ws://{self.base_url}")
        # print(f"[WS] Connected to {self.ws_uri} as client '{self.client_name}'.")

        # Send 'client_join' to identify ourselves
        await self._send_ws_message(
            message_type="client_join", client_name=self.client_name
        )

        # Start background listening for messages from the suite
        self.ws_listen_task = self.loop.create_task(self._ws_listen())

    async def close_ws(self):
        """
        Close the WebSocket connection (if open).
        """
        if self.websocket:
            await self.websocket.close()
            print("[WS] Connection closed.")
        if self.ws_listen_task:
            self.ws_listen_task.cancel()

    async def process_query_ws(self, agent_name: str, query: str) -> str:
        """
        Send a query via WebSocket to the SwiftSuite for agent_name and wait for response.
        Returns the result as a string.
        """
        if not self.websocket:
            raise ConnectionError(
                "WebSocket not connected. Call connect_ws() first."
            )

        # Create a unique request_id for correlating the response
        request_id = str(uuid.uuid4())

        # We store a Future in self.pending_ws_requests
        future = self.loop.create_future()
        self.pending_ws_requests[request_id] = future

        # Send the 'client_query' message to SwiftSuite
        await self._send_ws_message(
            message_type="client_query",
            agent_name=agent_name,
            query=query,
            request_id=request_id,
        )

        # Wait for the 'client_query_response' that references request_id
        result = await future
        return result

    async def _send_ws_message(self, message_type: str, **kwargs):
        """
        Send a JSON message to the SwiftSuite server over the websocket.
        """
        if not self.websocket:
            raise ConnectionError("WebSocket is not connected.")

        msg = {
            "type": message_type,
        }
        msg.update(kwargs)
        await self.websocket.send(json.dumps(msg))

    async def _ws_listen(self):
        """
        Background task to listen for messages from SwiftSuite,
        handle them (e.g. capturing agent responses), and resolve futures.
        """
        try:
            async for raw_msg in self.websocket:
                data = json.loads(raw_msg)
                msg_type = data.get("type")

                if msg_type == "client_query_response":
                    request_id = data.get("request_id")
                    result = data.get("result", "")

                    # Resolve the matching future
                    if request_id in self.pending_ws_requests:
                        fut = self.pending_ws_requests.pop(request_id)
                        fut.set_result(result)

                elif msg_type == "system":
                    print(f"[WS System] {data.get('message')}")

                elif msg_type == "error":
                    print(f"[WS Error] {data.get('message')}")

                else:
                    print(f"[WS] Unknown message type: {msg_type}")
        except websockets.ConnectionClosed:
            print("[WS] Connection to SwiftSuite closed.")
        except Exception as e:
            print(f"[WS] Error in _ws_listen: {e}")

    async def process_query(
        self,
        query: str,
    ) -> dict[
        str,
        Any,
    ]:
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
                    f"http://{self.base_url}/{self.agent_name}",
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if result.get("status") == "error":
                        raise ValueError(
                            f"Server error: {result.get('message')}"
                        )

                    return result["result"]

            except aiohttp.ClientError as e:
                raise aiohttp.ClientError(
                    f"Failed to communicate with SwiftAgent: {str(e)}"
                )
