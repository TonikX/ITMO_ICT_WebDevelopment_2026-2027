import socket
import threading

SERVER_ADDR = ("localhost", 8080)

tcp_client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_client_sock.connect(SERVER_ADDR)

# узнать имя пользователя
username = input("Введите свое имя: ")
tcp_client_sock.send(username.encode())


def receive_message():
    while True:
        data = tcp_client_sock.recv(1024)
        if not data:
            break
        print(data.decode())


thread = threading.Thread(target=receive_message, daemon=True)
thread.start()

# daemon=True Этот поток является вспомогательным. Когда основная программа закончится, его тоже можно завершить

while True:
    message = input()
    if message.strip() == '/exit':
        tcp_client_sock.send('/exit'.encode())
        print("Вы вышли из чата!")
        tcp_client_sock.close()
        break
    else:
        tcp_client_sock.send(message.encode())