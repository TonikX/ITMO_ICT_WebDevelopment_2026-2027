import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
    client_socket.sendto(b'Hello, server', ('127.0.0.1', 8001))
    message, peer_address = client_socket.recvfrom(4096)
    print(message.decode('utf-8'))
