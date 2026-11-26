import socket
import threading

HOST = "127.0.0.1"
PORT = 5003

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender_connection=None):
    with clients_lock:
        disconnected_clients = []

        for connection in clients:
            if connection != sender_connection:
                try:
                    connection.sendall(message.encode("utf-8"))
                except OSError:
                    disconnected_clients.append(connection)

        for connection in disconnected_clients:
            username = clients.pop(connection, "Unknown")
            try:
                connection.close()
            except OSError:
                pass

            print(f"Удален отключенный пользователь: {username}")


def handle_client(connection, address):
    username = None

    try:
        username = connection.recv(1024).decode("utf-8").strip()

        if not username:
            connection.sendall(
                "Ошибка: имя пользователя не может быть пустым.\n"
                .encode("utf-8")
            )
            return

        with clients_lock:
            clients[connection] = username

        print(f"{username} подключился: {address}")

        connection.sendall(
            "Добро пожаловать в чат!\n"
            "Для выхода введите /exit\n"
            .encode("utf-8")
        )

        broadcast(
            f"[Система] {username} вошел в чат.\n",
            connection
        )

        while True:
            data = connection.recv(4096)

            if not data:
                break

            message = data.decode("utf-8").strip()

            if message == "/exit":
                break

            if message:
                full_message = f"{username}: {message}\n"

                print(full_message.strip())

                broadcast(
                    full_message,
                    connection
                )

    except (ConnectionResetError, OSError):
        pass

    finally:
        with clients_lock:
            if connection in clients:
                clients.pop(connection)

        try:
            connection.close()
        except OSError:
            pass

        if username:
            print(f"{username} вышел из чата.")

            broadcast(
                f"[Система] {username} вышел из чата.\n"
            )


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Chat server запущен на {HOST}:{PORT}")

while True:
    connection, address = server_socket.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(connection, address),
        daemon=True
    )

    thread.start()