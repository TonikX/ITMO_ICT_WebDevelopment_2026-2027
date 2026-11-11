"""Задание 4: многопользовательский TCP-чат с потоками."""
import socket
import threading

HOST = "127.0.0.1"
PORT = 5004
ENCODING = "utf-8"

clients = {}
clients_lock = threading.Lock()

def send_line(connection, message):
    connection.sendall((message + "\n").encode(ENCODING))

def broadcast(message, exclude=None):
    with clients_lock:
        recipients = list(clients.keys())

    failed = []
    for connection in recipients:
        if connection is exclude:
            continue
        try:
            send_line(connection, message)
        except OSError:
            failed.append(connection)

    for connection in failed:
        remove_client(connection, announce=False)

def remove_client(connection, announce=True):
    with clients_lock:
        username = clients.pop(connection, None)
    try:
        connection.close()
    except OSError:
        pass
    if username and announce:
        print(f"{username} отключился.")
        broadcast(f"[Система] {username} вышел из чата.")

def handle_client(connection, address):
    username = None
    try:
        send_line(connection, "Введите имя пользователя:")
        reader = connection.makefile("r", encoding=ENCODING, newline="\n")
        username = reader.readline().strip()
        if not username:
            username = f"Гость-{address[1]}"

        # Убираем переводы строк и ограничиваем длину имени.
        username = username.replace("\r", "").replace("\n", "")[:24]
        with clients_lock:
            clients[connection] = username

        print(f"{username} подключился с адреса {address}")
        send_line(connection, f"[Система] Добро пожаловать, {username}! Для выхода введите /quit.")
        broadcast(f"[Система] {username} присоединился к чату.", exclude=connection)

        while True:
            line = reader.readline()
            if not line:
                break
            message = line.rstrip("\r\n")
            if message.strip().lower() == "/quit":
                break
            if not message.strip():
                continue
            if len(message) > 1000:
                message = message[:1000]
            formatted = f"{username}: {message}"
            print(formatted)
            broadcast(formatted)
        reader.close()
    except (OSError, UnicodeError) as error:
        print(f"Ошибка клиента {address}: {error}")
    finally:
        remove_client(connection)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"TCP-чат запущен на {HOST}:{PORT}")
        try:
            while True:
                connection, address = server.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(connection, address),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            print("\nОстанавливаю сервер...")

if __name__ == "__main__":
    main()
