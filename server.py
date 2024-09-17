import asyncio
import websockets
import csv
import time

async def send_csv(websocket, path):
    try:
        # Open the CSV file
        with open('./files/task4_dats_neurometric_07_05_2024.csv', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            
            for row in csv_reader:
                message = ','.join(row)  # Join row values with a comma
                await websocket.send(message)  # Send message to the client
                print(f"Sent: {message}")
                await asyncio.sleep(0.2)  # Wait 0.2 seconds between messages
    except Exception as e:
        print(f"Error: {e}")

async def main():
    async with websockets.serve(send_csv, "localhost", 9000):
        print("WebSocket server running on ws://localhost:9000")
        await asyncio.Future()  # Run forever

# Start the server
asyncio.run(main())