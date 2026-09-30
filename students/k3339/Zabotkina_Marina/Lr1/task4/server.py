import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8080))
server_socket.listen()
print("Cервер запущен на порту 8080...")

clients = []

def broadcast(message, sender_connection):
    for client in clients:
        if client != sender_connection:
            try:
                client.sendall(message)
            except:
                clients.remove(client)

def handle_client(client_connection, client_address):
    print(f"Новый участник подключился: {client_address}")
    while True:
        try:
            message = client_connection.recv(1024)
            if not message:
                break
            broadcast(message, client_connection)
        except:
            break

    clients.remove(client_connection)
    client_connection.close()
    print(f"Участник {client_address} отключился.")

while True:
    client_connection, client_address = server_socket.accept()
    clients.append(client_connection)
    thread = threading.Thread(target=handle_client, args=(client_connection, client_address))
    thread.start()