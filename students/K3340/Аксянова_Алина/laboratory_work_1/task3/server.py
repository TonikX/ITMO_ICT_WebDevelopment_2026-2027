import socket

HOST = "localhost"
PORT = 8082

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))

server_socket.listen(5)

print(f"HTTP-сервер запущен на http://{HOST}:{PORT}")

while True:
    # принимаем подключение от клиента
    client_connection, client_address = server_socket.accept()
    print(f"Подключение от {client_address}")

    # получаем HTTP-запрос от клиента
    request = client_connection.recv(1024).decode()
    print(f"Запрос клиента:\n{request}")

    # читаем HTML-страницу из файла
    with open("index.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # преобразуем HTML в байты
    html_bytes = html_content.encode("utf-8")

    # формируем HTTP-ответ
    http_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(html_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        + html_content
    )

     # отправляем заголовки и HTML-страницу клиенту
    client_connection.sendall(http_response.encode())

    # закрываем соединение с клиентом
    client_connection.close()