import socket
import threading

HOST = "localhost"
PORT = 8084

clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen()

print(f"Сервер чата запущен на {HOST}:{PORT}")


def broadcast(message, sender_connection):
    for client in clients:
        if client != sender_connection:
            client.sendall(message)


def handle_client(client_connection, client_address):
    username = client_connection.recv(1024).decode()

    print(f"{username} подключился {client_address}")

    join_message = f"{username} присоединился к чату".encode()
    broadcast(join_message, client_connection)

    while True:
        try:
            message = client_connection.recv(1024)

            if not message:
                break

            text = message.decode()

            if text == "/exit":
                break

            print(f"{username}: {text}")

            full_message = f"{username}: {text}".encode()
            broadcast(full_message, client_connection)

        except ConnectionError:
            break

    clients.remove(client_connection)

    client_connection.close()

    print(f"{username} вышел из чата")

    leave_message = f"{username} вышел из чата".encode()
    broadcast(leave_message, client_connection)


while True:
    client_connection, client_address = server_socket.accept()

    clients.append(client_connection)

    thread = threading.Thread(
        target=handle_client,
        args=(client_connection, client_address)
    )
    thread.start()