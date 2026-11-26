import socket
import os

HOST = "127.0.0.1"
PORT = 8080

# Создание серверного сокета
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(5)

print(f"Сервер работает по адресу http://{HOST}:{PORT}")

while True:
    client, address = server.accept()

    print(f"Клиент подключился: {address}")

    request = client.recv(1024).decode("utf-8")
    print(request)

    try:
        file_path = os.path.join(
    os.path.dirname(__file__),
    "../../files/index.html"
)
        with open(file_path, "r", encoding="utf-8") as f:
            page = f.read()

        status = "HTTP/1.1 200 OK"

    except FileNotFoundError:
        page = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Ошибка</title>
        </head>
        <body>
            <h1>404 Not Found</h1>
            <p>Страница не найдена.</p>
        </body>
        </html>
        """

        status = "HTTP/1.1 404 Not Found"

    # Перевод страницы в байты
    page_bytes = page.encode("utf-8")

    # Формирование HTTP-ответа
    response = (
        status + "\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        f"Content-Length: {len(page_bytes)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + page_bytes

    # Отправка ответа клиенту
    client.sendall(response)

    client.close()
