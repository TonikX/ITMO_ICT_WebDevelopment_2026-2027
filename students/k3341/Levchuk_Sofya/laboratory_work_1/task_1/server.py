import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(("localhost", 8080))
print("сервер запущен на localhost:8080")

data, client_address = server_socket.recvfrom(1024)
print(f"подключение от клиента: {client_address}")
print(f"получено сообщение от клиента: {data.decode()}")

response = "hello, client"
server_socket.sendto(response.encode(), client_address)
print(f"отправлен ответ от сервера: {response}")

server_socket.close()