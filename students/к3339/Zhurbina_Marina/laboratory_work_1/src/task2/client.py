import socket

a = input("Введите a: ")
b = input("Введите b: ")
c = input("Введите c: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9002))
client.send((a + " " + b + " " + c).encode())

answer = client.recv(1024).decode()
print("Ответ сервера:", answer)
client.close()