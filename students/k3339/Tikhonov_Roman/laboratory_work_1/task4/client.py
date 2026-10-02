import socket
import threading

HOST = '127.0.0.1'
PORT = 8084


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
        except Exception:
            break
        if not message:
            break
        print(message)


def main():
    nickname = input('Введите ваш ник: ')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(nickname.encode())

    thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    thread.start()

    print('Вы в чате! Введите сообщение, для выхода напишите "exit"')
    while True:
        message = input()
        client_socket.sendall(message.encode())
        if message == 'exit':
            break

    client_socket.close()


if __name__ == '__main__':
    main()