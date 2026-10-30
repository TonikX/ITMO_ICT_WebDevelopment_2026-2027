import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = "Hello, server"

client_socket.sendto(
    message.encode("utf-8"),
    ("127.0.0.1", 8080)
)

data, server_address = client_socket.recvfrom(1024)
print(data.decode("utf-8"))

client_socket.close()