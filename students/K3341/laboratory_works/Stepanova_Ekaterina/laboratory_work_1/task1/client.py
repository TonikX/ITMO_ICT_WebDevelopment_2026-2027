import socket

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# отправляем сообщение sendto(bytes, address)
client_sock.sendto(b'Hello, server', ('localhost', 8080))
# получаем ответ от сервера
data, addr = client_sock.recvfrom(1024)
print(f"Сообщение от сервера\n {data.decode('utf-8')}")

client_sock.close()