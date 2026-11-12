import socket 

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(('localhost', 8080))

a = input("a = ")
b = input("b = ")

messages = a + " " + b + "\n"

client_socket.sendall(messages.encode('utf-8'))

response = client_socket.recv(1024)

print(response.decode('utf-8'))

client_socket.close()




