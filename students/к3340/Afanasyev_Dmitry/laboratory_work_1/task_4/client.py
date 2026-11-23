import socket
import threading


def receive_messages():
    try:
        with client.makefile('r', encoding='utf-8') as messages:
            for message in messages:
                print(message.strip())
    except OSError:
        pass
    print("Соединение закрыто. Для выхода введите /exit.")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9999))
name = input("Ваше имя: ")
client.sendall((name + '\n').encode())
threading.Thread(target=receive_messages, daemon=True).start()

try:
    while True:
        message = input()
        client.sendall((message + '\n').encode())
        if message == '/exit':
            break
except (OSError, EOFError, KeyboardInterrupt):
    pass
finally:
    client.close()
