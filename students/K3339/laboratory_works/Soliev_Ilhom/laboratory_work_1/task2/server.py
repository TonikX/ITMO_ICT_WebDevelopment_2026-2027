import socket

HOST = "127.0.0.1"
PORT = 9090

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()

    while True:
        connection, address = server.accept()
        with connection:
            base, height = map(float, connection.recv(1024).decode().split())
            area = base * height
            connection.sendall(str(area).encode())
