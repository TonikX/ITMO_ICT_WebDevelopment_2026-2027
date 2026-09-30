import socket


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("Hello, server".encode(),("127.0.0.1", 8080))
data, addr = client.recvfrom(1024)
print(data.decode())
client.close()
