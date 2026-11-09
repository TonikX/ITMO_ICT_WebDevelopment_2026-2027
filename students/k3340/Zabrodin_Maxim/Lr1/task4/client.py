import socket
import threading


def receive_messages():
    reader = client.makefile("r", encoding="utf-8")

    try:
        for line in reader:
            print(line.strip())
    except OSError:
        pass
    finally:
        reader.close()
        print("Соединение с сервером закрыто")


name = input("Введите имя: ").strip()

while not name:
    name = input("Имя не должно быть пустым. Введите имя: ").strip()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5002))
client.sendall((name + "\n").encode("utf-8"))

thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

print("Пишите сообщения. Для выхода введите /exit")

try:
    while True:
        message = input()
        client.sendall((message + "\n").encode("utf-8"))

        if message == "/exit":
            break

except (OSError, EOFError, KeyboardInterrupt):
    pass

finally:
    try:
        client.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    client.close()