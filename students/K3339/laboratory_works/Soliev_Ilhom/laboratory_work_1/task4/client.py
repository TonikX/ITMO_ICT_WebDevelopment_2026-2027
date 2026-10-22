import socket
import threading

SERVER_ADDRESS = ("127.0.0.1", 5002)


def receive_messages(stream):
    for message in stream:
        print(message.rstrip())


name = input("Введите имя: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(SERVER_ADDRESS)
    client.sendall((name + "\n").encode("utf-8"))

    stream = client.makefile("r", encoding="utf-8")
    threading.Thread(target=receive_messages, args=(stream,), daemon=True).start()

    while True:
        message = input()
        client.sendall((message + "\n").encode("utf-8"))
        if message == "/quit":
            break
