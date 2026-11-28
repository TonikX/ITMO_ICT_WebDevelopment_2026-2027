import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 5010))
print("сервер запущен")

data, client_address = server.recvfrom(1024)
print(f"Получено от {client_address}: {data.decode('utf-8')}")
response = "Hello, client"
server.sendto(response.encode('utf-8'), client_address)
print("Ответ отправлен клиенту")
server.close()