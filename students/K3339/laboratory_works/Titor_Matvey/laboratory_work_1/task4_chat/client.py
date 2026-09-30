import socket
import threading

HOST = 'localhost'
PORT = 9002


def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            print('\nСоединение с сервером разорвано')
            break
        print(f'\r{data.decode()}\n> ', end='', flush=True)


username = input('Введите имя: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

client_socket.sendall(username.encode())
print(f'Подключено к чату {HOST}:{PORT}. Команда /exit — выход.')

threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

while True:
    text = input('> ')
    if text.strip() == '/exit':
        client_socket.sendall(b'/exit')
        break
    if text:
        client_socket.sendall(text.encode())

client_socket.close()
print('Вы вышли из чата.')
