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

def handle_choice_state(action):
    global current_state
    if action == "exercise":
        current_state = DOING_EXERCISES
        print("Transitioned to DOING_EXERCISES.")
    elif action == "game_preamble":
        current_state = GAME_PREAMBLE
        print("Transitioned to GAME_PREAMBLE.")
    elif action == "introduction":
        current_state = INTRODUCTION
        print("Returned to INTRODUCTION.")
    else:
        print("Invalid action for CHOICE state.")

# HTTP request handler
class StateHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Serve static files."""
        global current_state, current_user
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
        
        # For HTML files, inject the user's name
        if self.path.endswith(".html"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace '{{name}}' with current_user
                    if current_user:
                        content = content.replace('{{name}}', current_user)
                    else:
                        content = content.replace('{{name}}', '')
                    
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
        global current_user, current_state

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
                exists = False
                print(f"Benvenuto {name}")
            else:
                # Existing user
                exists = True
                print(f"Bentornato, {name}")

            current_user = name
            handle_introduction_state()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({
                "exists": exists,
                "message": f"Bentornato, {name}" if exists else f"Benvenuto {name}"
            }).encode("utf-8"))

        # Handle actions during CHOICE state
        elif current_state == CHOICE:
            if self.path == "/api/exercise":
                current_state = DOING_EXERCISES
                print("Transitioned to DOING_EXERCISES.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to DOING_EXERCISES"
                }).encode('utf-8'))
            elif self.path == "/api/game_preamble":
                current_state = GAME_PREAMBLE
                print("Transitioned to GAME_PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/introduction":
                current_state = INTRODUCTION
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid action in CHOICE state")

        # Handle actions during GAME_PREAMBLE state
        elif current_state == GAME_PREAMBLE:
            if self.path == "/api/game":
                current_state = GAME
                print("Transitioned to GAME.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME"
                }).encode('utf-8'))
            elif self.path == "/api/choice":
                current_state = CHOICE
                print("Returned to CHOICE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to CHOICE"
                }).encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid action in GAME_PREAMBLE state")

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
import socket
import csv
import time

def start_server():
    host = '0.0.0.0'
    port = 9000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server running on {host}:{port}")

    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    try:
        with open('files/task4_dats_neurometric_07_05_2024.csv', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                message = ','.join(row)  # Convert row to a string
                conn.sendall(message.encode('utf-8'))  # Send as UTF-8
                print(f"Sent: {message}")
                time.sleep(0.2)  # Wait 0.2 seconds
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

start_server()
'''

'''
import time
import socket
import subprocess
import json
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Define states
INITIAL_STATE = "INITIAL_STATE"
PRESENTATION = "PRESENTATION"
CHOICE = "CHOICE"
DOING_EXERCISES = "DOING_EXERCISES"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# List of states
states = [INITIAL_STATE, PRESENTATION, CHOICE, DOING_EXERCISES, GAME_PREAMBLE, GAME]
current_state = INITIAL_STATE
current_user = None  # Store the current user's name

# Serve static HTML files
class StateHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        global current_state, current_user
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            message = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return
        
        if self.path == "/api/presentation":
            # User submitted their name
            current_user = message.get("name")
            current_state = CHOICE
            self.redirect_to_state()
        elif self.path == "/api/choice":
            # Handle navigation to exercises or game preamble
            action = message.get("action")
            if action == "exercise":
                current_state = DOING_EXERCISES
            elif action == "game":
                current_state = GAME_PREAMBLE
            self.redirect_to_state()
        elif self.path == "/api/exercise":
            # Handle exercise state
            current_state = DOING_EXERCISES
            self.redirect_to_state()
        elif self.path == "/api/game_preamble":
            # Handle game preamble
            current_state = GAME
            self.redirect_to_state()
        elif self.path == "/api/back":
            # Handle back navigation
            self.handle_back_navigation()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown path")
    
    def redirect_to_state(self):
        """Redirect the user to the appropriate HTML page based on the current state."""
        self.send_response(302)
        self.send_header("Content-Type", "application/json")
        
        # Map states to HTML files
        state_to_page = {
            PRESENTATION: "index.html",
            CHOICE: "welcome.html",
            DOING_EXERCISES: "exercise.html",
            GAME_PREAMBLE: "gameIntroduction.html",
            GAME: "game.html",
        }
        next_page = state_to_page.get(current_state, "index.html")
        redirect_url = f"/{next_page}?name={current_user}"
        self.send_header("Location", redirect_url)
        self.end_headers()
    
    def handle_back_navigation(self):
        """Handle navigation back to the previous state."""
        global current_state
        # Map current state to previous states
        state_to_previous = {
            CHOICE: PRESENTATION,
            DOING_EXERCISES: CHOICE,
            GAME_PREAMBLE: CHOICE,
            GAME: GAME_PREAMBLE,
        }
        current_state = state_to_previous.get(current_state, PRESENTATION)
        self.redirect_to_state()

# Start the Node.js server
def start_node_server():
    subprocess.Popen(["node", "./server.js"], shell=False)
    print("Node.js server started")

# Start the HTTP server to serve HTML and handle state
def start_http_server():
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, StateHandler)
    print(f"Python HTTP server running on port {port}")
    httpd.serve_forever()

# Main entry point
if __name__ == "__main__":
    try:
        # Start the Node.js server in a separate thread
        node_thread = Thread(target=start_node_server)
        node_thread.start()

        # Start the HTTP server
        start_http_server()
    except KeyboardInterrupt:
        print("Shutting down servers...")


'''


