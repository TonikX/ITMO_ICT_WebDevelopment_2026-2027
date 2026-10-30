import socket
import threading

HOST = "127.0.0.1"
PORT = 8083

clients = {}


def send_to_all(message, sender):
    for client in clients:
        if client != sender:
            client.sendall(message.encode("utf-8"))


def handle_client(client_socket):
    name = client_socket.recv(1024).decode("utf-8")
    clients[client_socket] = name

    print(name, "подключился")

    while True:
        message = client_socket.recv(1024).decode("utf-8")

        if message == "/exit" or not message:
            break

        print(name + ":", message)

        send_to_all(name + ": " + message, client_socket)

    del clients[client_socket]
    client_socket.close()



server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


while True:
    client_socket, address = server_socket.accept()

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket,)
    )

    thread.start()