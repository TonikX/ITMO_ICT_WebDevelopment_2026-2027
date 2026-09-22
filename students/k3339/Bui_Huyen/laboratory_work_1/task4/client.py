import socket
import threading

HOST = '127.0.0.1'
PORT = 5002

# Цвета для вывода в терминале
CYAN = "\033[96m"
PINK = "\033[95m"
RESET = "\033[0m"

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if not message:
                break

            elif "вошёл в чат." in message or "вышел из чата." in message:
                print(f"{PINK}{message}{RESET}\n")

            else:
                print(f"{CYAN}{message}{RESET}\n")    

        except OSError:
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

username = input('\nВведите имя: ')
client_socket.send(username.encode())

print('Вы подключились к чату.')
print('Для выхода введите /exit\n')

receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

receive_thread.start()

while True:
    message = input()

    if not message.strip():
        continue

    client_socket.send(message.encode())

    if message == '/exit':
        break

client_socket.close()