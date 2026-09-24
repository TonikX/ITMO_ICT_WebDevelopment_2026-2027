import socket
import threading

HOST = 'localhost'
PORT = 9004

# username -> connection
clients = {}
clients_lock = threading.Lock()


def broadcast(message: str, exclude_username: str = None):
    """Рассылает сообщение всем клиентам, кроме exclude_username."""
    with clients_lock:
        for username, conn in list(clients.items()):
            if username == exclude_username:
                continue
            try:
                conn.sendall(message.encode('utf-8'))
            except OSError:
                pass


def handle_client(conn: socket.socket, addr):
    username = None
    try:
        conn.sendall("Введите имя пользователя: ".encode('utf-8'))
        username = conn.recv(1024).decode('utf-8').strip()

        with clients_lock:
            clients[username] = conn

        print(f"{username} ({addr}) присоединился к чату")
        broadcast(f"* {username} присоединился к чату", exclude_username=username)
        conn.sendall(f"Добро пожаловать, {username}! Введите /exit для выхода.\n".encode('utf-8'))

        while True:
            data = conn.recv(1024)
            if not data:
                break
            text = data.decode('utf-8').strip()
            if not text:
                continue
            if text == '/exit':
                break

            print(f"{username}: {text}")
            broadcast(f"{username}: {text}", exclude_username=username)

    except (ConnectionResetError, OSError):
        pass
    finally:
        if username:
            with clients_lock:
                clients.pop(username, None)
            print(f"{username} покинул чат")
            broadcast(f"* {username} покинул чат", exclude_username=username)
        conn.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    print(f"Чат-сервер запущен на {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == '__main__':
    main()
