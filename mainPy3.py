import os
import json
import time
import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from collections import deque
from audio import get_response
import requests
from YOLO.human_counter_test import human_counter

# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
EXERCISES = "EXERCISES"
EXERCISES_PREAMBLE = "EXERCISES_PREAMBLE"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# Rolling average parameters
ROLLING_WINDOW_SIZE = 10
# Deques to store recent values
workload_values = deque(maxlen=ROLLING_WINDOW_SIZE)
stress_values = deque(maxlen=ROLLING_WINDOW_SIZE)

# Globals
ACTIVE = True
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
response = ''

if not ACTIVE:
    def get_response():
        return
    
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
            if 'games_played' not in user:
                user['games_played'] = 0
        return users

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# State-specific handlers
def handle_initial_state():
    global current_state
    print("Starting INITIAL_STATE...")
    
    humans = human_counter()
    print("found",humans,'humans')
    
    while humans == 0:
        humans = human_counter()
        print("found",humans,'humans')
    call_to_docker_server(current_state, 'move', "greet")
    call_to_docker_server(current_state, 'say', "Hi, I am Pepper")
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
            rolling_avg_workload=None
            rolling_avg_stress=None

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

def audio_response():
    global response
    while True:
        response = get_response() 
        print('response: '+response)



def call_to_docker_server(state, action, additional_data=None):
    global ACTIVE
    if ACTIVE:
        url = "http://172.17.0.1:9001/act"
        payload = {"client":0, "state": state, "action": action, "additional_data": additional_data }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"Successfully notified external server: {response.json()}")
            else:
                print(f"Failed to notify external server: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during notification: {e}")    
        
    else:
        print(state, action, additional_data)
    return
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
        
        
        elif self.path == "/api/user_data":
            users = load_users()
            user = next((u for u in users if u["name"] == current_user), None)
            if user:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "last": user.get('last', 0),
                    "avg": user.get('avg', 0),
                    "last_level": user.get('last_level', 1),
                    "games_played": user.get('games_played', 0)
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"User not found")
            return
        
        
        # Determine the file to serve based on current state
        if self.path == "/":
            if current_state == INTRODUCTION:
                self.path = "/index.html"
                call_to_docker_server(current_state, 'say', "Insert a name to start")
            elif current_state == CHOICE:
                self.path = "/welcome.html"
            elif current_state == GAME_PREAMBLE:
                self.path = "/game_preamble.html"
            elif current_state == GAME:
                self.path = "/game.html"
            elif current_state == EXERCISES_PREAMBLE:
                self.path = "/exercise_preamble.html"
            elif current_state == EXERCISES:
                self.path = "/exercise.html"
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
                print(name)
                if not name:
                    self.send_response(400)
                    call_to_docker_server(current_state, 'move', "wrong")
                    call_to_docker_server(current_state, 'say', "Insert a valid name")
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if not user:
                    # New user
                    user = {"name": name, "last": 0, "avg": 0, "last_level": 0,"games_played": 0}   
                    users.append(user)
                    save_users(users)
                    print(f"Benvenuto {name}")
                    current_user = name
                    welcome_message = f"Welcome, {name}"
                    call_to_docker_server(current_state, 'move', "greet")
                    call_to_docker_server(current_state, 'say', welcome_message +" "+ "what do you want to do?")
                    
                    handle_introduction_state()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": False,
                        "message": f"Benvenuto {name}"
                    }).encode("utf-8"))
                else:
                    # Existing user
                    call_to_docker_server(current_state, 'move', "saymove")
                    call_to_docker_server(current_state, 'say', "The name already exist, please confirm to be you")
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
                    call_to_docker_server(current_state, 'move', "saymove")
                    call_to_docker_server(current_state, 'say', "Insert a valid name")
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if user:
                    current_user = name
                    welcome_message = f"Welcome back, {name}"
                    call_to_docker_server(current_state, 'move', "greet")
                    call_to_docker_server(current_state, 'say', welcome_message+" "+"what do you want to do?")
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
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "Let's play!")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/exercise_preamble":
                # Transition to EXERCISES_PREAMBLE
                current_state = EXERCISES_PREAMBLE
                print("Transitioned to EXERCISES_PREAMBLE.")
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "Let's Exercise!")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to EXERCISES_PREAMBLE"
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
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "insert a valid name")
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
                call_to_docker_server(current_state, 'say', "Start playing!")
                print("Transitioned to GAME.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME"
                }).encode('utf-8'))
            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Hi, {current_user}"
                print("Returned to CHOICE.")
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "You don't want to play anymore?")
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
            elif self.path == "/api/highstress":
                call_to_docker_server(current_state, 'move', "calm")
                call_to_docker_server(current_state, 'say', "Your stress levels are too high, try to relax a bit before starting to play")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to CHOICE"
                }).encode('utf-8'))
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                #global client_socket, connection_status
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
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "you have logged out, insert a new name")
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in GAME_PREAMBLE state")   
                
        elif current_state == EXERCISES_PREAMBLE:
            audio_thread = threading.Thread(target=audio_response, daemon=True)
            audio_thread.start()
            # Handle POST requests in EXERCISES_PREAMBLE state if needed
            if self.path == "/api/exercise":
                # Transition to EXERCISE
                current_state = EXERCISES
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "Let's Exercise!")
                call_to_docker_server(current_state, 'say', "say 'stop' to stop the exercises")
                print("Transitioned to EXERCISES.")
                for _ in range(3):
                    for i in range(1,8):
                        if 'STOP' in response or 'FERMA' in response:
                            current_state = CHOICE
                            print('stopped')
                            break
                        call_to_docker_server(current_state, 'say', str(i))
                        call_to_docker_server(current_state, 'move', "bigcircle;0.5")

                    time.sleep(5)

                    for i in range(1,8):
                        if 'STOP' in response or 'FERMA' in response:
                            current_state = CHOICE
                            print('stopped')
                            break
                        call_to_docker_server(current_state, 'say', str(i))
                        call_to_docker_server(current_state, 'move', "push;0.5")

                    time.sleep(5)

                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to EXERCISES"
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

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": "Transitioned to EXERCISES"
                    }).encode('utf-8'))
                    i = 0
                    for _ in range(3):
                        while i < 10:
                            if 'STOP' in response or 'FERMA' in response:
                                current_state = CHOICE
                                print('stopped')
                                break
                            call_to_docker_server(current_state, 'say', str(i))
                            call_to_docker_server(current_state, 'move', "bigcircle;"+str(0.5*(1/workload)))
                            if stress > 1.6 and i > 6:
                                break

                        time.sleep(5*stress)

                        while i < 10:
                            if 'STOP' in response or 'FERMA' in response:
                                current_state = CHOICE
                                print('stopped')
                                break
                            call_to_docker_server(current_state, 'say', str(i))
                            call_to_docker_server(current_state, 'move', "push;"+str(0.5*(1/workload)))
                            if stress > 1.6 and i > 6:
                                break

                        time.sleep(5*stress)                        
            
            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Hi, {current_user}"
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "Do you want to stop exercising?")
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
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                #global client_socket, connection_status
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
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "you have logged out, insert a new name")
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in EXERCISES_PREAMBLE state")


        # probabilmente da togliere tutto
        elif current_state == EXERCISES:
            # Handle POST requests in GAME state if needed
            if self.path == "/api/exercise_preamble":
                current_state = EXERCISES_PREAMBLE
                print("Transitioned to EXERCISES PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to EXERCISES PREAMBLE"
                }).encode('utf-8'))


        elif current_state == GAME:
            # Handle POST requests in GAME state if needed
            if self.path == "/api/gamepreamble":
                current_state = GAME_PREAMBLE
                call_to_docker_server(current_state, 'move', "saymove")
                call_to_docker_server(current_state, 'say', "Stop play for now)
                print("Transitioned to GAME PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME PREAMBLE"
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
                
            elif self.path == "/api/update_user_data":
                # Handle the request from client and update user data
                print("Received request to update user data")
                users = load_users()
                user = next((u for u in users if u["name"] == current_user), None)
                if user:
                    if connection_status == "connected":
                        user['last'] = data.get('last', user['last'])
                        user['avg'] = data.get('avg', user['avg'])
                        user['games_played'] = data.get('games_played', user['games_played'])
                    
                    user['last_level'] = data.get('last_level', user['last_level'])
                    
                    save_users(users)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": "User data updated successfully"
                    }).encode('utf-8'))
                    print(f"Updated user data for {current_user}")
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"User not found")
                    print(f"User {current_user} not found when updating data")
                return
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
#from audio import get_response
import requests

