import socket
import threading

HOST = "localhost"
PORT = 8084

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

username = input("Введите ваше имя: ")

client_socket.sendall(username.encode())

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024)

            if not message:
                break

            print(message.decode())

        except ConnectionError:
            break


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()


while True:
    message = input()

    client_socket.sendall(message.encode())

    if message == "/exit":
        break


client_socket.close()