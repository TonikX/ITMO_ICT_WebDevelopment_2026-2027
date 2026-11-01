"""Многопользовательский TCP-чат: сервер.

Держит ``имя -> сокет`` и рассылает сообщения всем, кроме автора.
"""

import socket
import threading

HOST = "127.0.0.1"
PORT = 11004

clients: dict[str, socket.socket] = {}
lock = threading.Lock()


def send_all(text: str, skip: str = "") -> None:
    """Рассылает текст всем клиентам, кроме skip.

    Args:
        text: Сообщение для рассылки.
        skip: Имя пользователя, которому не отправлять.

    Returns:
        None.
    """
    with lock:
        dead = []
        for name, conn in clients.items():
            if name == skip:
                continue
            try:
                conn.sendall((text + "\n").encode("utf-8"))
            except OSError:
                dead.append(name)
        for name in dead:
            clients.pop(name, None)


def handle(conn: socket.socket) -> None:
    """Обслуживает одного клиента в отдельном потоке.

    Args:
        conn: Сокет подключённого клиента. Первой строкой ждёт имя.

    Returns:
        None.
    """
    name = ""
    try:
        name = conn.recv(1024).decode("utf-8", errors="replace").strip()
        if not name:
            return
        with lock:
            clients[name] = conn
        send_all(f"* {name} в чате", skip=name)
        conn.sendall(f"Привет, {name}! /exit — выйти\n".encode("utf-8"))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            text = data.decode("utf-8", errors="replace").strip()
            if not text:
                continue
            if text == "/exit":
                break
            send_all(f"{name}: {text}", skip=name)
    except OSError:
        pass
    finally:
        if name:
            with lock:
                clients.pop(name, None)
            send_all(f"* {name} вышел")
        conn.close()


def main() -> None:
    """Запускает чат-сервер.

    Args:
        None.

    Returns:
        None. Каждое подключение уходит в свой поток.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(10)
        print(f"Чат: {HOST}:{PORT}")
        while True:
            conn, _ = sock.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
