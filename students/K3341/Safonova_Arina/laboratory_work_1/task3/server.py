import socket
from pathlib import Path

PAGE = Path(__file__).with_name('index.html')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8003))
    server_socket.listen(5)
    print('Откройте http://127.0.0.1:8003', flush=True)

    while True:
        peer, peer_address = server_socket.accept()
        with peer:
            peer.settimeout(5)
            try:
                with peer.makefile('rb') as incoming:
                    if not incoming.readline():
                        continue
                    while incoming.readline() not in (b'\r\n', b'\n', b''):
                        pass

                content = PAGE.read_bytes()
                header_data = (
                    'HTTP/1.1 200 OK\r\n'
                    'Content-Type: text/html; charset=utf-8\r\n'
                    f'Content-Length: {len(content)}\r\n'
                    'Connection: close\r\n\r\n'
                )
                peer.sendall(header_data.encode('ascii') + content)
            except OSError as error:
                print('Ошибка соединения:', error)
