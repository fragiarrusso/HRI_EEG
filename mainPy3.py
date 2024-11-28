'''
import os
import json
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
DOING_EXERCISES = "DOING_EXERCISES"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# Globals
current_state = INITIAL_STATE
current_user = None

welcome_message = ""
USERS_FILE = "users.json"

# Load and save users
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# State-specific handlers
def handle_initial_state():
    global current_state
    print("Starting INITIAL_STATE...")
    time.sleep(2)  # Simulate a short delay
    current_state = INTRODUCTION
    print("Transitioned to INTRODUCTION.")

def handle_introduction_state():
    global current_state
    print("Establishing connection...")
    current_state = CHOICE
    print("Connection established. Transitioned to CHOICE.")

# HTTP request handler
class StateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve static files."""
        global current_state, current_user, welcome_message
        if self.path.startswith("/api/"):
            self.send_response(405)
            self.end_headers()
            return

        # Determine the file to serve based on current state
        if self.path == "/":
            if current_state == INTRODUCTION:
                self.path = "/index.html"
            elif current_state == CHOICE:
                self.path = "/welcome.html"
            elif current_state == GAME_PREAMBLE:
                self.path = "/game_preamble.html"
            elif current_state == GAME:
                self.path = "/game.html"
            else:
                self.path = "/index.html"

        # Adjust the path
        file_path = f"web_interfaces/public{self.path}"

        # For HTML files, inject the user's name and welcome message
        if self.path.endswith(".html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace '{{name}}' and '{{welcome_message}}'
                    content = content.replace('{{name}}', current_user or '')
                    content = content.replace('{{welcome_message}}', welcome_message or '')
                    # Send the response
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
        else:
            # For other files, serve them as usual
            self.path = file_path
            super().do_GET()

    def do_POST(self):
        """Handle POST requests to change states."""
        global current_user, current_state, welcome_message

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # Handle name submission during INTRODUCTION state
        if current_state == INTRODUCTION and self.path == "/api/choice":
            name = data.get("name")
            if not name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Name is required")
                return

            users = load_users()
            user = next((u for u in users if u["name"] == name), None)

            if not user:
                # New user
                user = {"name": name, "last": "INTRODUCTION"}
                users.append(user)
                save_users(users)
                print(f"Benvenuto {name}")
                current_user = name
                welcome_message = f"Benvenuto, {name}"
                handle_introduction_state()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "exists": False,
                    "message": f"Benvenuto {name}"
                }).encode("utf-8"))
            else:
                # Existing user
                print(f"User {name} already exists. Awaiting confirmation.")
                current_user = name  # Set current_user to handle name injection
                welcome_message = ""  # Clear welcome message until confirmed
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "exists": True,
                    "message": "User exists"
                }).encode("utf-8"))

        # Handle confirmation from existing users
        elif current_state == INTRODUCTION and self.path == "/api/confirm":
            name = data.get("name")
            if not name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Name is required")
                return

            users = load_users()
            user = next((u for u in users if u["name"] == name), None)

            if user:
                current_user = name
                welcome_message = f"Bentornato, {name}"
                handle_introduction_state()
                print(f"Bentornato, {name}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": f"Bentornato, {name}"
                }).encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"User not found")

        # Handle back action from GAME_PREAMBLE state
        elif current_state == GAME_PREAMBLE and self.path == "/api/choice":
            current_state = CHOICE
            print("Returned to CHOICE.")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Transitioned to CHOICE"
            }).encode('utf-8'))
        elif current_state == CHOICE and self.path == "/api/introduction":
            current_state = INTRODUCTION
            current_user= None
            
            print("Returned to Introduction")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Transitioned to CHOICE"
            }).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown state or endpoint")

# Start the HTTP server
def start_http_server():
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, StateHandler)
    print(f"Python HTTP server running on port {port}")

    # Initialize the server state
    handle_initial_state()
    print("Server ready to handle requests.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down Python server...")

# Main entry point
if __name__ == "__main__":
    start_http_server()
'''
'''
import os
import json
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
DOING_EXERCISES = "DOING_EXERCISES"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# Globals
current_state = INITIAL_STATE
current_user = None
connection_to_helmet = None
welcome_message = ""
USERS_FILE = "users.json"


# Load and save users
def load_users():
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# State-specific handlers
def handle_initial_state():
    global current_state
    print("Starting INITIAL_STATE...")
    time.sleep(2)  # Simulate a short delay
    current_state = INTRODUCTION
    print("Transitioned to INTRODUCTION.")

def handle_introduction_state():
    global current_state
    print("Establishing connection...")
    current_state = CHOICE
    print("Connection established. Transitioned to CHOICE.")

# HTTP request handler
class StateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve static files."""
        global current_state, current_user, welcome_message
        if self.path.startswith("/api/"):
            self.send_response(405)
            self.end_headers()
            return

        # Determine the file to serve based on current state
        if self.path == "/":
            if current_state == INTRODUCTION:
                self.path = "/index.html"
            elif current_state == CHOICE:
                self.path = "/welcome.html"
            elif current_state == GAME_PREAMBLE:
                self.path = "/game_preamble.html"
            elif current_state == GAME:
                self.path = "/game.html"
            else:
                self.path = "/index.html"

        # Adjust the path
        file_path = f"web_interfaces/public{self.path}"

        # For HTML files, inject the user's name and welcome message
        if self.path.endswith(".html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace '{{name}}' and '{{welcome_message}}'
                    content = content.replace('{{name}}', current_user or '')
                    content = content.replace('{{welcome_message}}', welcome_message or '')
                    # Send the response
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
        else:
            # For other files, serve them as usual
            self.path = file_path
            super().do_GET()

    def do_POST(self):
        """Handle POST requests to change states."""
        global current_user, current_state, welcome_message

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # Handle requests based on current state
        if current_state == INTRODUCTION:
            if self.path == "/api/choice":
                # Handle name submission
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if not user:
                    # New user
                    user = {"name": name, "last": "INTRODUCTION"}
                    users.append(user)
                    save_users(users)
                    print(f"Benvenuto {name}")
                    current_user = name
                    welcome_message = f"Benvenuto, {name}"
                    handle_introduction_state()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": False,
                        "message": f"Benvenuto {name}"
                    }).encode("utf-8"))
                else:
                    # Existing user
                    print(f"User {name} already exists. Awaiting confirmation.")
                    current_user = name  # Set current_user to handle name injection
                    welcome_message = ""  # Clear welcome message until confirmed
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": True,
                        "message": "User exists"
                    }).encode("utf-8"))
            elif self.path == "/api/confirm":
                # Handle confirmation from existing users
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if user:
                    current_user = name
                    welcome_message = f"Bentornato, {name}"
                    handle_introduction_state()
                    print(f"Bentornato, {name}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": f"Bentornato, {name}"
                    }).encode("utf-8"))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"User not found")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in INTRODUCTION state")
        elif current_state == CHOICE:
            
            if self.path == "/api/game_preamble":
                # Transition to GAME_PREAMBLE
                current_state = GAME_PREAMBLE
                print("Transitioned to GAME_PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/exercise":
                # Transition to DOING_EXERCISES
                current_state = DOING_EXERCISES
                print("Transitioned to DOING_EXERCISES.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to DOING_EXERCISES"
                }).encode('utf-8'))
                
            elif self.path == "/api/introduction":
                # Return to INTRODUCTION
                current_state = INTRODUCTION
                current_user = None
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in CHOICE state")
            

        elif current_state == GAME_PREAMBLE:
            if self.path == "/api/game":
                # Transition to GAME
                current_state = GAME
                print("Transitioned to GAME.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME"
                }).encode('utf-8'))
            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Ciao, {current_user}"
                print("Returned to CHOICE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to CHOICE"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in GAME_PREAMBLE state")
                
        elif current_state == DOING_EXERCISES:
            # Handle POST requests in DOING_EXERCISES state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in DOING_EXERCISES state")
        elif current_state == GAME:
            # Handle POST requests in GAME state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in GAME state")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown state or endpoint")

# Start the HTTP server
def start_http_server():
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, StateHandler)
    print(f"Python HTTP server running on port {port}")

    # Initialize the server state
    handle_initial_state()
    print("Server ready to handle requests.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down Python server...")

# Main entry point
if __name__ == "__main__":
    start_http_server()
'''


