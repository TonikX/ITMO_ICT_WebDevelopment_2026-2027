"""TCP-клиент площади треугольника для варианта №2 задания №2."""

from __future__ import annotations

import argparse
import socket

from .math_server import DEFAULT_HOST, DEFAULT_PORT
from .protocol import receive_line, send_line


def request_triangle_area(
    host: str,
    port: int,
    base: float,
    height: float,
) -> str:
    """Передать основание и высоту TCP-серверу и вернуть его ответ."""
    with socket.create_connection((host, port)) as connection:
        send_line(connection, f"{base} {height}")
        response = receive_line(connection)

    if response is None:
        raise ConnectionError("Сервер закрыл соединение без ответа")
    return response


def main() -> None:
    """Запросить параметры треугольника и вывести результат сервера."""
    parser = argparse.ArgumentParser(
        description="TCP-клиент площади треугольника, вариант №2"
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    try:
        base = float(input("Введите основание треугольника: "))
        height = float(input("Введите высоту треугольника: "))
        response = request_triangle_area(args.host, args.port, base, height)
    except ValueError:
        parser.exit(status=1, message="Основание и высота должны быть числами.\n")
    except OSError as error:
        parser.exit(status=1, message=f"Ошибка TCP-соединения: {error}\n")

    print(response)


if __name__ == "__main__":
    main()
