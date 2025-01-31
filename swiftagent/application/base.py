import asyncio
from functools import (
    wraps,
)

from typing import Callable, Any, Optional, Type, overload

from swiftagent.application.types import (
    ApplicationType,
)

from swiftagent.actions.base import (
    Action,
)

from swiftagent.reasoning.base import (
    BaseReasoning,
)

from starlette.requests import (
    Request,
)
from starlette.applications import (
    Starlette,
)
from starlette.responses import (
    JSONResponse,
)
from starlette.routing import (
    Route,
)

import uvicorn

import logging
from logging.handlers import (
    RotatingFileHandler,
)

from swiftagent.core.utilities import (
    hash_url,
)

import websockets

from websockets.legacy.server import (
    WebSocketServerProtocol,
)

import json


class SwiftAgent:
    def __init__(
        self,
        name: str = "DefaultAgent",
        description: str = "An agent that does stuff",
        reasoning: Type[BaseReasoning] = BaseReasoning,
        llm_name: str = "gpt-4o-mini",
    ):
        self.name = name
        self.description = description

        # Collections to store actions/resources
        self._actions: dict[
            str,
            dict[
                str,
                Any,
            ],
        ] = {}

        self._resources: dict[
            str,
            dict[
                str,
                Any,
            ],
        ] = {}

        self.reasoning = reasoning(name=self.name)
        self.llm_name = llm_name

        self._server: Optional[Starlette] = None
        self.last_pong: Optional[float] = None
        self.websocket: Optional[WebSocketServerProtocol] = None

        self.setup_logging()

    def setup_logging(
        self,
        log_file="agent.log",
    ):
        self.file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,
            backupCount=5,  # 1MB  # Keep 5 backup files
        )

        self.file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

        # Run server with uvicorn
        self.logger = logging.getLogger("persistent_agent")
        self.logger.handlers.clear()  # Remove existing handlers
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)  # Set desired log level

    def _create_server(
        self,
    ):
        """Create Starlette app with single process route"""
        routes = [
            Route(
                f"/{self.name}",
                self._process_persistent,
                methods=["POST"],
            )
        ]
        return Starlette(routes=routes)

    def action(
        self,
        name: str,
        description: Optional[str] = None,
        params: Optional[
            dict[
                str,
                str,
            ]
        ] = None,
        strict: bool = True,
    ):
        """Decorator to register an action with the agent."""

        def decorator(
            func: Callable,
        ):
            action = Action(
                func=func,
                name=name,
                description=description,
                params=params,
                strict=strict,
            )

            self.add_action(
                name,
                action,
            )

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
                action_instance = action.__action_instance__
                self._actions[action_instance.name] = action_instance
                self.reasoning.set_action(action)
                return

        if isinstance(action, Action):
            self._actions[name] = action
            self.reasoning.set_action(action)
        else:
            action_instance = action.__action_instance__
            self._actions[action_instance.name] = action_instance
            self.reasoning.set_action(action)

    def resource(
        self,
        name: str,
        description: Optional[str] = None,
    ):
        """
        Decorator for resources (you can adapt the logic if you'd like the same
        parameter-introspection approach).
        """

        def decorator(
            func: Callable,
        ):
            @wraps(func)
            def wrapper(
                *args,
                **kwargs,
            ):
                return func(
                    *args,
                    **kwargs,
                )

            # For now, just store in self._resources.
            # If you want the same signature-based JSON schema, you can do so.
            resource_metadata = {
                "name": name,
                "description": description or (func.__doc__ or ""),
            }
            self.add_resource(
                name,
                wrapper,
                resource_metadata,
            )
            return wrapper

        return decorator

    def add_resource(
        self,
        name: str,
        func: Callable,
        metadata: dict[
            str,
            Any,
        ],
    ):
        """
        Register the resource with this agent.
        """
        self._resources[name] = {
            "callable": func,
            "metadata": metadata,
        }

    async def _process(
        self,
        query: str,
    ):
        return (
            await self.reasoning.flow(
                task=query,
                llm=self.llm_name,
            )
        )[-2:]

    async def _process_persistent(
        self,
        request: Request,
    ):
        """HTTP endpoint that handles process requests"""
        try:
            data: dict[
                str,
                str,
            ] = await request.json()
            result = await self._process(data.get("query"))
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

    async def _connect_hosted(
        self, host: str | None = None, port: int | None = None
    ):
        while True:
            try:
                async with websockets.connect(
                    f"ws://{host}:{port}"
                ) as websocket:
                    self.websocket = websocket
                    self.connected = True
                    print(f"Connected to ws://{host}:{port}")

                    await self.send_message(
                        "join",
                        name=self.name,
                    )

                    # Main message loop
                    async for message in websocket:
                        await self._process_hosted(message)

            except websockets.ConnectionClosed:
                print("Connection lost, attempting to reconnect...")
                self.connected = False
                await asyncio.sleep(5)  # Wait before reconnecting
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

    async def send_message(
        self,
        message_type: str,
        **data,
    ) -> None:
        """Send a message to the server"""
        # if self.websocket and self.connected:
        print(self.websocket, "heree")
        if self.websocket:
            try:
                message = {
                    "type": message_type,
                    **data,
                }
                await self.websocket.send(json.dumps(message))
            except websockets.ConnectionClosed:
                self.connected = False
                print("Connection lost while sending message")

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
            return await self._process(query=task)
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