'''
import os
import json
import time
import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from collections import deque


# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
DOING_EXERCISES = "DOING_EXERCISES"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"


ROLLING_WINDOW_SIZE = 10
# Deques to store recent values
workload_values = deque(maxlen=ROLLING_WINDOW_SIZE)
stress_values = deque(maxlen=ROLLING_WINDOW_SIZE)


# Globals
current_state = INITIAL_STATE
current_user = None
welcome_message = ""
USERS_FILE = "users.json"

# helmet Connection-related variables
connection_to_helmet = None
connection_status = "disconnected"
connection_lock = threading.Lock()
client_socket = None
connection_thread = None

# Global variables for rolling averages
rolling_avg_workload = None
rolling_avg_stress = None


# Load and save users
def load_users():
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# State-specific handlers
def handle_initial_state():
    global current_state
    print("Starting INITIAL_STATE...")
    time.sleep(2)  # Simulate a short delay
    current_state = INTRODUCTION
    print("Transitioned to INTRODUCTION.")

def handle_introduction_state():
    global current_state,connection_thread
    print("Establishing connection...")
    current_state = CHOICE
    print("Connection established. Transitioned to CHOICE.")
    
    # Start connection attempt thread
    connection_thread = threading.Thread(target=attempt_connection, daemon=True)
    connection_thread.start()

def listen_to_second_server():
    global client_socket, connection_status, rolling_avg_workload, rolling_avg_stress
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Connection closed
            
            try:
                message = data.decode('utf-8').strip()
                workload_str, stress_str = message.split(',')
                workload = float(workload_str)
                stress = float(stress_str)
            except ValueError as ve:
                print(f"Error parsing data: {ve}")
                continue  # Skip to the next iteration

            # Update rolling averages
            with connection_lock:
                workload_values.append(workload)
                stress_values.append(stress)
                rolling_avg_workload = sum(workload_values) / len(workload_values)
                rolling_avg_stress = sum(stress_values) / len(stress_values)

            # Optional: Print or log the rolling averages
            print(f"Rolling Average - Workload: {rolling_avg_workload:.2f}, Stress: {rolling_avg_stress:.2f}")

    except Exception as e:
        print(f"Connection to second server lost: {e}")
    finally:
        with connection_lock:
            if client_socket:
                client_socket.close()
                client_socket = None
            connection_status = "disconnected"
        attempt_connection()





def attempt_connection():
    global client_socket, connection_status, current_state
    while current_state != INTRODUCTION:
        try:
            # Try to establish the connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 9000))  # Replace with your server's host and port
            with connection_lock:
                connection_status = "connected"
            print("Connected to the second server.")
            # Start the listener thread
            listener_thread = threading.Thread(target=listen_to_second_server, daemon=True)
            listener_thread.start()
            break  # Exit the loop once connected
        except Exception as e:
            with connection_lock:
                connection_status = "disconnected"
            print(f"Connection attempt failed: {e}")
            time.sleep(10)  # Wait before retrying


# HTTP request handler
class StateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global current_state, current_user, welcome_message, connection_status
        if self.path == "/api/connection_status":
            # Return the connection status
            with connection_lock:
                status = connection_status
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status}).encode('utf-8'))
            return

        # Determine the file to serve based on current state
        if self.path == "/":
            if current_state == INTRODUCTION:
                self.path = "/index.html"
            elif current_state == CHOICE:
                self.path = "/welcome.html"
            elif current_state == GAME_PREAMBLE:
                self.path = "/game_preamble.html"
            elif current_state == GAME:
                self.path = "/game.html"
            else:
                self.path = "/index.html"

        # Adjust the path
        file_path = f"web_interfaces/public{self.path}"

        # For HTML files, inject the user's name and welcome message
        if self.path.endswith(".html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace '{{name}}' and '{{welcome_message}}'
                    content = content.replace('{{name}}', current_user or '')
                    content = content.replace('{{welcome_message}}', welcome_message or '')
                    # Send the response
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
        else:
            # For other files, serve them as usual
            self.path = file_path
            super().do_GET()

    def do_POST(self):
        """Handle POST requests to change states."""
        global current_user, current_state, welcome_message

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return
        
        # Handle requests based on current state
        if current_state == INTRODUCTION:
            if self.path == "/api/choice":
                # Handle name submission
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if not user:
                    # New user
                    user = {"name": name, "last": "INTRODUCTION"}
                    users.append(user)
                    save_users(users)
                    print(f"Benvenuto {name}")
                    current_user = name
                    welcome_message = f"Benvenuto, {name}"
                    handle_introduction_state()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": False,
                        "message": f"Benvenuto {name}"
                    }).encode("utf-8"))
                else:
                    # Existing user
                    print(f"User {name} already exists. Awaiting confirmation.")
                    current_user = name  # Set current_user to handle name injection
                    welcome_message = ""  # Clear welcome message until confirmed
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": True,
                        "message": "User exists"
                    }).encode("utf-8"))
            elif self.path == "/api/confirm":
                # Handle confirmation from existing users
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if user:
                    current_user = name
                    welcome_message = f"Bentornato, {name}"
                    handle_introduction_state()
                    print(f"Bentornato, {name}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": f"Bentornato, {name}"
                    }).encode("utf-8"))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"User not found")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in INTRODUCTION state")
        elif current_state == CHOICE:
            
            if self.path == "/api/game_preamble":
                # Transition to GAME_PREAMBLE
                current_state = GAME_PREAMBLE
                print("Transitioned to GAME_PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/exercise":
                # Transition to DOING_EXERCISES
                current_state = DOING_EXERCISES
                print("Transitioned to DOING_EXERCISES.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to DOING_EXERCISES"
                }).encode('utf-8'))
                
                
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                global client_socket, connection_status #da togliere(?)
                current_state = INTRODUCTION
                current_user = None
                # Close the connection to the second server
                if client_socket:
                    try:
                        client_socket.close()
                        print("Closed connection to the second server.")
                    except Exception as e:
                        print(f"Error closing connection: {e}")
                    finally:
                        client_socket = None
                        with connection_lock:
                            connection_status = "disconnected"
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in CHOICE state")

        elif current_state == GAME_PREAMBLE:
            if self.path == "/api/game":
                # Transition to GAME
                current_state = GAME
                print("Transitioned to GAME.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME"
                }).encode('utf-8'))
            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Ciao, {current_user}"
                print("Returned to CHOICE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to CHOICE"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in GAME_PREAMBLE state")
                
        elif current_state == DOING_EXERCISES:
            # Handle POST requests in DOING_EXERCISES state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in DOING_EXERCISES state")
        elif current_state == GAME:
            # Handle POST requests in GAME state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in GAME state")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown state or endpoint")

# Start the HTTP server
def start_http_server():
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, StateHandler)
    print(f"Python HTTP server running on port {port}")

    # Initialize the server state
    handle_initial_state()
    print("Server ready to handle requests.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down Python server...")
        if client_socket:
            try:
                client_socket.close()
                print("Closed connection to the second server.")
            except Exception as e:
                print(f"Error closing connection: {e}")


# Main entry point
if __name__ == "__main__":
    start_http_server()
'''

