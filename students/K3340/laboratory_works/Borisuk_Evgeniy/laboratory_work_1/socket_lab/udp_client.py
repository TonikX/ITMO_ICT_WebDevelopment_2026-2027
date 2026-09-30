"""UDP-клиент для обмена приветствиями из задания №1."""

from __future__ import annotations

import argparse
import socket

from .udp_server import (
    BUFFER_SIZE,
    CLIENT_GREETING,
    DEFAULT_HOST,
    DEFAULT_PORT,
)


DEFAULT_TIMEOUT_SECONDS = 3.0


def exchange_greetings(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Отправить ``Hello, server`` и вернуть ответ UDP-сервера."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(timeout)
        client.sendto(CLIENT_GREETING.encode("utf-8"), (host, port))
        payload, _ = client.recvfrom(BUFFER_SIZE)
        return payload.decode("utf-8")


def main() -> None:
    """Прочитать адрес сервера, выполнить обмен и вывести ответ."""
    parser = argparse.ArgumentParser(description="UDP-клиент приветствий")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    try:
        response = exchange_greetings(args.host, args.port)
    except (OSError, TimeoutError) as error:
        parser.exit(status=1, message=f"Ошибка UDP-обмена: {error}\n")

    print(response)


if __name__ == "__main__":
    main()
