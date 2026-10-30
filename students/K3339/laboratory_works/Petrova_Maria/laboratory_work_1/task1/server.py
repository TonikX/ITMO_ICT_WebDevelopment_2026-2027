import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("127.0.0.1", 8080))

data, client_address = server_socket.recvfrom(1024)

print(data.decode("utf-8"))
ans = "Hello, client"

server_socket.sendto(ans.encode("utf-8"), client_address)

server_socket.close()