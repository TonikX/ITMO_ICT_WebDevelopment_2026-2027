import socket
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8080))

username = input("Имя: ")
client_socket.sendall(username.encode("utf-8"))


def receive_messages():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(data.decode("utf-8"), end="")


threading.Thread(target=receive_messages, daemon=True).start()

while True:
    message = input()
    client_socket.sendall(message.encode("utf-8"))
    if message == "/exit":
        break

client_socket.close()
