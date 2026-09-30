import socket
import threading


clients = {}


def send_to_all_clients(message, sender_socket=None):
    for client_socket in list(clients):
        if client_socket != sender_socket:
            try:
                client_socket.sendall(message.encode())
            except:
                continue


def handle_client(client_socket):
    username = client_socket.recv(1024).decode()
    clients[client_socket] = username

    print(f"{username} подключился")
    client_socket.sendall("Вы подключились к чату".encode())
    send_to_all_clients(f"{username} вошёл в чат", client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message or message == "/exit":
                break

            print(f"{username}: {message}")
            send_to_all_clients(f"{username}: {message}", client_socket)
        except:
            break

    del clients[client_socket]
    client_socket.close()

    print(f"{username} вышел из чата")
    send_to_all_clients(f"{username} вышел из чата")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8083))
server_socket.listen()

print("Сервер чата запущен на порту 8083")

while True:
    client_socket, client_address = server_socket.accept()

    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()
