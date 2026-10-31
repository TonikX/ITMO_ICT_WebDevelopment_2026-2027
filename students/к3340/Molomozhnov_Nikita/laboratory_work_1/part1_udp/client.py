import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "Hello, server"
client.sendto(message.encode('utf-8'), ('127.0.0.1', 5010))
print(f"Отправлено: {message}")
response, server_address = client.recvfrom(1024)
print(f"Получен ответ: {response.decode('utf-8')}")
client.close()