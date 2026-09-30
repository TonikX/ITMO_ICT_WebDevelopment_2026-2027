import socket

# Параметры сервера
HOST = 'localhost'  # Адрес хоста (localhost для локальных соединений)
PORT = 9090         # Порт, на котором будет работать сервер

# Создаем сокет
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Привязываем сокет к адресу и порту
server_socket.bind((HOST, PORT))

# Начинаем слушать входящие соединения
server_socket.listen(5)
print(f"HTTP сервер запущен на {HOST}:{PORT}...")

while True:
    # Принимаем соединение от клиента
    client_connection, client_address = server_socket.accept()

    with open("index.html", "rb") as f: # читаем в бинарном режиме
        html_bytes = f.read()


    # Формируем HTTP-ответ с заголовками и HTML-контентом
    http_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    # Отправляем HTTP-ответ клиенту
    client_connection.sendall(http_response.encode('utf-8') + html_bytes)

    # Закрываем соединение
    client_connection.close()