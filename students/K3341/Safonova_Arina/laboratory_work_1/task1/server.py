import socket

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    server_socket.bind(('127.0.0.1', 8001))
    print('UDP-сервер: порт 8001', flush=True)

    while True:
        message, peer_address = server_socket.recvfrom(4096)
        print(message.decode('utf-8'), flush=True)
        server_socket.sendto(b'Hello, client', peer_address)