'''
import os
import json
import time
import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from collections import deque

# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
DOING_EXERCISES = "DOING_EXERCISES"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# Rolling average parameters
ROLLING_WINDOW_SIZE = 10
# Deques to store recent values
workload_values = deque(maxlen=ROLLING_WINDOW_SIZE)
stress_values = deque(maxlen=ROLLING_WINDOW_SIZE)

# Globals
current_state = INITIAL_STATE
current_user = None
welcome_message = ""
USERS_FILE = "users.json"

# Connection-related variables
connection_status = "disconnected"
connection_lock = threading.Lock()
client_socket = None
connection_thread = None

# Global variables for rolling averages
rolling_avg_workload = None
rolling_avg_stress = None

# Load and save users
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        # Ensure all users have 'last', 'avg', 'last_level'
        for user in users:
            if 'last' not in user:
                user['last'] = 0
            if 'avg' not in user:
                user['avg'] = 0
            if 'last_level' not in user:
                user['last_level'] = 0
        return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# State-specific handlers
def handle_initial_state():
    global current_state
    print("Starting INITIAL_STATE...")
    time.sleep(2)  # Simulate a short delay
    current_state = INTRODUCTION
    print("Transitioned to INTRODUCTION.")

def handle_introduction_state():
    global current_state, connection_thread
    print("Establishing connection...")
    current_state = CHOICE
    print("Connection established. Transitioned to CHOICE.")
    
    # Start connection attempt thread
    connection_thread = threading.Thread(target=attempt_connection, daemon=True)
    connection_thread.start()

def listen_to_second_server():
    global client_socket, connection_status, rolling_avg_workload, rolling_avg_stress
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Connection closed
            
            try:
                message = data.decode('utf-8').strip()
                workload_str, stress_str = message.split(',')
                workload = float(workload_str)
                stress = float(stress_str)
            except ValueError as ve:
                print(f"Error parsing data: {ve}")
                continue  # Skip to the next iteration

            # Update rolling averages
            with connection_lock:
                workload_values.append(workload)
                stress_values.append(stress)
                rolling_avg_workload = sum(workload_values) / len(workload_values)
                rolling_avg_stress = sum(stress_values) / len(stress_values)

            # Optional: Print or log the rolling averages
            print(f"Rolling Average - Workload: {rolling_avg_workload:.2f}, Stress: {rolling_avg_stress:.2f}")

    except Exception as e:
        print(f"Connection to second server lost: {e}")
    finally:
        with connection_lock:
            if client_socket:
                client_socket.close()
                client_socket = None
            connection_status = "disconnected"
        attempt_connection()

def attempt_connection():
    global client_socket, connection_status, current_state
    while current_state != INTRODUCTION:
        try:
            # Try to establish the connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 9000))  # Replace with your server's host and port
            with connection_lock:
                connection_status = "connected"
            print("Connected to the second server.")
            # Start the listener thread
            listener_thread = threading.Thread(target=listen_to_second_server, daemon=True)
            listener_thread.start()
            break  # Exit the loop once connected
        except Exception as e:
            with connection_lock:
                connection_status = "disconnected"
            print(f"Connection attempt failed: {e}")
            time.sleep(10)  # Wait before retrying

# HTTP request handler
class StateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global current_state, current_user, welcome_message, connection_status
        global rolling_avg_workload, rolling_avg_stress  # Added to access rolling averages

        if self.path == "/api/connection_status":
            # Return the connection status
            with connection_lock:
                status = connection_status
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status}).encode('utf-8'))
            return

        elif self.path == "/api/rolling_averages":
            # Return the rolling averages
            with connection_lock:
                workload = rolling_avg_workload
                stress = rolling_avg_stress
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "rolling_avg_workload": workload,
                "rolling_avg_stress": stress
            }).encode('utf-8'))
            return

        # Determine the file to serve based on current state
        if self.path == "/":
            if current_state == INTRODUCTION:
                self.path = "/index.html"
            elif current_state == CHOICE:
                self.path = "/welcome.html"
            elif current_state == GAME_PREAMBLE:
                self.path = "/game_preamble.html"
            elif current_state == GAME:
                self.path = "/game.html"
            else:
                self.path = "/index.html"

        # Adjust the path
        file_path = f"web_interfaces/public{self.path}"

        # For HTML files, inject the user's name and welcome message
        if self.path.endswith(".html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace '{{name}}' and '{{welcome_message}}'
                    content = content.replace('{{name}}', current_user or '')
                    content = content.replace('{{welcome_message}}', welcome_message or '')
                    # Send the response
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
        else:
            # For other files, serve them as usual
            self.path = file_path
            super().do_GET()

    def do_POST(self):
        """Handle POST requests to change states."""
        global current_user, current_state, welcome_message

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return
        
        # Handle requests based on current state
        if current_state == INTRODUCTION:
            if self.path == "/api/choice":
                # Handle name submission
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if not user:
                    # New user
                    user = {"name": name, "last": 0, "avg": 0, "last_level": 0}
                    users.append(user)
                    save_users(users)
                    print(f"Benvenuto {name}")
                    current_user = name
                    welcome_message = f"Benvenuto, {name}"
                    handle_introduction_state()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": False,
                        "message": f"Benvenuto {name}"
                    }).encode("utf-8"))
                else:
                    # Existing user
                    print(f"User {name} already exists. Awaiting confirmation.")
                    current_user = name  # Set current_user to handle name injection
                    welcome_message = ""  # Clear welcome message until confirmed
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": True,
                        "message": "User exists"
                    }).encode("utf-8"))
            elif self.path == "/api/confirm":
                # Handle confirmation from existing users
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if user:
                    current_user = name
                    welcome_message = f"Bentornato, {name}"
                    handle_introduction_state()
                    print(f"Bentornato, {name}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": f"Bentornato, {name}"
                    }).encode("utf-8"))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"User not found")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in INTRODUCTION state")
        elif current_state == CHOICE:
            
            if self.path == "/api/game_preamble":
                # Transition to GAME_PREAMBLE
                current_state = GAME_PREAMBLE
                print("Transitioned to GAME_PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/exercise":
                # Transition to DOING_EXERCISES
                current_state = DOING_EXERCISES
                print("Transitioned to DOING_EXERCISES.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to DOING_EXERCISES"
                }).encode('utf-8'))
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                global client_socket, connection_status
                current_state = INTRODUCTION
                current_user = None
                # Close the connection to the second server
                if client_socket:
                    try:
                        client_socket.close()
                        print("Closed connection to the second server.")
                    except Exception as e:
                        print(f"Error closing connection: {e}")
                    finally:
                        client_socket = None
                        with connection_lock:
                            connection_status = "disconnected"
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in CHOICE state")

        elif current_state == GAME_PREAMBLE:
            if self.path == "/api/game":
                # Transition to GAME
                current_state = GAME
                # Update the user's 'last' field to 1
                users = load_users()
                user = next((u for u in users if u["name"] == current_user), None)
                if user:
                    user['last'] = 1
                    save_users(users)
                print("Transitioned to GAME.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME"
                }).encode('utf-8'))

            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Ciao, {current_user}"
                print("Returned to CHOICE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to CHOICE"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in GAME_PREAMBLE state")
                
        elif current_state == DOING_EXERCISES:
            # Handle POST requests in DOING_EXERCISES state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in DOING_EXERCISES state")
        elif current_state == GAME:
            # Handle POST requests in GAME state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in GAME state")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown state or endpoint")

# Start the HTTP server
def start_http_server():
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, StateHandler)
    print(f"Python HTTP server running on port {port}")

    # Initialize the server state
    handle_initial_state()
    print("Server ready to handle requests.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down Python server...")
        if client_socket:
            try:
                client_socket.close()
                print("Closed connection to the second server.")
            except Exception as e:
                print(f"Error closing connection: {e}")

# Main entry point
if __name__ == "__main__":
    start_http_server()
'''

