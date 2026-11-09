import socket
import threading

HOST = '127.0.0.1'
PORT = 8083


def receive_messages(client_socket):
    """Поток для постоянного получения сообщений от сервера."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print("\n" + message)
            print("Вы: ", end="", flush=True)
        except:
            print("\n[Система] Соединение с сервером разорвано.")
            client_socket.close()
            break


username = input("Введите ваше имя для чата: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    client_socket.send(username.encode('utf-8'))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input("Вы: ")
        if message.lower() == '/exit':
            print("[Система] Выход из чата.")
            break
        client_socket.send(message.encode('utf-8'))

client_socket.close()
