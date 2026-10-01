import socket
import threading

HOST = "localhost"
PORT = 8084

# список подключенных клиентов
clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen()

print(f"Сервер чата запущен на {HOST}:{PORT}")


# отправляем сообщение всем клиентам, кроме отправителя
def broadcast(message, sender_connection):
    for client in clients:
        if client != sender_connection:
            client.sendall(message)


# обрабатываем сообщения отдельного клиента
def handle_client(client_connection, client_address):
    # получаем имя пользователя
    username = client_connection.recv(1024).decode()

    print(f"{username} подключился {client_address}")

    join_message = f"{username} присоединился к чату".encode()
    broadcast(join_message, client_connection)

    while True:
        try:
            # получаем сообщение от клиента
            message = client_connection.recv(1024)

            # если клиент отключился
            if not message:
                break

            text = message.decode()

            # проверяем команду выхода
            if text == "/exit":
                break

            print(f"{username}: {text}")

            # отправляем сообщение остальным пользователям
            full_message = f"{username}: {text}".encode()
            broadcast(full_message, client_connection)

        except ConnectionError:
            break

    # удаляем клиента из списка
    clients.remove(client_connection)

    client_connection.close()

    print(f"{username} вышел из чата")

    leave_message = f"{username} вышел из чата".encode()
    broadcast(leave_message, client_connection)


# принимаем подключения клиентов
while True:
    client_connection, client_address = server_socket.accept()

    # сохраняем подключение клиента
    clients.append(client_connection)

    # запускаем обработку клиента в отдельном потоке
    thread = threading.Thread(
        target=handle_client,
        args=(client_connection, client_address)
    )
    thread.start()