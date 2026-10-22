import socket
import threading

HOST = "127.0.0.1"
PORT = 5002
clients = []
clients_lock = threading.Lock()


def broadcast(message, sender):
    with clients_lock:
        sender_name = next(name for name, connection in clients if connection == sender)
        for _, connection in clients:
            if connection != sender:
                connection.sendall(f"{sender_name}: {message}\n".encode("utf-8"))


def handle_client(connection):
    with connection:
        stream = connection.makefile("r", encoding="utf-8")
        name = stream.readline().strip()

        with clients_lock:
            clients.append((name, connection))

        for message in stream:
            message = message.strip()
            if message == "/quit":
                break
            broadcast(message, connection)

        with clients_lock:
            clients.remove((name, connection))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()

    while True:
        connection, address = server.accept()
        threading.Thread(target=handle_client, args=(connection,), daemon=True).start()
