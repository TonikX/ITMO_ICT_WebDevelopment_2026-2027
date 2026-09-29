import socket
import threading


def receive(connection):
    while True:
        message = connection.recv(1024)
        if not message:
            break
        print(message.decode(), end="")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5004))
client.sendall((input("Имя: ") + "\n").encode())
threading.Thread(target=receive, args=(client,), daemon=True).start()

while True:
    message = input()
    client.sendall((message + "\n").encode())
    if message == "/quit":
        break

client.close()