import os
import json
import time
import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from collections import deque

# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
DOING_EXERCISES = "DOING_EXERCISES"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# Rolling average parameters
ROLLING_WINDOW_SIZE = 10
# Deques to store recent values
workload_values = deque(maxlen=ROLLING_WINDOW_SIZE)
stress_values = deque(maxlen=ROLLING_WINDOW_SIZE)

# Globals
current_state = INITIAL_STATE
current_user = None
welcome_message = ""
USERS_FILE = "users.json"

# Connection-related variables
connection_status = "disconnected"
connection_lock = threading.Lock()
client_socket = None
connection_thread = None

# Global variables for rolling averages
rolling_avg_workload = None
rolling_avg_stress = None

# Load and save users
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        # Ensure all users have 'last', 'avg', 'last_level'
        for user in users:
            if 'last' not in user:
                user['last'] = 0
            if 'avg' not in user:
                user['avg'] = 0
            if 'last_level' not in user:
                user['last_level'] = 1
        return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# State-specific handlers
def handle_initial_state():
    global current_state
    print("Starting INITIAL_STATE...")
    time.sleep(2)  # Simulate a short delay
    current_state = INTRODUCTION
    print("Transitioned to INTRODUCTION.")

def handle_introduction_state():
    global current_state, connection_thread
    print("Establishing connection...")
    current_state = CHOICE
    print("Connection established. Transitioned to CHOICE.")
    
    # Start connection attempt thread
    connection_thread = threading.Thread(target=attempt_connection, daemon=True)
    connection_thread.start()

