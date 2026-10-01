import socket
import threading

HOST = "localhost"
PORT = 8084

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

# получаем имя пользователя
username = input("Введите ваше имя: ")

# отправляем имя серверу
client_socket.sendall(username.encode())


# получаем сообщения от сервера
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024)

            if not message:
                break

            print(message.decode())

        except ConnectionError:
            break


# запускаем получение сообщений в отдельном потоке
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()


# отправляем сообщения серверу
while True:
    message = input()

    client_socket.sendall(message.encode())

    # выход из чата
    if message == "/exit":
        break


client_socket.close()