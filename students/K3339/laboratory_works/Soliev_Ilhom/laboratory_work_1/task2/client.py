import socket

SERVER_ADDRESS = ("127.0.0.1", 9090)

base = float(input("Base: "))
height = float(input("Height: "))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(SERVER_ADDRESS)
    client.sendall(f"{base} {height}".encode())
    print(client.recv(1024).decode())
