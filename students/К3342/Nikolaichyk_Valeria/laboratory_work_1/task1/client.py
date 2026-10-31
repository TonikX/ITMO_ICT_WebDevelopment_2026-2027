import socet

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('127.0.0.1', 5000)
message = b'Hello, server'
sock.sendto(message.encode(), server_address)

data, server = sock.recvfrom(1024)
response = data.decode()
print(response)
