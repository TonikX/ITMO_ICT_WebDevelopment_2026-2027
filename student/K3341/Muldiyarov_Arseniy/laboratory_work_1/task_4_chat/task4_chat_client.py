import socket
import threading
import sys

def receive_messages(sock):
    """Поток для приема сообщений"""
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message: break
            print(f"\n{message}")
            print(f"{username}> ", end="", flush=True) # Возвращаем приглашение ввода
        except:
            print("\nОшибка соединения.")
            break

username = input("Введите ваш ник: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8083))

# Запускаем поток для чтения входящих
recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
recv_thread.start()

print("Вы в чате. Введите /exit для выхода.")

try:
    while True:
        msg = input(f"{username}> ")
        if msg.lower() == '/exit':
            break
        # Форматируем сообщение, чтобы все видели, кто написал
        formatted_msg = f"[{username}]: {msg}"
        client_socket.sendall(formatted_msg.encode('utf-8'))
except KeyboardInterrupt:
    pass
finally:
    client_socket.close()
    sys.exit()