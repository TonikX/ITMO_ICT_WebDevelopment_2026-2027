import socket
import sys
import threading

HOST = 'localhost'
PORT = 8080

username = input('Введите ваш username: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Отправляем серверу свой ник первым сообщением
client_socket.sendall(username.encode('utf-8'))

def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\nСоединение закрыто сервером.")
                break
            print(data.decode('utf-8'))
        except OSError:
            break
    client_socket.close()
    sys.exit(0)

threading.Thread(target=receive_messages, daemon=True).start()

print("Вы в чате. Напишите /exit, чтобы выйти.")

while True:
    try:
        message = input()
    except:
        break

    if message.lower()  == '/exit':
        break

    try:
        client_socket.sendall(message.encode('utf-8'))
    except:
        break

client_socket.close()
print("Вы вышли из чата.")