# Задание 4. Многопользовательский чат

## Протокол

Чат работает поверх **TCP** с использованием потоков (`threading`). Сервер держит
список активных участников и рассылает входящие сообщения всем, кроме отправителя.
Для каждого подключения создаётся отдельный поток — так сервер обслуживает
несколько клиентов одновременно.

| Параметр       | Значение                          |
|----------------|-----------------------------------|
| Протокол       | TCP (`SOCK_STREAM`) + `threading` |
| Адрес          | `127.0.0.1`                       |
| Порт           | `8084`                            |
| Команда выхода | `exit`                            |

## Модель данных

- **Клиент** идентифицируется ником, введённым при подключении.
- **Сервер** хранит словарь «сокет ник» активных пользователей.
- **Сообщение** — текстовая строка, рассылается всем, кроме отправителя.

## Код сервера

    ```python
    import socket
    import threading

    HOST = '127.0.0.1'
    PORT = 8084

    clients = {}  # сокет -> ник
    lock = threading.Lock()


    def broadcast(message, sender_socket):
        with lock:
            recipients = list(clients.keys())
        to_remove = []
        for client_socket in recipients:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message.encode())
                except Exception:
                    to_remove.append(client_socket)
        with lock:
            for sock in to_remove:
                sock.close()
                clients.pop(sock, None)


    def handle_client(client_socket, address):
        nickname = client_socket.recv(1024).decode()
        if not nickname:
            client_socket.close()
            return
        with lock:
            clients[client_socket] = nickname
        print(f'{nickname} подключился ({address})')
        broadcast(f'{nickname} вошёл в чат', client_socket)

        while True:
            try:
                message = client_socket.recv(1024).decode()
            except Exception:
                message = ''
            if not message or message == 'exit':
                break
            print(f'{nickname}: {message}')
            broadcast(f'{nickname}: {message}', client_socket)

        with lock:
            clients.pop(client_socket, None)
        client_socket.close()
        print(f'{nickname} вышел из чата')
        broadcast(f'{nickname} вышел из чата', client_socket)


    def main():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f'Сервер запущен по адресу {HOST}:{PORT}...')

        while True:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.start()


    if __name__ == '__main__':
        main()
    ```

## Код клиента

```python
import socket
import threading

HOST = '127.0.0.1'
PORT = 8084


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
        except Exception:
            break
        if not message:
            break
        print(message)


def main():
    nickname = input('Введите ваш ник: ')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(nickname.encode())

    thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    thread.start()

    print('Вы в чате! Введите сообщение, для выхода напишите "exit"')
    while True:
        message = input()
        client_socket.sendall(message.encode())
        if message == 'exit':
            break

    client_socket.close()


if __name__ == '__main__':
    main()
```

## Пример работы в терминале

**Окно 1 — сервер:**

```
> python src/task4/server.py
Сервер запущен по адресу 127.0.0.1:8084...
Alice подключился ('127.0.0.1', 51001)
Bob подключился ('127.0.0.1', 51002)
Alice: Привет, Bob
Bob вышел из чата
```

**Окно 2 — клиент Alice:**

```
> python src/task4/client.py
Введите ваш ник: Alice
Вы в чате! Введите сообщение, для выхода напишите "exit"
Bob вошёл в чат
Привет, Bob
Bob вышел из чата
```

**Окно 3 — клиент Bob:**

```
> python src/task4/client.py
Введите ваш ник: Bob
Вы в чате! Введите сообщение, для выхода напишите "exit"
Alice: Привет, Bob
exit
```

## Запуск

1. Терминал 1: `python src/task4/server.py`
2. Терминалы 2, 3, …: `python src/task4/client.py` — один файл для всех пользователей, ник вводится при запуске.