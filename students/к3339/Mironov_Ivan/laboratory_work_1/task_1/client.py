import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("Hello server".encode("utf-8"), ("127.0.0.1", 12345))

data, address = client.recvfrom(1024)

print("Сообщение от сервера:", data.decode("utf-8"))

client.close()