import socket
import threading

HOST = "localhost"
PORT = 8080

username = input("Введите имя: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.sendall(username.encode())

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            print(message)
        except:
            break

thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

print("Вы подключились к чату")
print("Для выхода введите /exit")

while True:
    message = input()

    client_socket.sendall(message.encode())

    if message == "/exit":
        break

client_socket.close()