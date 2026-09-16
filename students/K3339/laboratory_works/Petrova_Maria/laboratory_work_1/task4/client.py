import socket
import threading

HOST = "127.0.0.1"
PORT = 8083

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

name = input("Введите имя: ")
client_socket.sendall(name.encode("utf-8"))


def receive():
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")

            if not message:
                break

            print(message)

        except:
            break


thread = threading.Thread(target=receive)
thread.start()

while True:
    message = input()

    client_socket.sendall(message.encode("utf-8"))

    if message == "/exit":
        break

client_socket.close()