import socket

HOST = "127.0.0.1"
PORT = 5001

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(1)

print(f"TCP-сервер запущен на {HOST}:{PORT}")
print("Ожидание подключения клиента...")

client_socket, client_address = server_socket.accept()

print(f"Клиент подключился: {client_address}")

data = client_socket.recv(1024).decode("utf-8")

print(f"Получены данные от клиента: {data}")

try:
    a, h = map(float, data.split())

    area = a * h

    result = f"Площадь параллелограмма: {area}"

except ValueError:
    result = "Ошибка: необходимо передать два числа"

client_socket.send(result.encode("utf-8"))

print(f"Результат отправлен клиенту: {result}")

client_socket.close()
server_socket.close()
