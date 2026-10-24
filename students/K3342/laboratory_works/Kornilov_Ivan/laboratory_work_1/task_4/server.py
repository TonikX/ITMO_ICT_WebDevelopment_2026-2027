import socket
import threading

clients = {}


def broadcast(message, sender=None):
    for client in list(clients):
        if client is not sender:
            client.sendall(message.encode("utf-8"))


def handle_client(client_socket):
    username = client_socket.recv(1024).decode("utf-8")
    clients[client_socket] = username
    broadcast(f"{username} вошёл в чат\n", sender=client_socket)

    while True:
        message = client_socket.recv(1024).decode("utf-8")
        if not message or message == "/exit":
            break
        broadcast(f"{username}: {message}\n", sender=client_socket)

    del clients[client_socket]
    client_socket.close()
    broadcast(f"{username} вышел из чата\n")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen()

while True:
    client_socket, _ = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
