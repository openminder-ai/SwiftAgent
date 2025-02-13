import asyncio
from functools import wraps
from typing import Callable, Any, Optional, Type, overload
from swiftagent.actions.set import ActionSet
from swiftagent.application.types import ApplicationType
from swiftagent.actions.base import Action
from swiftagent.memory.long_term import LongTermMemory
from swiftagent.memory.working import WorkingMemory
from swiftagent.reasoning.base import BaseReasoning
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
from swiftagent.core.utilities import hash_url
import websockets

# from websockets.legacy.server import WebSocketServerProtocol
from websockets import ServerConnection as WebSocketServerProtocol
import json
import os

from rich.console import Console
from rich.theme import Theme
from rich.status import Status
from rich.panel import Panel
from rich import box

from swiftagent.reasoning.salient import SalientMemoryReasoning
from swiftagent.styling.defaults import client_cli_default

from swiftagent.memory.semantic import SemanticMemory

from swiftagent.persistence.registry import AgentRegistry


class SwiftAgent:
    def __init__(
        self,
        name: str = "DefaultAgent",
        description: str = "An agent that does stuff",
        instruction: Optional[str] = None,
        reasoning: Type[BaseReasoning] = BaseReasoning,
        enable_salient_memory: bool = False,
        llm_name: str = "gpt-4o",
        verbose: bool = True,  # <-- added flag
        persist_path: Optional[str] = None,
        fresh_install: bool = False,
    ):
        self.name = name
        self.description = description
        self.instruction = instruction

        # Collections to store actions/resources
        self._actions: dict[str, dict[str, Any]] = {}
        self._resources: dict[str, dict[str, Any]] = {}

        self.persist_path = persist_path
        self.fresh_install = fresh_install

        # We track if the agent is fully loaded or not
        self.loaded_from_registry = False

        # self.reasoning = reasoning(name=self.name, instructions=instruction)
        self.llm_name = llm_name

        self._server: Optional[Starlette] = None
        self.last_pong: Optional[float] = None
        self.suite_connection: Optional[WebSocketServerProtocol] = None

        # Agent-wide verbosity toggle
        self.verbose = verbose

        # If verbose, attach a console for Rich printing. Otherwise None.
        self.console = Console(theme=client_cli_default) if verbose else None

        self.semantic_memories: dict[str, SemanticMemory] = {}

        if enable_salient_memory:
            # self.working_memory = WorkingMemory(
            #     max_text_items=10, max_action_items=10
            # )
            # self.long_term_memory = LongTermMemory(name=f"{self.name}_ltm_db")
            # self.working_memory.long_term_memory = self.long_term_memory

            # self.reasoning = SalientMemoryReasoning(
            #     name=self.name,
            #     instructions=self.instruction or "",
            #     working_memory=self.working_memory,
            #     long_term_memory=self.long_term_memory,
            # )
            self.reasoning = SalientMemoryReasoning(
                "test_stm", self.instruction
            )

            self._create_or_replace_working_memory()
            self._create_or_replace_long_term_memory(name=f"{self.name}_ltm_db")

        else:
            # fallback to plain BaseReasoning
            self.working_memory = None
            self.long_term_memory = None
            self.reasoning = BaseReasoning(
                name=self.name, instructions=self.instruction
            )

        if self.persist_path and not self.fresh_install:
            if os.path.exists(self.persist_path):
                AgentRegistry.load_agent_profile(self)
                self.loaded_from_registry = True
                # Now that we've loaded, if "enable_salient_memory" was in the profile,
                # we might already have a working_memory & LTM set up by the loader.
                # If not, they're created above anyway.
            else:
                # no directory yet, that means no existing profile
                pass

        # Done loading if any. The agent is now ready for usage.

    ##############################
    # Persistence / Registry Support
    ##############################
    def save(self) -> None:
        """
        Manually trigger a save of this agent’s profile to disk
        (if self.persist_path is set).
        """
        if not self.persist_path:
            # If user didn't specify persist_path, do nothing
            return
        AgentRegistry.save_agent_profile(self)

    def _print(self, message: str):
        """Helper to safely print only if verbose."""
        if self.verbose and self.console:
            self.console.print(message)

    def _status(self, message: str):
        """
        Context manager that shows a spinner if verbose=True, else does nothing.
        Usage:
            with self._status("Thinking..."):
                # do work
        """
        if self.verbose and self.console:
            return Status(message, spinner="dots", console=self.console)
        else:
            # Return a dummy context manager if not verbose
            class _NoOpCm:
                def __enter__(self_):
                    return self_

                def __exit__(self_, exc_type, exc_val, exc_tb):
                    pass

            return _NoOpCm()

    def _create_or_replace_working_memory(self, max_items=15) -> None:
        """
        Now that we have a single unified memory, we can ignore one of these or combine them.
        Let’s combine them by just summing them up, or default to 20.
        """
        from swiftagent.memory.working import WorkingMemory

        total_max = max_items
        self.working_memory = WorkingMemory(
            max_items=total_max, auto_evict=True
        )

        if self.reasoning and isinstance(
            self.reasoning, SalientMemoryReasoning
        ):
            self.reasoning.working_memory = self.working_memory

    def _create_or_replace_long_term_memory(
        self,
        name: str = "long_term_memory",
        persist_directory: str = "./chroma_ltm",
    ) -> None:
        """
        Internal helper that sets a brand-new LongTermMemory on the agent,
        discarding any older one. (Used by the registry loader.)
        """
        new_ltm = LongTermMemory(name=name, persist_directory=persist_directory)
        self.long_term_memory = new_ltm
        if self.reasoning and isinstance(
            self.reasoning, SalientMemoryReasoning
        ):
            self.reasoning.long_term_memory = self.long_term_memory

    def action(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        params: Optional[dict[str, str]] = None,
        strict: bool = True,
    ):
        """Decorator to register an action with the agent."""

        def decorator(func: Callable):
            action = Action(
                func=func,
                name=name,
                description=description,
                params=params,
                strict=strict,
            )

            self.add_action(name, action)

            return action.wrapped_func

        return decorator

    @overload
    def add_action(self, action: Any) -> None: ...
    @overload
    def add_action(self, name: str, action: Action | Any) -> None: ...
    def add_action(
        self,
        name: str | Any,
        action: Action | Any | None = None,
    ) -> None:
        """Manually add an action to the agent."""
        if action is None:
            action = name
            if hasattr(action, "__action_instance__"):
                action_instance: Action = action.__action_instance__
                self._actions[action_instance.name] = action_instance
                self.reasoning.set_action(action_instance)
                return

        if isinstance(action, Action):
            self._actions[name] = action
            self.reasoning.set_action(action)
        else:
            action_instance = action.__action_instance__
            self._actions[action_instance.name] = action_instance
            self.reasoning.set_action(action_instance)

    def add_actionset(self, actionset: ActionSet) -> None:
        """
        Adds all actions from an ActionSet to this agent.
        """
        for action_instance in actionset.actions:
            self.add_action(action_instance)

    def resource(
        self,
        name: str,
        description: Optional[str] = None,
    ):
        """
        Decorator for resources (you can adapt the logic if you'd like the same
        parameter-introspection approach).
        """

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # For now, just store in self._resources.
            # If you want the same signature-based JSON schema, you can do so.
            resource_metadata = {
                "name": name,
                "description": description or (func.__doc__ or ""),
            }
            self.add_resource(name, wrapper, resource_metadata)
            return wrapper

        return decorator

    def add_resource(
        self,
        name: str,
        func: Callable,
        metadata: dict[str, Any],
    ):
        """
        Register the resource with this agent.
        """
        self._resources[name] = {
            "callable": func,
            "metadata": metadata,
        }

    def add_semantic_memory_section(
        self, semantic_memory_section: SemanticMemory
    ):
        self.semantic_memories[semantic_memory_section.name] = (
            semantic_memory_section
        )
        self.reasoning.add_semantic_memory_section(semantic_memory_section)

        return self

    ##############################
    # Universal Agent Mode
    ##############################

    async def _process(self, query: str):
        return (
            await self.reasoning.flow(
                task=query,
                llm=self.llm_name,
            )
            # )[-2:]
        )[-1]["content"]

    ##############################
    # Persistent Agent Mode
    ##############################

    def _create_server(self):
        """Create Starlette app with single process route"""
        routes = [
            Route(f"/{self.name}", self._process_persistent, methods=["POST"]),
            Route(
                f"/{self.name}/add_memory_store",
                self._add_memory_store,
                methods=["POST"],
            ),
            Route(
                f"/{self.name}/ingest_memory_store",
                self._ingest_memory_store,
                methods=["POST"],
            ),
        ]
        return Starlette(routes=routes)

    async def _process_persistent(self, request: Request):
        """HTTP endpoint that handles process requests"""
        try:
            data: dict[str, str] = await request.json()

            # TODO: better query tracking
            self._print(
                f"[bright_black][[/bright_black][cyan]Client[/cyan][bright_black] →[/bright_black] "
                f"[green]{self.name}[/green][bright_black]][/bright_black] "
                f"[white]{data.get('query')}[/white]"
            )

            with self._status("Agent Thinking..."):
                result = await self._process(data.get("query"))

            # TODO: better query tracking
            self._print(
                f"[bright_black][[/bright_black][green]{self.name}[/green][bright_black] →[/bright_black] "
                f"[cyan]Client[/cyan][bright_black]][/bright_black] "
                f"[white]{result}[/white]"
            )

            return JSONResponse(
                {
                    "status": "success",
                    "result": result,
                }
            )
        except Exception as e:
            return JSONResponse(
                {
                    "status": "error",
                    "message": str(e),
                },
                status_code=500,
            )

    async def _add_memory_store(self, request: Request):
        """
        Create a new semantic memory store by name.
        Expected JSON body: {"store_name": "some_unique_identifier"}
        """
        try:
            data = await request.json()
            store_name = data.get("store_name")
            if not store_name:
                return JSONResponse(
                    {"status": "error", "message": "Missing 'store_name'."},
                    status_code=400,
                )

            # Check if the store already exists
            if store_name in self.semantic_memories:
                return JSONResponse(
                    {
                        "status": "error",
                        "message": f"Store '{store_name}' already exists.",
                    },
                    status_code=400,
                )

            # Create new store and add to this agent's dictionary
            new_memory = SemanticMemory(name=store_name)
            self.add_semantic_memory_section(new_memory)

            return JSONResponse(
                {
                    "status": "success",
                    "message": f"Semantic memory store '{store_name}' created.",
                }
            )

        except Exception as e:
            return JSONResponse(
                {"status": "error", "message": str(e)}, status_code=500
            )

    async def _ingest_memory_store(self, request: Request):
        """
        Ingest content into an existing semantic memory store by name.
        Expected JSON body: {"store_name": "some_unique_identifier", "content": "some text to store"}
        """
        try:
            data = await request.json()
            store_name = data.get("store_name")
            content = data.get("content")

            if not store_name or not content:
                return JSONResponse(
                    {
                        "status": "error",
                        "message": "Missing 'store_name' or 'content'.",
                    },
                    status_code=400,
                )

            if store_name not in self.semantic_memories:
                return JSONResponse(
                    {
                        "status": "error",
                        "message": f"Store '{store_name}' does not exist. Create it first.",
                    },
                    status_code=400,
                )

            # Ingest the content into the requested memory store
            self.semantic_memories[store_name].ingest(content)

            return JSONResponse(
                {
                    "status": "success",
                    "message": f"Content ingested into store '{store_name}'.",
                }
            )

        except Exception as e:
            return JSONResponse(
                {"status": "error", "message": str(e)}, status_code=500
            )

    ##############################
    # Hosted Agent Mode
    ##############################

    async def _connect_hosted(
        self, host: str | None = None, port: int | None = None
    ):
        while True:
            try:
                async with websockets.connect(
                    f"ws://{host}:{port}"
                ) as suite_connection:
                    self.suite_connection = suite_connection
                    self.connected = True

                    await self.send_message(
                        "join",
                        name=self.name,
                    )

                    # Main message loop
                    async for message in suite_connection:
                        await self._process_hosted(message)

            except websockets.ConnectionClosed:
                print("Connection lost, attempting to reconnect...")
                self.connected = False
                await asyncio.sleep(5)  # Wait before reconnecting
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

    async def _process_hosted(self, raw_message: str):
        """
        Called whenever the SwiftSuite sends us a JSON string.
        We parse it and decide what to do.
        """
        try:
            data = json.loads(raw_message)
            message_type = data.get("type")

            # Handle an incoming "agent_query"
            if message_type == "agent_query":
                request_id = data.get("request_id")
                query = data.get("query", "")

                # Run your normal reasoning logic
                result_list = await self._process(
                    query
                )  # result is typically a list or string
                # Let's just use the final item as a string result
                # or join them if it's multiple
                if isinstance(result_list, list):
                    result_str = "\n".join(str(r) for r in result_list)
                else:
                    result_str = str(result_list)

                # Send back the response so SwiftSuite can forward to the client
                if request_id:
                    await self.send_message(
                        "agent_query_response",
                        request_id=request_id,
                        result=result_str,
                    )

            else:
                # Handle any other incoming message types if needed
                print(
                    f"{self.name} got an unknown message type: {message_type}"
                )
                print(data)
        except json.JSONDecodeError:
            print("Failed to decode incoming message as JSON")

    async def send_message(self, message_type: str, **data) -> None:
        """Send a message to the server"""
        # if self.websocket and self.connected:
        if self.suite_connection:
            try:
                message = {
                    "type": message_type,
                    **data,
                }
                await self.suite_connection.send(json.dumps(message))
            except websockets.ConnectionClosed:
                self.connected = False
                print("Connection lost while sending message")

    ##############################
    # Run Agent
    ##############################

    async def run(
        self,
        type_: ApplicationType = ApplicationType.STANDARD,
        host: str | None = None,
        port: int | None = None,
        task: str | None = None,
    ):
        """
        Run the SwiftAgent in either server or public mode.

        Args:
            mode: Either 'server' (local HTTP server) or 'public' (websocket client)
            **kwargs: Additional arguments
                For server mode:
                    - host: Server host (default: "0.0.0.0")
                    - port: Server port (default: 8000)
                For public mode:
                    - websocket_uri: URI of the websocket server
        """
        if type_ == ApplicationType.STANDARD:
            # Show query being sent
            self._print(
                Panel(
                    f"[info]Query:[/info] {task}",
                    title=f"[ws]→ Sending to {self.name}[/ws]",
                    box=box.ROUNDED,
                    border_style="blue",
                )
            )

            # Show thinking animation while waiting
            # with Status("[ws]Agent thinking...[/ws]", spinner="dots") as status:
            # result = await self._process(query=task)

            with self._status("Thinking..."):
                result = await self._process(query=task)

            self._print(
                Panel(
                    result,
                    title="[success]← Response Received[/success]",
                    border_style="green",
                    box=box.HEAVY,
                )
            )

            if self.persist_path:
                print("saving")
                self.save()

            return result
        elif type_ == ApplicationType.PERSISTENT:
            # Create app if not exists
            if not self._server:
                self._server = self._create_server()

            # Get server settings
            host = "0.0.0.0"
            port = port or 8001

            # Run server with uvicorn
            config = uvicorn.Config(
                self._server,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                log_config=None,  # This prevents uvicorn from using its default logging config
            )

            server = uvicorn.Server(config)

            await server.serve()
        elif type_ == ApplicationType.HOSTED:
            connection_task = asyncio.create_task(
                self._connect_hosted(host, port)
            )

            try:
                while True:
                    await asyncio.sleep(1)
            except:
                connection_task.cancel()
        else:
            raise ValueError(f"Unknown mode: {type_}")
