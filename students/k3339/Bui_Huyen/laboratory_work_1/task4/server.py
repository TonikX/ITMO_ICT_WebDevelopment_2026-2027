import socket
import threading

HOST = '127.0.0.1'
PORT = 5002

clients = {}

# Отправка сообщения
def broadcast(message, sender):
    for client in clients:
        if client != sender:
            client.send(message.encode())

# Обработка отдельного клиента
def handle_client(connection):
    username = connection.recv(1024).decode()

    clients[connection] = username
    print(f'{username} подключился к чату.')

    broadcast(f'{username} вошёл в чат.', connection)

    while True:
        try:
            message = connection.recv(1024).decode()
            if not message or message == '/exit':
                break

            print(f'{username}: {message}')

            broadcast(f'{username}: {message}', connection)

        except:
            break

    del clients[connection]

    connection.close()
    print(f'{username} отключился.')

    broadcast(f'{username} вышел из чата.', connection)

# Создаем tcp сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen()

print('Сервер запущен.')
print('Ожидание подключений...')

while True:
    connection, client_address = server_socket.accept()
    print('Новое подключение:', client_address)

    thread = threading.Thread(target=handle_client, args=(connection,))

    thread.start()