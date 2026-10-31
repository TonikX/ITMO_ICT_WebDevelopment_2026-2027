import socket
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 8000))

name = input("Введите ваше имя: ")
client_socket.sendall(name.encode())
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            print(message)
        except ConnectionAbortedError:
            break
            
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()
while True:
    message = input()

    if message == "/выход":
        break

    client_socket.sendall(message.encode())

client_socket.close()