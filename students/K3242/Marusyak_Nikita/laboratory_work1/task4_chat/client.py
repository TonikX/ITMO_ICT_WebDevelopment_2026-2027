import socket
import threading

HOST = "127.0.0.1"
PORT = 5002


username = input("Введите имя пользователя: ")


client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client_socket.connect((HOST, PORT))


def receive_messages():

    while True:

        try:

            message = client_socket.recv(1024).decode("utf-8")

            if message == "USERNAME":

                client_socket.send(
                    username.encode("utf-8")
                )

            else:

                print(message)

        except:

            print("Соединение с сервером закрыто.")

            client_socket.close()

            break


def send_messages():

    while True:

        message = input()

        try:

            client_socket.send(
                message.encode("utf-8")
            )

        except:

            break

        if message == "/exit":

            client_socket.close()

            break


receive_thread = threading.Thread(
    target=receive_messages
)

receive_thread.start()


send_thread = threading.Thread(
    target=send_messages
)

send_thread.start()
