"""Многопользовательский TCP-чат: клиент.

Один скрипт запускается каждым пользователем отдельно.
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 11004


def listen(sock: socket.socket) -> None:
    """Печатает входящие сообщения сервера.

    Args:
        sock: Подключённый к чату сокет.

    Returns:
        None.
    """
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            print("Сервер закрыл соединение")
            break
        print(data.decode("utf-8", errors="replace").rstrip())


def main() -> None:
    """Подключается к чату, читает ввод и отправляет его серверу.

    Args:
        None.

    Returns:
        None. Выход по ``/exit``.
    """
    name = input("Имя: ").strip()
    if not name:
        print("Нужно имя")
        return
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(name.encode("utf-8"))
        threading.Thread(target=listen, args=(sock,), daemon=True).start()
        while True:
            try:
                text = input()
            except EOFError:
                break
            sock.sendall(text.encode("utf-8"))
            if text.strip() == "/exit":
                break


if __name__ == "__main__":
    main()
