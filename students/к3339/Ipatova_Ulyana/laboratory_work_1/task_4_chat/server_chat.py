import socket
import threading

clients = {}

def broadcast(message, sender_socket=None):
    message_bytes = message.encode()

    for client_socket in list(clients.keys()):
        if client_socket == sender_socket:
            continue
        try:
            client_socket.sendall(message_bytes)
        except OSError:
            pass


def handle_client(client_socket, client_address):
    username = None
    try:
        username = client_socket.recv(1024).decode()
        clients[client_socket] = username

        print(f"{username} подключился {client_address}")
        broadcast(f"{username} вошёл в чат",sender_socket=client_socket)

        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            message = data.decode()

            if message == "/покинуть группу/":
                break

            full_message = username + ": " + message 
            print(full_message)
            
            broadcast(full_message,sender_socket=client_socket)

    except OSError as error:
        print(f"Ошибка соединения с {username}: {error}")

    finally:
        if client_socket in clients:
            del clients[client_socket]

        client_socket.close()

        if username is not None:
            print(f"{username} вышел из чата")
            broadcast(f"{username} вышел из чата")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 8080))
server_socket.listen()
print("Сервер запущен...")

while True: #основной поток 
    client_socket, client_address = server_socket.accept()

    thread = threading.Thread(target=handle_client,args=(client_socket, client_address))
    thread.start()