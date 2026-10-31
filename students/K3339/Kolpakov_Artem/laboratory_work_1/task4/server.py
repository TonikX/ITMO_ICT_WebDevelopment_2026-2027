import socket
import threading

HOST = "localhost"
PORT = 8080

clients = {}

def send_to_all(message, sender=None):
    for client in list(clients):
        if client != sender:
            client.sendall(message.encode())

def handle_client(client):
    username = client.recv(1024).decode()
    clients[client] = username

    print(f"{username} подключился")
    send_to_all(f"{username} вошёл в чат", client)

    while True:
        message = client.recv(1024).decode()

        if not message or message == "/exit":
            break

        full_message = f"{username}: {message}"
        print(full_message)
        send_to_all(full_message, client)

    del clients[client]
    client.close()

    print(f"{username} отключился")
    send_to_all(f"{username} вышел из чата")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Сервер запущен на {HOST}:{PORT}")

while True:
    client_connection, client_address = server_socket.accept()
    print("Подключение от:", client_address)

    thread = threading.Thread(
        target=handle_client,
        args=(client_connection,)
    )
    
    thread.start()