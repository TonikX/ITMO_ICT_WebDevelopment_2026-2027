import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 8081)

client_socket.sendto(b"Hello, server", server_address)
data, server = client_socket.recvfrom(1024)
print(f"Ответ сервера: {data.decode('utf-8')}")
client_socket.close()
