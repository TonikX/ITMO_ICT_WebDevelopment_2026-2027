import socket
import threading

clients = {}
lock = threading.Lock()


def broadcast(message, sender=None):
    data = (message + "\n").encode("utf-8")

    with lock:
        for client in clients:
            if client != sender:
                try:
                    client.sendall(data)
                except OSError:
                    pass


def handle_client(connection):
    reader = connection.makefile("r", encoding="utf-8")
    name = ""

    try:
        name = reader.readline().strip()
        if not name:
            return

        with lock:
            clients[connection] = name

        print(f"{name} подключился")
        broadcast(f"{name} вошёл в чат")

        for line in reader:
            message = line.strip()

            if message == "/exit":
                break

            if message:
                print(f"{name}: {message}")
                broadcast(f"{name}: {message}", connection)

    except OSError:
        pass

    finally:
        with lock:
            registered = connection in clients
            clients.pop(connection, None)

        reader.close()
        connection.close()

        if registered:
            print(f"{name} отключился")
            broadcast(f"{name} вышел из чата")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5002))
server.listen(5)

print("Сервер чата запущен")

while True:
    connection, address = server.accept()
    thread = threading.Thread(
        target=handle_client,
        args=(connection,),
        daemon=True
    )
    thread.start()