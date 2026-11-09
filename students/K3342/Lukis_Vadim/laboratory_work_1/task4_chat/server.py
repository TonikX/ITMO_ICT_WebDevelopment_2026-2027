import socket
import threading

HOST = '127.0.0.1'
PORT = 8083

clients = []
usernames = {}


def broadcast(message, sender_socket):
    """Рассылает сообщение всем клиентам, кроме отправителя."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                remove_client(client)


def remove_client(client_socket):
    """Удаляет клиента из списков."""
    if client_socket in clients:
        clients.remove(client_socket)
        username = usernames.get(client_socket, "Неизвестный")
        del usernames[client_socket]
        print(f"[Server] {username} отключился.")


def handle_client(client_socket):
    """Обрабатывает сообщения от конкретного клиента."""
    try:
        username = client_socket.recv(1024).decode('utf-8')
        usernames[client_socket] = username
        clients.append(client_socket)

        print(f"[Server] Подключился {username}. Всего клиентов: {len(clients)}")
        broadcast(f"[Система] {username} присоединился к чату.".encode('utf-8'), client_socket)

        while True:
            message = client_socket.recv(1024)
            if not message:
                break

            full_message = f"[{username}] {message.decode('utf-8')}".encode('utf-8')
            broadcast(full_message, client_socket)

    except ConnectionResetError:
        pass
    finally:
        remove_client(client_socket)
        client_socket.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[Chat Server] Запущен на {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()
