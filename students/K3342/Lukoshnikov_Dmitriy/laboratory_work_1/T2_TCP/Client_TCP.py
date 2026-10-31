import socket

host = 'localhost'
port = 8081

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((host, port))
print("Это клиент серверное часть приложения для счета гипотенузы по теореме пифагора")
while True:
    try:
        k1 = float(input("Введите длину первого катета: "))
        k2 = float(input("Введите длину второго катета: "))
    except ValueError:
        print("Катеты должны быть в формате float")
        print("Попробуй еще раз")
        continue
    request = f"{k1},{k2}"
    break

client_socket.sendall(request.encode())

response = client_socket.recv(1024)
print(f'Ответ от сервера: {response.decode()}')

client_socket.close()