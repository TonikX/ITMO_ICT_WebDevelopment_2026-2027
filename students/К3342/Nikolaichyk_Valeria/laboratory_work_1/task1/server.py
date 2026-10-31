import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(("127.0.0.1", 5000))
data, address = sock.recvfrom(1024)

message = data.decode()
print(message)

response = "Hello, client"
sock.sendto(response.encode(), address)
##client
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("127.0.0.1", 5000)
message = "Hello, server"
sock.sendto(message.encode(), server_address)

data, address = sock.recvfrom(1024)
response = data.decode()
print(response)
