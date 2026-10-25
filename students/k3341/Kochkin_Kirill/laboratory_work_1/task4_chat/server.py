import socket
import threading

HOST = "127.0.0.1"
PORT = 8080
users = []
usernames = {}

def broadcast(message, sender_socket=None):
    for u in users:
        if u != sender_socket:
            u.sendall(message.encode())

def handle_client(client_socket):
    username = client_socket.recv(1024).decode()
    usernames[client_socket] = username

    print(f"{username} вошел в чат")
    broadcast(f"{username} вошел в чат", client_socket)

    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                break

            message = data.decode()
            print(f"{username}: {message}")
            broadcast(f"{username}: {message}", client_socket)

        except:
            break

    users.remove(client_socket)
    usernames.pop(client_socket)

    client_socket.close()

    print(username + " вышел из чата")
    broadcast(username + " вышел из чата")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen()
print("Сервер запущен")

while True:
    client_socket, client_address = server_socket.accept()
    print("Подключился клиент:", client_address)

    users.append(client_socket)
    thread = threading.Thread(
        target=handle_client,
        args=(client_socket,)
    )

    thread.start()