# Define states
INITIAL_STATE = "INITIAL_STATE"
INTRODUCTION = "INTRODUCTION"
CHOICE = "CHOICE"
EXERCISES = "EXERCISES"
EXERCISES_PREAMBLE = "EXERCISES_PREAMBLE"
GAME_PREAMBLE = "GAME_PREAMBLE"
GAME = "GAME"

# Rolling average parameters
ROLLING_WINDOW_SIZE = 10
# Deques to store recent values
workload_values = deque(maxlen=ROLLING_WINDOW_SIZE)
stress_values = deque(maxlen=ROLLING_WINDOW_SIZE)

# Globals
ACTIVE = False
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
    call_to_docker_server(current_state, 'say', "Ciao, Sono Pepper")
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
            rolling_avg_workload=None
            rolling_avg_stress=None

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


def call_to_docker_server(state, action, additional_data=None):
    global ACTIVE
    if ACTIVE:
        url = "http://172.17.0.1:9001/act"
        payload = {"client":0, "state": state, "action": action, "additional_data": additional_data }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"Successfully notified external server: {response.json()}")
            else:
                print(f"Failed to notify external server: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error during notification: {e}")    
        
    else:
        print(state, action, additional_data)
    return
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
        
        elif self.path == "/api/user_data":
            users = load_users()
            user = next((u for u in users if u["name"] == current_user), None)
            if user:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "last": user.get('last', 0),
                    "avg": user.get('avg', 0),
                    "last_level": user.get('last_level', 1),
                    "games_played": user.get('games_played', 0)
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"User not found")
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
            elif current_state == EXERCISES_PREAMBLE:
                self.path = "/exercise_preamble.html"
            elif current_state == EXERCISES:
                self.path = "/exercise.html"
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
                print(name)
                if not name:
                    self.send_response(400)
                    call_to_docker_server(current_state, 'say', "inserisci un nome valido")
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
                    call_to_docker_server(current_state, 'say', welcome_message +" "+ "cosa vuoi fare?")
                    
                    handle_introduction_state()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "exists": False,
                        "message": f"Benvenuto {name}"
                    }).encode("utf-8"))
                else:
                    # Existing user
                    
                    call_to_docker_server(current_state, 'say', "Il nome esiste gi, conferma di essere tu")
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
                    call_to_docker_server(current_state, 'say', "inserisci un nome valido")
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Name is required")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == name), None)

                if user:
                    current_user = name
                    welcome_message = f"Bentornato, {name}"
                    call_to_docker_server(current_state, 'say', welcome_message+" "+"cosa vuoi fare?")
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
                call_to_docker_server(current_state, 'say', "Benvenuto in game preamble")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME_PREAMBLE"
                }).encode('utf-8'))
            elif self.path == "/api/exercise_preamble":
                # Transition to EXERCISES_PREAMBLE
                current_state = EXERCISES_PREAMBLE
                print("Transitioned to EXERCISES_PREAMBLE.")
                call_to_docker_server(current_state, 'say', "Benvenuto in exercise preamble")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to EXERCISES_PREAMBLE"
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
                call_to_docker_server(current_state, 'say', "inserisci un nome valido")
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
                call_to_docker_server(current_state, 'say', "Inizia a giocare!")
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
                call_to_docker_server(current_state, 'say', "Non ti va piu di giocare?")
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
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                #global client_socket, connection_status
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
                call_to_docker_server(current_state, 'say', "Hai effettuato il logout, inserisci un nome valido")
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in GAME_PREAMBLE state")   
                
        elif current_state == EXERCISES_PREAMBLE:
            # Handle POST requests in EXERCISES_PREAMBLE state if needed
            if self.path == "/api/exercise":
                # Transition to EXERCISE
                current_state = EXERCISES
                call_to_docker_server(current_state, 'say', "Alleniamoci!")
                print("Transitioned to EXERCISES.")
                for _ in range(8):
                    call_to_docker_server(current_state, 'move', "bigcircle;0.5")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to EXERCISES"
                }).encode('utf-8'))
                #audio_thread = threading.Thread(target=attempt_connection, daemon=True)
                while True:
                    print('nel while')
                    response = get_response()
                    print('response: '+response)
                    if 'STOP' in response or 'FERMA' in response:
                        current_state = CHOICE
                        print('stopped')
                        break
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

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": "Transitioned to EXERCISES"
                    }).encode('utf-8'))
                    i = 0
                    while i < 10:
                        call_to_docker_server(current_state, 'move', "bigcircle;"+str(0.5*(1/workload)))
                        if stress > 1.6 and i > 6:
                            break
                        
                        
            elif self.path == "/api/update_user_data":
                # Handle user data update
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                try:
                    data = json.loads(post_data) if post_data else {}
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Invalid JSON")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == current_user), None)
                if user:
                    user['last'] = data.get('last', user['last'])
                    user['avg'] = data.get('avg', user['avg'])
                    user['last_level'] = data.get('last_level', user['last_level'])
                    user['games_played'] = data.get('games_played', user.get('games_played', 0))
                    save_users(users)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": "User data updated successfully"
                    }).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"User not found")
                return

            
            elif self.path == "/api/choice":
                # Return to CHOICE
                current_state = CHOICE
                welcome_message = f"Ciao, {current_user}"
                call_to_docker_server(current_state, 'say', "Non vuoi piu allenarti?")
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
            elif self.path == "/api/introduction": 
                # Return to INTRODUCTION
                #global client_socket, connection_status
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
                call_to_docker_server(current_state, 'say', "Hai effettuato il logout, inserisci un nome valido")
                print("Returned to INTRODUCTION.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to INTRODUCTION"
                }).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Unknown endpoint in EXERCISES_PREAMBLE state")


        # probabilmente da togliere tutto
        elif current_state == EXERCISES:
            # Handle POST requests in GAME state if needed
            if self.path == "/api/exercise_preamble":
                current_state = EXERCISES_PREAMBLE
                print("Transitioned to EXERCISES PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to EXERCISES PREAMBLE"
                }).encode('utf-8'))


        elif current_state == GAME:
            # Handle POST requests in GAME state if needed
            if self.path == "/api/gamepreamble":
                current_state = GAME_PREAMBLE
                call_to_docker_server(current_state, 'say', "Non vuoi piu giocare?")
                print("Transitioned to GAME PREAMBLE.")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "message": "Transitioned to GAME PREAMBLE"
                }).encode('utf-8'))
            
            #elif self.path == "/api/rolling_averages":
                # Return rolling averages
                #with connection_lock:
                    #workload = rolling_avg_workload
                    #stress = rolling_avg_stress
                #self.send_response(200)
                #self.send_header("Content-Type", "application/json")
                #self.end_headers()
                #self.wfile.write(json.dumps({
                    #"rolling_avg_workload": workload,
                    #"rolling_avg_stress": stress
                #}).encode('utf-8'))
            
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

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": "Transitioned to EXERCISES"
                    }).encode('utf-8'))
                    i = 0
                    while i < 10:
                        call_to_docker_server(current_state, 'move', "bigcircle;"+str(0.5*(1/workload)))
                        if stress > 1.6 and i > 6:
                            break
                        
                        
            elif self.path == "/api/update_user_data":
                # Handle user data update
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                try:
                    data = json.loads(post_data) if post_data else {}
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Invalid JSON")
                    return

                users = load_users()
                user = next((u for u in users if u["name"] == current_user), None)
                if user:
                    user['last'] = data.get('last', user['last'])
                    user['avg'] = data.get('avg', user['avg'])
                    user['last_level'] = data.get('last_level', user['last_level'])
                    user['games_played'] = data.get('games_played', user.get('games_played', 0))
                    save_users(users)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "message": "User data updated successfully"
                    }).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"User not found")
                return
                
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