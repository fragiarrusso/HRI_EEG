import socket
import json
import threading 

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 12345))  # '0.0.0.0' permette connessioni da qualsiasi indirizzo
server_socket.listen(5)

def handle_connection(client_socket, addr):
    try:
        print("receiving...")
        while True:
            received = client_socket.recv(1024)
            if not received:
                break

            received = received.decode('UTF-8')
            received = json.loads(received)
            data = {str(k): str(v) for k, v in received.items()}
            
            print(f"received: {data}")

            response = data

            response = json.dumps(response)
            client_socket.sendall(b'Done')
    except:
        print("Released ", addr)
        client_socket.close()

    
    return

while True:
    try:
        client_socket, addr = server_socket.accept()
        print("Connected by", addr)
        client_handler = threading.Thread(target=handle_connection, args=(client_socket, addr,))
        client_handler.start()
    except:
        print("Crashed")
    
    