import aiohttp
from typing import Any, Literal

import asyncio
import websockets

import json
import uuid

from rich.console import Console
from rich.theme import Theme
from rich.status import Status
from rich.panel import Panel
from rich import box

from swiftagent.styling.defaults import client_cli_default

from swiftagent.application.types import ApplicationType


class SwiftClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8001,
        client_name: str = "SwiftClient",
    ):
        """
        Initialize the SwiftClient client.

        Args:
            host: The hostname where SwiftSuite is running (for websockets)
            port: The port number SwiftSuite is listening on
            client_name: A display name for logging / identification
        """
        self.base_url = f"{host}:{port}"
        self.connection = None
        self.loop = asyncio.get_event_loop()
        self.ws_listen_task = None

        # Keep track of pending requests => Future objects
        # key: request_id => value: Future that we set_result(...) upon receiving the response
        self.pending_ws_requests = {}
        self.client_name = client_name
        self.console = Console(theme=client_cli_default)

    ##############################
    # Universal
    ##############################
    async def send(
        self,
        query: str,
        agent_name: str | None = None,
        type_: Literal["agent", "suite"] = "agent",
    ):
        if type_ == "agent":
            return await self.process_query(query, agent_name)
        elif type_ == "suite":
            await self._connect_to_suite()

            response = await self.process_query_ws(agent_name, query)

            await self._close_connection_to_suite()
            return response

    ##############################
    # Persistent
    ##############################
    async def process_query(
        self, query: str, agent_name: str
    ) -> dict[str, Any]:
        """
        Send a query to the SwiftAgent server.

        Args:
            query: The query string to process
            agent_name: Name of the agent to process the query

        Returns:
            Dict containing the response from the server

        Raises:
            aiohttp.ClientError: If the request fails
            ValueError: If the server returns an error response
        """
        self.console.print(
            Panel(
                f"[info]Query:[/info] {query}",
                title=f"[ws]→ Sending to {agent_name}[/ws]",
                box=box.ROUNDED,
                border_style="blue",
            )
        )

        async with aiohttp.ClientSession() as session:
            try:
                # Show thinking animation while making the request
                with Status(
                    "[ws]Agent thinking...[/ws]", spinner="dots"
                ) as status:
                    async with session.post(
                        f"http://{self.base_url}/{agent_name}",
                        json={"query": query},
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        response.raise_for_status()
                        result = await response.json()

                if result.get("status") == "error":
                    raise ValueError(f"Server error: {result.get('message')}")

                # After request completes, show the response
                self.console.print(
                    Panel(
                        result.get("result"),
                        title="[success]← Response Received[/success]",
                        border_style="green",
                        box=box.HEAVY,
                    )
                )

                return result["result"]

            except aiohttp.ClientError as e:
                raise aiohttp.ClientError(
                    f"Failed to communicate with SwiftAgent: {str(e)}"
                )

    async def add_memory_store(self, agent_name: str, store_name: str):
        """
        Create a new memory store on the given agent (in persistent mode).
        """
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.base_url}/{agent_name}/add_memory_store"
            payload = {"store_name": store_name}
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def ingest_memory_store(
        self, agent_name: str, store_name: str, content: str
    ):
        """
        Ingest text into an existing memory store on the given agent.
        """
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.base_url}/{agent_name}/ingest_memory_store"
            payload = {"store_name": store_name, "content": content}
            async with session.post(url, json=payload) as resp:
                resp.raise_for_status()
                return await resp.json()

    ##############################
    # Hosted
    ##############################
    async def _connect_to_suite(self):
        """
        Connect to the SwiftSuite via WebSocket and register as a client.
        Also start a background listening task to handle incoming messages.
        """
        if self.connection:
            # already connected
            return

        ws_uri = f"ws://{self.base_url}"
        self.connection = await websockets.connect(ws_uri)

        # Identify ourselves as a 'client'
        await self._send_message_to_suite(
            message_type="client_join", client_name=self.client_name
        )

        # Start background listening for messages from the suite
        self.ws_listen_task = self.loop.create_task(self._listen_to_suite())

    async def _close_connection_to_suite(self):
        """
        Close the WebSocket connection (if open).
        """
        if self.connection:
            await self.connection.close()
        if self.ws_listen_task:
            self.ws_listen_task.cancel()

    async def process_query_ws(self, agent_name: str, query: str) -> str:
        """
        Send a query via WebSocket to the SwiftSuite for agent_name and wait for response.
        Returns the result as a string.
        """
        if not self.connection:
            raise ConnectionError(
                "WebSocket not connected. Call connect_ws() first."
            )

        # Create a unique request_id for correlating the response
        request_id = str(uuid.uuid4())

        # We store a Future in self.pending_ws_requests
        future = self.loop.create_future()
        self.pending_ws_requests[request_id] = future

        # Show query being sent
        self.console.print(
            Panel(
                f"[info]Query:[/info] {query}",
                title=f"[ws]→ Sending to {agent_name}[/ws]",
                box=box.ROUNDED,
                border_style="blue",
            )
        )

        await self._send_message_to_suite(
            message_type="client_query",
            agent_name=agent_name,
            query=query,
            request_id=request_id,
        )

        # Show thinking animation while waiting
        with Status("[ws]Agent thinking...[/ws]", spinner="dots") as status:
            result = await future

        # Show result
        self.console.print(
            Panel(
                result,
                title="[success]← Response Received[/success]",
                border_style="green",
                box=box.HEAVY,
            )
        )

        return result

    async def _send_message_to_suite(self, message_type: str, **kwargs):
        """
        Send a JSON message to the SwiftSuite server over the websocket.
        """
        if not self.connection:
            raise ConnectionError("WebSocket is not connected.")
        msg = {"type": message_type}
        msg.update(kwargs)
        await self.connection.send(json.dumps(msg))

    async def _listen_to_suite(self):
        """
        Background task to listen for messages from SwiftSuite,
        handle them (e.g., capturing agent responses), and resolve futures.
        """
        try:
            async for raw_msg in self.connection:
                data = json.loads(raw_msg)
                msg_type = data.get("type")

                # Single-agent response
                if msg_type == "client_query_response":
                    req_id = data.get("request_id")
                    if req_id in self.pending_ws_requests:
                        fut = self.pending_ws_requests.pop(req_id)
                        fut.set_result(data["result"])

                # Multi-agent pipeline final response
                elif msg_type == "client_multi_agent_query_response":
                    req_id = data.get("request_id")
                    if req_id in self.pending_ws_requests:
                        fut = self.pending_ws_requests.pop(req_id)
                        fut.set_result(data["result"])

                elif msg_type == "system":
                    self.console.print(
                        f"[info][System][/info] {data.get('message')}"
                    )

                elif msg_type == "error":
                    self.console.print(
                        f"[error]Error: {data.get('message')}[/error]"
                    )

                else:
                    # For debugging or ignoring other message types
                    self.console.print(
                        f"[warning]Unknown WS message type[/warning]: {msg_type}"
                    )

        except websockets.ConnectionClosed:
            self.console.print("[warning]WebSocket connection closed[/warning]")
        except Exception as e:
            self.console.print(f"[error]Error in _listen_to_suite: {e}[/error]")

    async def process_multi_agent_query_ws(self, query: str) -> dict:
        """
        Send a multi-agent pipeline query to SwiftSuite.
        Returns the final dictionary (the aggregated pipeline results).

        Usage:
            result = await client.process_multi_agent_query_ws("some big multi-agent task")
        """
        await self._connect_to_suite()

        request_id = str(uuid.uuid4())
        future = self.loop.create_future()
        self.pending_ws_requests[request_id] = future

        self.console.print(
            Panel(
                f"[info]Multi-Agent Query:[/info] {query}",
                title="[ws]→ SwiftSuite (Router)[/ws]",
                box=box.ROUNDED,
                border_style="blue",
            )
        )

        # Send the multi-agent request
        await self._send_message_to_suite(
            message_type="client_multi_agent_query",
            request_id=request_id,
            query=query,
        )

        # Wait for final pipeline response
        with Status(
            "[ws]Orchestrating multi-agent tasks...[/ws]", spinner="dots"
        ) as status:
            result = await future  # should be a dict of outputs

        self.console.print(
            Panel(
                json.dumps(result, indent=2),
                title="[success]← Multi-Agent Pipeline Response[/success]",
                border_style="green",
                box=box.HEAVY,
            )
        )
        return result
