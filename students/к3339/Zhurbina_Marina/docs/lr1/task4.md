# Задание 4. Многопользовательский чат

## Протокол

Чат работает поверх **TCP** с использованием потоков (`threading`). Сервер хранит
список активных участников и рассылает входящие сообщения всем, кроме отправителя.
Для каждого подключения создаётся отдельный поток.

| Параметр       | Значение                          |
|----------------|-----------------------------------|
| Протокол       | TCP (`SOCK_STREAM`) + `threading` |
| Адрес          | `127.0.0.1`                       |
| Порт           | `9004`                            |
| Команда выхода | `exit`                            |

## Модель данных

- **Клиент** идентифицируется ником, введённым при подключении.
- **Сервер** хранит словарь «сокет → ник» активных пользователей.
- **Сообщение** — текстовая строка, рассылается всем, кроме отправителя.

## Код сервера

    ```python
    import socket
    import threading

    ADDRESS = "127.0.0.1"
    PORT = 9004

    members = {}
    guard = threading.Lock()


    def spread(text, skip):
        with guard:
            current = list(members.keys())
        broken = []
        for client in current:
            if client != skip:
                try:
                    client.sendall(text.encode())
                except Exception:
                    broken.append(client)
        with guard:
            for client in broken:
                client.close()
                members.pop(client, None)


    def serve(client_socket, address):
        name = client_socket.recv(1024).decode()
        if not name:
            client_socket.close()
            return
        with guard:
            members[client_socket] = name
        print(f"{name} вошёл ({address})")
        spread(f"{name} зашёл в чат", client_socket)

        while True:
            try:
                text = client_socket.recv(1024).decode()
            except Exception:
                text = ""
            if not text or text == "exit":
                break
            print(f"{name}: {text}")
            spread(f"{name}: {text}", client_socket)

        with guard:
            members.pop(client_socket, None)
        client_socket.close()
        print(f"{name} вышел")
        spread(f"{name} покинул чат", client_socket)


    def main():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ADDRESS, PORT))
        server.listen(5)
        print(f"Чат запущен на {ADDRESS}:{PORT}")

        while True:
            client_socket, address = server.accept()
            threading.Thread(target=serve, args=(client_socket, address)).start()


    main()
    ```

## Код клиента

```python
import socket
import threading

ADDRESS = "127.0.0.1"
PORT = 9004


def listener(sock):
    while True:
        try:
            text = sock.recv(1024).decode()
        except Exception:
            break
        if not text:
            break
        print(text)


def main():
    nick = input("Ваш ник: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ADDRESS, PORT))
    sock.sendall(nick.encode())
    threading.Thread(target=listener, args=(sock,), daemon=True).start()
    print("Вы в чате. Для выхода введите 'exit'")

    while True:
        text = input()
        sock.sendall(text.encode())
        if text == "exit":
            break

    sock.close()


main()
```



## Пример работы в терминале

**Окно 1 — сервер:**

```
> python src/task4/server.py
Чат запущен на 127.0.0.1:9004
Alice вошёл ('127.0.0.1', 54001)
Bob вошёл ('127.0.0.1', 54002)
Alice: Привет, Bob
Bob вышел
```

**Окно 2 — клиент Alice:**

```
> python src/task4/client.py
Ваш ник: Alice
Вы в чате. Для выхода введите 'exit'
Bob зашёл в чат
Привет, Bob
Bob покинул чат
```

**Окно 3 — клиент Bob:**

```
> python src/task4/client.py
Ваш ник: Bob
Вы в чате. Для выхода введите 'exit'
Alice: Привет, Bob
exit
```

## Запуск

1. Терминал 1: `python src/task4/server.py`
2. Терминалы 2, 3, …: `python src/task4/client.py` — один файл для всех, ник вводится при запуске.