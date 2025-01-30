import asyncio
import json
import websockets
import logging
from typing import Dict, Callable, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketClient:
    def __init__(self, uri: str, name: str):
        self.uri = uri
        self.name = name
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        
        # Register default message handlers
        self.register_handler("chat", self.handle_chat)
        self.register_handler("system", self.handle_system)
        self.register_handler("status", self.handle_status)
        self.register_handler("error", self.handle_error)

    def register_handler(self, message_type: str, handler: Callable):
        """Register a new message handler"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def handle_chat(self, data: dict) -> None:
        """Handle chat messages"""
        sender = data.get("sender", "Unknown")
        message = data.get("message", "")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        print(f"[{timestamp}] {sender}: {message}")

    async def handle_system(self, data: dict) -> None:
        """Handle system messages"""
        message = data.get("message", "")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        print(f"[{timestamp}] SYSTEM: {message}")

    async def handle_status(self, data: dict) -> None:
        """Handle status updates"""
        clients = data.get("clients", 0)
        uptime = data.get("uptime", "unknown")
        print(f"Server Status - Clients: {clients}, Uptime: {uptime}")

    async def handle_error(self, data: dict) -> None:
        """Handle error messages"""
        message = data.get("message", "Unknown error")
        logger.error(f"Server error: {message}")

    async def send_message(self, message_type: str, **data) -> None:
        """Send a message to the server"""
        if self.websocket and self.connected:
            try:
                message = {
                    "type": message_type,
                    **data
                }
                await self.websocket.send(json.dumps(message))
            except websockets.ConnectionClosed:
                self.connected = False
                logger.warning("Connection lost while sending message")

    async def handle_message(self, message: str) -> None:
        """Route incoming messages to appropriate handlers"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error("Failed to parse message as JSON")

    async def connect(self) -> None:
        """Connect to the WebSocket server with automatic reconnection"""
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    self.websocket = websocket
                    self.connected = True
                    logger.info(f"Connected to {self.uri}")

                    # Send join message
                    await self.send_message("join", name=self.name)

                    # Main message loop
                    async for message in websocket:
                        await self.handle_message(message)

            except websockets.ConnectionClosed:
                logger.warning("Connection lost, attempting to reconnect...")
                self.connected = False
                await asyncio.sleep(5)  # Wait before reconnecting
            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(5)

    async def start(self):
        """Start the client"""
        # Start the connection handler
        connection_task = asyncio.create_task(self.connect())

        # Start command line interface
        while True:
            try:
                # Get input from the user
                message = await asyncio.get_event_loop().run_in_executor(
                    None, input, ""
                )

                # Process commands
                if message.startswith("/"):
                    command = message[1:].lower()
                    if command == "quit":
                        break
                    elif command == "status":
                        await self.send_message("status")
                    elif command.startswith("name "):
                        new_name = command[5:].strip()
                        self.name = new_name
                        await self.send_message("join", name=new_name)
                    elif command == "help":
                        print("Available commands:")
                        print("/quit - Exit the client")
                        print("/status - Get server status")
                        print("/name <new_name> - Change your name")
                        print("/help - Show this help message")
                else:
                    # Send chat message
                    if message.strip():
                        await self.send_message("chat", message=message)

            except KeyboardInterrupt:
                break

        # Cleanup
        connection_task.cancel()

# Example usage
async def main():
    client = WebSocketClient("ws://localhost:8765", "TestUser2")
    
    # Register a custom message handler
    async def handle_custom_response(data):
        print(f"Received custom response: {data.get('data')}")
    
    client.register_handler("custom_response", handle_custom_response)
    
    # Start the client
    await client.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient shutdown")