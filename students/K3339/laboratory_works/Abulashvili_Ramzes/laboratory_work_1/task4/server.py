import socket
import threading

HOST = "127.0.0.1"
PORT = 5004
clients = {}
clients_lock = threading.Lock()


def disconnect(connection):
    with clients_lock:
        client = clients.pop(connection, None)
    try:
        connection.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    connection.close()
    return client


def broadcast(message, sender=None):
    data = (message + "\n").encode("utf-8")
    with clients_lock:
        receivers = list(clients.items())
    for connection, (name, send_lock) in receivers:
        if connection is sender:
            continue
        try:
            with send_lock:
                connection.sendall(data)
        except OSError:
            disconnect(connection)


def handle_client(connection):
    name = ""
    try:
        with connection.makefile("r", encoding="utf-8", newline="\n") as reader:
            name = reader.readline().strip()
            if not name:
                return
            with clients_lock:
                clients[connection] = (name, threading.Lock())
            print(f"Подключился: {name}")
            broadcast(f"{name} вошёл в чат.", connection)
            while True:
                line = reader.readline()
                if not line:
                    break
                message = line.rstrip("\r\n")
                if message == "/exit":
                    break
                if message.strip():
                    broadcast(f"{name}: {message}", connection)
    except (OSError, UnicodeError):
        pass
    finally:
        if disconnect(connection) is not None:
            print(f"Отключился: {name}")
            broadcast(f"{name} вышел из чата.")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Чат запущен: {HOST}:{PORT}. Остановка: Ctrl+C.")
        try:
            while True:
                connection, address = server.accept()
                threading.Thread(target=handle_client, args=(connection,), daemon=True).start()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
        finally:
            with clients_lock:
                connections = list(clients)
            for connection in connections:
                disconnect(connection)


if __name__ == "__main__":
    try:
        main()
    except OSError as error:
        print(f"Не удалось запустить сервер: {error}")
