import socket

a = float(input("Введите основание: "))
h = float(input("Введите высоту: "))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5001))

message = f"{a} {h}\n"
client.sendall(message.encode("utf-8"))

reader = client.makefile("r", encoding="utf-8")
result = reader.readline().strip()
print(result)

reader.close()
client.close()