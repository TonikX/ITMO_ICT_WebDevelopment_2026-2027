import socket
from utils import calculate

HOST = '127.0.0.1'
PORT = 12345


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"TCP Математический сервер запущен на {HOST}:{PORT}...")

while True:
    conn, addr = server_socket.accept()
    data = conn.recv(1024).decode('utf-8')
    if data:
        parts = data.strip().split()
        variant = int(parts[0])
        params = parts[1:]
        result = calculate(variant, params)
        conn.send(result.encode('utf-8'))
    conn.close()