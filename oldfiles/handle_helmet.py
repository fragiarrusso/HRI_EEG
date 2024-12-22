import threading
import socket

class handle_helmet:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT

    def connect_to_server(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.IP, self.PORT))
            print(f"Connected to server at {self.IP}:{self.PORT}")
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                print(f"Received: {message}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def start_client_thread(self):
        client_thread = threading.Thread(target=self.connect_to_server)
        client_thread.start()
