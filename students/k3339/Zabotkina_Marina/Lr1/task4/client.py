import socket
import threading

nickname = input("Введите ваш ник: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

def receive_messages():
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            print(msg)
        except:
            print("Соединение разорвано.")
            client_socket.close()
            break

recv_thread = threading.Thread(target=receive_messages)
recv_thread.daemon = True
recv_thread.start()

print("Добро пожаловать! Введите сообщение и нажмите Enter:")
while True:
    text = input()
    message = f"[{nickname}]: {text}"
    client_socket.sendall(message.encode())