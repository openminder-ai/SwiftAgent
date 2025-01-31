import asyncio
import json
import websockets
import logging
from typing import (
    Dict,
    Callable,
    Any,
)
from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Client:
    websocket: websockets.WebSocketServerProtocol
    name: str
    last_pong: float


class WebSocketServer:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
    ):
        self.host = host
        self.port = port
        self.clients: Dict[
            websockets.WebSocketServerProtocol,
            Client,
        ] = {}
        self.message_handlers: Dict[
            str,
            Callable,
        ] = {}
        self.heartbeat_interval = 30

        # Register default message handlers
        self.register_handler(
            "join",
            self.handle_join,
        )
        self.register_handler(
            "chat",
            self.handle_chat,
        )
        self.register_handler(
            "status",
            self.handle_status,
        )

    def register_handler(
        self,
        message_type: str,
        handler: Callable,
    ):
        """Register a new message handler"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def handle_join(
        self,
        websocket: websockets.WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """Handle join messages"""
        name = data.get(
            "name",
            "Anonymous",
        )
        self.clients[websocket] = Client(
            websocket=websocket,
            name=name,
            last_pong=asyncio.get_event_loop().time(),
        )
        await self.broadcast(
            {
                "type": "system",
                "message": f"{name} joined the server",
                "timestamp": datetime.now().isoformat(),
            }
        )
        logger.info(f"Client {name} joined")

    async def handle_chat(
        self,
        websocket: websockets.WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """Handle chat messages"""
        if websocket in self.clients:
            client = self.clients[websocket]
            await self.broadcast(
                {
                    "type": "chat",
                    "sender": client.name,
                    "message": data.get(
                        "message",
                        "",
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    async def handle_status(
        self,
        websocket: websockets.WebSocketServerProtocol,
        data: dict,
    ) -> None:
        """Handle status requests"""
        if websocket in self.clients:
            await websocket.send(
                json.dumps(
                    {
                        "type": "status",
                        "clients": len(self.clients),
                        "uptime": "server_uptime",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

    async def broadcast(
        self,
        message: dict,
    ) -> None:
        """Broadcast a message to all connected clients"""
        dead_clients = set()
        for client in self.clients.values():
            try:
                await client.websocket.send(json.dumps(message))
            except websockets.ConnectionClosed:
                dead_clients.add(client.websocket)

        # Cleanup dead clients
        for websocket in dead_clients:
            await self.handle_disconnect(websocket)

    async def handle_disconnect(
        self,
        websocket: websockets.WebSocketServerProtocol,
    ) -> None:
        """Handle client disconnection"""
        if websocket in self.clients:
            client = self.clients[websocket]
            del self.clients[websocket]
            await self.broadcast(
                {
                    "type": "system",
                    "message": f"{client.name} left the server",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Client {client.name} disconnected")

    async def heartbeat(
        self,
        websocket: websockets.WebSocketServerProtocol,
    ) -> None:
        """Send periodic heartbeats and check for responses"""
        while True:
            try:
                await websocket.ping()
                await asyncio.sleep(self.heartbeat_interval)

                if websocket in self.clients:
                    client = self.clients[websocket]
                    time_since_pong = asyncio.get_event_loop().time() - client.last_pong

                    if time_since_pong > self.heartbeat_interval * 1.5:
                        logger.warning(f"Client {client.name} timed out")
                        await websocket.close(
                            code=1000,
                            reason="Heartbeat timeout",
                        )
                        break

            except websockets.ConnectionClosed:
                break

    async def handle_pong(
        self,
        websocket: websockets.WebSocketServerProtocol,
    ) -> None:
        """Update last_pong time when pong is received"""
        if websocket in self.clients:
            self.clients[websocket].last_pong = asyncio.get_event_loop().time()

    async def message_handler(
        self,
        websocket: websockets.WebSocketServerProtocol,
        message: str,
    ) -> None:
        """Route messages to appropriate handlers"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](
                    websocket,
                    data,
                )
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await websocket.send(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )

        except json.JSONDecodeError:
            logger.error("Failed to parse message as JSON")
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
        websocket: websockets.WebSocketServerProtocol,
    ) -> None:
        """Handle new client connections"""
        # Set up pong handler
        websocket.pong_handler = lambda: asyncio.create_task(self.handle_pong(websocket))

        # Start heartbeat
        heartbeat_task = asyncio.create_task(self.heartbeat(websocket))

        try:
            async for message in websocket:
                await self.message_handler(
                    websocket,
                    message,
                )
        except websockets.ConnectionClosed:
            logger.info("Connection closed")
        finally:
            heartbeat_task.cancel()
            await self.handle_disconnect(websocket)

    async def start(
        self,
    ) -> None:
        """Start the WebSocket server"""
        async with websockets.serve(
            self.connection_handler,
            self.host,
            self.port,
        ):
            logger.info(f"Server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever


# Example usage
async def main():
    server = WebSocketServer()

    # Register a custom message handler
    async def handle_custom(
        websocket,
        data,
    ):
        if websocket in server.clients:
            await websocket.send(
                json.dumps(
                    {
                        "type": "custom_response",
                        "data": "Processed custom message",
                    }
                )
            )

    server.register_handler(
        "custom",
        handle_custom,
    )
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
