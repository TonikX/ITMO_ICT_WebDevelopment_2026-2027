import socket
import threading

users = {}
users_lock = threading.Lock()

def send_to_all(message, sender):
    data = (message + '\n').encode('utf-8')
    with users_lock:
        for peer in users:
            if peer != sender:
                try:
                    peer.sendall(data)
                except OSError:
                    pass

def handle_client(peer, peer_address):
    try:
        with peer, peer.makefile('r', encoding='utf-8') as stream:
            name = stream.readline().strip()
            if not name:
                return
            name = f'{name} ({peer_address[1]})'
            with users_lock:
                users[peer] = name

            for line in stream:
                message = line.rstrip('\r\n')
                if message == '/exit':
                    break
                if message:
                    send_to_all(f'{name}: {message}', peer)
    except (OSError, UnicodeError):
        pass
    finally:
        with users_lock:
            users.pop(peer, None)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8004))
    server_socket.listen()
    print('Чат: порт 8004', flush=True)
    while True:
        peer, peer_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(peer, peer_address), daemon=True).start()
