import asyncio
import websockets

async def listen():
    uri = "ws://localhost:9000"  # Connect to the server
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.get_event_loop().run_until_complete(listen())
