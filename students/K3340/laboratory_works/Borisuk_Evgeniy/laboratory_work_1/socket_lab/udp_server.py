"""UDP-сервер для обмена приветствиями из задания №1."""

from __future__ import annotations

import argparse
import socket


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8001
BUFFER_SIZE = 1024
CLIENT_GREETING = "Hello, server"
SERVER_GREETING = "Hello, client"


def serve_once(server: socket.socket) -> tuple[str, tuple[str, int]]:
    """Принять одно UDP-сообщение, ответить клиенту и вернуть его данные."""
    payload, client_address = server.recvfrom(BUFFER_SIZE)
    message = payload.decode("utf-8")
    print(f"Получено от клиента: {message}")

    server.sendto(SERVER_GREETING.encode("utf-8"), client_address)
    return message, client_address


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Создать UDP-сокет и выполнить один обязательный обмен сообщениями."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((host, port))
        print(f"UDP-сервер запущен: {host}:{port}")
        serve_once(server)


def main() -> None:
    """Прочитать адрес из аргументов и запустить UDP-сервер."""
    parser = argparse.ArgumentParser(description="UDP-сервер приветствий")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
