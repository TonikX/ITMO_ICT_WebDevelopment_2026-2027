import socket


def calculate(a, b):
    return (a * a + b * b) ** 0.5

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5002))
server.listen()
print("TCP server started")

while True:
    connection, _ = server.accept()
    a, b = map(float, connection.recv(1024).decode().split())
    connection.sendall(str(calculate(a, b)).encode())
    connection.close()
