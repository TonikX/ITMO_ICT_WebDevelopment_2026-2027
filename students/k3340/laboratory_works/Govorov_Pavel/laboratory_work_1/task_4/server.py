import socket
import threading

clients = []


def handle_client(connection):
    name = connection.recv(1024).decode().strip()
    clients.append((connection, name))
    for client, _ in clients:
        client.sendall(f"{name} вошёл в чат\n".encode())

    while True:
        message = connection.recv(1024)
        if not message or message.strip() == b"/quit":
            break
        for client, _ in clients:
            if client != connection:
                client.sendall(f"{name}: {message.decode().strip()}\n".encode())

    clients.remove((connection, name))
    connection.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5004))
server.listen()
print("Chat server started")

while True:
    connection, _ = server.accept()
    threading.Thread(target=handle_client, args=(connection,)).start()
