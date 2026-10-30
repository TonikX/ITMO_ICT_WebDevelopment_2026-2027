import socket 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(('localhost', 8080))
server_socket.listen(1)
print("Сервер запущен на порту 8080...")

while True: 
    client_connection, client_address = server_socket.accept()
    parameters = client_connection.recv(1024).decode()
    print(f'Подключение от {client_address}')

    a, b, c = parameters.split() 
    if float(a) == 0: 
        client_connection.sendall("Это не квадратное уравнение".encode())
        client_connection.close() 
        continue
    discriminant = float(b)**2 - 4 * float(a) * float(c)
    if discriminant > 0: 
        x1 = (-float(b) + discriminant**0.5)/(2 * float(a)) 
        x2 = (-float(b) - discriminant**0.5)/(2 * float(a))
        answer = "Первый корень: " + str(x1) + " Второй корень: " + str(x2)
        client_connection.sendall(answer.encode())
    elif discriminant == 0: 
        x1 = -float(b)/(2 * float(a))
        answer = "Первый корень: " + str(x1)
        client_connection.sendall(answer.encode())
    else: 
        client_connection.sendall("Нет корней!".encode()) 

    client_connection.close() 

    
    