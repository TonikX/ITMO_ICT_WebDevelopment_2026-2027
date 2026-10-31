import socket
import threading

HOST = 'localhost'
PORT = 9090

clients = {}
clients_lock = threading.Lock()


def broadcast(message, excluded_username=None):
    encoded_message = message.encode('utf-8')
    with clients_lock:
        receviers = [
            (username, client_socket, send_lock)
            for username, (client_socket, send_lock) in clients.items()
            if username != excluded_username
        ]

    for _, client_socket, send_lock in receviers:
        try:
            with send_lock:
                client_socket.sendall(encoded_message)
        except:
            pass


def handle_client(client_socket, address):
    username = None
    reader = client_socket.makefile('r', encoding='utf-8')

    try:
        client_socket.sendall(b'Enter your username:\n')
        username = reader.readline().strip()

        with clients_lock:
            if username and username not in clients:
                client_send_lock = threading.Lock()
                client_socket.sendall(
                    f'Welcome {username}! You can start chatting now.\n'.encode('utf-8')
                )
                clients[username] = (client_socket, client_send_lock)
                username_is_available = True
            else:
                username_is_available = False

        if not username_is_available:
            client_socket.sendall(b'Username is empty or already in use.\n')
            return

        print(f'{username} connected from {address}')
        broadcast(f'{username} joined the chat.\n', excluded_username=username)

        for line in reader:
            message = line.strip()
            if message.lower() == 'exit':
                client_socket.sendall(b'You have left the chat.\n')
                break
            if message:
                broadcast(f'{username}: {message}\n', excluded_username=username)
    except (ConnectionError, OSError) as error:
        print(f'Connection with {address} ended: {error}')
    finally:
        if username:
            with clients_lock:
                client = clients.get(username)
                if client and client[0] is client_socket:
                    del clients[username]
                    broadcast_disconnect = True
                else:
                    broadcast_disconnect = False
            if broadcast_disconnect:
                broadcast(f'{username} left the chat.\n')
                print(f'{username} has disconnected.')

        reader.close()
        client_socket.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Server is listening on {HOST}:{PORT}...')

        while True:
            client_socket, address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True,
            )
            client_thread.start()


if __name__ == '__main__':
    main()