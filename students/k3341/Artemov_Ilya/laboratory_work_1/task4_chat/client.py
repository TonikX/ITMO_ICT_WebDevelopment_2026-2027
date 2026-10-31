import socket
import threading

HOST = "localhost"
PORT = 9004


def receive_messages(client_socket):
    try:
        for line in client_socket.makefile("r", encoding="utf-8"):
            print(line, end="")
    except OSError:
        pass


name = ""
while not name:
    name = input("Введите ваше имя: ").strip()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(f"{name}\n".encode())
print("Вы вошли в чат. Для выхода введите /exit")

threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

try:
    while True:
        message = input().strip()
        if not message:
            continue
        client_socket.sendall(f"{message}\n".encode())
        if message == "/exit":
            break
except (EOFError, KeyboardInterrupt, OSError):
    pass

client_socket.close()
print("Вы вышли из чата")