def listen_to_second_server():
    global client_socket, connection_status, rolling_avg_workload, rolling_avg_stress
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Connection closed
            
            try:
                message = data.decode('utf-8').strip()
                workload_str, stress_str = message.split(',')
                workload = float(workload_str)
                stress = float(stress_str)
            except ValueError as ve:
                print(f"Error parsing data: {ve}")
                continue  # Skip to the next iteration

            # Update rolling averages
            with connection_lock:
                workload_values.append(workload)
                stress_values.append(stress)
                rolling_avg_workload = sum(workload_values) / len(workload_values)
                rolling_avg_stress = sum(stress_values) / len(stress_values)

            # Optional: Print or log the rolling averages
            print(f"Rolling Average - Workload: {rolling_avg_workload:.2f}, Stress: {rolling_avg_stress:.2f}")

    except Exception as e:
        print(f"Connection to second server lost: {e}")
    finally:
        with connection_lock:
            if client_socket:
                client_socket.close()
                client_socket = None
            connection_status = "disconnected"
        attempt_connection()

def attempt_connection():
    global client_socket, connection_status, current_state
    while current_state != INTRODUCTION:
        try:
            # Try to establish the connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 9000))  # Replace with your server's host and port
            with connection_lock:
                connection_status = "connected"
            print("Connected to the second server.")
            # Start the listener thread
            listener_thread = threading.Thread(target=listen_to_second_server, daemon=True)
            listener_thread.start()
            break  # Exit the loop once connected
        except Exception as e:
            with connection_lock:
                connection_status = "disconnected"
            print(f"Connection attempt failed: {e}")
            time.sleep(10)  # Wait before retrying

