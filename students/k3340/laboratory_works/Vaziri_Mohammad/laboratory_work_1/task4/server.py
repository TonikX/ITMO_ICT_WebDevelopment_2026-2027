"""Задание 4. Многопользовательский чат: TCP + threading.

Каждый клиент обслуживается в отдельном потоке. Сервер хранит словарь
{сокет: имя} и рассылает каждое сообщение всем остальным участникам.
Команда /exit — выход из чата.
"""
import socket
import threading

HOST, PORT = "127.0.0.1", 9094
clients: dict[socket.socket, str] = {}
lock = threading.Lock()                           # словарь клиентов меняют разные потоки


def broadcast(message: str, sender: socket.socket | None = None) -> None:
    with lock:
        targets = [c for c in clients if c is not sender]
    for client in targets:
        try:
            client.sendall((message + "\n").encode("utf-8"))
        except OSError:
            remove(client)


def remove(conn: socket.socket) -> None:
    with lock:
        name = clients.pop(conn, None)
    if name is not None:
        conn.close()
        broadcast(f"* {name} вышел из чата")
        print(f"{name} отключился")


def handle(conn: socket.socket) -> None:
    try:
        name = conn.recv(1024).decode("utf-8").strip() or "Аноним"   # первое сообщение — имя
        with lock:
            clients[conn] = name
        conn.sendall(f"Добро пожаловать, {name}! Для выхода введите /exit\n".encode("utf-8"))
        broadcast(f"* {name} присоединился к чату", conn)
        print(f"{name} подключился")
        while True:
            data = conn.recv(1024)
            if not data:                            # клиент закрыл соединение
                break
            text = data.decode("utf-8").strip()
            if text == "/exit":
                break
            if text:
                broadcast(f"[{name}]: {text}", conn)
    except OSError:
        pass
    finally:
        remove(conn)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"Чат-сервер слушает {HOST}:{PORT}")
        while True:
            conn, _ = srv.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()
