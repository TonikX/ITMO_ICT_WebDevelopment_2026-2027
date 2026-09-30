import socket
import threading

ADDRESS = ("localhost", 5004)


def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            print("Сервер закрыл соединение")
            break
        print(data.decode(), end="")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ADDRESS)
sock.sendall(input("Ваше имя: ").encode())

threading.Thread(target=receive, args=(sock,), daemon=True).start()
print("Вы в чате. Для выхода введите /exit")

while True:
    message = input()
    if not message.strip():
        continue
    try:
        sock.sendall(message.encode())
    except OSError:
        print("Сервер недоступен")
        break
    if message == "/exit":
        break

sock.close()
