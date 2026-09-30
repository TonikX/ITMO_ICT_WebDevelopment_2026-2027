import socket

HOST = '127.0.0.1'
PORT = 12345

print("Доступные варианты:")
print("1. Теорема Пифагора (параметры: катет_a катет_b)")
print("2. Решение квадратного уравнения (параметры: a b c)")
print("3. Площадь трапеции (параметры: основание_a основание_b высота_h)")
print("4. Площадь параллелограмма (параметры: основание_a высота_h)")

variant = input("\nВведите номер вашего варианта (1-4): ").strip()
params = input("Введите параметры через пробел: ").strip()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Формируем запрос
request = f"{variant} {params}"
client_socket.send(request.encode('utf-8'))

# Получаем результат
response = client_socket.recv(1024).decode('utf-8')
print(f"\nРезультат от сервера: {response}")

client_socket.close()