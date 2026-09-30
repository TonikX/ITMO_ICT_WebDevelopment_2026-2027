import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8002))
    server_socket.listen()
    print('TCP-сервер: порт 8002', flush=True)

    while True:
        peer, peer_address = server_socket.accept()
        with peer, peer.makefile('r', encoding='utf-8') as stream:
            base, height = map(float, stream.readline().split())
            area = base * height
            peer.sendall(f'Площадь параллелограмма: {area:g}\n'.encode('utf-8'))
