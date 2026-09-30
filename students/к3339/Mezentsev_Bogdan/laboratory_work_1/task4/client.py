import socket
import threading


def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            print(f"\n{message}")
        except:
            break


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8083))

username = input("Введите свое имя: ")
client_socket.sendall(username.encode())

welcome_message = client_socket.recv(1024).decode()
print(welcome_message)
print("Для выхода введите /exit")

thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

while True:
    message = input()
    client_socket.sendall(message.encode())

    if message == "/exit":
        break

client_socket.close()
