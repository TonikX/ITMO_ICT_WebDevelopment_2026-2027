from __future__ import annotations

import socket
import threading

HOST = "127.0.0.1"
PORT = 8084
BUFFER_SIZE = 1024

clients: dict[socket.socket, str] = {}
clients_lock = threading.Lock()


def broadcast(message: str, sender: socket.socket | None = None) -> None:
    payload = message.encode("utf-8")
    with clients_lock:
        dead: list[socket.socket] = []
        for conn in clients:
            if conn is sender:
                continue
            try:
                conn.sendall(payload)
            except OSError:
                dead.append(conn)
        for conn in dead:
            clients.pop(conn, None)
            try:
                conn.close()
            except OSError:
                pass


def handle_client(conn: socket.socket, address: tuple[str, int]) -> None:
    nickname = f"user_{address[1]}"
    with clients_lock:
        clients[conn] = nickname

    try:
        conn.sendall(
            (
                "Добро пожаловать в чат.\n"
                "Сначала отправьте никнейм одной строкой.\n"
                "Команда /exit — выход.\n"
            ).encode("utf-8")
        )
        raw_nick = conn.recv(BUFFER_SIZE)
        if not raw_nick:
            return
        nickname = raw_nick.decode("utf-8").strip() or nickname
        with clients_lock:
            clients[conn] = nickname

        join_msg = f"[сервер] {nickname} вошёл в чат"
        print(join_msg)
        broadcast(join_msg + "\n", sender=conn)
        conn.sendall(f"Вы вошли как {nickname}\n".encode("utf-8"))

        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            text = data.decode("utf-8").strip()
            if not text:
                continue

            if text == "/exit":
                conn.sendall("Вы вышли из чата.\n".encode("utf-8"))
                break

            message = f"{nickname}: {text}\n"
            print(message.strip())
            broadcast(message, sender=conn)
    except OSError:
        pass
    finally:
        with clients_lock:
            left_name = clients.pop(conn, nickname)
        leave_msg = f"[сервер] {left_name} покинул чат"
        print(leave_msg)
        broadcast(leave_msg + "\n")
        try:
            conn.close()
        except OSError:
            pass


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(10)
        print(f"Чат-сервер на {HOST}:{PORT}")

        while True:
            conn, address = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    main()
