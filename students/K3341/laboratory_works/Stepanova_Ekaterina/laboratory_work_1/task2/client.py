import socket

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_sock.connect(('localhost', 8080))

inp = input("Введите величины катов a и b через пробел: ")
client_sock.send(inp.encode('utf-8'))

data = client_sock.recv(1024)
print(f"Ответ от сервера: c = {data.decode('utf-8')}")

client_sock.close()
