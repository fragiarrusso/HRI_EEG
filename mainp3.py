import time
import socket
import subprocess
import json
from threading import Thread

# Define states
INITIAL_STATE = "INITIAL_STATE"
PRESENTATION = "PRESENTATION"
PLAYING_TABLET = "PLAYING_TABLET"
DOING_EXERCISES = "DOING_EXERCISES"

# List of states
states = [INITIAL_STATE, PRESENTATION, PLAYING_TABLET, DOING_EXERCISES]
current_state = INITIAL_STATE

# Globals for cleanup
node_process = None
server_socket = None

# Start the Node.js server
def start_node_server():
    global node_process
    try:
        node_process = subprocess.Popen(["node", "./server.js"], shell=False)
        print("Node.js server started")
    except Exception as e:
        print(f"Error starting Node.js server: {e}")

# TCP server to communicate with Node.js client
def start_tcp_server():
    global current_state, server_socket
    HOST = 'localhost'
    PORT = 9001

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Python server listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print("Connected by", addr)
            handle_client(client_socket)

    except KeyboardInterrupt:
        print("Shutting down the Python server...")
    finally:
        if server_socket:
            server_socket.close()
            print("Python server socket closed")

def handle_client(client_socket):
    global current_state

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            try:
                message = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                print(f"Invalid data received: {data}")
                continue

            print(f"Received message: {message}")

            if message.get("type") == "say":
                current_state = PLAYING_TABLET
            elif message.get("type") == "exercise":
                current_state = DOING_EXERCISES

            print(f"Transitioned to state: {current_state}")

            response = json.dumps({"message": "State updated successfully"})
            client_socket.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()
        print("Client disconnected")

# Gracefully stop both servers on CTRL+C
def cleanup():
    global node_process, server_socket
    if node_process:
        node_process.terminate()
        print("Node.js server terminated")
    if server_socket:
        server_socket.close()
        print("Python TCP server closed")

# Main entry point
if __name__ == "__main__":
    try:
        node_thread = Thread(target=start_node_server)
        node_thread.start()

        start_tcp_server()
    except KeyboardInterrupt:
        print("Shutting down servers...")
        cleanup()
