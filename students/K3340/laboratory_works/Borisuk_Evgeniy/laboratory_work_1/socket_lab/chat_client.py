"""Консольный клиент многопользовательского TCP-чата."""

from __future__ import annotations

import argparse
import socket
import threading

from .chat_server import DEFAULT_HOST, DEFAULT_PORT
from .protocol import receive_line, send_line


def _receive_messages(connection: socket.socket) -> None:
    """Получать сообщения сервера, пока соединение не будет закрыто."""
    try:
        while (message := receive_line(connection)) is not None:
            print(message)
    except (OSError, UnicodeDecodeError, ValueError):
        # Сервер закрыл соединение или прислал некорректное сообщение.
        return


def run_client(host: str, port: int) -> None:
    """Подключиться к серверу и передавать ему строки из консоли."""
    with socket.create_connection((host, port)) as connection:
        listener = threading.Thread(
            target=_receive_messages,
            args=(connection,),
            daemon=True,
        )
        listener.start()

        try:
            while True:
                message = input()
                send_line(connection, message)
                if message == "/quit":
                    break
        except (EOFError, KeyboardInterrupt):
            try:
                send_line(connection, "/quit")
            except OSError:
                pass


def main() -> None:
    """Прочитать адрес сервера и запустить консольный клиент."""
    parser = argparse.ArgumentParser(description="Клиент TCP-чата")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    try:
        run_client(args.host, args.port)
    except OSError as error:
        parser.exit(status=1, message=f"Не удалось подключиться: {error}\n")


if __name__ == "__main__":
    main()
