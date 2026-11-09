import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                print("Соединение с сервером потеряно.")
                break
            print(msg)
        except:
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8084))

name = input("Введите ваше имя: ")
client.send(name.encode('utf-8'))

# Запускаем поток для чтения входящих сообщений
threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

print("Вы в чате! Вводите сообщения (или 'exit' для выхода):")
while True:
    msg = input()
    if msg.lower() == 'exit':
        break
    if msg:
        client.send(msg.encode('utf-8'))

client.close()
