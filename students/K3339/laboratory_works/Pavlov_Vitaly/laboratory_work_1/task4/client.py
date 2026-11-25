import socket
import threading

SERVER = ("127.0.0.1", 8084)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(SERVER)


def receive():
    while True:
        try:
            data = client.recv(1024)
        except OSError:
            break
        if not data:
            print("Сервер закрыл соединение")
            break
        print(data.decode(), end="")


threading.Thread(target=receive, daemon=True).start()

try:
    while True:
        text = input().strip()
        if text == "/quit":
            break
        if text:
            client.sendall(text.encode())
except (KeyboardInterrupt, OSError):
    pass

client.close()
print("Вы вышли из чата")
