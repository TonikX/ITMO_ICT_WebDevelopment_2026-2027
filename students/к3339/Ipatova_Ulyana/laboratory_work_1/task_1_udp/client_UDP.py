import socket 

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto("Hello server!".encode(), ('localhost', 8080))
data, server_address =  client_socket.recvfrom(1024) 
answer = data.decode()
print(answer) 

client_socket.close()

