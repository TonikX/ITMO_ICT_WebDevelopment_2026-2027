import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.sendto(b"hello, server", ('localhost', 8080))

response, _ = client_socket.recvfrom(1024)
print(f"получен ответ от сервера: {response.decode()}")

client_socket.close()