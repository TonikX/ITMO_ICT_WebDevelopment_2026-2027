import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto(
    "Hello, server".encode("utf-8"),
    ("127.0.0.1", 5000)
)

data, address = client.recvfrom(1024)
print("Получено от сервера:", data.decode("utf-8"))

client.close()