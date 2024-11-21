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
            welcome_message = f"Ciao, {current_user}"
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
