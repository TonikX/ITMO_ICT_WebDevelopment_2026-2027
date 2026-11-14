import socket
import threading

SERVER_ADDR = ("localhost", 8080)

udp_client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# узнать имя пользователя
username = input("Введите свое имя: ")
udp_client_sock.sendto(username.encode(), SERVER_ADDR)


def receive_message():
    while True:
        data, addr = udp_client_sock.recvfrom(1024)
        print(data.decode())


thread = threading.Thread(target=receive_message, daemon=True)
thread.start()

# daemon=True Этот поток является вспомогательным. Когда основная программа закончится, его тоже можно завершить

while True:
    message = input()
    if message.strip() == '/exit':
        udp_client_sock.sendto('/exit'.encode(), SERVER_ADDR)
        print("Вы вышли из чата!")
        break
    else:
        udp_client_sock.sendto(message.encode(), SERVER_ADDR)

