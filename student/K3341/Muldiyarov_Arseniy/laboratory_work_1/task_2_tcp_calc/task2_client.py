import socket
import json

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8081))


print("Введите коэффициенты квадратного уравнения (a, b, c):")
a = float(input("a = "))
b = float(input("b = "))
c = float(input("c = "))

params = [a, b, c]

# Отправляем JSON
client_socket.sendall(json.dumps(params).encode('utf-8'))

# Получаем ответ
response = client_socket.recv(1024).decode('utf-8')
result = json.loads(response)
print(f"Результат вычислений: {result['result']}")

client_socket.close()