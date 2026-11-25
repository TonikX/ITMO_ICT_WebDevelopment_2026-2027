import socket

SERVER = ("127.0.0.1", 8081)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(3)
client.sendto("Hello, server".encode(), SERVER)

try:
    data, address = client.recvfrom(1024)
    print(f"Ответ сервера: {data.decode()}")
except OSError:
    print("Сервер не ответил")

client.close()
