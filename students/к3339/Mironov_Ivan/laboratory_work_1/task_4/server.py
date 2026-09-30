import socket
import threading

HOST = "127.0.0.1"
PORT = 12345

clients = {}
lock = threading.Lock()


def broadcast(message, sender):
    with lock:
        for client in clients:
            if client != sender:
                client.send(message.encode("utf-8"))


def handle_client(client, address):
    try:
        name = client.recv(1024).decode("utf-8")

        with lock:
            clients[client] = name

        print(f"{name} подключился")

        broadcast(f"{name} присоединился к чату", client)

        while True:
            data = client.recv(1024)

            if not data:
                break

            message = data.decode("utf-8")

            if message == "/exit":
                break

            print(f"{name}: {message}")

            broadcast(f"{name}: {message}", client)

    finally:
        with lock:
            name = clients.pop(client, "Неизвестный пользователь")

        client.close()

        print(f"{name} вышел из чата")
        broadcast(f"{name} вышел из чата", client)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Сервер запущен на {HOST}:{PORT}")

    while True:
        client, address = server.accept()

        thread = threading.Thread(
            target = handle_client,
            args = (client, address)
        )

        thread.start()


start_server()