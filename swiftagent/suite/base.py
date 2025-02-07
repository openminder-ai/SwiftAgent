from swiftagent.application import SwiftAgent
from swiftagent.application.types import ApplicationType
from swiftagent.core.utilities import hash_url
import websockets

from websockets import ServerConnection as WebSocketServerProtocol
import asyncio
from typing import Callable
import json

from rich.console import Console
from rich.panel import Panel
from rich import box

from swiftagent.styling.defaults import suite_cli_default

from swiftagent.router.base import SwiftRouter
from swiftagent.router.output import RouterOutput
from swiftagent.executor import SwiftExecutor


class SwiftSuite:
    def __init__(
        self,
        name: str = "",
        description: str = "",
        agents: list[SwiftAgent] = [],
    ):

        self.console = Console(theme=suite_cli_default)
        # Just create a live display for dynamic lines
        # self.live = Live("", console=self.console, refresh_per_second=4)
        # self.live.start()

        self.heartbeat_interval = 30

        # Maps a WebSocketServerProtocol to the SwiftAgent instance
        self.agents: dict[WebSocketServerProtocol, SwiftAgent] = {}

        # Maps a message_type string to a callable handler
        self.message_handlers: dict[str, Callable] = {}

        # Agents we want to automatically start
        self.agents_to_be_joined = agents

        # (NEW) Keep track of client websockets (not agent websockets)
        # e.g. external user-facing clients
        self.clients: dict[WebSocketServerProtocol, str] = {}

        # (NEW) Keep track of requests so we know which client to send
        # the final result back to when an agent completes a query
        # key: request_id, value: client_websocket
        self.pending_requests: dict[str, WebSocketServerProtocol] = {}

        # Register default agent-based handlers
        self.register_handler("join", self.handle_join)

        # (NEW) Register new client handlers
        self.register_handler("client_join", self.handle_client_join)
        self.register_handler("client_query", self.handle_client_query)
        self.register_handler(
            "agent_query_response", self.handle_agent_query_response
        )

    ##############################
    # Hosted
    ##############################

    def register_handler(
        self,
        message_type: str,
        handler: Callable,
    ):
        """Register a new message handler."""
        self.message_handlers[message_type] = handler

    async def handle_join(
        self,
        websocket: WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """Handle an 'agent' joining the suite."""
        name = data.get("name", "Anonymous")
        # Find an already constructed SwiftAgent with that name:
        agent_ = [a for a in self.agents_to_be_joined if a.name == name][0]

        ##ADD NEW AGENT HERE

        # Show pending status
        # Show pending status
        # Show pending status
        self.console.print(f"Agent{name}: [ ] Pending", end="\r")

        await asyncio.sleep(0.5)

        # Update to checkmark on same line and add newline at end
        self.console.print(f"Agent {name}: [green][✓] Connected")

        self.agents[websocket] = agent_
        agent_.last_pong = asyncio.get_event_loop().time()

    async def handle_client_join(
        self,
        websocket: WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """
        Handle a 'client_join' message.
        The client is not an agent; it’s a user-facing client that wants
        to send queries to agents and get responses.
        """
        client_name = data.get("client_name", "AnonymousClient")
        self.clients[websocket] = client_name

        self.console.print(f"Client {client_name}: [ ] Pending", end="\r")

        await asyncio.sleep(0.5)

        # Update to checkmark on same line and add newline at end
        self.console.print(f"Client {client_name}: [green][✓] Connected")

    async def handle_client_query(
        self,
        websocket: WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """
        Handle a 'client_query' message from a client that wants to
        query a specific agent by name.
        """
        client_name = self.clients.get(websocket, "UnknownClient")
        agent_name = data.get("agent_name")
        query = data.get("query")
        request_id = data.get("request_id")

        if not agent_name or not query or not request_id:
            # Some basic validation
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": "Missing agent_name, query, or request_id",
                    }
                )
            )
            return

        # Find the agent's websocket by agent_name
        agent_ws = None
        for ws, agent_obj in self.agents.items():
            if agent_obj.name == agent_name:
                agent_ws = ws
                break

        if not agent_ws:
            # No agent with that name
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Agent '{agent_name}' not found",
                    }
                )
            )
            return

        # Store which client made this request
        self.pending_requests[request_id] = websocket

        # Forward the query to the agent (via the agent's websocket)
        await agent_ws.send(
            json.dumps(
                {
                    "type": "agent_query",
                    "request_id": request_id,
                    "query": query,
                }
            )
        )

        self.console.print(
            f"[bright_black][[/bright_black][cyan]{client_name}[/cyan][bright_black] →[/bright_black] "
            f"[green]{agent_name}[/green][bright_black]][/bright_black] "
            f"[white]{query}[/white]"
        )

    async def handle_agent_query_response(
        self,
        websocket: WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """
        Handle 'agent_query_response' from an agent. Then forward
        the response back to the client that initiated the query.
        """
        request_id = data.get("request_id")
        result = data.get("result", "")

        if not request_id or request_id not in self.pending_requests:
            print("Unknown or missing request_id in agent_query_response.")
            return

        # Find the client WebSocket that initiated the query
        client_ws = self.pending_requests.pop(request_id)

        if client_ws in self.clients:
            # Forward the result back to the client
            await client_ws.send(
                json.dumps(
                    {
                        "type": "client_query_response",
                        "request_id": request_id,
                        "result": result,
                    }
                )
            )

            # TODO: better query tracking
            self.console.print(
                f"[bright_black][[/bright_black][green]Agent[/green][bright_black] →[/bright_black] "
                f"[cyan]Client[/cyan][bright_black]][/bright_black] "
                f"[white]{result}[/white]"
            )

    async def handle_disconnect(
        self,
        websocket: WebSocketServerProtocol,
    ) -> None:
        """Handle client/agent disconnection."""
        if websocket in self.agents:
            agent = self.agents[websocket]
            del self.agents[websocket]
            # print(f"Agent {agent.name} disconnected.")
        elif websocket in self.clients:
            client_name = self.clients[websocket]
            del self.clients[websocket]
            # print(f"Client {client_name} disconnected.")

    async def handle_pong(
        self,
        websocket: WebSocketServerProtocol,
    ) -> None:
        """Update last_pong time when pong is received (agent only)."""
        if websocket in self.agents:
            self.agents[websocket].last_pong = asyncio.get_event_loop().time()

    async def heartbeat(
        self,
        websocket: WebSocketServerProtocol,
    ) -> None:
        """Send periodic heartbeats and check for responses (agents only)."""
        while True:
            try:
                await websocket.ping()
                await asyncio.sleep(self.heartbeat_interval)

                if websocket in self.agents:
                    agent = self.agents[websocket]
                    time_since_pong = (
                        asyncio.get_event_loop().time() - agent.last_pong
                    )
                    if time_since_pong > self.heartbeat_interval * 1.5:
                        # print(f"Agent {agent.name} timed out.")
                        await websocket.close(
                            code=1000,
                            reason="Heartbeat timeout",
                        )
                        break

            except websockets.ConnectionClosed:
                break

    async def message_handler(
        self,
        websocket: WebSocketServerProtocol,
        message: str,
    ) -> None:
        """Route messages to appropriate handlers."""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](websocket, data)
            else:
                print(f"Unknown message type: {message_type}")
                await websocket.send(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )

        except json.JSONDecodeError:
            print("Failed to parse message as JSON")
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                    }
                )
            )

    async def connection_handler(
        self,
        websocket: WebSocketServerProtocol,
    ) -> None:
        """Handle new WebSocket connections (both clients and agents)."""
        # Set up pong handler (only relevant for Agents that respond to pings)
        websocket.pong_handler = lambda: asyncio.create_task(
            self.handle_pong(websocket)
        )

        # Start heartbeat for Agents
        heartbeat_task = asyncio.create_task(self.heartbeat(websocket))

        try:
            async for message in websocket:
                await self.message_handler(websocket, message)
        except websockets.ConnectionClosed:
            print("Connection closed.")
        finally:
            heartbeat_task.cancel()
            await self.handle_disconnect(websocket)

    async def broadcast(
        self,
        message: dict,
    ) -> None:
        """Broadcast a message to all connected agent websockets."""
        # You could also broadcast to clients if you choose,
        # but here we only broadcast to Agents
        dead_agents = set()
        for agent in self.agents.values():
            try:
                await agent.suite_connection.send(json.dumps(message))
            except websockets.ConnectionClosed:
                dead_agents.add(agent.suite_connection)

        # Cleanup dead agents
        for dead_ws in dead_agents:
            await self.handle_disconnect(dead_ws)

    async def run(
        self,
        host: str | None = None,
        port: int | None = None,
        mode: ApplicationType = ApplicationType.HOSTED,
        task: str | None = None,
    ):
        if mode == ApplicationType.HOSTED:
            suite_url = f"{host}{port}"
            hashed_suite_url = hash_url(suite_url)

            self.console.rule(
                "[info]SwiftSuite Initialization", style="bright_blue"
            )

            with self.console.status(
                "Initializing SwiftSuite", spinner="dots9", spinner_style="cyan"
            ) as status:
                await websockets.serve(
                    self.connection_handler,
                    host,
                    port,
                )

            self.console.print(
                "[success]✓[/success] SwiftSuite Started Successfully"
            )

            code_panel = Panel(
                f"✨ Suite Address: [code]{hashed_suite_url}[/code]",
                box=box.ROUNDED,
                style="bright_blue",
                padding=(0, 2),
            )
            self.console.print(code_panel)

            # Connection info in subtle styling
            self.console.print(
                f"[optional]Direct WS Connection: ws://{host}:{port}[/optional]"
            )

            self.console.rule("", style="bright_blue")

            # Launch all "to be joined" agents in Hosted mode
            for agent in self.agents_to_be_joined:
                await agent.run(
                    type_=ApplicationType.HOSTED, host=host, port=port
                )

            # Keep the server running
            await asyncio.Future()  # run forever
        elif mode == ApplicationType.STANDARD:
            router = SwiftRouter(agents=[*self.agents_to_be_joined])

            response = await router.route(
                llm="gpt-4o-mini",
                query=task,
            )

            agent_dict = {
                agent.name: agent for agent in self.agents_to_be_joined
            }

            executor = SwiftExecutor(agent_dict)

            _response = await executor.execute_pipeline(response)

            return _response