# HTTP request handler
class StateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global current_state, current_user, welcome_message, connection_status

        global rolling_avg_workload, rolling_avg_stress
        if self.path == "/api/connection_status":
            # Return the connection status
            with connection_lock:
                status = connection_status
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status}).encode('utf-8'))
            return

        elif self.path == "/api/rolling_averages":
            # Return the rolling averages
            with connection_lock:
                workload = rolling_avg_workload
                stress = rolling_avg_stress
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "rolling_avg_workload": workload,
                "rolling_avg_stress": stress
            }).encode('utf-8'))
            return

        elif self.path == "/api/user_status":
            # Return 'last' and 'connection_status'
            with connection_lock:
                status = connection_status
            last = 0
            users = load_users()
            user = next((u for u in users if u["name"] == current_user), None)
            if user:
                last = user.get('last', 0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": status,
                "last": last
            }).encode('utf-8'))
            return

        # Determine the file to serve based on current state
        if self.path == "/":
            if current_state == INTRODUCTION:
                self.path = "/index.html"
            elif current_state == CHOICE:
                self.path = "/welcome.html"
            elif current_state == GAME_PREAMBLE:
                self.path = "/game_preamble.html"
            elif current_state == GAME:
                self.path = "/game.html"
            else:
                self.path = "/index.html"

        # Adjust the path
        file_path = f"web_interfaces/public{self.path}"

        # For HTML files, inject the user's name and welcome message
        if self.path.endswith(".html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace '{{name}}' and '{{welcome_message}}'
                    content = content.replace('{{name}}', current_user or '')
                    content = content.replace('{{welcome_message}}', welcome_message or '')
                    # Send the response
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File not found")
        else:
            # For other files, serve them as usual
            self.path = file_path
            super().do_GET()

    def do_POST(self):
        """Handle POST requests to change states."""
        global current_user, current_state, welcome_message

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return
        
        # Handle requests based on current state
        if current_state == INTRODUCTION:
            if self.path == "/api/choice":
                # Handle name submission
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if not user:
                    # New user
                    user = {"name": name, "last": 0, "avg": 0, "last_level": 0}
                    users.append(user)
                    save_users(users)
                    print(f"Benvenuto {name}")
                    current_user = name
                    welcome_message = f"Benvenuto, {name}"
                    handle_introduction_state()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": False,
                        "message": f"Benvenuto {name}"
                    }).encode("utf-8"))
                else:
                    # Existing user
                    print(f"User {name} already exists. Awaiting confirmation.")
                    current_user = name  # Set current_user to handle name injection
                    welcome_message = ""  # Clear welcome message until confirmed
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": True,
                        "message": "User exists"
                    }).encode("utf-8"))
            elif self.path == "/api/confirm":
                # Handle confirmation from existing users
                name = data.get("name")
                if not name:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if user:
                    current_user = name
                    welcome_message = f"Bentornato, {name}"
                    handle_introduction_state()
                    print(f"Bentornato, {name}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": f"Bentornato, {name}"
                    }).encode("utf-8"))
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"User not found")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in INTRODUCTION state")
        elif current_state == CHOICE:
            
            if self.path == "/api/game_preamble":
                # Transition to GAME_PREAMBLE
                current_state = GAME_PREAMBLE
                print("Transitioned to GAME_PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/exercise":
                # Transition to DOING_EXERCISES
                current_state = DOING_EXERCISES
                print("Transitioned to DOING_EXERCISES.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to DOING_EXERCISES"
                }).encode('utf-8'))
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                global client_socket, connection_status
                current_state = INTRODUCTION
                current_user = None
                # Close the connection to the second server
                if client_socket:
                    try:
                        client_socket.close()
                        print("Closed connection to the second server.")
                    except Exception as e:
                        print(f"Error closing connection: {e}")
                    finally:
                        client_socket = None
                        with connection_lock:
                            connection_status = "disconnected"
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in CHOICE state")
        
        elif current_state == GAME_PREAMBLE:
            if self.path == "/api/game":
                # Transition to GAME
                current_state = GAME
                print("Transitioned to GAME.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME"
                }).encode('utf-8'))
            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Ciao, {current_user}"
                print("Returned to CHOICE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to CHOICE"
                }).encode('utf-8'))
            elif self.path == "/api/rolling_averages":
                # Return rolling averages
                with connection_lock:
                    workload = rolling_avg_workload
                    stress = rolling_avg_stress
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "rolling_avg_workload": workload,
                    "rolling_avg_stress": stress
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in GAME_PREAMBLE state")   
                
        elif current_state == DOING_EXERCISES:
            # Handle POST requests in DOING_EXERCISES state if needed
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"No endpoints defined in DOING_EXERCISES state")



        elif current_state == GAME:
            # Handle POST requests in GAME state if needed
            if self.path == "/api/gamepreamble":
                current_state = GAME_PREAMBLE
                print("Transitioned to GAME PREAMBLE.")
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME PREAMBLE"
                }).encode('utf-8'))
                
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown state or endpoint")

# Start the HTTP server
def start_http_server():
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, StateHandler)
    print(f"Python HTTP server running on port {port}")

    # Initialize the server state
    handle_initial_state()
    print("Server ready to handle requests.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down Python server...")
        if client_socket:
            try:
                client_socket.close()
                print("Closed connection to the second server.")
            except Exception as e:
                print(f"Error closing connection: {e}")

# Main entry point
if __name__ == "__main__":
    start_http_server()
