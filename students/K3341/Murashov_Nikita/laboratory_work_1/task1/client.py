"""UDP-клиент задания 1.

Отправляет ``Hello, server`` и печатает ответ сервера.
"""

import socket

HOST = "127.0.0.1"
PORT = 11001


def main() -> None:
    """Отправляет сообщение серверу и печатает ответ.

    Args:
        None.

    Returns:
        None.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(b"Hello, server", (HOST, PORT))
        data, _ = sock.recvfrom(1024)
        print(data.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
