import socket
import threading

username = input("введите ваше имя: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("localhost", 8080))

client_socket.sendall(username.encode())

def receive_message():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(data)
        except Exception:
            break

receive_thread = threading.Thread(target=receive_message)
receive_thread.daemon = True
receive_thread.start()
print("Вы присоединились к чату. Можете писать сообщения. Для завершения введите /exit")

while True:
    message = input()
    if message.strip() == "/exit":
        client_socket.sendall(b"/exit")
        break
    client_socket.sendall(message.encode())

client_socket.close()
print("Вы покинули чат")