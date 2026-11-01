"""TCP-сервер задания 2, вариант 1: теорема Пифагора.

Протокол: клиент присылает ``a b`` (два катета через пробел),
сервер возвращает гипотенузу текстом.
"""

import math
import socket

HOST = "127.0.0.1"
PORT = 11002


def hypotenuse(a: float, b: float) -> float:
    """Вычисляет гипотенузу по двум катетам.

    Args:
        a: Длина первого катета.
        b: Длина второго катета.

    Returns:
        Длина гипотенузы.

    Raises:
        ValueError: Если хотя бы один катет не положителен.
    """
    if a <= 0 or b <= 0:
        raise ValueError("катеты должны быть > 0")
    return math.hypot(a, b)


def answer(payload: str) -> str:
    """Строит ответ на сырую строку клиента.

    Args:
        payload: Строка вида ``a b``.

    Returns:
        Строка с результатом или текстом ошибки.
    """
    try:
        a, b = (float(p) for p in payload.split())
        return f"{hypotenuse(a, b):.4f}"
    except ValueError as exc:
        return f"error: {exc}"


def main() -> None:
    """Запускает TCP-сервер.

    Args:
        None.

    Returns:
        None. Обслуживает клиентов по очереди бесконечно.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"TCP сервер: {HOST}:{PORT}")
        while True:
            conn, addr = sock.accept()
            with conn:
                data = conn.recv(1024).decode("utf-8", errors="replace")
                print(f"{addr}: {data.strip()}")
                conn.sendall(answer(data).encode("utf-8"))


if __name__ == "__main__":
    main()
