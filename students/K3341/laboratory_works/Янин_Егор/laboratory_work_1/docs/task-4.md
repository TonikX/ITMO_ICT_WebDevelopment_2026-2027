# Практическое задание 4. Чат на сокетах

## Задание

Реализовать двухпользовательский или многопользовательский чат. Для максимального количества баллов реализуйте многопользовательский чат.

## Выполнение

```py
clients = {}
clients_lock = threading.Lock()


def broadcast(message, excluded_username=None):
    encoded_message = message.encode('utf-8')
    with clients_lock:
        receviers = [
            (username, client_socket, send_lock)
            for username, (client_socket, send_lock) in clients.items()
            if username != excluded_username
        ]

    for _, client_socket, send_lock in receviers:
        try:
            with send_lock:
                client_socket.sendall(encoded_message)
        except:
            pass
```

Функция `broadcast` рассылает всем пользователям, кроме исключенного, блокируя добавление новых пользователей главным потоком и обработку собщений потоками пользователей.

```py
def handle_client(client_socket, address):
    username = None
    reader = client_socket.makefile('r', encoding='utf-8')

    try:
        client_socket.sendall(b'Enter your username:\n')
        username = reader.readline().strip()

        with clients_lock:
            if username and username not in clients:
                client_send_lock = threading.Lock()
                client_socket.sendall(
                    f'Welcome {username}! You can start chatting now.\n'.encode('utf-8')
                )
                clients[username] = (client_socket, client_send_lock)
                username_is_available = True
            else:
                username_is_available = False

        if not username_is_available:
            client_socket.sendall(b'Username is empty or already in use.\n')
            return

        print(f'{username} connected from {address}')
        broadcast(f'{username} joined the chat.\n', excluded_username=username)

        for line in reader:
            message = line.strip()
            if message.lower() == 'exit':
                client_socket.sendall(b'You have left the chat.\n')
                break
            if message:
                broadcast(f'{username}: {message}\n', excluded_username=username)
    except (ConnectionError, OSError) as error:
        print(f'Connection with {address} ended: {error}')
    finally:
        if username:
            with clients_lock:
                client = clients.get(username)
                if client and client[0] is client_socket:
                    del clients[username]
                    broadcast_disconnect = True
                else:
                    broadcast_disconnect = False
            if broadcast_disconnect:
                broadcast(f'{username} left the chat.\n')
                print(f'{username} has disconnected.')

        reader.close()
        client_socket.close()

```

В `handle_client` сервер получает имя пользователя, вносит его в список и отправляет сообщение о его вступлении в чат. Далее он построчно читает сообщения от пользователя, если он отправит "exit", соединение закроется. Также соединение прервется в случае ошибки. Все другие сообщения пользователя отправятся другим пользователям.

```py
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f'Server is listening on {HOST}:{PORT}...')

        while True:
            client_socket, address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True,
            )
            client_thread.start()

```

`main` слушает на заданном порте и принимает новые подключения, для каждого клиента запускается отдельный поток с функцией `hadle_client`, который уничтожится в случае завершения выполнения программы.

```py
import socket
import threading

HOST = 'localhost'
PORT = 9090


def receive_message_loop(reader):
    for message in reader:
        print(message, end='')


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        reader = client_socket.makefile('r', encoding='utf-8')

        prompt = reader.readline()
        if not prompt:
            print('Server closed the connection.')
            return
        print(prompt, end='')
        username = input().strip()
        client_socket.sendall(f'{username}\n'.encode('utf-8'))

        response = reader.readline()
        if not response:
            print('Server closed the connection.')
            return
        print(response, end='')
        if response.startswith('Username is empty or already in use.'):
            return

        receive_thread = threading.Thread(
            target=receive_message_loop,
            args=(reader,),
            daemon=True,
        )
        receive_thread.start()

        try:
            while True:
                message = input()
                client_socket.sendall(f'{message}\n'.encode('utf-8'))
                if message.lower() == 'exit':
                    break
        except (EOFError, OSError):
            pass

        receive_thread.join()
        reader.close()


if __name__ == '__main__':
    main()
```

Клиент подключается к серверу, отправляет имя пользователя из консоли, принимает сообщения от других пользователей чата в отдельном потоке и отправляет свои.
