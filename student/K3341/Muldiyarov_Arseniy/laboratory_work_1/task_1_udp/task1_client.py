import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 8080)

try:
    message = "Hello, server"
    print(f"Отправляю: {message}")
    # В UDP мы не делаем connect(), а сразу шлем на адрес
    client_socket.sendto(message.encode('utf-8'), server_address)

    # Ждем ответ
    response, _ = client_socket.recvfrom(1024)
    print(f"Получен ответ: {response.decode('utf-8')}")
finally:
    client_socket.close()