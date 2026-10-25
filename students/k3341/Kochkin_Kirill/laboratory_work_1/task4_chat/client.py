import socket
import threading

HOST = "127.0.0.1"
PORT = 8080

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                break

            print("\n" + data.decode())

        except ConnectionResetError:
            break


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
username = input("Введите имя: ")
client_socket.sendall(username.encode())

thread = threading.Thread(
    target=receive_messages,
    args=(client_socket,),
    daemon=True
)

thread.start()

while True:
    message = input()

    if message == "exit":
        break

    client_socket.sendall(message.encode())

client_socket.close()