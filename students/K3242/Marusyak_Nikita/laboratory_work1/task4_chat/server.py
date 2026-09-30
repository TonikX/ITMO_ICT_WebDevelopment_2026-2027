import socket
import threading

HOST = "127.0.0.1"
PORT = 5002

clients = []
usernames = []


def broadcast(message, sender_socket=None):

    for client in clients:

        if client != sender_socket:

            try:
                client.send(message)

            except:
                remove_client(client)


def remove_client(client):

    if client in clients:

        index = clients.index(client)

        clients.remove(client)

        username = usernames[index]

        usernames.remove(username)

        client.close()

        print(f"{username} отключился")

        broadcast(
            f"{username} вышел из чата".encode("utf-8")
        )


def handle_client(client):

    while True:

        try:

            message = client.recv(1024)

            if not message:
                break

            decoded_message = message.decode("utf-8")

            if decoded_message == "/exit":
                break

            index = clients.index(client)

            username = usernames[index]

            full_message = f"{username}: {decoded_message}"

            print(full_message)

            broadcast(
                full_message.encode("utf-8"),
                client
            )

        except:
            break

    remove_client(client)


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind((HOST, PORT))

server_socket.listen()

print(f"Чат-сервер запущен на {HOST}:{PORT}")
print("Ожидание пользователей...")


while True:

    client, address = server_socket.accept()

    print(f"Новое подключение: {address}")

    client.send("USERNAME".encode("utf-8"))

    username = client.recv(1024).decode("utf-8")

    usernames.append(username)

    clients.append(client)

    print(f"Пользователь {username} подключился")

    broadcast(
        f"{username} вошел в чат".encode("utf-8"),
        client
    )

    client.send(
        "Вы подключены к чату. Для выхода используйте /exit".encode("utf-8")
    )

    thread = threading.Thread(
        target=handle_client,
        args=(client,)
    )

    thread.start()

    print(f"Активных пользователей: {threading.active_count() - 1}")
