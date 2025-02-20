from swiftagent.application import SwiftAgent
from swiftagent.application.types import RuntimeType
from swiftagent.core.utilities import hash_url
import websockets

from websockets import ServerConnection as WebSocketServerProtocol
import asyncio
from typing import Any, Callable, Union
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
        self.heartbeat_interval = 30

        # Agents that connect
        self.agents: dict[WebSocketServerProtocol, SwiftAgent] = {}

        # Clients that connect
        self.clients: dict[WebSocketServerProtocol, str] = {}

        # Maps a message_type string to a callable handler
        self.message_handlers: dict[str, Callable] = {}

        # Normal "top-level" pending requests for single-agent queries:
        self.pending_requests: dict[str, WebSocketServerProtocol] = {}

        # NEW: For multi-agent subrequests inside the pipeline:
        self.pending_subrequests: dict[str, dict] = {}

        # So we can create futures:
        self.loop = asyncio.get_event_loop()

        # Agents we want to automatically start
        self.agents_to_be_joined = agents

        # Register message handlers
        self.register_handler("join", self.handle_join)
        self.register_handler("client_join", self.handle_client_join)
        self.register_handler("client_query", self.handle_client_query)
        self.register_handler(
            "agent_query_response", self.handle_agent_query_response
        )

        # NEW:
        self.register_handler(
            "client_multi_agent_query", self.handle_client_multi_agent_query
        )

    ##############################
    # Hosted
    ##############################

    async def handle_client_multi_agent_query(
        self,
        websocket: WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """
        Handle a multi-agent pipeline query from a client.
        We'll parse the user query, run the SwiftRouter, then
        orchestrate all tasks/tiers among the connected agents.
        """
        client_name = self.clients.get(websocket, "UnknownClient")
        query = data.get("query")
        request_id = data.get("request_id")
        return_all = data.get("return_all", False)

        if not query or not request_id:
            await websocket.send(
                json.dumps(
                    {
                        "type": "error",
                        "message": "Missing 'query' or 'request_id' in client_multi_agent_query",
                    }
                )
            )
            return

        # 1) Use the SwiftRouter to get a pipeline (like standard mode)
        from swiftagent.router.base import SwiftRouter

        router = SwiftRouter(
            agents=[*self.agents.values()]
        )  # pass actual agent objects

        router_output = await router.route(query=query, llm="gpt-4o-mini")
        # router_output is a RouterOutput

        # 2) Now run that pipeline with our new method
        await self.execute_pipeline_ws(
            pipeline=router_output,
            request_id=request_id,
            client_ws=websocket,
            return_all=return_all,
        )

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
        Handle 'agent_query_response' from an agent.
        We now check if it's a top-level single-agent request or a pipeline subrequest.
        """
        req_id = data.get("request_id")
        result = data.get("result", "")

        if not req_id:
            return  # can't do anything without an ID

        # Case 1: check if it's a subrequest
        if req_id in self.pending_subrequests:
            info = self.pending_subrequests.pop(req_id)
            fut = info["future"]
            unique_id = info["task_unique_id"]

            # We'll set the future's result as a dict with "unique_id" + "output"
            fut.set_result({"unique_id": unique_id, "output": result})

            # You could also do logging, printing, etc.:
            agent = self.agents.get(websocket)
            agent_name = agent.name if agent else "UnknownAgent"
            self.console.print(
                f"[bright_black][[/bright_black][green]{agent_name}[/green][bright_black] → SUBREQUEST[/bright_black]] "
                f"[white]{result}[/white]"
            )
            return

        # Case 2: top-level single-agent request
        if req_id in self.pending_requests:
            client_ws = self.pending_requests.pop(req_id)
            # Forward the result to the client
            await client_ws.send(
                json.dumps(
                    {
                        "type": "client_query_response",
                        "request_id": req_id,
                        "result": result,
                    }
                )
            )

            # Logging
            agent = self.agents.get(websocket)
            agent_name = agent.name if agent else "UnknownAgent"
            self.console.print(
                f"[bright_black][[/bright_black][green]{agent_name}[/green][bright_black] →[/bright_black] "
                f"[cyan]Client[/cyan][bright_black]][/bright_black] "
                f"[white]{result}[/white]"
            )
            return

        # If we get here, we have an unknown request ID
        # Possibly we just ignore or log an error:
        self.console.print(
            f"[error]Unknown request_id {req_id} in agent_query_response[/error]"
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

    async def execute_pipeline_ws(
        self,
        pipeline: RouterOutput,
        request_id: str,
        client_ws: Any,
        return_all: bool = False,
    ):
        """
        Execute a multi-tier pipeline via websockets.

        Args:
            pipeline: The RouterOutput (tiers) from SwiftRouter.
            request_id: The unique request_id for the overall query.
            client_ws: The websocket of the client that initiated the query.
        """
        # We'll store each task's output in a dictionary keyed by that task's unique_id.
        # Similar to SwiftExecutor.outputs
        all_task_outputs = {}

        # Sort tiers by integer key, then run each tier's tasks
        for tier_id in sorted(pipeline.tiers.keys()):
            tier = pipeline.tiers[tier_id]
            tasks = tier.tasks

            # We'll run tasks in this tier concurrently
            # by making sub-requests to each relevant agent.
            subtask_futures = []

            for task in tasks:
                # Gather any needed inputs from the tasks that this one depends on
                dependency_outputs = []
                if task.accepts_inputs_from:
                    for dep_id in task.accepts_inputs_from:
                        dep_output = all_task_outputs.get(dep_id, "")
                        dependency_outputs.append(dep_output)

                # Build final instruction to send to the agent
                # For convenience, we append the dependency text to the end
                final_instruction = task.instruction
                if dependency_outputs:
                    final_instruction += "\n".join(
                        ["\n---\n"] + dependency_outputs
                    )

                # We create a sub-request ID for this particular agent call
                import uuid

                subrequest_id = (
                    f"{request_id}--{task.unique_id}--{uuid.uuid4().hex}"
                )

                # We'll store an asyncio.Future so that when the agent responds,
                # we can set the result. We'll keep it in a dictionary
                fut = self.loop.create_future()
                self.pending_subrequests[subrequest_id] = {
                    "future": fut,
                    "task_unique_id": task.unique_id,
                }

                # Find the relevant agent's websocket
                agent_ws = None
                for ws, agent_obj in self.agents.items():
                    if agent_obj.name == task.agent:
                        agent_ws = ws
                        break

                if not agent_ws:
                    # If we don't find the agent, we fail immediately
                    await client_ws.send(
                        json.dumps(
                            {
                                "type": "error",
                                "message": f"Agent '{task.agent}' not available",
                            }
                        )
                    )
                    # You might want to raise or just skip
                    continue

                # Send the agent_query
                await agent_ws.send(
                    json.dumps(
                        {
                            "type": "agent_query",
                            "request_id": subrequest_id,
                            "query": final_instruction,
                        }
                    )
                )

                subtask_futures.append(fut)

            # Wait for all tasks in this tier to complete
            tier_results = await asyncio.gather(*subtask_futures)

            # Store each result in all_task_outputs
            for res in tier_results:
                if res["unique_id"] and res["output"] is not None:
                    all_task_outputs[res["unique_id"]] = res["output"]

        # After all tiers are complete, you decide how to combine final results:
        # Option A: Suppose the last tier has a single aggregator => return that output
        # Option B: Return everything. For demonstration, we just pass them all back
        # Overwrite - Now doing Option A :)
        # final_output = {}
        # for k, v in all_task_outputs.items():
        #     final_output[k] = v

        if return_all:
            # Return everything from all tiers
            final_output = all_task_outputs
        else:
            # Return *only* the final tier’s results
            last_tier_id = max(pipeline.tiers.keys())
            final_tier = pipeline.tiers[last_tier_id]

            final_result_dict = {}
            for t in final_tier.tasks:
                final_result_dict[t.unique_id] = all_task_outputs.get(
                    t.unique_id, ""
                )

            if len(final_result_dict) == 1:
                # only one final task => return the string
                final_output = list(final_result_dict.values())[0]
            else:
                # multiple final tasks => return dict of them
                final_output = final_result_dict

        # Send a single response back to the client
        await client_ws.send(
            json.dumps(
                {
                    "type": "client_multi_agent_query_response",
                    "request_id": request_id,
                    "result": final_output,
                }
            )
        )

    async def run(
        self,
        task: str | None = None,
        host: str | None = None,
        port: int | None = None,
        runtime: Union[RuntimeType, str] = RuntimeType.STANDARD,
        return_all: bool = False,
    ):
        if isinstance(runtime, str):
            try:
                runtime = RuntimeType[runtime.upper()]
            except KeyError:
                raise ValueError(f"Invalid runtime value: {runtime}")

        if runtime == RuntimeType.HOSTED:
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
                asyncio.create_task(
                    agent.run(type_=RuntimeType.HOSTED, host=host, port=port)
                )

            # Keep the server running
            await asyncio.Future()  # run forever
        elif runtime == RuntimeType.STANDARD:
            router = SwiftRouter(agents=[*self.agents_to_be_joined])

            response = await router.route(
                llm="gpt-4o-mini",
                query=task,
            )

            agent_dict = {
                agent.name: agent for agent in self.agents_to_be_joined
            }

            executor = SwiftExecutor(agent_dict)

            _response = await executor.execute_pipeline(
                response, return_all=return_all
            )

            return _response
