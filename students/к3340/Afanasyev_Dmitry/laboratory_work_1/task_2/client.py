import socket

a = input("Первое основание: ")
b = input("Второе основание: ")
h = input("Высота: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9999))
client.sendall(f'{a} {b} {h}\n'.encode())
with client.makefile('r', encoding='utf-8') as response:
    print(response.readline().strip())
client.close()
