import socket
import threading


HOST = "127.0.0.1"
PORT = 5002
ENCODING = "utf-8"


class ChatServer:
    def __init__(self) -> None:
        self._clients: dict[socket.socket, str] = {}
        self._clients_lock = threading.Lock()

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            print(f"TCP-чат запущен на {HOST}:{PORT}")
            print("Ожидание подключений...")

            try:
                while True:
                    client_socket, client_address = server_socket.accept()

                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True,
                    )
                    thread.start()
            except KeyboardInterrupt:
                print("\nСервер остановлен")

    def _handle_client(
        self,
        client_socket: socket.socket,
        client_address: tuple[str, int],
    ) -> None:
        username = None

        try:
            reader = client_socket.makefile(
                "r",
                encoding=ENCODING,
                newline="\n",
            )

            username = reader.readline().strip()

            if not username:
                self._send(client_socket, "ERROR: Имя пользователя не указано")
                return

            with self._clients_lock:
                if username in self._clients.values():
                    self._send(
                        client_socket,
                        "ERROR: Пользователь с таким именем уже подключён",
                    )
                    return

                self._clients[client_socket] = username

            self._send(
                client_socket,
                f"OK Добро пожаловать в чат, {username}!",
            )

            print(f"Подключён пользователь {username}: {client_address}")

            self._broadcast(
                f"[Система] Пользователь {username} вошёл в чат",
                exclude=client_socket,
            )

            for line in reader:
                message = line.rstrip("\n")

                if message == "/exit":
                    break

                if not message:
                    continue

                print(f"{username}: {message}")

                self._broadcast(
                    f"{username}: {message}",
                    exclude=client_socket,
                )

        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            disconnected = False

            with self._clients_lock:
                if client_socket in self._clients:
                    del self._clients[client_socket]
                    disconnected = True

            client_socket.close()

            if disconnected and username is not None:
                print(f"Пользователь {username} отключился")

                self._broadcast(
                    f"[Система] Пользователь {username} вышел из чата"
                )

    def _broadcast(
        self,
        message: str,
        exclude: socket.socket | None = None,
    ) -> None:
        with self._clients_lock:
            recipients = [
                client_socket
                for client_socket in self._clients
                if client_socket is not exclude
            ]

        for client_socket in recipients:
            try:
                self._send(client_socket, message)
            except OSError:
                pass

    @staticmethod
    def _send(client_socket: socket.socket, message: str) -> None:
        client_socket.sendall(
            f"{message}\n".encode(ENCODING)
        )


if __name__ == "__main__":
    ChatServer().run()