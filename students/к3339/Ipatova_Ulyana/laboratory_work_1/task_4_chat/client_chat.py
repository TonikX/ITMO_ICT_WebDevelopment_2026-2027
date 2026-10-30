import socket
import threading


def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)

            if not data:
                break
            message = data.decode()
            print(message)

        except OSError:
            break


client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect(("localhost", 8080))
username = input("Введите имя: ")
client_socket.sendall(username.encode())

receive_thread = threading.Thread(target=receive_messages,args=(client_socket,),daemon=True)

receive_thread.start()


while True: #основной поток 
    message = input()

    if message == "/покинуть группу/":
        client_socket.sendall(message.encode())
        client_socket.close()

        break

    try:
        client_socket.sendall(message.encode())
    except:
        print("Соединение с сервером потеряно")
        break

    