import websockets.legacy
import websockets.legacy.server
from swiftagent.application import SwiftAgent

from swiftagent.core.utilities import hash_url, unhash_url

import websockets
from websockets.legacy.server import WebSocketServerProtocol

import asyncio

from datetime import datetime

from typing import Callable

import json


class SwiftSuite:
    def __init__(
        self,
        name: str = "",
        description: str = "",
        agents: list[SwiftAgent] = [],
    ):

        self.heartbeat_interval = 30

        self.agents: dict[WebSocketServerProtocol, SwiftAgent] = {}

    async def heartbeat(
        self, websocket: WebSocketServerProtocol
    ) -> None:
        """Send periodic heartbeats and check for responses"""
        while True:
            try:
                await websocket.ping()
                await asyncio.sleep(self.heartbeat_interval)

                if websocket in self.agents:
                    agent = self.agents[websocket]
                    time_since_pong = (
                        asyncio.get_event_loop().time()
                        - agent.last_pong
                    )

                    if (
                        time_since_pong
                        > self.heartbeat_interval * 1.5
                    ):
                        print(f"Client {agent.name} timed out")
                        await websocket.close(
                            code=1000, reason="Heartbeat timeout"
                        )
                        break

            except websockets.ConnectionClosed:
                break

    async def handle_disconnect(
        self, websocket: WebSocketServerProtocol
    ) -> None:
        """Handle client disconnection"""
        if websocket in self.agents:
            agent = self.agents[websocket]
            del self.agents[websocket]
            await self.broadcast(
                {
                    "type": "system",
                    "message": f"{agent.name} left the server",
                    "timestamp": datetime.now().isoformat(),
                }
            )
            print(f"Client {agent.name} disconnected")

    async def handle_pong(
        self, websocket: WebSocketServerProtocol
    ) -> None:
        """Update last_pong time when pong is received"""
        if websocket in self.agents:
            self.agents[websocket].last_pong = (
                asyncio.get_event_loop().time()
            )

    async def message_handler(
        self, websocket: WebSocketServerProtocol, message: str
    ):
        pass

    async def connection_handler(
        self, websocket: WebSocketServerProtocol
    ) -> None:
        """Handle new agent connections"""
        # Set up pong handler
        websocket.pong_handler = lambda: asyncio.create_task(
            self.handle_pong(websocket)
        )

        # Start heartbeat
        heartbeat_task = asyncio.create_task(
            self.heartbeat(websocket)
        )

        try:
            async for message in websocket:
                await self.message_handler(websocket, message)
        except websockets.ConnectionClosed:
            print("Connection closed")
        finally:
            heartbeat_task.cancel()
            await self.handle_disconnect(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients"""
        dead_agents = set()
        for agent in self.agents.values():
            try:
                await agent.websocket.send(json.dumps(message))
            except websockets.ConnectionClosed:
                dead_agents.add(agent.websocket)

        # Cleanup dead agents
        for websocket in dead_agents:
            await self.handle_disconnect(websocket)

    async def setup(
        self,
        host: str | None = None,
        port: int | None = None,
    ):
        suite_url = host + port

        self.host = host
        self.port = port

        hashed_suite_url = hash_url(suite_url)

        async with websockets.serve(
            self.connection_handler, self.host, self.port
        ):
            print(f"Server started on ws://{self.host}:{self.port}")
            print(f"Hashed URL: {hashed_suite_url}")
            await asyncio.Future()  # run forever
