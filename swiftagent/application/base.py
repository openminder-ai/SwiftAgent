from functools import wraps

from typing import Callable, Any, Optional, Type

from swiftagent.application.types import ApplicationType

from swiftagent.actions.base import Action

from swiftagent.reasoning.base import BaseReasoning

from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

import uvicorn

import logging
from logging.handlers import RotatingFileHandler


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
        self._actions: dict[str, dict[str, Any]] = {}
        self._resources: dict[str, dict[str, Any]] = {}

        self.reasoning = reasoning(name=self.name)
        self.llm_name = llm_name

        self._server: Optional[Starlette] = None

        self.setup_logging()

    def setup_logging(self, log_file="agent.log"):
        self.file_handler = RotatingFileHandler(
            log_file, maxBytes=1024 * 1024, backupCount=5  # 1MB  # Keep 5 backup files
        )

        self.file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        # Run server with uvicorn
        self.logger = logging.getLogger("persistent_agent")
        self.logger.handlers.clear()  # Remove existing handlers
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)  # Set desired log level

    def _create_server(self):
        """Create Starlette app with single process route"""
        routes = [Route(f"/{self.name}", self._process_persistent, methods=["POST"])]
        return Starlette(routes=routes)

    def action(
        self,
        name: str,
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

    def add_action(self, name: str, action: Action):
        """Manually add an action to the agent."""
        self._actions[name] = action
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

    def add_resource(self, name: str, func: Callable, metadata: dict[str, Any]):
        """
        Register the resource with this agent.
        """
        self._resources[name] = {
            "callable": func,
            "metadata": metadata,
        }

    async def _process(self, query: str):
        return (await self.reasoning.flow(task=query, llm=self.llm_name))[-2:]

    async def _process_persistent(self, request: Request):
        """HTTP endpoint that handles process requests"""
        try:
            data: dict[str, str] = await request.json()
            result = await self._process(data.get("query"))
            return JSONResponse({"status": "success", "result": result})
        except Exception as e:
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    async def run(
        self,
        type_: ApplicationType = ApplicationType.STANDARD,
        port: int | None = None,
        task: str | None = None,
    ):
        """
        Run the FastAgent in either server or public mode.

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
        if type_ == ApplicationType.PERSISTENT:
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
        else:
            raise ValueError(f"Unknown mode: {type_}")
