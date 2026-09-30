"""Многопользовательский TCP-чат с отдельным потоком на клиента."""

from __future__ import annotations

import argparse
import socket
import threading
from dataclasses import dataclass, field

from .protocol import receive_line, send_line


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
MAX_NAME_LENGTH = 40
ACCEPT_TIMEOUT_SECONDS = 0.2


@dataclass
class ChatServer:
    """TCP-сервер, который рассылает сообщения всем участникам чата."""

    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    _server: socket.socket | None = field(default=None, init=False, repr=False)
    _clients: dict[socket.socket, str] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )
    _lock: threading.Lock = field(
        default_factory=threading.Lock,
        init=False,
        repr=False,
    )
    _stopped: threading.Event = field(
        default_factory=threading.Event,
        init=False,
        repr=False,
    )

    @property
    def address(self) -> tuple[str, int]:
        """Вернуть фактический адрес сервера после привязки сокета."""
        if self._server is None:
            return self.host, self.port
        return self._server.getsockname()[:2]

    def start(self) -> None:
        """Создать, настроить и начать прослушивать серверный сокет."""
        if self._server is not None:
            raise RuntimeError("Сервер уже запущен")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()
        server.settimeout(ACCEPT_TIMEOUT_SECONDS)

        self._server = server
        self._stopped.clear()

    def serve_forever(self) -> None:
        """Принимать подключения до вызова :meth:`stop`."""
        if self._server is None:
            self.start()

        server = self._server
        assert server is not None
        print(f"Чат запущен: {self.address[0]}:{self.address[1]}")

        while not self._stopped.is_set():
            try:
                connection, _ = server.accept()
            except TimeoutError:
                continue
            except OSError:
                if self._stopped.is_set():
                    break
                raise

            client_thread = threading.Thread(
                target=self._handle_client,
                args=(connection,),
                daemon=True,
            )
            client_thread.start()

    def stop(self) -> None:
        """Остановить приём подключений и закрыть клиентские сокеты."""
        self._stopped.set()

        server = self._server
        if server is not None:
            try:
                server.close()
            except OSError:
                pass

        with self._lock:
            clients = list(self._clients)

        for client in clients:
            self._remove_client(client)

    def _broadcast(
        self,
        message: str,
        *,
        exclude: socket.socket | None = None,
    ) -> None:
        """Отправить сообщение всем подключённым клиентам, кроме указанного."""
        with self._lock:
            recipients = [
                client
                for client in self._clients
                if client is not exclude
            ]

        for client in recipients:
            try:
                send_line(client, message)
            except OSError:
                # Клиент мог отключиться между копированием списка и отправкой.
                self._remove_client(client)

    def _remove_client(self, connection: socket.socket) -> str | None:
        """Удалить клиента из реестра и безопасно закрыть его сокет."""
        with self._lock:
            name = self._clients.pop(connection, None)

        try:
            connection.close()
        except OSError:
            pass

        return name

    def _register_client(
        self,
        connection: socket.socket,
        raw_name: str | None,
    ) -> str | None:
        """Проверить имя и зарегистрировать клиента при отсутствии конфликта."""
        name = raw_name.strip() if raw_name is not None else ""
        if not name or len(name) > MAX_NAME_LENGTH:
            send_line(connection, "Некорректное имя.")
            return None

        with self._lock:
            if name in self._clients.values():
                send_line(connection, "Это имя уже занято.")
                return None
            self._clients[connection] = name

        return name

    def _handle_client(self, connection: socket.socket) -> None:
        """Обслуживать одного клиента до отключения или команды ``/quit``."""
        try:
            send_line(connection, "Введите имя:")
            name = self._register_client(connection, receive_line(connection))
            if name is None:
                return

            self._broadcast(
                f"* {name} присоединился к чату *",
                exclude=connection,
            )
            send_line(connection, "Подключение установлено. /quit — выйти.")

            while (message := receive_line(connection)) is not None:
                if message == "/quit":
                    break
                if message:
                    self._broadcast(f"{name}: {message}", exclude=connection)
        except (OSError, UnicodeDecodeError, ValueError):
            # Разрыв соединения и повреждённое сообщение завершают сессию клиента.
            pass
        finally:
            removed_name = self._remove_client(connection)
            if removed_name:
                self._broadcast(f"* {removed_name} покинул чат *")


def main() -> None:
    """Прочитать аргументы командной строки и запустить сервер чата."""
    parser = argparse.ArgumentParser(description="Многопользовательский TCP-чат")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    server = ChatServer(args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
