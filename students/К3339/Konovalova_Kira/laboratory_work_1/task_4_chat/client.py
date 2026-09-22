import socket
import threading

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("127.0.0.1", 5004)
client_socket.connect(server_address)

username = input("Enter username: ")

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if message == "USERNAME":
                client_socket.send(username.encode())
            else:
                print(message)

        except:
            print("Connection closed.")
            client_socket.close()
            break

def send_messages():
    while True:
        message = input()

        if message == "/exit":
            client_socket.close()
            break

        full_message = f"{username}: {message}"
        client_socket.send(full_message.encode())


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_messages()