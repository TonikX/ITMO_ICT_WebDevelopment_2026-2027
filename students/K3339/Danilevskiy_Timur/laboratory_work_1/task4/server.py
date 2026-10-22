"""Задание 4. Многопользовательский TCP-чат: сервер.

Каждый клиент обслуживается в отдельном потоке. Сообщения передаются
строками, разделёнными символом "\n".

Протокол регистрации: клиент присылает имя, сервер отвечает
NAME_OK, NAME_TAKEN (имя занято) или NAME_EMPTY (пустое имя).
После регистрации доступны команды /users и /exit.
"""
import socket
import threading

HOST = "127.0.0.1"
PORT = 9092

clients = {}  # сокет клиента -> имя пользователя
clients_lock = threading.Lock()


def send_line(conn, text):
    conn.sendall((text + "\n").encode("utf-8"))


def broadcast(text, exclude=None):
    """Отправляет сообщение всем подключённым, кроме exclude."""
    with clients_lock:
        recipients = [conn for conn in clients if conn is not exclude]
    for conn in recipients:
        try:
            send_line(conn, text)
        except OSError:
            pass  # клиент отключился — его удалит собственный поток


def register(conn, reader):
    """Запрашивает имя, пока клиент не пришлёт свободное. Возвращает имя или None."""
    for line in reader:
        name = line.strip()
        if not name:
            send_line(conn, "NAME_EMPTY")
            continue

        with clients_lock:
            is_taken = name in clients.values()
            if not is_taken:
                clients[conn] = name

        if is_taken:
            send_line(conn, "NAME_TAKEN")
            continue
        send_line(conn, "NAME_OK")
        return name
    return None  # клиент отключился, не выбрав имя


def handle_client(conn, addr):
    reader = conn.makefile("r", encoding="utf-8")
    name = None
    try:
        name = register(conn, reader)
        if name is None:
            return

        print(f"{name} подключился ({addr[0]}:{addr[1]})")
        send_line(conn, f"* Добро пожаловать, {name}! Команды: /users — участники, /exit — выход")
        broadcast(f"* {name} вошёл в чат", exclude=conn)

        for line in reader:
            message = line.strip()
            if not message:
                continue
            if message == "/exit":
                break
            if message == "/users":
                with clients_lock:
                    names = ", ".join(clients.values())
                send_line(conn, f"* Сейчас в чате: {names}")
                continue

            print(f"[{name}]: {message}")
            broadcast(f"[{name}]: {message}", exclude=conn)
    except (OSError, UnicodeDecodeError):
        pass  # соединение оборвалось — просто удаляем клиента
    finally:
        with clients_lock:
            clients.pop(conn, None)
        reader.close()
        conn.close()
        if name:
            print(f"{name} отключился")
            broadcast(f"* {name} вышел из чата")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Сервер чата запущен на {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            # daemon=True — потоки клиентов не мешают завершить сервер по Ctrl+C
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
