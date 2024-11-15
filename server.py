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
