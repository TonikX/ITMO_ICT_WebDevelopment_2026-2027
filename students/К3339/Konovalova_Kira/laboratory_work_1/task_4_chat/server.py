import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("127.0.0.1", 5004)
server_socket.bind(server_address)

server_socket.listen()

clients = []
usernames = []


# функция рассылки
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(message)

# обработка одного клиента
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)

            if not message:
                break

            broadcast(message, client_socket)

        except:
            break

    # удаление клиента
    if client_socket in clients:
        index = clients.index(client_socket)

        clients.remove(client_socket)
        username = usernames[index]
        usernames.remove(username)

        client_socket.close()

        leave_message = f"{username} left the chat.".encode()
        broadcast(leave_message, client_socket)

# добавление нового клиента
def receive_clients():
    while True:
        client_socket, client_address = server_socket.accept()

        client_socket.send("USERNAME".encode())
        username = client_socket.recv(1024).decode()

        clients.append(client_socket)
        usernames.append(username)

        print(f"{username} connected.")

        join_message = f"{username} joined the chat.".encode()
        broadcast(join_message, client_socket)

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket,)
        )
        thread.start()


print("Server is running...")
receive_clients()