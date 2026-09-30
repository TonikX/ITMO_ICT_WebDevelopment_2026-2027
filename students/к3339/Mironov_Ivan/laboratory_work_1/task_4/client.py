import socket
import threading

HOST = "127.0.0.1"
PORT = 12345


def receive_messages(client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")

            if not message:
                break

            print("\n" + message)
            print("> ", end="", flush=True)

        except:
            break


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

name = input("Введите ваше имя: ")

client.send(name.encode("utf-8"))

thread = threading.Thread(
    target=receive_messages,
    args=(client,)
)

thread.daemon = True
thread.start()

print("Вы подключились к чату.")
print("Чтобы выйти введите /exit")

while True:
    message = input("> ")

    client.send(message.encode("utf-8"))

    if message == "/exit":
        break

client.close()