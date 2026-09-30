import socket
import threading


HOST = "127.0.0.1"
PORT = 5002

clients: dict[socket.socket, str] = {}
clients_lock = threading.Lock()


def send_message(connection: socket.socket, message: str) -> None:
    connection.sendall(f"{message}\n".encode("utf-8"))


def disconnect_client(connection: socket.socket) -> str | None:
    with clients_lock:
        username = clients.pop(connection, None)

    try:
        connection.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    connection.close()
    return username


def broadcast(message: str, sender: socket.socket | None = None) -> None:
    with clients_lock:
        recipients = [
            connection for connection in clients if connection is not sender
        ]

    for connection in recipients:
        try:
            send_message(connection, message)
        except OSError:
            disconnect_client(connection)


def handle_client(connection: socket.socket, address: tuple[str, int]) -> None:
    username: str | None = None

    try:
        reader = connection.makefile("r", encoding="utf-8")
        username = reader.readline().strip()
        if not username:
            return

        with clients_lock:
            clients[connection] = username

        print(f"{username} connected from {address}")
        send_message(connection, "Вы подключились к чату. Команда /exit — выход.")
        broadcast(f"* {username} вошёл в чат", sender=connection)

        for line in reader:
            message = line.rstrip("\n")
            if message == "/exit":
                break
            if message:
                print(f"{username}: {message}")
                broadcast(f"{username}: {message}", sender=connection)
    except (ConnectionError, OSError, UnicodeError):
        pass
    finally:
        disconnected_username = disconnect_client(connection)
        if disconnected_username:
            print(f"{disconnected_username} left the chat")
            broadcast(f"* {disconnected_username} вышел из чата")


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Chat server is running on {HOST}:{PORT}")

        try:
            while True:
                connection, address = server_socket.accept()
                threading.Thread(
                    target=handle_client,
                    args=(connection, address),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            print("\nChat server stopped")
        finally:
            with clients_lock:
                active_connections = list(clients)
            for connection in active_connections:
                disconnect_client(connection)


if __name__ == "__main__":
    main()
