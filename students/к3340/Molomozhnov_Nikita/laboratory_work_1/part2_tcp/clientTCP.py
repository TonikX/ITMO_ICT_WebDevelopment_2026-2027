import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5011))
print("Введите параметры трапеции:")
a = input("a: ")
b = input("b: ")
h = input("h: ")
message = f"{a},{b},{h}"
client.send(message.encode('utf-8'))
print(f"Отправлено: {message}")
response = client.recv(1024).decode('utf-8')
print(f"Ответ от сервера: {response}")
client.close()