import socket
import threading

HOST = 'localhost'
PORT = 9004


def receive_messages(sock: socket.socket):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Соединение с сервером закрыто.")
                break
            print(data.decode('utf-8'))
        except OSError:
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Первое сообщение от сервера - запрос имени пользователя
    prompt = client_socket.recv(1024).decode('utf-8')
    print(prompt, end='')
    username = input()
    client_socket.sendall(username.encode('utf-8'))

    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receiver_thread.start()

    while True:
        try:
            message = input()
        except EOFError:
            break
        if not message:
            continue
        client_socket.sendall(message.encode('utf-8'))
        if message == '/exit':
            break

    client_socket.close()


if __name__ == '__main__':
    main()
