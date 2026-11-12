import socket
from math import sqrt

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.bind(('localhost', 8080))
socket_server.listen(1)

print('Server is listening on port 8080...')

def calculate(a, b):
    return float(sqrt(a**2 + b**2))


while True:
    client_connection, address = socket_server.accept()
    data = b""

    while b"\n" not in data:
        request = client_connection.recv(1024)

        if request == b'':
            break

        data += request

    if b"\n" not in data:
        client_connection.close()
        break
    
    line = data.split(b"\n", 1)[0]
    a, b = line.decode("utf-8").split()

    print(f'Received request from {address}: {a,b}')

    response = str(calculate(float(a), float(b)))
    client_connection.sendall(f"result: {response}\n".encode("utf-8"))

    client_connection.close()
    break

socket_server.close()

