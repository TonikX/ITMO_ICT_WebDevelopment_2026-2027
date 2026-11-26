import socket
import threading

HOST = "127.0.0.1"
PORT = 5003


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)

            if not data:
                print("\nСоединение с сервером закрыто.")
                break

            print(data.decode("utf-8"), end="")

        except (ConnectionResetError, OSError):
            break


client_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:
    client_socket.connect((HOST, PORT))

    username = input("Введите имя пользователя: ").strip()

    if not username:
        print("Имя пользователя не может быть пустым.")
        client_socket.close()
        exit()

    client_socket.sendall(username.encode("utf-8"))

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client_socket,),
        daemon=True
    )

    receive_thread.start()

    print("Вы подключены к чату.")
    print("Введите сообщение.")
    print("Для выхода введите /exit.")

    while True:
        message = input()

        client_socket.sendall(
            message.encode("utf-8")
        )

        if message == "/exit":
            break

except ConnectionRefusedError:
    print("Не удалось подключиться к серверу.")

except KeyboardInterrupt:
    try:
        client_socket.sendall(
            "/exit".encode("utf-8")
        )
    except OSError:
        pass

finally:
    client_socket.close()