"""TCP-сервер площади треугольника для варианта №2 задания №2."""

from __future__ import annotations

import argparse
import socket

from .protocol import receive_line, send_line


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8002


def calculate_triangle_area(base: float, height: float) -> float:
    """Вычислить площадь треугольника по положительным основанию и высоте."""
    if base <= 0 or height <= 0:
        raise ValueError("Основание и высота должны быть положительными")
    return base * height / 2


def process_request(request: str) -> str:
    """Преобразовать строку ``основание высота`` в строку с результатом."""
    parts = request.split()
    if len(parts) != 2:
        return "ERROR: введите основание и высоту через пробел"

    try:
        base, height = map(float, parts)
        area = calculate_triangle_area(base, height)
    except ValueError as error:
        return f"ERROR: {error}"

    return f"Площадь треугольника: {area:g}"


def handle_client(connection: socket.socket) -> None:
    """Принять один запрос клиента и отправить результат вычисления."""
    request = receive_line(connection)
    if request is not None:
        send_line(connection, process_request(request))


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Принимать TCP-подключения и вычислять площадь для каждого клиента."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"TCP-сервер варианта №2 запущен: {host}:{port}")

        while True:
            connection, _ = server.accept()
            with connection:
                try:
                    handle_client(connection)
                except (OSError, UnicodeDecodeError, ValueError):
                    # Некорректный или оборванный запрос завершает это подключение.
                    continue


def main() -> None:
    """Прочитать адрес из аргументов и запустить TCP-сервер."""
    parser = argparse.ArgumentParser(
        description="TCP-сервер площади треугольника, вариант №2"
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        print("\nСервер остановлен.")


if __name__ == "__main__":
    main()
